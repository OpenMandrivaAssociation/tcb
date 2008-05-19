Name:	 		tcb
Version:	 	1.0.2
Release:	 	%mkrel 2

%define major		0
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d

Summary:	Libraries and tools implementing the tcb password shadowing scheme
License:	BSD or GPL
Group:		System/Libraries
URL: 		http://www.openwall.com/tcb/
Source0:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz

BuildRoot: 	%{_tmppath}/%{name}-%{version}
BuildRequires:	glibc-crypt_blowfish-devel
BuildRequires:	pam-devel

Requires:	%{libname} = %{version}
Requires:	pam_tcb = %{version}
Requires:	nss_tcb = %{version}
Requires:	shadow-utils >= 4.0.12-10mdv

%description
The tcb package consists of three components: pam_tcb, libnss_tcb, and
libtcb.  pam_tcb is a PAM module which supersedes pam_unix and pam_pwdb.
It also implements the tcb password shadowing scheme (see tcb(5) for
details).  The tcb scheme allows many core system utilities (passwd(1)
being the primary example) to operate with little privilege.  libnss_tcb
is the accompanying NSS module.  libtcb contains code shared by the
PAM and NSS modules and is also used by programs from the shadow-utils
package.


%package -n %{libname}
Summary:        Libraries and tools implementing the tcb password shadowing scheme
Group:          System/Libraries
Requires:	glibc-crypt_blowfish
Requires(pre):	setup >= 2.7.12-2mdv

%description -n %{libname}
libtcb contains code shared by the PAM and NSS modules and is also used
by programs from the shadow-utils package.


%package -n pam_tcb
Summary:	PAM module for TCB
Group:		System/Libraries
Requires:	%{libname} = %{version}
Conflicts:	pam <= 0.99.8.1-8mdv

%description -n pam_tcb
pam_tcb is a PAM module which supersedes pam_unix and pam_pwdb.
It also implements the tcb password shadowing scheme (see tcb(5) for
details).  The tcb scheme allows many core system utilities (passwd(1)
being the primary example) to operate with little privilege.


%package -n nss_tcb
Summary:	NSS library for TCB
Group:		System/Libraries
Requires(post):	rpm-helper
Requires(postun): rpm-helper
Requires:	%{libname} = %{version}

%description -n nss_tcb
libnss_tcb is the accompanying NSS module for pam_tcb.


%package -n %{develname}
Summary:	Libraries and header files for building tcb-aware applications
Group:		Development/Other
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
This package contains static libraries and header files needed for
building tcb-aware applications.


%prep
%setup -q


%build
%serverbuild
CFLAGS="%{optflags} -DENABLE_SETFSUGID" %make


%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

make install-non-root install-pam_unix install-pam_pwdb \
    DESTDIR=%{buildroot} \
    MANDIR=%{_mandir} \
    LIBDIR=%{_libdir} \
    LIBEXECDIR=%{_libdir} \
    SLIBDIR=/%{_lib}


%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig


%post -n nss_tcb
/sbin/ldconfig
%_post_service nscd


%postun -n nss_tcb
/sbin/ldconfig
%_preun_service nscd


%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}


%files
%defattr(-,root,root)
%doc LICENSE
/sbin/tcb_convert
/sbin/tcb_unconvert
%{_mandir}/man8/tcb_convert.8*
%{_mandir}/man8/tcb_unconvert.8*

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/libtcb.so.*
%attr(0710,root,chkpwd) %verify(not mode group) %dir %{_libdir}/chkpwd
%attr(2711,root,shadow) %verify(not mode group) %{_libdir}/chkpwd/tcb_chkpwd
%{_mandir}/man5/tcb.5*

%files -n nss_tcb
%defattr(-,root,root)
/%{_lib}/libnss_tcb.so.2

%files -n pam_tcb
%defattr(-,root,root)
/%{_lib}/security/pam_pwdb.so
/%{_lib}/security/pam_tcb.so
/%{_lib}/security/pam_unix.so
/%{_lib}/security/pam_unix_acct.so
/%{_lib}/security/pam_unix_auth.so
/%{_lib}/security/pam_unix_passwd.so
/%{_lib}/security/pam_unix_session.so
%{_mandir}/man8/pam_pwdb.8*
%{_mandir}/man8/pam_tcb.8*
%{_mandir}/man8/pam_unix.8*

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/tcb.h
%{_libdir}/libtcb.a
%{_libdir}/libtcb.so

