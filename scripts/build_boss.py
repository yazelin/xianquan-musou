import json,urllib.request,os,copy
from mcp_call import call as mcp
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='project-e35e734b-478d-458b-9221-294f81398b59'; base='https://larch.ink/api/agent/projects/'+P
r=urllib.request.urlopen(urllib.request.Request(base+'/boards/board-main',headers={'Authorization':'Bearer '+K})); brev=int(r.headers.get('X-Larch-Revision'))
b=json.loads(r.read())['board']; n=[x for x in b['nodes'] if x['id']=='map-arena'][0]; m=n['data']['pluginValues']['map']; m=json.loads(m) if isinstance(m,str) else m
W,H=m['width'],m['height']; U=json.load(open('boss_urls.json'))
occ={(e['x'],e['y']) for e in m['events']}
blocked=lambda x,y: any(L.get('collision') and L['tiles'][y*W+x] for L in m['layers'])
def free(x,y):
    for d in range(0,12):
        for dx in range(-d,d+1):
            for dy in range(-d,d+1):
                X,Y=x+dx,y+dy
                if 0<=X<W and 0<=Y<H and (X,Y) not in occ and not blocked(X,Y): occ.add((X,Y)); return X,Y
z=lambda **k:{"text":"","cardId":"","itemId":"","itemName":"","amount":1,"variable":"","value":"",**k}
V=lambda id,var,val,op=None: z(id=id,kind="variable",variable=var,value=str(val),**({"op":op} if op else {}))
C=lambda var,val,op="eq": {"kind":"variable","variable":var,"op":op,"value":str(val),"itemId":"","count":1}
ST=C("started","true")
def spr(k,scale): u=U[k]; return {"url":u['url'],"width":u['w'],"height":u['h'],"frames":3,"rows":1,"offsetX":0,"offsetY":0,"idleFrame":0,"scale":scale,"faces":"right"}
ops=[]
# bosses
BOSS=[('liubei','劉備',1,(40,18),1.4,'liu'),('guanyu','關羽',1,(43,20),1.5,'guan'),('zhangfei','張飛',1,(40,22),1.45,'zhang'),
      ('dongzhuo','董卓',3,(44,30),2.2,None),('caocao1','曹操',5,(14,30),1.8,None),('jiling','紀靈',7,(46,10),1.8,None),('caocao2','曹操・下邳',9,(28,34),2.1,None)]
for k,nm,stg,pos,sc,flag in BOSS:
    eid='boss-'+k; x,y=free(*pos); s=spr('caocao' if k.startswith('caocao') else k,sc)
    def acts(t):
        a=[z(id=f'{eid}-b{t}',kind="battle",cardId=f'boss-{k}-{t}')]
        if flag: a+=[V(f'{eid}-k{t}','kills',5,'add'),z(id=f'{eid}-m{t}',kind="item",itemId="medal",itemName="戰功",amount=5),V(f'{eid}-d{t}','sanying_down',1,'add'),V(f'{eid}-f{t}',flag+'_down','true')]
        else: a+=[V(f'{eid}-k{t}','kills',10,'add'),z(id=f'{eid}-m{t}',kind="item",itemId="medal",itemName="戰功",amount=10),V(f'{eid}-s{t}','boss_stage',1,'add'),V(f'{eid}-z{t}','bk',0)]
        a+=[z(id=f'{eid}-p{t}',kind="item",itemId="potion",itemName="補血藥水",amount=2),z(id=f'{eid}-e{t}',kind="item",itemId="ether",itemName="回氣丹",amount=2)]
        return a
    base_c=[ST,C('boss_stage',stg)]
    pg=lambda t:{"id":f'{eid}-t{t}',"name":f'第{t}輪',"conditions":base_c+[C('boss_round',t,'gte')],"actor":"npc","sprite":s,"movement":"approach","approach":20,"direction":"left","solid":True,"trigger":"touch","once":False,"actions":acts(t)}
    pages=[pg(t) for t in range(2,11)]
    if flag: pages.append({"id":f'{eid}-down',"name":"倒下","conditions":base_c+[C(flag+'_down','true')],"actor":"none","sprite":s,"movement":"still","solid":False,"trigger":"action","once":False,"actions":[]})
    ops.append({"kind":"event","id":eid,"patch":{"name":nm+"（Boss）","x":x,"y":y,"actor":"npc","kind":"monster","sprite":s,"movement":"approach","approach":20,"direction":"left","solid":True,"trigger":"touch","once":False,"conditions":base_c+[],"actions":acts(1),"pages":pages,
        "badge":{"icon":"crown","color":"#d23c3c"}}})
# directors on top row
def dir_(eid,nm,conds,acts):
    x,y=free(20,0); ops.append({"kind":"event","id":eid,"patch":{"name":nm,"x":x,"y":y,"actor":"none","movement":"still","solid":False,"trigger":"parallel","once":False,"conditions":[ST]+conds,"actions":acts}})
FX=lambda p:[z(id=p+'-snd',kind="sound",audio={"url":"","sound":"roar","volume":0.9}),z(id=p+'-shk',kind="screen",screen={"effect":"shake","strength":0.6,"durationMs":700,"wait":False})]
SAY=lambda p,t:z(id=p+'-say',kind="dialogue",text=t,speaker="narrator",presentation="text")
for stg,gap,line in [(0,40,'虎牢關前，劉備、關羽、張飛三人一起殺到。'),(2,50,'董卓現身。'),(4,60,'曹操領兵來到濮陽。'),(6,70,'紀靈率袁術軍殺到。'),(8,80,'下邳城外，曹操親自來了。')]:
    p=f'dir-{stg+1}'; dir_(p,f'Boss 出場 {stg+1}',[C('boss_round',1),C('boss_stage',stg),C('bk',gap,'gte')],[V(p+'-v','boss_stage',stg+1)]+FX(p)+[SAY(p,line)])
