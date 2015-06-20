# ClearSync File Watch Plugin RPM spec
Name: csplugin-filewatch
Version: 1.0
Release: 17%{dist}
Vendor: ClearFoundation
License: GPL
Group: System/Plugins
Packager: ClearFoundation
Source: %{name}-%{version}.tar.gz
BuildRoot: /var/tmp/%{name}-%{version}
Requires: clearsync >= 1.5 /sbin/service /usr/bin/sudo
BuildRequires: clearsync-devel >= 1.5
BuildRequires: autoconf >= 2.63
BuildRequires: automake
BuildRequires: libtool
BuildRequires: expat-devel
Summary: ClearSync file watch plugin
Requires(pre): /sbin/ldconfig

%description
This plugin watches file and/or directory changes and can
execute configurable actions.
Report bugs to: http://www.clearfoundation.com/docs/developer/bug_tracker/

# Build
%prep
%setup -q
./autogen.sh
%{configure}

%build
make %{?_smp_mflags}

# Install
%install
make install DESTDIR=$RPM_BUILD_ROOT
rm -f ${RPM_BUILD_ROOT}/%{_libdir}/libcsplugin-filewatch.a
rm -f ${RPM_BUILD_ROOT}/%{_libdir}/libcsplugin-filewatch.la

# Clean-up
%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Post install
%post
/sbin/ldconfig
%if "0%{dist}" == "0.v6"
/sbin/service clearsyncd condrestart 2>&1 || :
%else
/usr/bin/systemctl reload-or-restart clearsync.service -q
%endif

# Add command(s) to sudo configuration
CHECK=`grep "^clearsync[[:space:]]*" /etc/sudoers`
if [ -z "$CHECK" ]; then
    echo "Cmnd_Alias CLEARSYNC = " >> /etc/sudoers
	echo "clearsync ALL=NOPASSWD: CLEARSYNC" >> /etc/sudoers
fi

CMD=/sbin/service
LINE=`grep "^Cmnd_Alias CLEARSYNC" /etc/sudoers 2>/dev/null`
CHECK=`echo $LINE, | grep $CMD,`
if [ -z "$CHECK" ]; then
	ESCAPE=`echo $CMD | sed 's/\//\\\\\//g'`
	sed -i -e "s/Cmnd_Alias CLEARSYNC.*=/Cmnd_Alias CLEARSYNC = $ESCAPE,/i" /etc/sudoers
	sed -i -e "s/[[:space:]]*,[[:space:]]*$//i" /etc/sudoers
	chmod 440 /etc/sudoers
fi

# Post uninstall
%postun
/sbin/ldconfig
%if "0%{dist}" == "0.v6"
/sbin/service clearsyncd condrestart 2>&1 || :
%else
/usr/bin/systemctl reload-or-restart clearsync.service -q
%endif

# Files
%files
%defattr(-,root,root)
%{_libdir}/libcsplugin-filewatch.so*

