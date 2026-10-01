"""Read-only comparison with Experiment 1; writes evidence only in Experiment 2."""
from pathlib import Path
import hashlib
import json
import datetime
from PIL import Image

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parent
PREV = ROOT / 'YOLO_Large_Seg_MOTS20_Benchmark'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    manifests = PREV / 'manifests'
    dataset = json.loads((manifests / 'dataset_manifest.json').read_text())
    images = json.loads((manifests / 'images.json').read_text())
    errors = []
    if sha(manifests / 'images.json') != dataset['image_manifest_sha256']:
        errors.append('Experiment 1 image manifest hash mismatch')
    expected = []
    for sequence in dataset['sequences']:
        name = sequence['sequence']
        base = ROOT / dataset['dataset_root'] / name
        for relative, key in [('gt/gt.txt', 'gt_sha256'), ('seqinfo.ini', 'seqinfo_sha256')]:
            if sha(base / relative) != sequence[key]:
                errors.append(f'{name}/{relative}: hash mismatch')
        expected.extend((name, int(p.stem)) for p in sorted((base / 'img1').iterdir()) if p.is_file())
    if expected != [(x['sequence'], x['frame']) for x in images] or len(images) != 2862:
        errors.append('Frame list/count/order mismatch')
    for index, record in enumerate(images):
        path = ROOT / record['path']
        if sha(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            errors.append(f"{record['path']}: image hash/size mismatch")
        with Image.open(path) as image:
            image.load()
            if image.size != (record['width'], record['height']):
                errors.append(f"{record['path']}: dimension mismatch")
        if (index + 1) % 500 == 0:
            print(f'Audited {index + 1}/2862 images', flush=True)
    evidence = {
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'FAIL' if errors else 'PASS',
        'frames': len(images), 'errors': errors,
        'reference_hashes': {
            str(p.relative_to(PREV)): sha(p)
            for p in [PREV / 'REPORT.md', PREV / 'EXPERIMENT_PROTOCOL.md',
                      *[manifests / name for name in ['dataset_manifest.json', 'images.json',
                         'preflight_frames.json', 'timing_frames.json', 'visualization_frames.json']]]
        },
    }
    (EXP / 'manifests').mkdir(parents=True, exist_ok=True)
    (EXP / 'manifests/shared_input_audit.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2), flush=True)
    if errors:
        raise SystemExit('STOP: dataset consistency gate failed')

if __name__ == '__main__':
    main()
