"""Final read-only integrity gates and publishable environment/plot evidence."""
import sys
import json
import subprocess
import importlib.metadata as md
import platform
import os
from pathlib import Path
from validate import EXP, ROOT, sha, write, now

def main(run):
    frozen = json.loads((EXP / 'manifests' / f'{run}_full_freeze.json').read_text())
    assert all(sha(EXP / p) == h for p, h in frozen['sources'].items())
    assert sha(EXP / 'configs/benchmark.yaml') == frozen['config_sha256']
    assert sha(EXP / 'EXPERIMENT_PROTOCOL.md') == frozen['protocol_sha256']
    previous = ROOT / 'YOLO_Large_Seg_MOTS20_Benchmark'
    reference = json.loads((EXP / 'manifests/cross_tier_frozen_reference.json').read_text())
    assert all(sha(previous / p) == h for p, h in reference['hashes'].items())
    archive = EXP / 'reports' / run / 'frozen_inputs'
    hashes = json.loads((EXP / 'manifests' / f'{run}_input_archive.json').read_text())['hashes']
    assert all(sha(archive / p) == h for p, h in hashes.items())
    for name in ['images.json', 'preflight_frames.json', 'timing_frames.json', 'visualization_frames.json']:
        assert sha(EXP / 'manifests' / name) == sha(previous / 'manifests' / name)
    for name in ['gt_instances.csv', 'gt_frames.csv', 'person_size_distribution.json']:
        assert sha(EXP / 'metrics' / name) == sha(previous / 'metrics' / name)
    env = json.loads((EXP / 'manifests/environment.json').read_text())
    import torch, torchvision
    final = {'timestamp': now(), 'hostname': platform.node(), 'os': platform.platform(), 'python': sys.version,
             'packages': {k: md.version(k) for k in env['packages']},
             'torch_version': torch.__version__, 'torchvision_version': torchvision.__version__,
             'cuda_runtime': torch.version.cuda, 'cuda_available': torch.cuda.is_available(),
             'CUDA_VISIBLE_DEVICES': os.getenv('CUDA_VISIBLE_DEVICES'),
             'gpu': str(torch.cuda.get_device_properties(0))}
    assert all(final[k] == env[k] for k in final if k != 'timestamp')
    final['driver_and_gpu'] = subprocess.check_output(['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv'], text=True)
    assert '580.178.04' in final['driver_and_gpu'] and 'Tesla T4' in final['driver_and_gpu']
    final['status'] = 'PASS'
    final['raw_initial_environment_sha256'] = sha(EXP / 'manifests/environment.json')
    write(EXP / 'manifests/environment_public.json', final)
    # Use the same presentation-only refinement as Experiment 1, with tier title updated.
    source_path = previous / 'src/refine_scatter_plots.py'
    source = source_path.read_text().replace('Largest available variants', 'Second-largest available variants')
    target = EXP / 'logs' / run / 'refine_scatter_plots_source.py'
    target.write_text(source)
    ns = {'__name__': 'presentation_only', '__file__': str(target)}
    exec(compile(source, str(target), 'exec'), ns)
    ns['main'](run)
    summary = EXP / 'reports' / run / 'SUMMARY.md'
    summary.write_text(summary.read_text().replace('](EXPERIMENT_PROTOCOL.md)', '](../../EXPERIMENT_PROTOCOL.md)'))
    write(EXP / 'manifests/final_integrity.json', {
        'timestamp': now(), 'status': 'PASS', 'frozen_runtime_sources_unchanged': True,
        'archive_unchanged': True, 'experiment1_reference_unchanged': True,
        'exact_shared_lists_and_gt_descriptives': True, 'environment_unchanged': True,
        'presentation_source_reference_sha256': sha(source_path),
        'presentation_source_sha256': sha(target),
        'post_freeze_reporting_sources': {str(p.relative_to(EXP)): sha(p) for p in (EXP / 'src').rglob('*.py') if str(p.relative_to(EXP)) not in frozen['sources']},
    })
    print('FINAL INTEGRITY PASS: reference, source freeze, archive, shared lists, GT distribution and environment unchanged.')

if __name__ == '__main__': main(sys.argv[1])
