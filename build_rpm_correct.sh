#!/bin/bash

echo "Building Zeitgeist Teflon Pharma RPM package..."

# Clean previous builds
rm -rf ~/rpmbuild

# Install rpmbuild tools
sudo dnf install -y rpm-build

# Create RPM build directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create the source directory
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/bin
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/applications

# Copy files from current directory
cp -r src /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/
cp -r resources /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/
cp requirements.txt /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/ 2>/dev/null || true
cp icon.png /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/ 2>/dev/null || true

# Create launcher script
cat > /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/bin/zeitgeist-teflon-pharma << 'LAUNCHER'
#!/bin/bash
cd /usr/share/zeitgeist-teflon-pharma
python3 -m src.main "$@"
LAUNCHER
chmod 755 /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/bin/zeitgeist-teflon-pharma

# Create desktop entry
cat > /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/applications/zeitgeist-teflon-pharma.desktop << 'DESKTOP'
[Desktop Entry]
Version=1.0.0
Type=Application
Name=Zeitgeist Teflon Pharma
Comment=Pharmacy Management System
Exec=zeitgeist-teflon-pharma
Icon=zeitgeist-teflon-pharma
Terminal=false
Categories=Office;Business;Medical;
StartupNotify=true
DESKTOP

# Create the tarball
cd /tmp/rpm-source
tar -czf ~/rpmbuild/SOURCES/zeitgeist-teflon-pharma-1.0.0.tar.gz zeitgeist-teflon-pharma-1.0.0
cd ~/Projects/chemist-app

# Clean up temp directory
rm -rf /tmp/rpm-source

# Create spec file
cat > ~/rpmbuild/SPECS/zeitgeist-teflon-pharma.spec << 'RPMEOF'
%define name zeitgeist-teflon-pharma
%define version 1.0.0
%define release 1

Name:           %{name}
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        Complete Pharmacy Management System

License:        MIT
URL:            https://github.com/jardani/zeitgeist-teflon-pharma
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3 >= 3.8
Requires:       python3-pyqt6
Requires:       python3-pyqt6-webengine
Requires:       python3-sqlalchemy
Requires:       python3-reportlab
Requires:       python3-bcrypt
Requires:       python3-werkzeug
Requires:       python3-requests
Requires:       python3-matplotlib

%description
Zeitgeist Teflon Pharma - A full-featured pharmacy POS system with inventory
management, sales tracking, receipt generation, and reporting capabilities.

Features:
  * Point of Sale (POS) with search and cart
  * Inventory management with stock tracking
  * Sales reports with PDF export
  * Expiry tracking and alerts
  * User management (admin/cashier roles)
  * Dashboard with sales graphs
  * Receipt generation with preview
  * Multi-currency support (KES)

%prep
%setup -q

%install
# Copy everything from the source directory to buildroot
cp -a * %{buildroot}/

%files
/usr/share/zeitgeist-teflon-pharma/
/usr/bin/zeitgeist-teflon-pharma
/usr/share/applications/zeitgeist-teflon-pharma.desktop

%post
echo "===================================================="
echo "Zeitgeist Teflon Pharma installed successfully!"
echo "===================================================="
echo "Launch from:"
echo "  - Application Menu: 'Zeitgeist Teflon Pharma'"
echo "  - Terminal: zeitgeist-teflon-pharma"
echo "===================================================="
echo ""
echo "Default login credentials:"
echo "  Admin: jardani / jardani13"
echo "  Cashier: cashier1 / cashier123"
echo "===================================================="

%changelog
* Sun Sep 06 2026 jardani <jardani@localhost> - 1.0.0-1
- Initial package release
RPMEOF

# Build the RPM
echo "Building RPM package..."
cd ~/rpmbuild
rpmbuild -ba SPECS/zeitgeist-teflon-pharma.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================================="
    echo "RPM built successfully!"
    echo "===================================================="
    echo "Location: ~/rpmbuild/RPMS/noarch/zeitgeist-teflon-pharma-1.0.0-1*.rpm"
    ls -lh ~/rpmbuild/RPMS/noarch/zeitgeist-teflon-pharma-*.rpm
    echo ""
    echo "To install:"
    echo "sudo dnf install ~/rpmbuild/RPMS/noarch/zeitgeist-teflon-pharma-1.0.0-1*.rpm"
    echo "===================================================="
else
    echo "RPM build failed!"
    exit 1
fi
