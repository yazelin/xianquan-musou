import json,urllib.request,os
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='project-e35e734b-478d-458b-9221-294f81398b59'
base=f'https://larch.ink/api/agent/projects/{P}'
def req(method,url,body=None,headers={}):
    r=urllib.request.Request(url,method=method,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+K,'Content-Type':'application/json',**headers})
    with urllib.request.urlopen(r) as f: return f.status,dict(f.headers),json.loads(f.read())
st,h,j=req('GET',base+'/boards/board-main'); rev=36; print({k:v for k,v in h.items() if k.lower() in ('etag',)}, list(j.keys())[:8])
T={'slime':('史萊姆','slime',[(24,50),(45,110),(80,220)]),
   'bat':('蝙蝠','ghost',[(28,40),(50,90),(90,180)]),
   'spider':('毒蜘蛛','slime',[(40,130),(70,260),(120,500)]),
   'ghost':('幽靈','ghost',[(55,200),(95,400),(160,750)]),
   'demon':('紅魔將','dragon',[(90,900),(140,1500),(220,2500)])}
names=['精英','狂暴','魔化']
y=0
for k,(nm,rig,tiers) in T.items():
    for i,(atk,hp) in enumerate(tiers):
        nid=f'battle-{k}-{i+2}'
        en={"id":k,"name":names[i]+nm,"image":"","hp":hp,"attack":atk,"defense":2+3*i,"rig":rig}
        if k=='demon': en["specials"]=[{"kind":"strike","name":"烈焰重擊","every":4,"power":2}]
        body={"summary":f"強化戰鬥卡：{names[i]}{nm} 攻{atk} 血{hp}","create":True,"position":{"x":800+i*300,"y":100+y*160},
              "battle":{"name":names[i]+nm,"enemies":[en],"allowEscape":True,"rewardItemId":"","rewardItemName":"","rewardCount":0}}
        try:
            st,h,j=req('POST',base+f'/boards/board-main/nodes/{nid}/rpg-battle',body,{'If-Match':str(rev)})
            rev=j.get('revision',rev); print(nid,st,rev)
        except urllib.error.HTTPError as e: print(nid,e.code,e.read()[:300]); raise SystemExit
    y+=1
