from pathlib import Path
import sys, random, time, json, csv, math
root=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(root))
from bst_id.region_algebra import *
from bst_id.encoder import BSTIDEncoder
from bst_id.decoder import BSTIDDecoder
AXES=('x','y','f','t')
rng=random.Random(260903)
results=[]; failures=[]
def record(name,cases,passed,t): results.append({'test':name,'cases':cases,'passed':passed,'failed':cases-passed,'seconds':round(t,4)})
def all_1d(maxd): return [Cell.from_parts(x=(z,i)) for z in range(1,maxd+1) for i in range(1<<z)]
def all_2d(maxd):
 o=[]
 for zx in range(1,maxd+1):
  for zy in range(1,maxd+1):
   for ix in range(1<<zx):
    for iy in range(1<<zy): o.append(Cell.from_parts(x=(zx,ix),y=(zy,iy)))
 return o
def rc(dims,zmin,zmax):
 kw={}
 for a in dims:
  z=rng.randint(zmin,zmax); kw[a]=(z,rng.randrange(1<<z))
 return Cell.from_parts(**kw)
def union_oracle(a,b,w): return region_atoms(a,w)|region_atoms(b,w)
def indexes(c,dims): return tuple(c.values[AXES.index(a)] for a in dims)
def atom(idx,dims,w): return Cell.from_parts(**{a:(w[a],idx[j]) for j,a in enumerate(dims)})
def morph_atoms(region,w,dims,offsets,op):
 A=set(region_atoms(region,w)); lim=[1<<w[a] for a in dims]
 if op=='dilate':
  out=set()
  for q in A:
   ii=indexes(q,dims)
   for off in offsets:
    jj=tuple(ii[j]+off[j] for j in range(len(dims)))
    if all(0<=jj[j]<lim[j] for j in range(len(dims))): out.add(atom(jj,dims,w))
  return frozenset(out)
 if op=='erode':
  out=set()
  for q in A:
   ii=indexes(q,dims); ok=True
   for off in offsets:
    jj=tuple(ii[j]+off[j] for j in range(len(dims)))
    if not all(0<=jj[j]<lim[j] for j in range(len(dims))) or atom(jj,dims,w) not in A: ok=False; break
   if ok: out.add(q)
  return frozenset(out)
 if op=='frontier': return frozenset(A-set(morph_atoms(region,w,dims,offsets,'erode')))

# 1D exhaustive bool depths <=5 @6
T=time.perf_counter(); cells=all_1d(5); w={'x':6}; cases=passed=0
for a in cells:
 for b in cells:
  for got,exp,tag in [
   (region_atoms(intersection([a],[b]),w), dense_intersection_oracle([a],[b],w),'int'),
   (region_atoms(difference([a],[b],working_zoom=w),w), dense_difference_oracle([a],[b],w),'diff')]:
   cases+=1; ok=got==exp; passed+=ok
   if not ok and len(failures)<20: failures.append(('1D',tag,a,b))
record('1D exhaustive Boolean (depth 1-5)',cases,passed,time.perf_counter()-T)

# 2D exhaustive <=2 @3x3
T=time.perf_counter(); cells=all_2d(2); w={'x':3,'y':3}; cases=passed=0
for a in cells:
 for b in cells:
  vals=[
   (region_atoms(union([a],[b]),w), union_oracle([a],[b],w),'union'),
   (region_atoms(intersection([a],[b]),w), dense_intersection_oracle([a],[b],w),'int'),
   (region_atoms(difference([a],[b],working_zoom=w),w), dense_difference_oracle([a],[b],w),'diff')]
  for got,exp,tag in vals:
   cases+=1; ok=got==exp; passed+=ok
   if not ok and len(failures)<20: failures.append(('2D',tag,a,b))
record('2D exhaustive Boolean (depth 1-2)',cases,passed,time.perf_counter()-T)

# Random 3D/4D boolean, zoom 2-4 @4
for dims,n in [(('x','y','f'),1500),(('x','y','f','t'),1000)]:
 T=time.perf_counter(); w={a:4 for a in dims}; cases=passed=0
 for _ in range(n):
  a=rc(dims,2,4); b=rc(dims,2,4)
  vals=[(region_atoms(union([a],[b]),w),union_oracle([a],[b],w),'union'),
        (region_atoms(intersection([a],[b]),w),dense_intersection_oracle([a],[b],w),'int'),
        (region_atoms(difference([a],[b],working_zoom=w),w),dense_difference_oracle([a],[b],w),'diff')]
  for got,exp,tag in vals:
   cases+=1; ok=got==exp; passed+=ok
   if not ok and len(failures)<20: failures.append((f'{len(dims)}D',tag,a,b))
 record(f'{len(dims)}D randomized Boolean',cases,passed,time.perf_counter()-T)

