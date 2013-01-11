%define set_tcbver 0.7

%define major 0
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define libpamname %mklibname pam 0

Summary:	Libraries and tools implementing the tcb password shadowing scheme
Name:		tcb
Version:	1.0.6
Release:	%mkrel 3
License:	BSD or GPL
Group:		System/Libraries
URL: 		http://www.openwall.com/tcb/
Source0:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.openwall.com/pub/projects/tcb/%{name}-%{version}.tar.gz.sign
Source2:	set_tcb-%{set_tcbver}.tar.bz2
Patch0:		tcb-1.0.2-assume_shadow.patch
Patch2:		set_tcb-0.7-nofork.patch
# Fix handling of negative fields in /etc/shadow on x86_64 with recent glibc (#52330)
Patch3:		tcb-1.0.3-warn.patch
# Use translations from pam for the available messages (#59331)
Patch4:		tcb-1.0.3-i18n.patch
BuildRequires:	glibc-crypt_blowfish-devel
BuildRequires:	pam-devel
%if %mdvver >= 201300
# (tpg) provides rpc/rpc.h
BuildRequires:	tirpc-devel
%endif
Requires:	%{libname} >= %{version}
Requires:	pam_tcb = %{version}
Requires:	nss_tcb = %{version}
Requires:	shadow-utils >= 4.0.12-10mdv
BuildRoot: 	%{_tmppath}/%{name}-%{version}

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
Requires:	%{libname} >= %{version}
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
Requires:	%{libname} >= %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
This package contains static libraries and header files needed for
building tcb-aware applications.


%prep
%setup -q -a2
%patch0 -p1
%patch2 -p0
%patch3 -p1
%patch4 -p1

cat Make.defs | sed -e "s|LIBEXECDIR = /usr/libexec|LIBEXECDIR = %{_libdir}|" >Make.defs.new
cat Make.defs.new | sed -e "s|/lib$|/%{_lib}|g" >Make.defs

%build
%serverbuild
CFLAGS="%{optflags} -DENABLE_SETFSUGID" %make

%install
rm -rf %{buildroot}

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
rm -rf %{buildroot}

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
/%{_lib}/libtcb.so.%{major}*
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


%changelog
* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.6-1mdv2011.0
+ Revision: 670668
- mass rebuild

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.6-0mdv2011.0
+ Revision: 609635
- 1.0.6
- drop P5, it's applied upstream
- spec file massage

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.3-7mdv2011.0
+ Revision: 607982
- rebuild

* Fri Jun 04 2010 Pascal Terjan <pterjan@mandriva.org> 1.0.3-6mdv2010.1
+ Revision: 547106
- fix tcb_is_suspect (breaks at least on btrfs) (#59588)
- translate more strings

* Fri May 21 2010 Pascal Terjan <pterjan@mandriva.org> 1.0.3-4mdv2010.1
+ Revision: 545602
- Use translations from pam for available messages (#59331)

* Thu Dec 17 2009 Pascal Terjan <pterjan@mandriva.org> 1.0.3-3mdv2010.1
+ Revision: 479732
- Fix handling of negative fields in /etc/shadow on x86_64 with recent glibc (#52330)

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 1.0.3-2mdv2010.0
+ Revision: 427284
- rebuild

* Thu Apr 09 2009 Oden Eriksson <oeriksson@mandriva.com> 1.0.3-1mdv2009.1
+ Revision: 365388
- 1.0.3
- drop the exit patch, it's implemented upstream (P1)

* Tue Mar 31 2009 Pascal Terjan <pterjan@mandriva.org> 1.0.2-21mdv2009.1
+ Revision: 362887
- Do not set fork option

* Mon Mar 30 2009 Pascal Terjan <pterjan@mandriva.org> 1.0.2-20mdv2009.1
+ Revision: 362228
- Don't call atexit signals in child process (#43106)

* Thu Dec 18 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-19mdv2009.1
+ Revision: 315404
- set_tcb 0.7; should fix some issues with changing password hashes

* Wed Aug 27 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-18mdv2009.0
+ Revision: 276450
- set_tcb 0.6

* Mon Aug 25 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-17mdv2009.0
+ Revision: 275953
- relax permissions of the password checker

* Tue Aug 12 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-16mdv2009.0
+ Revision: 271142
- remove the %%trigger script, due to install ordering it will never be run so put it in the pam package instead

* Sun Aug 10 2008 Olivier Blin <oblin@mandriva.com> 1.0.2-15mdv2009.0
+ Revision: 270204
- conflict with pam and libpam0 < 0.99.8.1-13
  (or else we can end up with no pam_unix on the system)

* Sat Aug 09 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-14mdv2009.0
+ Revision: 270080
- set_tcb 0.5
  don't install pam_unix compat symlinks
  call set_tcb to migrate login.defs and system-auth

* Fri Aug 08 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-13mdv2009.0
+ Revision: 269005
- set_tcb 0.3

* Sat Jul 19 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-12mdv2009.0
+ Revision: 238837
- set_tcb 0.2

* Mon Jul 14 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-11mdv2009.0
+ Revision: 234436
- include the set_tcb script

* Sat Jun 14 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-10mdv2009.0
+ Revision: 219107
- really fix the nscd restart

* Wed Jun 11 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-9mdv2009.0
+ Revision: 218049
- make the nscd test exit 0 if the nscd initscript doesn't exist

* Mon Jun 09 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-8mdv2009.0
+ Revision: 217264
- make sure the nscd initscript exists before trying to restart it

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sat May 31 2008 Frederik Himpe <fhimpe@mandriva.org> 1.0.2-7mdv2009.0
+ Revision: 213851
- Fix conflicts to make it upgrade without conflicts from 2008.1

* Fri May 30 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-6mdv2009.0
+ Revision: 213352
- make /usr/lib/chkpwd world-executable so gnome-screensaver will work (as we cannot make it sgid chkpwd)

* Fri May 23 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-5mdv2009.0
+ Revision: 210386
- further make fixes

* Fri May 23 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-4mdv2009.0
+ Revision: 210180
- fix where pam_tcb is finding it's password helper

* Wed May 21 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-3mdv2009.0
+ Revision: 209784
- added assume_shadow.patch: pam_unix assumes that 'shadow' is set always,
  but pam_tcb only assumes this for account, so add it to the other pam types

* Mon May 19 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-2mdv2009.0
+ Revision: 209102
- add conflicts on old pre-TCB-aware pam
- requires TCB-aware shadow-utils

* Sun May 18 2008 Vincent Danen <vdanen@mandriva.com> 1.0.2-1mdv2009.0
+ Revision: 208802
- fix group on the -devel package
- import tcb from Annvix


