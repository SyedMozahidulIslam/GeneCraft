from __future__ import annotations
import math, random
from typing import Tuple

def clamp(value, lo, hi): return max(lo, min(hi, value))
def clamp01(v): return clamp(v, 0.0, 1.0)
def normalise(v, lo, hi): return clamp01((v-lo)/(hi-lo) if hi!=lo else 0.0)
def lerp(a, b, t): return a + (b-a)*clamp01(t)
def smoothstep(t): t=clamp01(t); return t*t*(3-2*t)
def distance(x1,y1,x2,y2): return math.hypot(x2-x1,y2-y1)
def distance_sq(x1,y1,x2,y2): dx,dy=x2-x1,y2-y1; return dx*dx+dy*dy
def manhattan(x1,y1,x2,y2): return abs(x2-x1)+abs(y2-y1)
def lerp_color(c1,c2,t):
    t=clamp01(t)
    return (int(c1[0]+(c2[0]-c1[0])*t),int(c1[1]+(c2[1]-c1[1])*t),int(c1[2]+(c2[2]-c1[2])*t))

def shannon_entropy(counts: dict) -> float:
    total = sum(counts.values())
    if total==0 or len(counts)<2: return 0.0
    h=0.0
    for count in counts.values():
        if count>0:
            p=count/total; h -= p*math.log(p)
    max_h=math.log(len(counts))
    return h/max_h if max_h>0 else 0.0

def weighted_choice(items, weights):
    total=sum(weights); r=random.uniform(0,total); cum=0.0
    for item,w in zip(items,weights):
        cum+=w
        if r<=cum: return item
    return items[-1]

def fade(t): return t*t*t*(t*(t*6-15)+10)
def grad(h,x,y): h=h&3; u=x if h<2 else y; v=y if h<2 else x; return (u if (h&1)==0 else -u)+(v if (h&2)==0 else -v)

class PerlinNoise2D:
    def __init__(self, seed=0):
        rng=random.Random(seed); p=list(range(256)); rng.shuffle(p); self._perm=p*2
    def sample(self,x,y):
        xi=int(math.floor(x))&255; yi=int(math.floor(y))&255
        xf=x-math.floor(x); yf=y-math.floor(y)
        u=fade(xf); v=fade(yf); p=self._perm
        aa=p[p[xi]+yi]; ab=p[p[xi]+yi+1]; ba=p[p[xi+1]+yi]; bb=p[p[xi+1]+yi+1]
        return lerp(lerp(grad(aa,xf,yf),grad(ba,xf-1,yf),u),lerp(grad(ab,xf,yf-1),grad(bb,xf-1,yf-1),u),v)
    def sample01(self,x,y): return clamp01((self.sample(x,y)+1.0)*0.5)
    def octaves(self,x,y,octaves=6,persistence=0.5,lacunarity=2.0,scale=0.01):
        total=0.0; amplitude=1.0; frequency=scale; max_val=0.0
        for _ in range(octaves):
            total+=self.sample(x*frequency,y*frequency)*amplitude
            max_val+=amplitude; amplitude*=persistence; frequency*=lacunarity
        return clamp01((total/max_val+1.0)*0.5)
