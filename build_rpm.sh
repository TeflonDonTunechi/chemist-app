#!/bin/bash

# Build RPM for Zeitgeist Teflon Pharma

echo "Building Zeitgeist Teflon Pharma RPM package..."

# Install rpmbuild tools if not already installed
sudo dnf install -y rpm-build

# Create RPM build directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create spec file
cat > ~/rpmbuild/SPECS/zeitgeist-teflon-pharma.spec << 'RPMEOF'
%define name zeitgeist-teflon-pharma
%define version 1.0.0
%define release 1
%define summary "Complete Pharmacy Management System"

Name:           %{name}
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        %{summary}

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
mkdir -p %{buildroot}/usr/share/%{name}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps

# Copy application files
cp -r src %{buildroot}/usr/share/%{name}/
cp -r resources %{buildroot}/usr/share/%{name}/
cp requirements.txt %{buildroot}/usr/share/%{name}/ 2>/dev/null || true

# Create data directory
mkdir -p %{buildroot}/usr/share/%{name}/data

# Create launcher script
cat > %{buildroot}/usr/bin/%{name} << 'LAUNCHER'
#!/bin/bash
cd /usr/share/zeitgeist-teflon-pharma
python3 -m src.main "$@"
LAUNCHER
chmod 755 %{buildroot}/usr/bin/%{name}

# Create desktop entry
cat > %{buildroot}/usr/share/applications/%{name}.desktop << 'DESKTOP'
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

# Copy icon if exists
if [ -f icon.png ]; then
    cp icon.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/%{name}.png
fi

%files
/usr/share/%{name}/
/usr/bin/%{name}
/usr/share/applications/%{name}.desktop
/usr/share/icons/hicolor/256x256/apps/%{name}.png

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

# Create source tarball
echo "Creating source tarball..."
tar -czf ~/rpmbuild/SOURCES/zeitgeist-teflon-pharma-1.0.0.tar.gz \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='data/pharma_pos.db' \
    --exclude='*.pyc' \
    --exclude='packaging' \
    src resources requirements.txt icon.png 2>/dev/null || true

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
