Name:	 		tcb
Version:	 	1.0.3
Release:	 	%mkrel 7
%define set_tcbver	0.7

%define major		0
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d
%define libpamname	%mklibname pam 0

Summary:	Libraries and tools implementing the tcb password shadowing scheme
License:	BSD or GPL
Group:		System/Libraries
URL: 		http://www.openwall.com/tcb/
Source0:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz
Source1:	set_tcb-%{set_tcbver}.tar.bz2
Patch0:		tcb-1.0.2-assume_shadow.patch
Patch2:		set_tcb-0.7-nofork.patch
# Fix handling of negative fields in /etc/shadow on x86_64 with recent glibc (#52330)
Patch3:		tcb-1.0.3-warn.patch
# Use translations from pam for the available messages (#59331)
Patch4:		tcb-1.0.3-i18n.patch
# Fix tcb_is_suspect (breaks at least on btrfs) (#59588)
Patch5:		tcb-1.0.3-btrfs.patch
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
Conflicts:	pam < 0.99.8.1-13
Conflicts:	%{libpamname} < 0.99.8.1-13

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
%setup -q -a 1
%patch0 -p1
%patch2 -p0
%patch3 -p1
%patch4 -p1
%patch5 -p1

cat Make.defs | sed -e "s|LIBEXECDIR = /usr/libexec|LIBEXECDIR = %{_libdir}|" >Make.defs.new
cat Make.defs.new | sed -e "s|/lib$|/%{_lib}|g" >Make.defs


%build
%serverbuild
CFLAGS="%{optflags} -DENABLE_SETFSUGID" %make


%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

make install-non-root install-pam_pwdb \
    DESTDIR=%{buildroot} \
    MANDIR=%{_mandir} \
    LIBDIR=%{_libdir} \
    LIBEXECDIR=%{_libdir} \
    SLIBDIR=/%{_lib}

mkdir -p %{buildroot}%{_sbindir}
install -m 0750 set_tcb-%{set_tcbver}/set_tcb %{buildroot}%{_sbindir}/
install -m 0644 set_tcb-%{set_tcbver}/set_tcb.8 %{buildroot}%{_mandir}/man8/


%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif


%post -n nss_tcb
%if %mdkversion < 200900
/sbin/ldconfig
%endif
if [ -f %{_initrddir}/nscd ]; then
    %_post_service nscd
fi


%postun -n nss_tcb
%if %mdkversion < 200900
/sbin/ldconfig
%endif
if [ -f %{_initrddir}/nscd ]; then
    %_preun_service nscd
fi


%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}


%files
%defattr(-,root,root)
%doc LICENSE
/sbin/tcb_convert
/sbin/tcb_unconvert
%{_sbindir}/set_tcb
%{_mandir}/man8/tcb_convert.8*
%{_mandir}/man8/tcb_unconvert.8*
%{_mandir}/man8/set_tcb.8*

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/libtcb.so.*
%attr(0755,root,chkpwd) %verify(not mode group) %dir %{_libdir}/chkpwd
%attr(2755,root,shadow) %verify(not mode group) %{_libdir}/chkpwd/tcb_chkpwd
%{_mandir}/man5/tcb.5*

%files -n nss_tcb
%defattr(-,root,root)
/%{_lib}/libnss_tcb.so.2

%files -n pam_tcb
%defattr(-,root,root)
/%{_lib}/security/pam_pwdb.so
/%{_lib}/security/pam_tcb.so
%{_mandir}/man8/pam_pwdb.8*
%{_mandir}/man8/pam_tcb.8*

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/tcb.h
%{_libdir}/libtcb.a
%{_libdir}/libtcb.so

