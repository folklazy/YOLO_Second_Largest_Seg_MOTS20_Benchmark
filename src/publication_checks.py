"""Synchronize final human interpretation and audit the small Git publication bundle."""
import sys
import json
import subprocess
from validate import EXP, sha, write, now

def main(run):
    report = (EXP / 'REPORT.md').read_text()
    summary = report.replace('](outputs/', '](../../outputs/').replace('](EXPERIMENT_PROTOCOL.md)', '](../../EXPERIMENT_PROTOCOL.md)')
    (EXP / 'reports' / run / 'SUMMARY.md').write_text(summary)
    terminal_path = EXP / 'reports' / run / 'terminal_summary.txt'
    old = terminal_path.read_text()
    table = old[old.index('| Model | mAP'):]
    terminal = report[:report.index('## 1. Research question')] + '\n' + table
    terminal_path.write_text(terminal)
    frozen = json.loads((EXP / 'manifests' / f'{run}_full_freeze.json').read_text())
    assert all(sha(EXP / name) == digest for name, digest in frozen['sources'].items())
    sources = {str(path.relative_to(EXP)): sha(path) for path in (EXP / 'src').rglob('*.py')}
    for path in (EXP / 'src').rglob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    paths = subprocess.check_output(['git', '-C', str(EXP), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
    files = []
    for relative in sorted(set(paths) - {''}):
        path = EXP / relative
        assert not relative.startswith(('predictions/', '.venv/', '.venvs/', 'models/', 'datasets/'))
        assert path.suffix not in ['.pt', '.pyc', '.partial']
        assert path.stat().st_size < 50 * 1024**2, f'Review large file before staging: {relative}'
        files.append({'path': relative, 'bytes': path.stat().st_size})
    write(EXP / 'manifests/publication_audit.json', {
        'timestamp': now(), 'status': 'PASS', 'frozen_runtime_sources_unchanged': True,
        'current_source_sha256': sources, 'report_sha256': sha(EXP / 'REPORT.md'),
        'insights_sha256': sha(EXP / 'BENCHMARK_INSIGHTS_TH.md'),
        'reviewed_file_count': len(files), 'reviewed_total_bytes': sum(x['bytes'] for x in files),
        'largest_files': sorted(files, key=lambda x: -x['bytes'])[:20],
        'raw_predictions_weights_environments_and_datasets_excluded': True,
    })
    print('PUBLICATION AUDIT PASS:', len(files), 'files,', round(sum(x['bytes'] for x in files)/1e6, 2), 'MB; no file >=50 MiB.')
    print('Frozen runtime/evaluator sources unchanged. Human interpretation and archived summary synchronized.')

if __name__ == '__main__': main(sys.argv[1])
