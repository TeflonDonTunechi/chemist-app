# src/utils/drug_importer.py
import csv
from src.database import Session
from src.models import Drug

def import_drugs_from_csv(filepath):
    sess = Session()
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                price = float(row.get('unit_price', 0))
            except:
                price = 0.0
            drug = Drug(
                brand_name=row.get('brand_name', '').strip(),
                drug_name=row.get('drug_name', '').strip(),
                strength=row.get('strength', '').strip(),
                dosing_bands=row.get('dosing_bands', '').strip(),
                moa=row.get('moa', '').strip(),
                unit_price=price
            )
            sess.add(drug)
            count += 1
        sess.commit()
    sess.close()
    return count