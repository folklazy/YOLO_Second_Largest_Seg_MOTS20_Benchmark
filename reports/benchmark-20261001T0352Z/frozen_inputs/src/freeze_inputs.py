"""Archive exact pre-full inputs and reference summaries without editing originals."""
from pathlib import Path
import sys
import shutil
import importlib.metadata as md
from validate import EXP, ROOT, sha, write, now
import json

def main(run):
    assert json.loads((EXP / 'manifests' / f'{run}_preflight.json').read_text())['selected_max_dets'] == 200
    previous = ROOT / 'YOLO_Large_Seg_MOTS20_Benchmark'
    reference = [previous / 'REPORT.md', previous / 'metrics/comparison_summary.csv',
                 previous / 'metrics/per_model.csv', previous / 'timing/benchmark-20260929T0520Z/clean_repetition/summary.csv']
    directory = EXP / 'reports' / run / 'frozen_inputs'
    directory.mkdir(parents=True, exist_ok=False)
    write(EXP / 'manifests/cross_tier_frozen_reference.json', {
        'timestamp': now(), 'hashes': {str(p.relative_to(previous)): sha(p) for p in reference}})
    write(EXP / 'manifests/package_inventory.json', {
        'timestamp': now(), 'packages': sorted([{'name': d.metadata['Name'], 'version': d.version}
                                              for d in md.distributions()], key=lambda x: x['name'].lower())})
    for name in ['src', 'configs', 'manifests']:
        shutil.copytree(EXP / name, directory / name)
    for name in ['EXPERIMENT_PROTOCOL.md', 'requirements.txt']:
        shutil.copyfile(EXP / name, directory / name)
    for path in reference:
        destination = directory / 'experiment1_reference' / path.relative_to(previous)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    for path in (EXP / 'src').rglob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    write(EXP / 'manifests' / f'{run}_input_archive.json', {
        'timestamp': now(), 'hashes': {str(p.relative_to(directory)): sha(p) for p in directory.rglob('*') if p.is_file()}})
    print('Pre-full sources compile; inputs and cross-tier reference archived and hashed.')

if __name__ == '__main__': main(sys.argv[1])
