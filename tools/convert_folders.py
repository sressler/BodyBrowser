# Batch, resumable PLY -> GLB conversion for CAESAR data folders.
# Usage: python3 convert_folders.py <data_root> <folder_regex> [time_budget_seconds]
#   e.g. python3 convert_folders.py ~/CAESARall/data 'a\d+' 0      (status only)
#        python3 convert_folders.py ~/CAESARall/data 'b\d+' 110    (one time-boxed step)
# For each matching folder, converts scans/<name>.ply.gz (or <name>.ply) plus landmarks/<name>.lnd
# to gltf/<name>.glb. Existing .glb files are skipped; output is written as .part then renamed.
# A budget of 0 only prints status. Leftover .part files are removed at the start of a step.
import os,sys,time,re
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from ply2glb import convert
ROOT=os.path.expanduser(sys.argv[1]);PAT=sys.argv[2]
BUDGET=float(sys.argv[3]) if len(sys.argv)>3 else 110
LOG=os.path.join(os.path.dirname(os.path.abspath(__file__)),'convert_log.txt')
def folders():
    fs=[d for d in os.listdir(ROOT) if re.fullmatch(PAT,d) and os.path.isdir(os.path.join(ROOT,d,'scans'))]
    return sorted(fs,key=lambda d:(d[0],int(re.sub(r'\D','',d) or 0)))
def scans(d):
    fs=os.listdir(os.path.join(ROOT,d,'scans'))
    m={f[:-7]:f for f in fs if f.endswith('.ply.gz')}
    for f in fs:
        if f.endswith('.ply') and f[:-4] not in m:m[f[:-4]]=f
    return m
def job(d,n,f):
    out=os.path.join(ROOT,d,'gltf',n+'.glb')
    try:nv,nf,nl=convert(os.path.join(ROOT,d,'scans',f),os.path.join(ROOT,d,'landmarks',n+'.lnd'),out);return f'ok {d}/{n} {nv} {nf} {nl}'
    except Exception as e:
        try:os.remove(out+'.part')
        except OSError:pass
        return f'FAIL {d}/{n} {e!r}'
if __name__=='__main__':
    t0=time.time();todo=[];per=[];tot=done=0
    for d in folders():
        g=os.path.join(ROOT,d,'gltf');os.makedirs(g,exist_ok=True)
        if BUDGET>0:
            for f in os.listdir(g):
                if f.endswith('.part'):os.remove(os.path.join(g,f))
        have={f[:-4] for f in os.listdir(g) if f.endswith('.glb')};s=scans(d)
        k=len(set(s)&have);tot+=len(s);done+=k;per.append(f'{d}:{k}/{len(s)}')
        todo+=[(d,n,s[n]) for n in sorted(s) if n not in have]
    n_ok=n_fail=0
    if todo and BUDGET>0:
        with ProcessPoolExecutor(4) as ex, open(LOG,'a') as log:
            it=iter(todo);running=set()
            def submit():
                for a in it:running.add(ex.submit(job,*a));return True
                return False
            for _ in range(4):submit()
            while running:
                fin,running=wait(running,return_when=FIRST_COMPLETED)
                for f in fin:
                    r=f.result();log.write(r+'\n');log.flush()
                    if r.startswith('ok'):n_ok+=1;done+=1
                    else:n_fail+=1
                    if time.time()-t0<BUDGET-12:submit()
    fails=sum(1 for l in open(LOG) if l.startswith('FAIL')) if os.path.exists(LOG) else 0
    print(f'STEP ok={n_ok} fail={n_fail} in {time.time()-t0:.0f}s | DONE {done}/{tot} REMAINING {tot-done} | TOTAL FAILS {fails} | {time.strftime("%H:%M")}')
    print(' '.join(per))
