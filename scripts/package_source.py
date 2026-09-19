from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'dist/deliverables/project-source.zip'
from build_site import EXCLUDE
paths=[p for folder in ('dist','redesign','scripts','tests') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name not in EXCLUDE and p.name!='demo-recorder.html' and p!=target]
paths += [ROOT/n for n in ('README.md','requirements.txt','VERIFICATION.md','.gitignore') if (ROOT/n).exists()]
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(paths):z.write(p,p.relative_to(ROOT))
print(f'Packaged {len(paths)} source and public asset files; original workbook and credentials excluded.')
