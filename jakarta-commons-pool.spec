%define base_name	pool
%define short_name	commons-%{base_name}
%define name		jakarta-%{short_name}
%define version		1.3
%define	section		free
%define gcj_support	1

Name:		%{name}
Version:	%{version}
Release:	%mkrel 2.2
Epoch:		0
Summary:	Jakarta Commons Pool Package
License:	Apache License
Group:		Development/Java
#Vendor:		JPackage Project
#Distribution:	JPackage
Source0:	http://www.apache.org/dist/jakarta/commons/pool/source/commons-pool-%{version}-src-MDVCLEAN.tar.bz2
Url:		http://jakarta.apache.org/commons/%{base_name}/
BuildRequires:	ant
BuildRequires:	jakarta-commons-collections >= 0:2.0
BuildRequires:  jpackage-utils > 0:1.5
Requires:	jakarta-commons-collections >= 0:2.0
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
Requires(post):   java-gcj-compat
Requires(postun): java-gcj-compat
%else
BuildArch:      noarch
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot
Provides:	%{short_name}
Obsoletes:	%{short_name}

%description
The goal of Pool package it to create and maintain an object 
(instance) pooling package to be distributed under the ASF license.
The package should support a variety of pool implementations, but
encourage support of an interface that makes these implementations
interchangeable.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{short_name}-%{version}-src
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;

%build
mkdir ./tmp
export CLASSPATH=%(build-classpath commons-collections)
%ant -Djava.io.tmpdir=. clean dist

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

# fix end-of-line
%{__perl} -pi -e 's/\r\n/\n/g' *.txt

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc README.txt LICENSE.txt
%{_javadir}/*
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}


