%define set_tcbver 0.7

%define major	0
%define nssmajor 2
%define libname	%mklibname %{name} %{major}
%define libnss	%mklibname nss_%{name} %{nssmajor}
%define devname	%mklibname %{name} -d

Summary:	Libraries and tools implementing the tcb password shadowing scheme
Name:		tcb
Version:	1.1
Release:	4
License:	BSD or GPL
Group:		System/Libraries
URL: 		http://www.openwall.com/tcb/
Source0:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz.sign
Source2:	set_tcb-%{set_tcbver}.tar.bz2
Patch0:		tcb-1.0.2-assume_shadow.patch
Patch2:		set_tcb-0.7-nofork-blowfish-1.2.diff
# Fix handling of negative fields in /etc/shadow on x86_64 with recent glibc (#52330)
Patch3:		tcb-1.0.3-warn.patch
# Use translations from pam for the available messages (#59331)
Patch4:		tcb-1.0.3-i18n.patch
Patch5:		tcb-1.1-nss_soname_fix.diff
Patch6:		tcb-1.1-link-against-libtirpc.patch
BuildRequires:	glibc-crypt_blowfish-devel >= 1.2
BuildRequires:	pam-devel
%if "%{distepoch}" >= "2013.0"
# (tpg) provides rpc/rpc.h
BuildRequires:	pkgconfig(libtirpc)
%endif

# for what was in the lib pkg (group IDs)
Requires(pre):	setup >= 2.7.12-2
Requires:	shadow-utils >= 4.0.12-10
Requires:	pam_tcb = %{version}-%{release}
Requires:	%{libnss} = %{version}-%{release}
Conflicts:	%{libname} < 1.1-2

%description
The tcb package consists of three components: pam_tcb, libnss_tcb, and
libtcb.  pam_tcb is a PAM module which supersedes pam_unix and pam_pwdb.
It also implements the tcb password shadowing scheme (see tcb(5) for
details).  The tcb scheme allows many core system utilities (passwd(1)
being the primary example) to operate with little privilege.  libnss_tcb
is the accompanying NSS module.  libtcb contains code shared by the
PAM and NSS modules and is also used by programs from the shadow-utils
package.

%package -n	%{libname}
Summary:        Libraries and tools implementing the tcb password shadowing scheme
Group:          System/Libraries

%description -n	%{libname}
libtcb contains code shared by the PAM and NSS modules and is also used
by programs from the shadow-utils package.

%package -n	pam_tcb
Summary:	PAM module for TCB
Group:		System/Libraries
Conflicts:	pam < 0.99.8.1-13
Conflicts:	%{_lib}pam0 < 0.99.8.1-13

%description -n	pam_tcb
pam_tcb is a PAM module which supersedes pam_unix and pam_pwdb.
It also implements the tcb password shadowing scheme (see tcb(5) for
details).  The tcb scheme allows many core system utilities (passwd(1)
being the primary example) to operate with little privilege.

%package -n	%{libnss}
Summary:	NSS library for TCB
Group:		System/Libraries
Requires(post):	rpm-helper
Requires(postun):rpm-helper
%rename		nss_tcb

%description -n	%{libnss}
libnss_tcb is the accompanying NSS module for pam_tcb.

%package -n	%{devname}
Summary:	Libraries and header files for building tcb-aware applications
Group:		Development/Other
Requires:	%{libname} >= %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains static libraries and header files needed for
building tcb-aware applications.

%prep
%setup -q -a2
%patch0 -p1
%patch2 -p0
%patch3 -p1
%patch4 -p1
%patch5 -p0
%patch6 -p1 -b .tirpc~

%build
%serverbuild
CFLAGS="%{optflags} -DENABLE_SETFSUGID" LDFLAGS="%{ldflags}" %make LIBEXECDIR=%{_libexecdir} LIBDIR=%{_libdir} SLIBDIR=/%{_lib}

%install
make install-non-root install-pam_pwdb \
    DESTDIR=%{buildroot} \
    MANDIR=%{_mandir} \
    LIBDIR=%{_libdir} \
    LIBEXECDIR=%{_libdir} \
    SLIBDIR=/%{_lib}

install -m750 set_tcb-%{set_tcbver}/set_tcb -D %{buildroot}%{_sbindir}/set_tcb
install -m644 set_tcb-%{set_tcbver}/set_tcb.8 -D %{buildroot}%{_mandir}/man8/set_tcb.8*

%post -n %{libnss}
if [ -f %{_initrddir}/nscd ]; then
    %_post_service nscd
fi

%postun -n %{libnss}
if [ -f %{_initrddir}/nscd ]; then
    %_preun_service nscd
fi

%files
%doc LICENSE
/sbin/tcb_convert
/sbin/tcb_unconvert
%attr(0755,root,chkpwd) %verify(not mode group) %dir %{_libexecdir}/chkpwd
%attr(2755,root,shadow) %verify(not mode group) %{_libexecdir}/chkpwd/tcb_chkpwd
%{_mandir}/man5/tcb.5*
%{_sbindir}/set_tcb
%{_mandir}/man8/tcb_convert.8*
%{_mandir}/man8/tcb_unconvert.8*
%{_mandir}/man8/set_tcb.8*

%files -n %{libname}
/%{_lib}/libtcb.so.%{major}*

%files -n %{libnss}
/%{_lib}/libnss_tcb.so.%{nssmajor}

%files -n pam_tcb
/%{_lib}/security/pam_pwdb.so
/%{_lib}/security/pam_tcb.so
%{_mandir}/man8/pam_pwdb.8*
%{_mandir}/man8/pam_tcb.8*

%files -n %{devname}
%{_includedir}/tcb.h
%{_libdir}/libtcb.a
%{_libdir}/libtcb.so
