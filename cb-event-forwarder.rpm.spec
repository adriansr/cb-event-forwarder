%define name cb-event-forwarder
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%define bare_version 3.7.4

%define release 1

Summary: VMware Carbon Black EDR Event Forwarder
Name: %{name}
Version: %{bare_version}
Release: %{release}%{?dist}
Source0: %{name}-%{bare_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: VMware Carbon Black
Url: http://www.carbonblack.com/

%description
VMware Carbon Black EDR Event Forwarder is a standalone service that will listen on the EDR enterprise bus and
export events (both watchlist/feed hits as well as raw endpoint events, if configured) in a normalized JSON or LEEF format.
The events can be saved to a file, delivered to a network service or archived automatically to an Amazon AWS S3 bucket.
These events can be consumed by any external system that accepts JSON or LEEF, including Splunk and IBM QRadar.

%prep
%setup -n %{name}-%{bare_version}

$build
cd ./src/github.com/carbonblack/cb-event-forwarder && make rpmbuild 

%install
cd ./src/github.com/carbonblack/cb-event-forwarder && make rpminstall

%clean
rm -rf $RPM_BUILD_ROOT

%pretrans
#!/bin/sh
# since the "old" cb-event-forwarder controls itself through the file we're about to replace
# we should stop it before we install anything on upgrade
# but first we have to stop the service if already running under Upstart
%if "%{dist}" == ".el6"
initctl stop cb-event-forwarder &> /dev/null || :
%endif

if [ -x /etc/init.d/cb-event-forwarder ] || [ -e /etc/systemd/system/cb-event-forwarder.service ]; then
    service cb-event-forwarder stop &> /dev/null || :
fi

%post
#!/bin/sh
mkdir -p /var/log/cb/integrations/cb-event-forwarder
mkdir -p /var/cb/data


%files -f MANIFEST
%defattr(-,root,root)
%config(noreplace) /etc/cb/integrations/event-forwarder/cb-event-forwarder.conf

%defattr(755,root,root,-)
/usr/share/cb/integrations/event-forwarder/cb-edr-fix-permissions.sh

