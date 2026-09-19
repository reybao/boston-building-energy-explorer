"""Fetch a read-only MassGIS ZIP boundary snapshot; never geocode building points."""
from pathlib import Path
import json, subprocess, urllib.parse, hashlib, datetime
ROOT=Path(__file__).resolve().parents[1]
base='https://services1.arcgis.com/hGdibHYSPO59RG1h/ArcGIS/rest/services/ZIP_Codes_5_Digit_from_HERE/FeatureServer/0'
params={'where':'1=1','outFields':'POSTCODE,PC_NAME,CITY_TOWN','returnGeometry':'true','outSR':'4326','geometryPrecision':'5','maxAllowableOffset':'0.00005','f':'geojson'}
url=base+'/query?'+urllib.parse.urlencode(params)
raw=subprocess.check_output(['curl','-fsSL','--retry','2',url])
data=json.loads(raw)
assert data.get('type')=='FeatureCollection' and len(data['features'])>400 and not data.get('exceededTransferLimit'),data.keys()
# Derive interior label anchors; these represent ZIP labels, never buildings.
for feature in data['features']:
    polygons=[feature['geometry']['coordinates']] if feature['geometry']['type']=='Polygon' else feature['geometry']['coordinates']
    def area(ring):
        return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))/2)
    polygon=max(polygons,key=lambda rings:area(rings[0]))
    ys=[p[1] for p in polygon[0]]
    low,high=min(ys),max(ys)
    best=(0,None)
    for fraction in (.35,.5,.65):
        y=low+(high-low)*fraction
        xs=[]
        for ring in polygon:
            for a,b in zip(ring,ring[1:]):
                if (a[1]>y)!=(b[1]>y):
                    xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        xs.sort()
        for i in range(0,len(xs)-1,2):
            gap=xs[i+1]-xs[i]
            if gap>best[0]: best=(gap,[(xs[i+1]+xs[i])/2,y])
    feature['properties']['label_point']=best[1]
    feature['properties']['label_width']=best[0]*740

out=ROOT/'redesign/data';out.mkdir(exist_ok=True,parents=True)
(out/'ma-zip-boundaries.json').write_text(json.dumps(data,separators=(',',':')))
meta={'source':'MassGIS ZIP Codes (5-Digit) from HERE','url':base,'attribution':'HERE, MassGIS','fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':params,'source_sha256':hashlib.sha256(raw).hexdigest(),'features':len(data['features']),'note':'ZIP delivery-area polygons, not neighborhoods or building locations. Source uses HERE Q2 2018, with Boston boundary edits documented March 2024. Current service snapshot retained; boundaries may change.'}
(out/'map-provenance.json').write_text(json.dumps(meta,indent=2))
print('Fetched',len(data['features']),'ZIP boundary features;',len(raw),'bytes')
