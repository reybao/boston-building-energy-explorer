"""Assemble the reviewed interface and course materials into build/."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build'
EXCLUDE = {
    'project-source.zip', 'boston-energy-walkthrough.webm',
    'boston-energy-walkthrough.mp4', 'boston-energy-walkthrough-narrated.mp4',
    'narration-timing.json', 'walkthrough-narration-draft.md',
    'natural-voice-preview.mp3',
}

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    for source in (ROOT / 'dist').rglob('*'):
        if source.is_file() and source.name not in EXCLUDE:
            target = OUT / source.relative_to(ROOT / 'dist')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for source in (ROOT / 'redesign').rglob('*'):
        if not source.is_file() or source.suffix == '.md' or source.name == 'demo-recorder.html':
            continue
        target = OUT / source.relative_to(ROOT / 'redesign')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for path in OUT.rglob('*'):
        if path.suffix not in ('.html', '.js', '.css'):
            continue
        text = path.read_text()
        text = text.replace('../dist/', './').replace('../redesign/index.html', 'index.html')
        text = text.replace(' · Design preview', '').replace('DESIGN PREVIEW', '2025 DISCLOSURE')
        if path.name in ('methodology.html', 'presentation.html', 'reflection.html'):
            for route in ('explore', 'methods', 'priorities', 'overview'):
                text = text.replace('index.html#' + route, 'analysis.html#' + route)
        if path.name == 'walkthrough.html':
            text = text.replace('Open design preview', 'Open explorer').replace('design-preview website', 'website').replace('Recorded from the local design preview.', 'Recorded from the reviewed website interface.')
        path.write_text(text)
    package = ROOT / 'dist/deliverables/project-source.zip'
    if package.exists():
        shutil.copy2(package, OUT / 'deliverables/project-source.zip')
    print('Built current interface, shared analysis, data, and final course materials in build/.')

if __name__ == '__main__':
    build()
