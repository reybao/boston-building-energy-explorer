"""Rebuild public analysis from the untouched disclosure workbook.
Only reads XLSX. Public source records exclude owner names and free-text notes.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import csv, gzip, hashlib, json, math, re, statistics
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'2025-reported-energy-and-water-metrics.xlsx'
OUT=ROOT/'dist/data'
AREA='Reported Gross Floor Area (Sq Ft)'
ENERGY='Total Site Energy Usage (kBtu)'
EUI='Site EUI (Energy Use Intensity kBtu/ft²)'
GHG='Estimated Total GHG Emissions (kgCO2e)'
TYPE='Largest Property Type'
EMAREA='BERDO Emissions Gross Floor Area (Sq Ft)'
BANDS=[(0,25000,'Under 25,000'),(25000,50000,'25,000–49,999'),(50000,100000,'50,000–99,999'),(100000,250000,'100,000–249,999'),(250000,math.inf,'250,000 and above')]
MIN_PEERS=20

def number(v):
    if v is None or (isinstance(v,str) and not v.strip()): return None,'missing'
    if isinstance(v,str) and v.strip().upper() in ('#N/A','#NA','NA','N/A','NOT AVAILABLE'): return None,'missing_marker'
    if isinstance(v,str) and v.strip().lower() in ('not applicable',): return None,'not_applicable'
    try:
        x=float(v.replace(',','').strip() if isinstance(v,str) else v)
        if not math.isfinite(x): return None,'unparseable'
        return x, 'negative' if x<0 else 'zero' if x==0 else 'numeric_text' if isinstance(v,str) else 'numeric'
    except (ValueError,TypeError): return None,'unparseable'

def identifier(v,fmt=''):
    if v is None: return None
    if isinstance(v,(int,float)) and math.isfinite(v) and v==int(v):
        return str(int(v)).zfill(len(fmt)) if re.fullmatch('0+',fmt or '') else str(int(v))
    s=str(v).strip()
    return s or None

def percentile(values,p):
    a=sorted(values)
    if not a:return None
    pos=(len(a)-1)*p; i=int(pos); j=min(i+1,len(a)-1)
    return a[i]+(a[j]-a[i])*(pos-i)

def summary(values):
    return dict(n=len(values),min=min(values) if values else None,q1=percentile(values,.25),median=percentile(values,.5),q3=percentile(values,.75),max=max(values) if values else None)

def write_json(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False))

def write_csv(name,rows,fields=None):
    fields=fields or list(rows[0])
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');wr.writeheader()
        for r in rows:
            vals={k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in fields}
            # Keep CSV spreadsheet formulas inert without modifying analysis values.
            vals={k:("'"+v if isinstance(v,str) and v.startswith(('=','+','@')) else v) for k,v in vals.items()}
            wr.writerow(vals)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    wb=openpyxl.load_workbook(SOURCE,read_only=True,data_only=True)
    records=[]; sections=[]
    for sn in ['Data Disclosure','Data Disclosure - Campuses']:
        header=None; kind=None;section=None
        for rownum,cells in enumerate(wb[sn].iter_rows(),1):
            vals=[c.value for c in cells]
            if not vals:continue
            labels=[v.strip() if isinstance(v,str) else v for v in vals]
            if labels[0] in ('BERDO ID','Campus ID'):
                header=labels
                kind='campus_summary' if labels[0]=='Campus ID' else 'building'
                section={'sheet':sn,'header_row':rownum,'kind':kind,'records':0};sections.append(section)
                continue
            if not header:continue
            ident=identifier(vals[0])
            is_campus=bool(ident and re.fullmatch(r'C\d+',ident))
            is_building=bool(ident and re.fullmatch(r'\d{6}',ident))
            if not (is_campus or is_building):continue
            hdr=list(header)
            rk='campus_summary' if is_campus else 'building'
            if is_campus and hdr[0]=='BERDO ID':
                # Main-sheet appended summaries reuse the building column layout,
                # with the first two cells repurposed. Confirmed against campus headers.
                hdr[0]='Campus ID';hdr[1]='BERDO IDs in Campus'
            raw={str(h):v for h,v in zip(hdr,vals) if h and h not in ('Property Owner Name','Notes')}
            fmts={str(h):c.number_format for h,c in zip(hdr,cells) if h and h not in ('Property Owner Name','Notes')}
            norm={k:identifier(v,fmts.get(k,'')) if ('Zip Code' in k or k in ('BERDO ID','Campus ID','Tax Parcel ID','Corresponding Campus ID')) else v.strip() if isinstance(v,str) else v for k,v in raw.items()}
            section['records']+=1
            records.append({'id':ident,'kind':rk,'sheet':sn,'row':rownum,'header_row':section['header_row'],'raw':raw,'formats':fmts,'normalized':norm})
    grouped=defaultdict(list)
    for r in records:grouped[(r['kind'],r['id'])].append(r)
    conflicts=[]; chosen={}
    for key,rr in grouped.items():
        # Purpose-specific campus worksheet wins campus summaries and duplicated members.
        rr.sort(key=lambda r:(r['sheet']!='Data Disclosure - Campuses',r['row']))
        chosen[key]=rr[0]
        for other in rr[1:]:
            for field in set(rr[0]['normalized']) & set(other['normalized']):
                a,b=rr[0]['normalized'][field],other['normalized'][field]
                na,sa=number(a);nb,sb=number(b)
                same=(a==b) or (na is not None and nb is not None and abs(na-nb)<1e-8)
                if not same:
                    conflicts.append({'record_kind':key[0],'id':key[1],'field':field,'selected_value':a,'other_value':b,'selected_source':rr[0]['sheet']+':'+str(rr[0]['row']),'other_source':other['sheet']+':'+str(other['row'])})
    membership=defaultdict(set);declared=defaultdict(set)
    for (kind,i),r in chosen.items():
        if kind=='campus_summary':
            for bid in re.findall(r'\b\d{6}\b',str(r['normalized'].get('BERDO IDs in Campus',''))):membership[bid].add(i)
        else:
            cid=r['normalized'].get('Corresponding Campus ID')
            if cid:declared[i].add(cid)
    relation_issues=[]
    for i in sorted(membership.keys()|declared.keys()):
        if membership[i]!=declared[i]:relation_issues.append({'id':i,'summary_campuses':sorted(membership[i]),'member_campuses':sorted(declared[i])})
    relations=[{'berdo_id':i,'campus_id':c,'in_summary_list':c in membership[i],'in_member_field':c in declared[i],'building_record_present':('building',i) in chosen} for i in sorted(membership.keys()|declared.keys()) for c in sorted(membership[i]|declared[i])]
    conflict_by=defaultdict(list)
    for c in conflicts:conflict_by[(c['record_kind'],c['id'])].append(c['field'])
    entities=[]
    for (kind,i),src in chosen.items():
        n=src['normalized'];raw=src['raw'];nums={};states={}
        for f,v in n.items():
            if any(x in f for x in ('(Sq Ft)','(kBtu)','(kWh)','(kgCO2e)','kBtu/ft²','Gallons/ft²')) or f=='Energy Star Score':nums[f],states[f]=number(v)
        area=nums.get(AREA);energy=nums.get(ENERGY);reported=nums.get(EUI);em=nums.get(GHG)
        campuses=sorted(membership[i]|declared[i]) if kind=='building' else []
        grain='campus_summary' if kind=='campus_summary' else 'campus_member' if campuses else 'non_campus'
        flags=[];energy_issues=[];emission_issues=[]
        def flag(s,category=None):
            flags.append(s)
            if category=='energy':energy_issues.append(s)
            if category=='emissions':emission_issues.append(s)
        for f,label in ((AREA,'floor_area'),(ENERGY,'site_energy'),(EUI,'reported_eui')):
            val=nums.get(f)
            if val is None:flag(label+'_'+states.get(f,'missing'),'energy')
            elif val<0 or (f==AREA and val==0):flag(label+'_nonpositive' if f==AREA else label+'_negative','energy')
        calc=energy/area if energy is not None and energy>=0 and area is not None and area>0 else None
        diff=calc-reported if calc is not None and reported is not None else None
        if diff is not None and abs(diff)>.11:flag('eui_difference_gt_0.11','energy')
        for f,v in nums.items():
            if ('Usage' in f and f!=ENERGY and 'Water' not in f):
                if v is not None and v<0:flag('negative_'+f.split(' (')[0].lower().replace(' ','_'),'energy')
                elif states[f]=='unparseable':flag('unparseable_'+f.split(' (')[0].lower().replace(' ','_'),'energy')
        energy_components=[v*(3.412141633 if '(kWh)' in f else 1) for f,v in nums.items() if 'Usage' in f and 'Water' not in f and f!=ENERGY and v is not None and v>=0]
        if energy is not None and energy>=0 and energy_components and max(energy_components)>energy+max(1,energy*0.0001):flag('energy_component_exceeds_total','energy')
        if em is None:flag('estimated_emissions_'+states.get(GHG,'missing'),'emissions')
        elif em<0:flag('estimated_emissions_negative','emissions')
        components=[v for f,v in nums.items() if 'Emissions (kgCO2e)' in f and f!=GHG and v is not None]
        full_components=all(v is not None for f,v in nums.items() if 'Emissions (kgCO2e)' in f and f!=GHG)
        component_sum=sum(components) if components else None
        emdiff=em-component_sum if em is not None and component_sum is not None else None
        if any(v<0 for v in components):flag('negative_emissions_component','emissions')
        if emdiff is not None and abs(emdiff)>max(.01,abs(em)*1e-6):flag('emissions_component_sum_difference','emissions')
        if not full_components:flags.append('emissions_components_incomplete')
        water=nums.get('Water Usage Intensity (Gallons/ft²)')
        if water is not None and (water<0 or water>1000):flag('water_negative' if water<0 else 'water_intensity_gt_1000')
        cf=conflict_by[(kind,i)]
        if cf:
            flag('duplicate_source_conflict')
            if any(f in (AREA,ENERGY,EUI,TYPE,'Corresponding Campus ID') or ('Usage' in f and 'Water' not in f) for f in cf):energy_issues.append('duplicate_energy_source_conflict')
        if grain=='campus_member' and (len(campuses)!=1 or i in {x['id'] for x in relation_issues}):flag('campus_relationship_disagreement','energy')
        if grain=='campus_summary' and any(i in x['summary_campuses'] for x in relation_issues):flag('campus_member_record_missing')
        if not n.get(TYPE):flag('property_type_missing','energy')
        band=next((label for lo,hi,label in BANDS if area is not None and area>0 and lo<=area<hi),None)
        address=n.get('Building Address') or n.get('Parcel Address') or 'Address unavailable'
        address_source='Building address' if n.get('Building Address') else 'Parcel address fallback' if n.get('Parcel Address') else 'Unavailable'
        energy_ok=grain=='non_campus' and not energy_issues
        e={'id':i,'grain':grain,'campus_ids':campuses,'address':address,'address_source':address_source,'zip':n.get('Building Address Zip Code') or n.get('Parcel Address Zip Code'),'parcel_id':n.get('Tax Parcel ID'),'type':n.get(TYPE) or 'Not reported','area':area,'emissions_area':nums.get(EMAREA),'site_energy':energy,'reported_eui':reported,'calculated_eui':calc,'eui_difference':diff,'estimated_emissions_kg':em,'estimated_emissions_tonnes':em/1000 if em is not None else None,'emissions_component_sum':component_sum,'emissions_difference':emdiff,'emissions_components_complete':full_components,'emissions_intensity':em/nums[EMAREA] if em is not None and em>=0 and nums.get(EMAREA) and nums[EMAREA]>0 else None,'water_intensity':water,'electricity_kwh':nums.get('Electricity Usage (kWh)'),'status':n.get('Reporting Compliance Status') or 'Not provided','area_band':band,'energy_eligible':energy_ok,'energy_exclusions':energy_issues,'emissions_exclusions':emission_issues,'quality_flags':flags,'review_required':bool(energy_issues or emission_issues or any(x.startswith(('water_','duplicate_','campus_')) for x in flags)),'source_sheet':src['sheet'],'source_row':src['row'],'source_locations':[{'sheet':r['sheet'],'row':r['row']} for r in grouped[(kind,i)]],'value_states':states,'raw_values':raw}
        entities.append(e)
    ref=defaultdict(list)
    for e in entities:
        if e['energy_eligible']:ref[(e['type'],e['area_band'])].append(e['calculated_eui'])
    peers=[{'type':k[0],'area_band':k[1],**summary(v),'comparison_available':len(v)>=MIN_PEERS} for k,v in sorted(ref.items())]
    pmap={(p['type'],p['area_band']):p for p in peers}
    for e in entities:
        p=pmap.get((e['type'],e['area_band']))
        e['peer_n']=p['n'] if p else 0
        e['peer_median']=p['median'] if p else None;e['peer_q1']=p['q1'] if p else None;e['peer_q3']=p['q3'] if p else None
        e['comparison_eligible']=e['energy_eligible'] and bool(p and p['comparison_available'])
        e['relative_to_peer']=e['calculated_eui']/p['median'] if e['comparison_eligible'] and p['median']>0 else None
        e['peer_percentile']=100*sum(x<=e['calculated_eui'] for x in ref[(e['type'],e['area_band'])])/p['n'] if e['comparison_eligible'] else None
        e['full_gap_kbtu']=max(0,e['calculated_eui']-p['median'])*e['area'] if e['comparison_eligible'] else None
        e['investigation_candidate']=bool(e['comparison_eligible'] and e['calculated_eui']>p['q3'])
    buildings=[e for e in entities if e['grain']!='campus_summary']
    non=[e for e in entities if e['grain']=='non_campus'];campuses=[e for e in entities if e['grain']=='campus_summary']
    aggregate=non+campuses
    def coverage(pop,key,eligible):
        vals=[e[key] for e in pop if e[key] is not None]
        elig=[e for e in pop if eligible(e)]
        return {'population_n':len(pop),'numeric_n':len(vals),'numeric_coverage_pct':100*len(vals)/len(pop) if pop else None,'eligible_n':len(elig),'excluded_n':len(pop)-len(elig)}
    type_stats=[]
    for t in sorted({e['type'] for e in non}):
        pop=[e for e in non if e['type']==t];eligible=[e for e in pop if e['energy_eligible']]
        type_stats.append({'type':t,'population_n':len(pop),'numeric_eui_n':sum(e['calculated_eui'] is not None for e in pop),**summary([e['calculated_eui'] for e in eligible]),'area_distribution':summary([e['area'] for e in pop if e['area'] is not None and e['area']>0])})
    aggregates={}
    for key in ('site_energy','estimated_emissions_kg'):
        vals=[e[key] for e in aggregate if e[key] is not None]
        screened=[e[key] for e in aggregate if e[key] is not None and e[key]>=0 and not e['energy_exclusions' if key=='site_energy' else 'emissions_exclusions']]
        aggregates[key]={'entities':len(aggregate),'numeric_n':len(vals),'reported_sum':sum(vals) if vals else None,'screened_n':len(screened),'screened_sum':sum(screened) if screened else None}
    meta={'release':'2025 disclosure release','energy_year':None,'period_label':'2025 disclosure release; energy-use year not independently confirmed.','processed_at':datetime.now(timezone.utc).isoformat(),'original_download_date':None,'source_file':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_url':'https://data.boston.gov/dataset/building-emissions-reduction-and-disclosure-ordinance/resource/911db0b1-437f-43ba-86bb-860cc1cd9319','official_context_url':'https://www.boston.gov/departments/environment/berdo','official_resource_created':'2025-10-02','official_resource_updated':'2026-03-03','year_evidence':'Official Boston BERDO page says annual reports concern the previous calendar year, suggesting 2024. The resource page and supplied workbook do not explicitly confirm the consumption year for this particular release; therefore it remains unconfirmed.','buildings_n':len(buildings),'non_campus_n':len(non),'campus_members_n':len(buildings)-len(non),'campus_summaries_n':len(campuses),'aggregate_entities_n':len(aggregate),'reported_eui_numeric_n':sum(e['reported_eui'] is not None for e in non),'reported_eui_preclean_median':statistics.median(e['reported_eui'] for e in non if e['reported_eui'] is not None),'energy_eligible_n':sum(e['energy_eligible'] for e in non),'comparison_eligible_n':sum(e['comparison_eligible'] for e in non),'investigation_candidates_n':sum(e['investigation_candidate'] for e in non),'review_cases_n':sum(e['review_required'] for e in non),'coverage':{'calculated_eui':coverage(non,'calculated_eui',lambda e:e['energy_eligible']),'estimated_emissions':coverage(non,'estimated_emissions_kg',lambda e:e['estimated_emissions_kg'] is not None and not e['emissions_exclusions'])},'energy_exclusion_counts':dict(Counter(x for e in non for x in e['energy_exclusions'])),'quality_flag_counts':dict(Counter(x for e in non for x in e['quality_flags'])),'status_counts':dict(Counter(e['status'] for e in buildings)),'sections':sections,'source_records_n':len(records),'duplicate_records_removed':len(records)-len(entities),'conflict_field_count':len(conflicts),'conflict_record_count':len({(c['record_kind'],c['id']) for c in conflicts}),'relationship_issues':relation_issues,'relationships_n':len(relations),'area_bands':[b[2] for b in BANDS],'minimum_peers':MIN_PEERS,'aggregates':aggregates,'type_stats':type_stats,'area_distribution':summary([e['area'] for e in non if e['area'] is not None and e['area']>0])}
    dictionary=[{'field':str(r[0]).strip(),'definition':r[1],'source':'Workbook Data Dictionary','excel_row':i} for i,r in enumerate(wb['Data Dictionary'].values,1) if r[0] and r[1] and r[0]!='Property Owner Name']
    write_json('metadata.json',meta);write_json('peers.json',peers);write_json('dictionary.json',dictionary)
    write_json('buildings.json',[{k:v for k,v in e.items() if k not in ('raw_values','value_states')} for e in buildings]);write_json('campuses.json',[{k:v for k,v in e.items() if k not in ('raw_values','value_states')} for e in campuses])
    with (OUT/'source-records.json.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as gz:gz.write(json.dumps(records,ensure_ascii=False,separators=(',',':')).encode())
    (OUT/'source-records.json').unlink(missing_ok=True)
    write_json('conflicts.json',conflicts);write_json('relationships.json',relations)
    write_csv('buildings.csv',buildings);write_csv('campus-summaries.csv',campuses);write_csv('aggregate-entities.csv',aggregate);write_csv('campus-relationships.csv',relations);write_csv('peer-benchmarks.csv',peers);write_csv('duplicate-conflicts.csv',conflicts,['record_kind','id','field','selected_value','other_value','selected_source','other_source'])
    print(json.dumps({k:v for k,v in meta.items() if k not in ('type_stats','sections','aggregates','status_counts')},indent=2))
    print('FOCUS',json.dumps([x for x in type_stats if x['type'] in ('Multifamily Housing','Office')],indent=2))
    print('CONFLICTS',json.dumps(conflicts[:10],indent=2));print('AGGREGATES',json.dumps(aggregates,indent=2))

if __name__=='__main__':main()
