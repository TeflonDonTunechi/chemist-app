#!/bin/bash

echo "============================================================"
echo "Building Zeitgeist Teflon Pharma v1.0 Packages"
echo "============================================================"

# Ensure we're in the project root
cd ~/Projects/chemist-app

# Clean previous builds
rm -rf packaging/deb/zeitgeist-teflon-pharma_1.0.0
rm -rf packaging/deb/zeitgeist-teflon-pharma_1.0.0.deb
rm -rf ~/rpmbuild

# Ensure data directory exists
mkdir -p data

# Remove existing database (so it's fresh)
rm -f data/pharma_pos.db

echo ""
echo "Step 1: Building .deb package..."
echo "----------------------------------------------"

# Create debian packaging directory
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/DEBIAN
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/zeitgeist-teflon-pharma
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/bin
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/applications
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/icons/hicolor/256x256/apps

# Copy source files
cp -r src packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/zeitgeist-teflon-pharma/
cp -r resources packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/zeitgeist-teflon-pharma/
mkdir -p packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/zeitgeist-teflon-pharma/data
cp requirements.txt packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/zeitgeist-teflon-pharma/

# Copy icon if exists
if [ -f icon.png ]; then
    cp icon.png packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/icons/hicolor/256x256/apps/zeitgeist-teflon-pharma.png
fi

# Create launcher
cat > packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/bin/zeitgeist-teflon-pharma << 'LAUNCHER'
#!/bin/bash
cd /usr/share/zeitgeist-teflon-pharma
python3 -m src.main "$@"
LAUNCHER
chmod 755 packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/bin/zeitgeist-teflon-pharma

# Create desktop entry
cat > packaging/deb/zeitgeist-teflon-pharma_1.0.0/usr/share/applications/zeitgeist-teflon-pharma.desktop << 'DESKTOP'
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

# Create DEBIAN control file
cat > packaging/deb/zeitgeist-teflon-pharma_1.0.0/DEBIAN/control << 'DEBCONTROL'
Package: zeitgeist-teflon-pharma
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Maintainer: jardani <jardani@localhost>
Depends: python3 (>= 3.8), python3-pyqt6, python3-pyqt6-webengine, python3-sqlalchemy, python3-reportlab, python3-bcrypt, python3-werkzeug, python3-requests, python3-matplotlib
Description: Zeitgeist Teflon Pharma - Complete Pharmacy Management System
 A full-featured pharmacy POS system with inventory management,
 sales tracking, receipt generation, and reporting capabilities.
 Features include:
  * Point of Sale (POS) with search and cart
  * Inventory management with stock tracking
  * Sales reports with PDF export
  * Expiry tracking and alerts
  * User management (admin/cashier roles)
  * Dashboard with sales graphs
  * Receipt generation with preview
  * Multi-currency support (KES)
DEBCONTROL

# Create post-install script
cat > packaging/deb/zeitgeist-teflon-pharma_1.0.0/DEBIAN/postinst << 'POSTINST'
#!/bin/bash
set -e
mkdir -p /usr/share/zeitgeist-teflon-pharma/data
mkdir -p /home/$SUDO_USER/Documents/receipts 2>/dev/null || true
echo "============================================================"
echo "Zeitgeist Teflon Pharma v1.0 installed successfully!"
echo "============================================================"
echo ""
echo "Default login credentials:"
echo "  Admin: admin / zeitgeist"
echo "  Cashier: cashier1 / cashier123"
echo ""
echo "Launch from:"
echo "  - Application Menu: 'Zeitgeist Teflon Pharma'"
echo "  - Terminal: zeitgeist-teflon-pharma"
echo "============================================================"
exit 0
POSTINST
chmod 755 packaging/deb/zeitgeist-teflon-pharma_1.0.0/DEBIAN/postinst

# Build .deb
cd packaging/deb
dpkg-deb --build zeitgeist-teflon-pharma_1.0.0
cd ../..

echo ""
echo "✅ .deb package built successfully!"
echo "   Location: packaging/deb/zeitgeist-teflon-pharma_1.0.0.deb"
echo ""

echo "Step 2: Building .rpm package..."
echo "----------------------------------------------"

# Install rpmbuild tools
sudo dnf install -y rpm-build 2>/dev/null || true

# Create RPM build directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source directory for RPM
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/bin
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/applications

# Copy files
cp -r src /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/
cp -r resources /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/
mkdir -p /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/data
cp requirements.txt /tmp/rpm-source/zeitgeist-teflon-pharma-1.0.0/usr/share/zeitgeist-teflon-pharma/

# Create launcher
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

# Create tarball
cd /tmp/rpm-source
tar -czf ~/rpmbuild/SOURCES/zeitgeist-teflon-pharma-1.0.0.tar.gz zeitgeist-teflon-pharma-1.0.0
cd ~/Projects/chemist-app
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
cp -a * %{buildroot}/

%files
/usr/share/zeitgeist-teflon-pharma/
/usr/bin/zeitgeist-teflon-pharma
/usr/share/applications/zeitgeist-teflon-pharma.desktop

%post
echo "============================================================"
echo "Zeitgeist Teflon Pharma v1.0 installed successfully!"
echo "============================================================"
echo ""
echo "Default login credentials:"
echo "  Admin: admin / zeitgeist"
echo "  Cashier: cashier1 / cashier123"
echo ""
echo "Launch from:"
echo "  - Application Menu: 'Zeitgeist Teflon Pharma'"
echo "  - Terminal: zeitgeist-teflon-pharma"
echo "============================================================"

%changelog
* Sun Sep 06 2026 jardani <jardani@localhost> - 1.0.0-1
- Initial release
- Admin password: zeitgeist
- Empty inventory (users add drugs via CSV or manually)
RPMEOF

# Build RPM
cd ~/rpmbuild
rpmbuild -ba SPECS/zeitgeist-teflon-pharma.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ .rpm package built successfully!"
    echo "   Location: ~/rpmbuild/RPMS/noarch/zeitgeist-teflon-pharma-1.0.0-1*.rpm"
else
    echo "❌ RPM build failed!"
    exit 1
fi

echo ""
echo "============================================================"
echo "Package Summary"
echo "============================================================"
echo "1. .deb package:"
echo "   packaging/deb/zeitgeist-teflon-pharma_1.0.0.deb"
echo ""
echo "2. .rpm package:"
echo "   ~/rpmbuild/RPMS/noarch/zeitgeist-teflon-pharma-1.0.0-1*.rpm"
echo ""
echo "Default credentials:"
echo "  Admin: admin / zeitgeist"
echo "  Cashier: cashier1 / cashier123"
echo ""
echo "Inventory starts empty. Add drugs via CSV import or manually."
echo "============================================================"
