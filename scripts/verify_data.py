"""Independent workbook controls, analytical invariants, exports and static assets."""
from pathlib import Path
import json,csv,statistics,hashlib,math,zipfile,gzip
from decimal import Decimal
from collections import defaultdict
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'dist/data'
m=json.loads((D/'metadata.json').read_text());b=json.loads((D/'buildings.json').read_text());c=json.loads((D/'campuses.json').read_text());p=json.loads((D/'peers.json').read_text())
assert hashlib.sha256((ROOT/m['source_file']).read_bytes()).hexdigest()==m['source_sha256']=='640b6a3ecb48084bfb169dcc8a6df8978ec5439f44c5f794f010cadbbf84bbb6'
w=openpyxl.load_workbook(ROOT/m['source_file'],read_only=True,data_only=True)
raw={};cols=None
for row in w['Data Disclosure'].values:
    if not row:continue
    if row[0]=='BERDO ID':cols={str(v).strip():j for j,v in enumerate(row) if v};continue
    if cols and isinstance(row[0],(int,float)):
        raw[str(int(row[0]))]={k:row[j] for k,j in cols.items()}
assert len(raw)==len(b)==5487
rel=json.loads((D/'relationships.json').read_text());member_ids={r['berdo_id'] for r in rel if r['building_record_present']}
assert len(member_ids)==453 and len(c)==91
non=[r for r in b if r['id'] not in member_ids];assert len(non)==5034
assert all(r['grain']=='non_campus' for r in non)
source_euis=[raw[r['id']]['Site EUI (Energy Use Intensity kBtu/ft²)'] for r in non if isinstance(raw[r['id']]['Site EUI (Energy Use Intensity kBtu/ft²)'],(int,float))]
assert len(source_euis)==m['reported_eui_numeric_n']==3285
assert statistics.median(source_euis)==m['reported_eui_preclean_median']==64.5
for r in non:
    source=raw[r['id']];a=source['Reported Gross Floor Area (Sq Ft)'];e=source['Total Site Energy Usage (kBtu)']
    if isinstance(a,(int,float)) and a>0 and isinstance(e,(int,float)) and e>=0:
        calc=float(Decimal(str(e))/Decimal(str(a)))
        assert math.isclose(calc,r['calculated_eui'],rel_tol=1e-12)
    else:assert r['calculated_eui'] is None
    if r['energy_eligible']:assert r['area']>0 and r['site_energy']>=0 and abs(r['calculated_eui']-r['reported_eui'])<=.11 and not r['energy_exclusions']
    if r['comparison_eligible']:
        assert r['energy_eligible'] and r['peer_n']>=20
        assert math.isclose(r['full_gap_kbtu'],max(0,r['calculated_eui']-r['peer_median'])*r['area'],abs_tol=1e-6)
        assert r['investigation_candidate']==(r['calculated_eui']>r['peer_q3'])
    else:assert r['full_gap_kbtu'] is None
    if r['estimated_emissions_kg'] is not None:assert r['estimated_emissions_tonnes']==r['estimated_emissions_kg']/1000
assert sum(r['energy_eligible'] for r in non)==m['energy_eligible_n']
assert sum(r['comparison_eligible'] for r in non)==m['comparison_eligible_n']
for peer in p:
    values=[r['calculated_eui'] for r in non if r['energy_eligible'] and r['type']==peer['type'] and r['area_band']==peer['area_band']]
    assert len(values)==peer['n'] and math.isclose(statistics.median(values),peer['median'],rel_tol=1e-12)
    if len(values)>1:
        qs=statistics.quantiles(values,n=4,method='inclusive')
        assert math.isclose(qs[0],peer['q1'],rel_tol=1e-12) and math.isclose(qs[2],peer['q3'],rel_tol=1e-12)
assert all(not r['comparison_eligible'] and not r['energy_eligible'] for r in b if r['grain']=='campus_member')
for id in ('102879','105219'):assert not next(r for r in b if r['id']==id)['energy_eligible']
assert next(r for r in b if r['id']=='102879')['calculated_eui'] is None
assert any(r['calculated_eui']==0 and r['energy_eligible'] for r in non),'Valid genuine zero must survive'
assert any('water_intensity_gt_1000' in r['quality_flags'] and r['energy_eligible'] for r in non),'Water flag must not invalidate energy'
with (D/'aggregate-entities.csv').open(encoding='utf-8-sig') as f:agg=list(csv.DictReader(f))
assert len(agg)==5125 and len({r['id'] for r in agg})==5125 and all(r['grain']!='campus_member' for r in agg)
for key in ('site_energy','estimated_emissions_kg'):
    total=sum(Decimal(r[key]) for r in agg if r[key]!='')
    assert math.isclose(float(total),m['aggregates'][key]['reported_sum'],rel_tol=1e-12)
with (D/'buildings.csv').open(encoding='utf-8-sig') as f:csvrows=list(csv.DictReader(f))
assert len(csvrows)==len(b) and {r['id'] for r in csvrows}=={r['id'] for r in b}
for r in csvrows:
    v=next(x for x in b if x['id']==r['id'])
    assert (r['calculated_eui']=='' and v['calculated_eui'] is None) or float(r['calculated_eui'])==v['calculated_eui']
    assert 'Property Owner Name' not in r['raw_values']
source_records=json.loads(gzip.decompress((D/'source-records.json.gz').read_bytes()));assert len(source_records)==6122
assert all('Property Owner Name' not in r['raw'] and 'Notes' not in r['raw'] for r in source_records)
assert len(PdfReader(ROOT/'dist/deliverables/methodology.pdf').pages)==1
for file in ('index.html','style.css','app.js','analytics.js','favicon.svg','methodology.html','reflection.html','presentation.html','deliverables/speaking-outline.md','deliverables/methodology.pdf'):
    assert (ROOT/'dist'/file).stat().st_size>0
print('PASS: untouched source SHA, 5487/5034/453/91/5125 counts, median 64.5, all calculated EUIs independently recomputed with Decimal, quartiles with statistics, campus exclusion, missing/zero/negative handling, independent metric flags, CSV agreement, aggregate sums, privacy fields, one-page PDF and core files.')
