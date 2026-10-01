"""Repeat the unchanged timing pass in a fresh directory after idle GPU gates.

The first timing pass and all its telemetry remain untouched. The measured loop,
warmup, seed/order, frames, inference settings and statistics are taken verbatim
from the frozen runner. Only output location and waiting OUTSIDE measurements
change. Save the exact generated source and its hash for review.
"""
import inspect,sys,time,hashlib,random
import benchmark as b

def wait_idle():
    # An idle gate is explicitly permitted by the frozen contamination protocol.
    # Wait outside model loading, warmup, and measured inference; do not alter
    # the contamination classification or reclassify a previously flagged run.
    time.sleep(2)
    while True:
        g=b.gpu()
        if not b.contaminated(g,idle=True):return
        print('Waiting for uncontaminated idle GPU',g,flush=True)
        time.sleep(10)

def main(run):
    b.torch.manual_seed(20260929);b.np.random.seed(20260929);random.seed(20260929)
    b.torch.backends.cudnn.benchmark=False
    from ultralytics.utils import LOGGER
    LOGGER.addHandler(b.NMSWarningGuard())
    source=inspect.getsource(b.timing)
    substitutions={
        'def timing(run):':'def timing_repetition(run):',
        "base=EXP/'timing'/run;base.mkdir(parents=True,exist_ok=False)":
        "base=EXP/'timing'/run/'clean_repetition';base.mkdir(parents=True,exist_ok=False)",
        'clean();before=gpu();runmeta=':'clean();wait_idle();before=gpu();runmeta=',
    }
    for original,replacement in substitutions.items():
        assert source.count(original)==1
        source=source.replace(original,replacement)
    path=b.EXP/'logs'/run/'timing_repetition_source.py'
    assert not path.exists();path.write_text(source)
    b.write(b.EXP/'logs'/run/'timing_repetition_provenance.json',{
        'timestamp':b.now(),'reason':'Predeclared use of Experiment 1 idle-gated clean timing procedure for Experiment 2; unchanged measured loop.',
        'original_runner_sha256':b.sha(b.EXP/'src/benchmark.py'),
        'generated_timing_source_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'changes':substitutions,'measured_loop_unchanged':True,
        'original_timing_preserved':'timing/'+run,
        'primary_timing':'timing/'+run+'/clean_repetition'})
    namespace=dict(vars(b));namespace['wait_idle']=wait_idle
    exec(compile(source,str(path),'exec'),namespace)
    namespace['timing_repetition'](run)
if __name__=='__main__':main(sys.argv[1])
