"""Prepare Experiment 2 from preserved Experiment 1 sources; never edit reference."""
from pathlib import Path
import json
import shutil
import hashlib

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parent
PREV = ROOT / 'YOLO_Large_Seg_MOTS20_Benchmark'
REPLACEMENTS = {'yolo26x': 'yolo26l', 'yolo11x': 'yolo11l', 'yolov8x': 'yolov8l', 'yolov9e': 'yolov9c'}

def main():
    assert json.loads((EXP / 'manifests/shared_input_audit.json').read_text())['status'] == 'PASS'
    for directory in ['configs', 'manifests', 'metrics', 'predictions', 'timing', 'logs', 'reports', 'outputs/plots', 'outputs/visualizations', 'src/frozen_pilot']:
        (EXP / directory).mkdir(parents=True, exist_ok=True)
    for name in ['benchmark.py', 'benchmark_adapter.py', 'validate.py', 'repeat_clean_timing.py']:
        source = (PREV / 'src' / name).read_text()
        for old, new in REPLACEMENTS.items():
            source = source.replace(old, new)
        if name == 'validate.py':
            source = source.replace("src=ROOT/'Person_Segmentation_Pilot/src'/name", "src=ROOT/'YOLO_Large_Seg_MOTS20_Benchmark/src/frozen_pilot'/name")
            # Recomputed descriptive GT data must be byte-identical; frozen lists are copied, never sampled anew.
            source = source.replace("    records=[]", """    previous=ROOT/'YOLO_Large_Seg_MOTS20_Benchmark'
    for filename in ['images.json','preflight_frames.json','timing_frames.json','visualization_frames.json']:
        assert read_json(EXP/'manifests'/filename)==read_json(previous/'manifests'/filename), 'STOP: dataset/sample mismatch'
        shutil.copyfile(previous/'manifests'/filename,EXP/'manifests'/filename)
    assert sequences==read_json(previous/'manifests/dataset_manifest.json')['sequences'], 'STOP: GT/metadata mismatch'
    for filename in ['gt_instances.csv','gt_frames.csv','person_size_distribution.json']:
        assert sha(EXP/'metrics'/filename)==sha(previous/'metrics'/filename), 'STOP: GT descriptive data mismatch'
    previous_env=read_json(previous/'manifests/environment.json')
    comparison={k:{'previous':previous_env[k],'current':env[k]} for k in ['hostname','os','python','packages','torch_version','torchvision_version','cuda_runtime','cuda_available','CUDA_VISIBLE_DEVICES','gpu'] if previous_env[k]!=env[k]}
    write(EXP/'manifests/environment_comparison.json',{'differences':comparison})
    assert not comparison, 'STOP: environment mismatch; report before proceeding'
    records=[]""")
            source = source.replace('def main():', "def read_json(path): return json.loads(path.read_text())\ndef main():")
        if name == 'benchmark.py':
            source = source.replace("    assert selected is not None\n    csvwrite", "    assert selected is not None\n    csvwrite")
            source = source.replace("    write(EXP/'manifests'/f'{run}_preflight.json'", "    assert all(x['converged'] for x in rows if x['max_dets']==200), 'STOP: common maxDet 200 insufficient; inspect preflight_maxdet.csv'\n    selected=200\n    write(EXP/'manifests'/f'{run}_preflight.json'")
            source = source.replace("    write(EXP/'manifests'/f'{run}_full_freeze.json',frozen)", "    frozen['shared_reference']=read(EXP/'manifests/shared_input_audit.json')\n    frozen['checkpoint_manifest_sha256']=sha(EXP/'manifests/checkpoint_manifest.json')\n    frozen['dataset_manifest_sha256']=sha(EXP/'manifests/dataset_manifest.json')\n    write(EXP/'manifests'/f'{run}_full_freeze.json',frozen)")
        destination = EXP / 'src' / name
        assert not destination.exists()
        destination.write_text(source)
    for path in (PREV / 'src/frozen_pilot').glob('*.py'):
        shutil.copyfile(path, EXP / 'src/frozen_pilot' / path.name)
    shutil.copyfile(PREV / 'requirements.txt', EXP / 'requirements.txt')
    source = (PREV / 'configs/benchmark.yaml').read_text()
    for old, new in REPLACEMENTS.items(): source = source.replace(old, new)
    source = source.replace('ap_max_dets: 200', 'ap_max_dets: null')
    (EXP / 'configs/benchmark.yaml').write_text(source)
    protocol = (PREV / 'EXPERIMENT_PROTOCOL.md').read_text().split('## Preflight decision')[0]
    for old, new in REPLACEMENTS.items(): protocol = protocol.replace(old, new)
    protocol = protocol.replace('# Largest available YOLO segmentation variants on MOTS20', '# Experiment 2: Second-largest available variant comparison on MOTS20')
    protocol = protocol.replace('YOLOv9 e is its largest supported\nsegmentation variant; x/e do not imply equal capacity.', 'YOLOv9 c is its second-largest available supported\nsegmentation variant; there is no official v9 L segmentation checkpoint here. L/c do not imply equal capacity.')
    protocol = protocol.replace('Choose smallest common cap whose absolute', 'Require the cross-experiment common cap 200, whose absolute')
    protocol = protocol.replace('Freeze selected\ncap in YAML', 'STOP if 200 fails; otherwise freeze 200\nin YAML')
    start = protocol.index('## Evidence for selecting 200 rather than 100')
    end = protocol.index('## Outputs, analyses and final gate')
    protocol = protocol[:start] + protocol[end:]
    protocol += '''\n## Cross-experiment commitments frozen before preflight

Experiment 1 remains read-only. Use its exact saved ordered all-frame, preflight,
timing and visualization manifests, verified against current images, dimensions,
GT and sequence metadata before inference. Dataset audit and reference report
SHA256 are in manifests/shared_input_audit.json. Recomputed GT area and crowd
data must be byte-identical. The original reference evaluator, adapter and
visualization implementations are preserved byte-for-byte in src/frozen_pilot.
No Experiment 1 inference is rerun. Compare its preserved clean timing results.

The 100-frame preflight tests 100/200/300/1000. Even if 100 converges, retain 200.
If 200 fails any strict <0.0001 check, STOP before full inference and establish
a common policy with the user. No unilateral cap or methodology changes.

Timing uses Experiment 1's idle-gated clean repetition runner and identical
measured loop, ten warmups, seed and cyclic family ordering. All contaminated
rounds are excluded. Any required repetition retains the original records.

Cross-tier differences are second-largest minus largest. AP, recall and F1
percentage-point differences equal 100 times the difference on the 0–1 scale.
Relative change is 100*(second-largest/largest-1), reported separately.
Report inference and pipeline latency, mean-derived FPS, allocator peak VRAM,
parameters and checkpoint size without assuming that smaller models are faster.
No significance claim or arbitrary weighted score. Both experiments describe
available model tiers, not capacity-controlled architecture superiority or final
CCTV suitability, controlled blur/lighting/camera-angle/occlusion robustness.

Before full inference freeze config, protocol, sources, dataset/checkpoint
manifests, exact frame lists and Experiment 1 report hashes. Changes to model
names, storage paths and the stricter cross-tier cap gate do not change evaluator
semantics or the measurement method. This protocol is frozen before preflight;
only its predeclared maxDet decision may be appended before full inference.
'''
    (EXP / 'EXPERIMENT_PROTOCOL.md').write_text(protocol)
    (EXP / '.gitignore').write_text('predictions/\n.venv/\n.venvs/\n__pycache__/\n*.pyc\n*.pt\n*.partial\nlogs/ultralytics_config/\n.env\n')
    print('Prepared separate Experiment 2. Frozen evaluator and adapter copied without edits.')

if __name__ == '__main__': main()
