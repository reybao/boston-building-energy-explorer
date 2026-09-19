from pathlib import Path
import openpyxl, json
w = openpyxl.load_workbook(Path(__file__).resolve().parents[1] / '2025-reported-energy-and-water-metrics.xlsx', read_only=True, data_only=True)
for s in w:
    rows=list(s.values)
    print(s.title, len(rows), max(map(len,rows)))
    if s.title=='Data Disclosure':
        for i,r in enumerate(rows[5485:],5486):
            if i<5500 or any('BERDO ID' in str(v) for v in r[:5]) or i>len(rows)-4:
                print(i,[(j+1,v) for j,v in enumerate(r) if v is not None][:16])
    if s.title=='Data Dictionary':
        for r in rows:
            if r[0] and (any(x in str(r[0]) for x in ['Area','Zip','Parcel ID','EUI','Renewable System','Electricity Usage'])): print(r[:2])
