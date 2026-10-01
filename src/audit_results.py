"""Independent arithmetic, timing and publication integrity checks (no inference)."""
import sys
import csv
import json
import math
from pathlib import Path
from validate import EXP, MODELS, sha, write, now

def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))

def same(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-10), (a, b)

def main(run):
    metrics = EXP / 'metrics' / run
    timing = EXP / 'timing' / run / 'clean_repetition'
    pooled = rows(metrics / 'per_model.csv')
    sequences = rows(metrics / 'per_sequence.csv')
    assert {r['model'] for r in pooled} == set(MODELS)
    assert len(pooled) == 4 and len(sequences) == 16
    for model in MODELS:
        overall = next(r for r in pooled if r['model'] == model)
        per_sequence = [r for r in sequences if r['model'] == model]
        per_frame = rows(metrics / 'per_frame' / f'{model}.csv')
        assert len(per_frame) == 2862 and int(overall['gt_persons']) == 26894
        for field in ['frames', 'tp', 'fp', 'fn', 'gt_persons', 'predictions_ap_floor', 'predictions_at_confidence', 'ignored_predictions']:
            same(overall[field], sum(float(r[field]) for r in per_sequence))
            if field != 'frames': same(overall[field], sum(float(r[field]) for r in per_frame))
        for r in [overall, *per_sequence]:
            tp, fp, fn = (int(r[k]) for k in ['tp', 'fp', 'fn'])
            assert tp + fn == int(r['gt_persons'])
            assert tp + fp + int(r['ignored_predictions']) == int(r['predictions_at_confidence'])
            same(r['precision'], tp / (tp + fp))
            same(r['recall'], tp / (tp + fn))
            same(r['f1'], 2 * tp / (2 * tp + fp + fn))
        for round_number in range(1, 4):
            meta = json.loads((timing / f'round{round_number}-{model}.json').read_text())
            assert meta['status'] == 'PASS' and meta['contaminated'] is False
            measurements = rows(timing / f'round{round_number}-{model}.csv')
            assert len(measurements) == 100
            for r in measurements:
                assert r['contaminated'] == 'False'
                same(r['total_ms'], sum(float(r[k]) for k in ['preprocess_ms', 'inference_ms', 'postprocess_ms']))
    for row in rows(timing / 'summary.csv'):
        same(row['fps'], 1000 / float(row['total_ms_mean']))
        assert int(row['clean_rounds']) == 3 and int(row['frames']) == 300
    for row in rows(metrics / 'cross_tier_all_deltas.csv'):
        old, new = float(row['largest']), float(row['second_largest'])
        same(row['absolute_delta'], new - old)
        same(row['relative_percent_delta'], 100 * (new - old) / old)
        if row['percentage_point_delta']: same(row['percentage_point_delta'], 100 * (new - old))
    for path in (EXP / 'src').rglob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    report = (EXP / 'REPORT.md').read_text()
    for heading in ['1. ทดสอบอะไร', '2. เงื่อนไขการทดลอง', '3. ผลหลัก', '4. แต่ละโมเดลเด่นด้านไหน',
                    '5. เทียบกับรุ่นใหญ่สุดที่ทดสอบก่อนหน้า', '6. ข้อจำกัด', '7. ทำอะไรต่อ']:
        assert '## ' + heading in report
    assert (EXP / 'BENCHMARK_INSIGHTS_TH.md').stat().st_size > 1000
    visual_frames = json.loads((EXP / 'manifests/visualization_frames.json').read_text())
    assert len(visual_frames) == 12
    for model in MODELS:
        directory = EXP / 'outputs/visualizations' / run / model.removesuffix('.pt')
        assert {p.name for p in directory.glob('*.jpg')} == {
            f"{r['sequence']}_{r['frame']:06d}.jpg" for r in visual_frames}
    plots = EXP / 'outputs/plots' / run
    for name in ['mask_map', 'ap50_ap75', 'precision_recall_f1', 'matched_mask_quality',
                 'inference_latency', 'pipeline_latency', 'fps', 'peak_vram',
                 'accuracy_vs_latency', 'accuracy_vs_parameters', 'cross_tier_map',
                 'cross_tier_latency', 'cross_tier_vram', 'delta_accuracy_vs_latency',
                 'delta_accuracy_vs_parameters']:
        assert (plots / (name + '.png')).is_file()
    assert (plots / 'underlying_values.csv').is_file() and (plots / 'cross_tier_plot_values.csv').is_file()
    write(EXP / 'manifests/result_arithmetic_audit.json', {
        'status': 'PASS', 'timestamp': now(), 'pooled_counts_equal_sequence_and_frame_sums': True,
        'fixed_metrics_recomputed_from_counts': True, 'timing_stage_sums_and_fps_verified': True,
        'cross_tier_absolute_relative_and_percentage_point_deltas_verified': True,
        'source_syntax_valid': True, 'required_thai_sections_present': True,
        'exact_48_predetermined_visualizations': True, 'all_15_requested_plots_and_values_present': True,
        'report_sha256': sha(EXP / 'REPORT.md'), 'insights_sha256': sha(EXP / 'BENCHMARK_INSIGHTS_TH.md'),
    })
    print('RESULT AUDIT PASS: accuracy count identities, timing arithmetic, cross-tier deltas and report completeness.')

if __name__ == '__main__': main(sys.argv[1])
