from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from scipy import ndimage
SRC={'weixu':'sd/weixu_side1b_raw.png','xiang':'sd/xiang_han_raw.png'}
FLIP={'weixu'}
def cut(k,h):
    a=np.array(Image.open(SRC.get(k,f'sd/{k}_raw.png')).convert('RGBA')).astype(int)
    r,g,b=a[...,0],a[...,1],a[...,2]
    key=(g>140)&(g>r+60)&(g>b+60); s=a.shape[0]/1024
    edge=(~key)&ndimage.binary_dilation(key,iterations=max(2,int(3*s)))
    a[...,3]=np.where(key,0,255); a[...,1]=np.where(edge,np.minimum(g,np.maximum(r,b)+25),g)
    if k!='quan':
        pure=(g>170)&(r<110)&(b<110)&(g>r+90)&(g>b+90); a[...,3]=np.where(pure,0,a[...,3])
    o=Image.fromarray(a.astype('uint8')); o=o.crop(o.getbbox()); w=round(o.width*h/o.height); o=o.resize((w,h),Image.LANCZOS)
    return o.transpose(Image.FLIP_LEFT_RIGHT) if k in FLIP else o
mp=Image.open('map_render.png').convert('RGBA')
bg=mp.crop((384,0,960,324)).resize((1920,1080),Image.NEAREST); W,H=bg.size
px=np.zeros((H,W,4),dtype=np.uint8); xs=np.arange(W)/W
px[...,3]=(np.clip(0.82-1.3*np.maximum(xs-0.12,0),0.15,0.82)*255).astype(np.uint8)[None,:]; px[...,:3]=(10,12,18)
bg.alpha_composite(Image.fromarray(px))
S=0.92; DX=int(__import__('os').environ.get('DX','-170'))
L=[('weixu',440,1010,800),('xiang',440,1790,800),('lubu',580,1400,820),('quan',400,1120,1000),('diaochan',420,1680,1000)]
for k,h,cx,fy in L:
    h=int(h*S); cx=int(1400+(cx-1400)*S)+DX; fy=int(560+(fy-560)*S)+40
    c=cut(k,h); sh=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(sh)
    d.ellipse((cx-c.width*0.32,fy-16,cx+c.width*0.32,fy+16),fill=(0,0,0,120)); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    bg.alpha_composite(c,(int(cx-c.width/2),int(fy-c.height)))
bg.convert('RGB').save(__import__('os').environ.get('OUT','cover/cover3.png'))