dir_('dir-sy','三英全倒',[C('boss_stage',1),C('sanying_down',3,'gte')],[V('dsy-1','boss_stage',2),V('dsy-2','bk',0),V('dsy-3','sanying_down',0),V('dsy-4','liu_down','false'),V('dsy-5','guan_down','false'),V('dsy-6','zhang_down','false')])
dir_('dir-loop','無雙下一輪',[C('boss_stage',10)],[V('dl-1','boss_stage',0),V('dl-2','bk',0),V('dl-3','boss_round',1,'add')]+FX('dl')+[SAY('dl','五員大將都倒下了。無雙開始，接下來的每一位都更強。')])
NAMES=[(1,'劉備、關羽、張飛'),(3,'董卓'),(5,'曹操'),(7,'紀靈'),(9,'下邳的曹操')]
dir_('dir-musou','無雙 隨機出王',[C('boss_round',2,'gte'),C('boss_stage',0),C('bk',40,'gte')],
  [z(id='dm-r',kind="random",random={"min":1,"max":5,"options":[{"id":f"dm-o{i}","label":nm,"from":i+1,"to":i+1,"actions":[V(f'dm-v{i}','boss_stage',stg),SAY(f'dm{i}',f'無雙！{nm}殺到，比上一位更強。')]} for i,(stg,nm) in enumerate(NAMES)]})]+FX('dm'))
for stg in (2,4,6,8):
    dir_(f'dir-next{stg}',f'無雙 下一位 {stg}',[C('boss_round',2,'gte'),C('boss_stage',stg)],[V(f'dn{stg}-1','boss_stage',0),V(f'dn{stg}-2','bk',0),V(f'dn{stg}-3','boss_round',1,'add')])
RESET=lambda p:[V(p+'-r1','boss_stage',0),V(p+'-r2','bk',0),V(p+'-r3','boss_round',1),V(p+'-r4','sanying_down',0),V(p+'-r5','liu_down','false'),V(p+'-r6','guan_down','false'),V(p+'-r7','zhang_down','false')]
ev={e['id']:e for e in m['events']}
# init-score
ini=ev['init-score']; ops.append({"kind":"event","id":"init-score","patch":{"actions":[a for a in ini['actions'] if not a['id'].startswith('ini-r')]+RESET('ini')}})
# reaper: insert reset right after the choice in every list
rp=copy.deepcopy(ev['reaper'])
def addreset(acts,p):
    acts[:]=[a for a in acts if not a['id'].startswith(p+'-r')]
    i=[j for j,a in enumerate(acts) if a['kind']=='choice'][0]; acts[i+1:i+1]=RESET(p)
addreset(rp['actions'],'rp0')
for pgx in rp['pages']: addreset(pgx['actions'],'rp'+pgx['id'][3:])
ops.append({"kind":"event","id":"reaper","patch":{"actions":rp['actions'],"pages":rp['pages']}})
# bk on every monster kill
for e in m['events']:
    if not (e['id'].startswith('m-') or e['id'].startswith('h-')): continue
    e=copy.deepcopy(e)
    def addbk(acts,p):
        acts[:]=[a for a in acts if not a['id'].endswith('-bk')]
        i=[j for j,a in enumerate(acts) if a['kind']=='variable' and a['variable']=='kills'][0]; acts.insert(i+1,V(p+'-bk','bk',1,'add'))
    addbk(e['actions'],e['id']+'-0')
    for pgx in e.get('pages',[]): addbk(pgx['actions'],e['id']+'-'+pgx['id'])
    ops.append({"kind":"event","id":e['id'],"patch":{"actions":e['actions'],"pages":e.get('pages',[])}})
# guidance
G=[{"text":t,"eventId":eid,"conditions":c} for t,eid,c in [
 ('三英來襲：劉備、關羽、張飛三人一起上','boss-guanyu',[C('boss_stage',1)]),
 ('董卓現身：血厚力大，小心他的重擊','boss-dongzhuo',[C('boss_stage',3)]),
 ('濮陽：曹操來了，他會架起防守','boss-caocao1',[C('boss_stage',5)]),
 ('淮北：紀靈率袁術軍殺到','boss-jiling',[C('boss_stage',7)]),
 ('下邳決戰：曹操親至','boss-caocao2',[C('boss_stage',9)]),
 ('無雙模式：五員大將隨機殺到，一位比一位強','reaper',[C('boss_round',2,'gte')])]]
old=[g for g in m.get('guidance',[]) if g['eventId'] not in [x['eventId'] for x in G]]
ops.append({"kind":"settings","patch":{"guidance":G+old}})
json.dump(ops,open('ops_boss.json','w'),ensure_ascii=False)
print(len(ops),'ops', sum(len(json.dumps(o)) for o in ops),'bytes; brev',brev)
if os.environ.get('GO'):
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":brev,"summary":"加入五大 Boss（三英、董卓、曹操、紀靈、下邳曹操）與無雙輪迴","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:600] if 'isError' in t else 'ok')
