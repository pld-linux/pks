Summary:	PKS - public key server system
Summary(pl):	PKS - serwer kluczy publicznych
Name:		pks
Version:	0.9.4
Release:	3
License:	GPL
Group:		Daemons
Source0:	http://www.mit.edu/people/marc/pks/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Patch0:		%{name}-read_only.patch
URL:		http://www.mit.edu/people/marc/pks/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Prereq:		/sbin/chkconfig

%define		_localstatedir	/var/lib/pks
%define		_datadir	%{_prefix}/share/pks

%description
The public key server system is a set of programs which manages and
provides general access to a database of PGP public keys.

%description -l pl
System serwera kluczy publicznych zawiera zestaw programów do
zarz±dzania i udostêpniania bazy danych kluczy publicznych PGP.

%prep
%setup -q
%patch0 -p1

%build
cd db2-sleepycat/dist/
	aclocal
	autoconf
cd ../..
aclocal
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

# we don't need this
rm -f $RPM_BUILD_ROOT/%{_bindir}/db_*

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/pks

gzip -9nf README NEWS

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
[ -f /var/lib/pks/db/num_keydb ] || /usr/bin/pksclient /var/lib/pks/db create

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
	if [ -f /var/lock/sybsys/pks ]; then
		/etc/rc.d/init.d/pks stop >&2
	fi
	/sbin/chkconfig --del pks
	rm -f %{_datadir}/pks/errors
fi

%files
%defattr(644,root,root,755)
%doc *.gz pks-commands.html
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/pks
%{_mandir}/man*/*
%attr(775,root,pks) %dir %{_localstatedir}
%attr(775,root,pks) %dir %{_localstatedir}/db
%attr(775,root,pks) %dir %{_localstatedir}/incoming
%config(noreplace) %{_sysconfdir}/pksd.conf
