# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _without_maven 1
%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define base_name       pool
%define short_name      commons-%{base_name}
%define section         free

Name:           jakarta-commons-pool
Version:        1.3
Release:        %mkrel 9.2.2
Epoch:          0
Summary:        Jakarta Commons Pool Package
License:        Apache Software License
Group:          Development/Java
Source0:        http://www.apache.org/dist/jakarta/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{base_name}-%{version}-jpp-depmap.xml
Source5:        commons-build.tar.gz
# svn export -r '{2007-02-15}' http://svn.apache.org/repos/asf/jakarta/commons/proper/commons-build/trunk/ commons-build
# tar czf commons-build.tar.gz commons-build
Source6:        pool-tomcat5-build.xml
Patch0:         jakarta-commons-pool-build.patch

Url:            http://jakarta.apache.org/commons/%{base_name}/
BuildRequires:  ant
BuildRequires:  junit
BuildRequires:  jpackage-utils > 0:1.6
BuildRequires:  java-javadoc
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
BuildRequires:  maven-plugins-base
BuildRequires:  maven-plugin-test
BuildRequires:  maven-plugin-xdoc
BuildRequires:  maven-plugin-license
BuildRequires:  maven-plugin-changes
BuildRequires:  maven-plugin-jdepend
BuildRequires:  maven-plugin-jdiff
BuildRequires:  maven-plugin-jxr
BuildRequires:  maven-plugin-tasklist
BuildRequires:  saxon
BuildRequires:  saxon-scripts
BuildRequires:  xml-commons-jaxp-1.3-apis
BuildRequires:  xerces-j2
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Provides:       %{short_name} = %{epoch}:%{version}-%{release} 
Obsoletes:      %{short_name} < %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description
The goal of Pool package it to create and maintain an object 
(instance) pooling package to be distributed under the ASF license.
The package should support a variety of pool implementations, but
encourage support of an interface that makes these implementations
interchangeable.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires:       java-javadoc

%description javadoc
Javadoc for %{name}.

%package tomcat5
Summary:        Pool dependency for Tomcat5
Group:          Development/Java

%description tomcat5
Pool dependency for Tomcat5

%if %{with_maven}
%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.
%endif

%prep
cat <<EOT

                If you dont want to build with maven,
                give rpmbuild option '--without maven'

EOT

%setup -q -n %{short_name}-%{version}-src
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
gzip -dc %{SOURCE5} | tar xf -
%patch0
cp %{SOURCE6} .

%build
mkdir ./tmp
%if %{with_maven}
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done

maven \
        -Dmaven.javadoc.source=1.4 \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$(pwd)/.maven \
        jar javadoc xdoc:transform
%else
%{ant} -Djava.io.tmpdir=. clean dist 
%endif

%{ant} -f pool-tomcat5-build.xml

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
%if %{with_maven}
install -m 644 target/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%else
install -m 644 dist/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%endif

#tomcat5 jar
install -m 644 pool-tomcat5/%{short_name}-tomcat5.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-tomcat5-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 

%if %{with_maven}
# manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -pr target/docs/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%post tomcat5
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun tomcat5
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif


%files
%defattr(0644,root,root,0755)
%doc README.txt LICENSE.txt NOTICE.txt RELEASE-NOTES.txt
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{short_name}.jar
%{_javadir}/%{short_name}-%{version}.jar

%if %{gcj_support}
%attr(-,root,root) 
%dir %{_libdir}/gcj/%{name}
%{_libdir}/gcj/%{name}/%{name}-%{version}.jar.db
%{_libdir}/gcj/%{name}/%{name}-%{version}.jar.so
%endif

%files tomcat5
%defattr(0644,root,root,0755)
%{_javadir}/*-tomcat5*.jar

%if %{gcj_support}
%attr(-,root,root)
%{_libdir}/gcj/%{name}/*-tomcat5*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%if %{with_maven}
%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
%endif
