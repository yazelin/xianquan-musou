import json,urllib.request,os,copy,itertools,time,base64
from mcp_call import call as mcp
from regions import board, P
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
H={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
base='https://larch.ink/api/agent/projects/'+P
A=['weixu','diaochan','quan','lubu','xiang']; NM={'weixu':'魏續','diaochan':'貂蟬','quan':'呂荃','lubu':'呂布','xiang':'嚴湘'}
WP={'weixu':'環首刀','diaochan':'紫玉法器','quan':'小木弓','lubu':'方天畫戟','xiang':'漢代剪刀'}
z=lambda **k:{"text":"","cardId":"","itemId":"","itemName":"","amount":1,"variable":"","value":"",**k}
V=lambda id,var,val,op=None: z(id=id,kind="variable",variable=var,value=str(val),**({"op":op} if op else {}))
C=lambda var,val,op="eq": {"kind":"variable","variable":var,"op":op,"value":str(val),"itemId":"","count":1}
def rq(path,method='GET',body=None,extra={}):
    for t in range(8):
        try:
            r=urllib.request.Request(base+path,method=method,data=json.dumps(body).encode() if body else None,headers={**H,**extra})
            return json.loads(urllib.request.urlopen(r).read())
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(30); continue
            print(path,e.code,e.read()[:300]); raise
if os.environ.get('ITEM'):
    icon=rq('/media','POST',{"name":"musou_icon_ling.png","mimeType":"image/png","category":"ui","base64":base64.b64encode(open('icons/ling.png','rb').read()).decode()})['asset']['url']; time.sleep(4)
    lib=rq('/rpg-library'); rv=lib.pop('revision')
    lib['items']=[i for i in lib['items'] if i['id']!='ling']+[{"id":"ling","name":"帥令","icon":icon,"note":"按 C 換主角：從同行的隊友裡挑一位帶隊，等級、血量、技能都跟著換。","heal":0,
      "bag":{"consumable":False,"effectKind":"set","effectVar":"swap_req","effectValue":"true","useConditionVariable":"","useConditionValue":"","useConditionMessage":""},"hotkey":"c"}]
    lib['summary']='新增帥令（C 鍵換主角）'
    rq('/rpg-library','PUT',lib,{'If-Match':str(rv)}); print('item ok')
def swap_steps(pid,h,t):
    return [z(id=f'{pid}-{t}-r',kind="removeItem",itemId=f'g-{h}',itemName=WP[h]),
            z(id=f'{pid}-{t}-h',kind="hero",value=t,keep=True),
            z(id=f'{pid}-{t}-p',kind="party",value=h,party="follow"),
            V(f'{pid}-{t}-c','cur_hero',t),V(f'{pid}-{t}-j1','joined_'+h,'true'),V(f'{pid}-{t}-j2','joined_'+t,'false'),
            z(id=f'{pid}-{t}-i',kind="item",itemId=f'g-{t}',itemName=WP[t])]
rev,m=board(); ev={e['id']:e for e in m['events']}
pages=[]
for h in A:
    others=[a for a in A if a!=h]
    for n in range(1,5):
        for joined in itertools.combinations(others,n):
            pid=f'sw-{h}-'+'-'.join(joined)
            conds=[C('swap_req','true'),C('cur_hero',h)]+[C('joined_'+a,'true' if a in joined else 'false') for a in others]
            acts=[V(pid+'-off','swap_req','false')]
            if n==1: acts+=swap_steps(pid,h,joined[0])
            else: acts.append(z(id=pid+'-c',kind="choice",text="",speaker="narrator",choice={"options":[{"id":f'{pid}-o-{t}',"label":f'{NM[t]}帶隊',"actor":t,"actions":swap_steps(pid,h,t)} for t in joined],"look":"wheel","cancel":"*skip","color":"#e0b050"}))
            pages.append({"id":pid,"name":f"{NM[h]}帶隊時換人","conditions":conds,"actor":"none","sprite":{"url":"","width":32,"height":32,"frames":1,"rows":1,"offsetX":0,"offsetY":0,"idleFrame":0},
                          "movement":"still","solid":False,"trigger":"condition","once":False,"actions":acts})
occ={(e['x'],e['y']) for e in m['events']}
x,y=(ev['swap']['x'],ev['swap']['y']) if 'swap' in ev else next((x,0) for x in range(20,62) if (x,0) not in occ)
ops=[{"kind":"event","id":"swap","patch":{"name":"帥令換主角","x":x,"y":y,"actor":"none","movement":"still","solid":False,"trigger":"condition","once":False,
     "conditions":[C('swap_req','true')],"actions":[V('sw0-off','swap_req','false'),z(id='sw0-say',kind="dialogue",text="還沒有隊友同行。打倒王，援軍就會來。",speaker="narrator",presentation="text")],"pages":pages}}]
# intro: give 帥令 once + mention C in help
it=copy.deepcopy(ev['intro'])
it['actions']=[a for a in it['actions'] if a['id']!='ling-give']
i=[j for j,a in enumerate(it['actions']) if a['kind']=='choice'][0]
it['actions'].insert(i+1,z(id='ling-give',kind="item",itemId="ling",itemName="帥令"))
for a in it['actions']:
    if a['kind']=='dialogue' and '操作說明' in a['text'] and 'C 換主角' not in a['text']:
        a['text']=a['text'].replace("X 開選單","C 換主角（從同行的隊友挑一位帶隊）\nX 開選單")
ops.append({"kind":"event","id":"intro","patch":{"actions":it['actions']}})
print(len(pages),'pages',sum(len(json.dumps(o)) for o in ops),'bytes')
if os.environ.get('GO'):
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"帥令（C 鍵）換主角：等級、血量、技能一起換，原主角轉成隊友","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:800] if 'isError' in t else 'ok')
