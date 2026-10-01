import json,urllib.request,os,time,sys
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
def rev():
    r=urllib.request.urlopen(urllib.request.Request(base+'/boards/board-main',headers={'Authorization':'Bearer '+K})); return r.headers.get('X-Larch-Revision')
B={ # id: name, hp, atk, def, specials
 'liubei':('劉備',350,40,4,[{"kind":"heal","name":"仁德","below":40,"amount":80,"times":2}]),
 'guanyu':('關羽',400,48,5,[{"kind":"strike","name":"青龍斬","every":4,"power":2}]),
 'zhangfei':('張飛',380,44,3,[{"kind":"double","name":"燕人連突","every":3}]),
 'dongzhuo':('董卓',2000,75,8,[{"kind":"strike","name":"西涼鐵騎","every":4,"power":2},{"kind":"enrage","name":"暴怒","below":30,"power":1.5}]),
 'caocao1':('曹操',2500,100,12,[{"kind":"guard","name":"堅守","every":4},{"kind":"strike","name":"虎豹騎","every":5,"power":2}]),
 'jiling':('紀靈',3000,130,14,[{"kind":"double","name":"三尖連斬","every":3},{"kind":"enrage","name":"死戰","below":30,"power":1.5}]),
 'caocao2':('曹操・下邳',5000,170,18,[{"kind":"strike","name":"水淹下邳","every":4,"power":2},{"kind":"heal","name":"重整","below":30,"amount":800,"times":1},{"kind":"enrage","name":"決戰","below":20,"power":1.6}]),
}
NUM=['','貳','參','肆','伍','陸','柒','捌','玖','拾']
todo=[(k,t) for k in B for t in range(7,11)]
if len(sys.argv)>1: todo=[(sys.argv[1],int(sys.argv[2]))]
y=0
for k,t in todo:
    nm,hp,atk,df,sp=B[k]
    name=nm+('' if t==1 else '・'+NUM[t-1])
    en={"id":k,"name":name,"image":"","hp":min(9999,round(hp*1.6**(t-1))),"attack":min(9999,round(atk*1.35**(t-1))),"defense":df+2*(t-1),"specials":sp}
    body={"summary":f"Boss 戰鬥卡：{name} 血{en['hp']} 攻{en['attack']}","create":True,"position":{"x":2200+t*300,"y":100+list(B).index(k)*160},
          "battle":{"name":name,"enemies":[en],"allowEscape":False,"rewardItemId":"","rewardItemName":"","rewardCount":0}}
    for a in range(6):
        try:
            r=urllib.request.Request(base+f'/boards/board-main/nodes/boss-{k}-{t}/rpg-battle',method='POST',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+K,'Content-Type':'application/json','If-Match':rev()})
            urllib.request.urlopen(r).read(); print(f'boss-{k}-{t}',en['hp'],en['attack'],flush=True); break
        except urllib.error.HTTPError as e:
            msg=e.read()[:300]; print(k,t,e.code,msg,flush=True)
            if e.code==429: time.sleep(30)
            elif e.code==409: time.sleep(3)
            else: raise SystemExit
    time.sleep(2)
