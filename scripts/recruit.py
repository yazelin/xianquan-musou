import json,urllib.request,os,copy,itertools,time
from mcp_call import call as mcp
from regions import board, P
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/'+P
A=['weixu','diaochan','quan','lubu','xiang']; NM={'weixu':'魏續','diaochan':'貂蟬','quan':'呂荃','lubu':'呂布','xiang':'嚴湘'}
z=lambda **k:{"text":"","cardId":"","itemId":"","itemName":"","amount":1,"variable":"","value":"",**k}
V=lambda id,var,val,op=None: z(id=id,kind="variable",variable=var,value=str(val),**({"op":op} if op else {}))
C=lambda var,val,op="eq": {"kind":"variable","variable":var,"op":op,"value":str(val),"itemId":"","count":1}
STAY=lambda p:[z(id=f'{p}-st-{a}',kind="party",value=a,party="stay") for a in A]
TEAMRESET=lambda p:STAY(p)+[V(f'{p}-j-{a}','joined_'+a,'false') for a in A]+[V(f'{p}-rn','recruited_n',0)]
rev,m=board(); ev={e['id']:e for e in m['events']}
ops=[]
def strip(acts,p): return [a for a in acts if not a['id'].startswith(p+'-st-') and not a['id'].startswith(p+'-j-') and a['id']!=p+'-rn']
# reaper: after the boss reset block (or after the choice)
rp=copy.deepcopy(ev['reaper'])
def addteam(acts,p):
    acts[:]=strip(acts,p)
    i=[j for j,a in enumerate(acts) if a['kind']=='choice'][0]; acts[i+1:i+1]=TEAMRESET(p)
addteam(rp['actions'],'tm0')
for pg in rp['pages']: addteam(pg['actions'],'tm'+pg['id'][3:])
ops.append({"kind":"event","id":"reaper","patch":{"actions":rp['actions'],"pages":rp['pages']}})
# intro: after the hero choice
it=copy.deepcopy(ev['intro']); addteam(it['actions'],'tmi')
ops.append({"kind":"event","id":"intro","patch":{"actions":it['actions']}})
# recruit events
occ={(e['x'],e['y']) for e in m['events']}
def cell():
    for x in range(20,60):
        if (x,0) not in occ: occ.add((x,0)); return x,0
for k in range(1,5):
    pages=[]
    for h in A:
        others=[a for a in A if a!=h]
        for joined in itertools.combinations(others,k-1):
            pid=f'r{k}-{h}-'+('-'.join(joined) or 'none')
            avail=[a for a in others if a not in joined]
            opts=[{"id":f'{pid}-o-{a}',"label":f'{NM[a]} 加入',"actions":[z(id=f'{pid}-p-{a}',kind="party",value=a,party="follow"),V(f'{pid}-v-{a}','joined_'+a,'true'),z(id=f'{pid}-s-{a}',kind="sound",audio={"url":"","sound":"chime","volume":0.9}),z(id=f'{pid}-b-{a}',kind="balloon",balloon={"icon":"happy","target":"player","durationMs":2400})]} for a in avail]
            conds=[C('started','true'),C('boss_round',1),C('boss_stage',2*k),C('recruited_n',k-1),C('cur_hero',h)]+[C('joined_'+a,'true' if a in joined else 'false') for a in others]
            pages.append({"id":pid,"name":f"第{k}位：{NM[h]}帶隊","conditions":conds,"actor":"none","sprite":{"url":"","width":32,"height":32,"frames":1,"rows":1,"offsetX":0,"offsetY":0,"idleFrame":0},
               "movement":"still","solid":False,"trigger":"parallel","once":False,
               "actions":[V(f'{pid}-done','recruited_n',k)]+([z(id=f'{pid}-c',kind="choice",text="援軍到了。要誰一起上陣？",speaker="narrator",choice={"options":opts})] if len(opts)>1 else
                  [z(id=f'{pid}-say',kind="dialogue",text=f"{NM[avail[0]]}也趕到了。五個人，到齊了。",speaker="narrator",presentation="text")]+opts[0]['actions'])})
    x,y=(ev[f'rec-{k}']['x'],ev[f'rec-{k}']['y']) if f'rec-{k}' in ev else cell()
    ops.append({"kind":"event","id":f'rec-{k}',"patch":{"name":f"招募第{k}位隊友","x":x,"y":y,"actor":"none","movement":"still","solid":False,"trigger":"parallel","once":False,
        "conditions":[C('recruited_n',99)],"actions":[],"pages":pages}})
    print('rec',k,len(pages),'pages')
print(len(ops),'ops',sum(len(json.dumps(o)) for o in ops),'bytes')
if os.environ.get('GO'):
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"打倒前四位王各可選一位隊友加入；隊友平時在後方一起累積經驗","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:800] if 'isError' in t else 'ok')
