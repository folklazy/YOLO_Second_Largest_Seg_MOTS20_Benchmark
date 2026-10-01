"""Regenerate accuracy from saved lossless predictions into a fresh metrics folder."""
import argparse
from pathlib import Path
import benchmark as b

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, help='Existing completed accuracy run ID')
    parser.add_argument('--output-name', required=True, help='New directory name under metrics/')
    args = parser.parse_args()
    assert Path(args.run).name == args.run and Path(args.output_name).name == args.output_name
    output = b.EXP / 'metrics' / args.output_name
    output.mkdir(exist_ok=False)
    frozen = b.read(b.EXP / 'manifests' / f'{args.run}_full_freeze.json')
    assert b.sha(b.EXP / 'configs/benchmark.yaml') == frozen['config_sha256']
    frames = b.frames_for()
    rows = []
    for name in b.MODELS:
        saved = b.EXP / 'predictions' / args.run / 'accuracy' / name.removesuffix('.pt') / 'predictions'
        rows.extend(b.evaluate_model(name, frames, saved, output, b.config(), visualize=False))
    b.csvwrite(output / 'per_model.csv', [r for r in rows if r['sequence'] == 'ALL'])
    b.csvwrite(output / 'per_sequence.csv', [r for r in rows if r['sequence'] != 'ALL'])
    b.write(output / 'provenance.json', {'source_run': args.run, 'timestamp': b.now(), 'inference_rerun': False,
            'config_sha256': frozen['config_sha256'], 'source_manifest_sha256': b.sha(b.EXP / 'manifests/source_manifest.json')})
    print('Metrics regenerated without inference:', output)

if __name__ == '__main__': main()
