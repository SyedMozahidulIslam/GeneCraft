from __future__ import annotations
import colorsys, math
from typing import Tuple
Color = Tuple[int,int,int]

def with_alpha(c,a): return (c[0],c[1],c[2],a)
def darken(c,f=0.7): return (int(c[0]*f),int(c[1]*f),int(c[2]*f))
def lighten(c,f=1.3): return (min(255,int(c[0]*f)),min(255,int(c[1]*f)),min(255,int(c[2]*f)))
def lerp_color(c1,c2,t):
    t=max(0.0,min(1.0,t))
    return (int(c1[0]+(c2[0]-c1[0])*t),int(c1[1]+(c2[1]-c1[1])*t),int(c1[2]+(c2[2]-c1[2])*t))
def health_color(ratio):
    if ratio>0.6: return lerp_color((255,170,0),(0,210,100),(ratio-0.6)/0.4)
    return lerp_color((255,68,68),(255,170,0),ratio/0.6)
def species_color(sid):
    h=(hash(sid)&0xFFFFFF)/0xFFFFFF
    r,g,b=colorsys.hsv_to_rgb(h,0.7,0.9)
    return (int(r*255),int(g*255),int(b*255))
def pulse_alpha(tick,period=60,min_a=120,max_a=255):
    t=(math.sin(tick*2*math.pi/period)+1)/2
    return int(min_a+(max_a-min_a)*t)
