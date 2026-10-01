from PIL import Image
import numpy as np, json, os, base64, urllib.request, time
from scipy import ndimage
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
out={}
ks=['liubei','guanyu','zhangfei','dongzhuo','caocao','jiling']
prev=[]
for k in ks:
    a=np.array(Image.open(f'sd/boss_{k}_raw.png').convert('RGBA')).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]
    key=(r>150)&(b>150)&(g<r-70)&(g<b-70)
    # ponytail: only keep key regions connected to the border, so magenta-ish details inside survive
    lab,n=ndimage.label(key); border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    key=np.isin(lab,list(border))|((r>190)&(b>190)&(g<90))
    s=a.shape[0]/1024
    edge=(~key)&ndimage.binary_dilation(key,iterations=max(2,int(3*s)))
    a[...,3]=np.where(key,0,255)
    m=np.minimum(r,b); a[...,0]=np.where(edge,np.minimum(r,g+40),r); a[...,2]=np.where(edge,np.minimum(b,g+40),b)
    o=Image.fromarray(a.astype('uint8')); o=o.crop(o.getbbox()); h=128; w=round(o.width*h/o.height); o=o.resize((w,h),Image.LANCZOS)
    arr=np.array(o); arr[...,3]=np.where(arr[...,3]>128,255,0); o=Image.fromarray(arr)
    c=Image.new('RGBA',(max(w,96),h),(0,0,0,0)); c.paste(o,((c.width-w)//2,0),o); c.save(f'sd/boss_{k}.png')
    W,H=c.width,h+8
    def fr(dy,sx=1,sy=1):
        f=Image.new('RGBA',(W,H),(0,0,0,0)); t=c.resize((round(W*sx),round(h*sy)),Image.LANCZOS) if (sx,sy)!=(1,1) else c
        f.alpha_composite(t,((W-t.width)//2,H-t.height-dy)); return f
    sh=Image.new('RGBA',(W*3,H),(0,0,0,0))
    for i,f in enumerate([fr(0),fr(7),fr(0,1.04,0.96)]): sh.alpha_composite(f,(i*W,0))
    sh.save(f'sd/boss_{k}_walk.png'); prev.append(c)
    for t in range(6):
        try:
            rq=urllib.request.Request(base+'/media',method='POST',data=json.dumps({"name":f"musou_walk_boss_{k}.png","mimeType":"image/png","category":"character","base64":base64.b64encode(open(f'sd/boss_{k}_walk.png','rb').read()).decode()}).encode(),headers={'Authorization':'Bearer '+K,'Content-Type':'application/json'})
            out[k]={"url":json.loads(urllib.request.urlopen(rq).read())['asset']['url'],"w":W,"h":H}; print(k,W,H,flush=True); break
        except urllib.error.HTTPError as e: print(k,e.code); time.sleep(30)
    time.sleep(4)
json.dump(out,open('boss_urls.json','w'),indent=1)
tot=sum(p.width for p in prev)*2; bg=Image.new('RGB',(tot,272),(90,160,80)); x=0
for p in prev:
    q=p.resize((p.width*2,256),Image.NEAREST); bg.paste(q,(x,8),q); x+=q.width
bg.save('boss_cut_prev.png')
