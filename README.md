# Chemist App

A desktop point-of-sale and inventory management system built for pharmacies and chemist shops in Kenya. Built with Python and Qt, it handles sales, stock tracking, drug catalog management, receipts, and reporting in one offline-friendly application.

## Features

- **Point of Sale (POS)** — Fast checkout flow with receipt preview and printing
- **Inventory Management** — Track stock levels, add/edit drugs, low-stock alerts
- **Drug Catalog Import** — Bulk import drug records from CSV (includes a starter template and a Kenyan drug reference list)
- **Sales & Reports** — Dashboard with sales graphs and exportable reports
- **User Management** — Login system with role-based access for staff/admin
- **Herbal/Alternative Products View** — Separate handling for herbal stock
- **Customer Feedback** — Built-in feedback capture
- **PDF Generation** — Receipts and reports exportable as PDF
- **Currency Handling** — Localized currency formatting utilities

## Tech Stack

- **Language:** Python
- **UI Framework:** Qt (PySide/PyQt)
- **Database:** SQLite (via `src/database.py`)
- **PDF Generation:** ReportLab (or equivalent, see `requirements.txt`)
- **Packaging:** RPM build scripts for Fedora/RHEL-based distros

## Project Structure

```
chemist-app/
├── src/
│   ├── controllers/       # Business logic (auth, inventory, sales)
│   ├── views/              # UI screens (POS, dashboard, inventory, reports, etc.)
│   ├── utils/               # Helpers (currency, PDF generation, drug importer)
│   ├── database.py          # Database setup and access layer
│   └── main.py               # Application entry point
├── resources/
│   └── style.qss             # Application stylesheet
├── kenyan_drugs.csv         # Reference drug catalog
├── drug_template.csv        # Template for bulk drug import
├── build_rpm.sh              # RPM packaging script
├── build_packages.sh        # General build/packaging script
├── requirements.txt          # Python dependencies
└── icon.png                    # Application icon
```

## Installation

### From Source

```bash
git clone https://github.com/TeflonDonTunechi/chemist-app.git
cd chemist-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### RPM Package (Fedora/RHEL)

```bash
./build_rpm.sh
sudo dnf install ./dist/chemist-app-*.rpm
```

## Usage

1. Launch the application and log in with your staff credentials.
2. Import your drug catalog via the inventory screen, or start from `drug_template.csv`.
3. Use the POS view to process sales and print receipts.
4. Check the dashboard for sales trends and generate reports as needed.

## Contributing

Contributions, bug reports, and feature requests are welcome. Please open an issue or submit a pull request.

## License

Specify your license here (e.g. MIT, GPL-3.0). If unsure, [choosealicense.com](https://choosealicense.com) can help you pick one.