# normalize properties, bounded atoms @4, z 2-4
for dims,n in [(('x',),1000),(('x','y'),800),(('x','y','f'),400),(('x','y','f','t'),200)]:
 T=time.perf_counter(); w={a:4 for a in dims}; cases=passed=0
 for _ in range(n):
  reg=[rc(dims,2,4) for j in range(rng.randint(1,8))]; nn=normalize(reg)
  checks=[semantic_equal(reg,nn,w), normalize(nn)==nn, normalize(list(reversed(reg)))==nn,
          all(not (i!=j and subsumes(nn[i],nn[j])) for i in range(len(nn)) for j in range(len(nn)))]
  cases+=4; passed+=sum(checks)
  if not all(checks) and len(failures)<20: failures.append((f'{len(dims)}D normalize',checks,reg,nn))
 record(f'{len(dims)}D normalization properties',cases,passed,time.perf_counter()-T)

# refine/coarsen semantic exactness for refine, conservative cover for coarsen
for dims,n in [(('x',),1000),(('x','y'),800),(('x','y','f'),400),(('x','y','f','t'),200)]:
 T=time.perf_counter(); cases=passed=0
 for _ in range(n):
  c=rc(dims,2,3); axes=list(dims)[:min(2,len(dims))]
  kids=refine(c,axes)
  w={a:max([q.zooms[AXES.index(a)] for q in kids]) for a in dims}
  cases+=1; ok=semantic_equal([c],kids,w); passed+=ok
  # coarsen one bit each if possible and verify original is contained in coarsened cell
  targets={a:max(1,c.zooms[AXES.index(a)]-1) for a in dims}
  cc=coarsen(c,targets)
  cases+=1; ok2=subsumes(cc,c); passed+=ok2
  if (not ok or not ok2) and len(failures)<20: failures.append((f'{len(dims)}D refine/coarsen',c))
 record(f'{len(dims)}D refine/coarsen properties',cases,passed,time.perf_counter()-T)

# Morphology definitions + closure via canonicalizing dense atoms
for dims,w,offs,n in [
 (('x',),{'x':5},[(-1,),(0,),(1,)],600),
 (('x','y'),{'x':4,'y':4},[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1)],400)]:
 T=time.perf_counter(); cases=passed=0
 for _ in range(n):
  reg=normalize([rc(dims,2,min(w.values())) for j in range(rng.randint(1,5))])
  for op in ('dilate','erode','frontier'):
   aa=morph_atoms(reg,w,dims,offs,op); can=normalize(aa)
   ok=(region_atoms(can,w)==aa and normalize(can)==can)
   cases+=1; passed+=ok
   if not ok and len(failures)<20: failures.append((f'{len(dims)}D morph',op,reg))
 record(f'{len(dims)}D morphology/frontier reference semantics + closure',cases,passed,time.perf_counter()-T)

# Cell ID serialization round-trip for full XYHT only (avoids leading-zero flag ambiguity)
T=time.perf_counter(); cases=passed=0
for _ in range(2000):
 c=rc(('x','y','f','t'),1,16)
 cases+=1
 try:
  back=Cell.from_id(c.to_id()); ok=(back==c)
 except Exception: ok=False
 passed+=ok
 if not ok and len(failures)<20: failures.append(('XYHT Cell ID roundtrip',c))
record('XYHT Cell descriptor -> BST-ID int -> descriptor',cases,passed,time.perf_counter()-T)

# UAS membership exhaustive descendants of one reservation (+2 per axis)
T=time.perf_counter(); cases=passed=0
r=Cell.from_parts(x=(3,5),y=(4,6),f=(2,2),t=(3,3))
for sx in range(4):
 for sy in range(4):
  for sf in range(4):
   for st in range(4):
    q=Cell.from_parts(x=(5,(5<<2)|sx),y=(6,(6<<2)|sy),f=(4,(2<<2)|sf),t=(5,(3<<2)|st))
    cases+=1; ok=contains([r],q); passed+=ok
record('XYHT reserved-route descendant membership',cases,passed,time.perf_counter()-T)

# Selective difference complexity counts for single path, Delta 1..12, D 1..4 equal delta
complexity=[]
for D in range(1,5):
 for delta in range(1,13):
  G=2**(D*delta)
  # Idealized single localized path: one split per added bit along each active dimension, 2 children generated per split.
  K=2*D*delta
  complexity.append({'D':D,'delta':delta,'G_full_atoms':G,'K_selective_generated':K,'ratio_G_over_K':G/K})

outdir=Path(__file__).resolve().parent; outdir.mkdir(exist_ok=True)
with open(outdir/'validation_results.json','w') as f: json.dump({'results':results,'failures':failures,'complexity':complexity},f,indent=2,default=str)
with open(outdir/'validation_summary.csv','w',newline='') as f:
 wri=csv.DictWriter(f,fieldnames=['test','cases','passed','failed','seconds']); wri.writeheader(); wri.writerows(results)
with open(outdir/'complexity_curves.csv','w',newline='') as f:
 wri=csv.DictWriter(f,fieldnames=complexity[0].keys()); wri.writeheader(); wri.writerows(complexity)
print(json.dumps(results,indent=2))
print('TOTAL',sum(r['cases'] for r in results),'PASSED',sum(r['passed'] for r in results),'FAILED',sum(r['failed'] for r in results))
print('failures saved:',len(failures))
