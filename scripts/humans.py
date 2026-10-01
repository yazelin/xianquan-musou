import json,urllib.request,os,time
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
def req(method,url,body=None,headers={}):
    r=urllib.request.Request(url,method=method,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+K,'Content-Type':'application/json',**headers})
    with urllib.request.urlopen(r) as f: return json.loads(f.read())
rev=json.loads(urllib.request.urlopen(urllib.request.Request(base+'/rpg-library',headers={'Authorization':'Bearer '+K})).read())['revision']
H={'cao':('曹軍步兵',[(12,30),(28,70),(50,150),(85,300)]),
   'dong':('董卓軍刀兵',[(25,70),(45,150),(80,300),(130,550)]),
   'chang':('常山槍兵',[(35,110),(60,220),(100,420),(160,800)]),
   'cav':('西涼鐵騎',[(60,300),(95,600),(145,1100),(230,1900)])}
pre=['','精英','狂暴','魔化']
y=0
for k,(nm,tiers) in H.items():
    for i,(atk,hp) in enumerate(tiers):
        nid=f'battle-{k}' + ('' if i==0 else f'-{i+1}')
        en={"id":k,"name":pre[i]+nm,"image":"","hp":hp,"attack":atk,"defense":2+3*i,"rig":"slime"}
        body={"summary":f"人類敵兵戰鬥卡：{pre[i]}{nm} 攻{atk} 血{hp}","create":True,"position":{"x":800+i*300,"y":900+y*160},
              "battle":{"name":pre[i]+nm,"enemies":[en],"allowEscape":True,"rewardItemId":"","rewardItemName":"","rewardCount":0}}
        for t in range(30):
            try:
                j=req('POST',base+f'/boards/board-main/nodes/{nid}/rpg-battle',body,{'If-Match':str(rev)}); rev=j.get('revision',rev); print(nid,rev,flush=True); break
            except urllib.error.HTTPError as e:
                if e.code==429: time.sleep(30); continue
                print(nid,e.code,e.read()[:300],flush=True); raise SystemExit
        time.sleep(10)
    y+=1
print('done',rev)
