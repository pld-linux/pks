# TODO: fix+standardize useradd and groupadd
Summary:	PKS - public key server system
Summary(pl):	PKS - serwer kluczy publicznych
Name:		pks
Version:	0.9.4
Release:	4
License:	GPL
Group:		Daemons
Source0:	http://www.mit.edu/people/marc/pks/%{name}-%{version}.tar.gz
# Source0-md5:	365d062bbc3f7bfda745474693d0fdec
Source1:	%{name}.init
Source2:	pks_help.en
Patch0:		%{name}-read_only.patch
Patch1:		%{name}-ac25.patch
Patch2:		http://www.mit.edu/people/marc/pks/pks094-patch2
Patch3:		http://www.mit.edu/people/marc/pks/x509patch
Patch4:		%{name}-noinstall-db2.patch
URL:		http://www.mit.edu/people/marc/pks/
BuildRequires:	autoconf
BuildRequires:	automake
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/lib/pks
%define		_datadir	%{_prefix}/share/pks

%description
The public key server system is a set of programs which manages and
provides general access to a database of PGP public keys.

%description -l pl
System serwera kluczy publicznych zawiera zestaw programów do
zarządzania i udostępniania bazy danych kluczy publicznych PGP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0
%patch4 -p1

%build
cd db2-sleepycat/dist/
	%{__aclocal}
	%{__autoconf}
cd ../..
%{__aclocal}
%{__autoconf}
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	prefix=$RPM_BUILD_ROOT%{_prefix} \
	bindir=$RPM_BUILD_ROOT%{_bindir} \
	man5dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	man8dir=$RPM_BUILD_ROOT%{_mandir}/man8 \
	sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	datadir=$RPM_BUILD_ROOT%{_datadir} \
	localstatedir=$RPM_BUILD_ROOT%{_localstatedir}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/pks
install %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
grep -q pks /etc/group || (
    /usr/sbin/groupadd -g 92 -r -f pks 1>&2 || :
)
grep -q pks /etc/passwd || (
    /usr/sbin/useradd -M -o -r -u 92 \
        -g pks -c "public key server system" -d /var/lib/pks pks 1>&2 || :
)

%post
if [ "$1" = "1" ]; then
	/sbin/chkconfig --add pks
	echo "Run \"/etc/rc.d/init.d/pks start\" to start pks." >&2
else
	if [ -f /var/lock/subsys/pks ]; then
		/etc/rc.d/init.d/pks restart >&2
	fi
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/pks ]; then
		/etc/rc.d/init.d/pks stop >&2
	fi
	/sbin/chkconfig --del pks
	rm -f %{_datadir}/pks/errors
fi

%files
%defattr(644,root,root,755)
%doc README NEWS pks-commands.html
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/pks
%{_mandir}/man*/*
%{_datadir}
%attr(775,root,pks) %dir %{_localstatedir}
%attr(775,root,pks) %dir %{_localstatedir}/db
%attr(775,root,pks) %dir %{_localstatedir}/incoming
%config(noreplace) %{_sysconfdir}/pksd.conf
