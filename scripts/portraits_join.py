# 立繪（資料庫頭像＋成素結算立繪）、隊友加入圖、董卓海報換新版
import json,urllib.request,os,time,base64,copy,http.client
from mcp_call import call as mcp
PID='project-e35e734b-478d-458b-9221-294f81398b59'; K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='https://larch.ink/api/agent/projects/'+PID; A='../assets/'
NM={'weixu':'魏續','diaochan':'貂蟬','quan':'呂荃','lubu':'呂布','xiang':'嚴湘'}
def req(m,path,body=None,et=None,raw=False):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        try:
            r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
            with urllib.request.urlopen(r,timeout=600) as x: return (x.headers.get('ETag') or x.headers.get('X-Larch-Revision')),json.loads(x.read() or b'{}')
        except http.client.IncompleteRead: time.sleep(10)
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503,504): time.sleep(30); continue
            print(e.code,e.read()[:300]); raise
def up(path,name,cat):
    _,j=req('POST','/media',{"name":name,"mimeType":"image/webp","category":cat,"base64":base64.b64encode(open(path,'rb').read()).decode()}); time.sleep(3); return j['asset']['url']
urls=json.load(open(A+'portrait_urls.json')) if os.path.exists(A+'portrait_urls.json') else {}
for k in list(NM)+['chengsu']:
    if 'p_'+k not in urls: urls['p_'+k]=up(A+f'portraits/{k}.webp',f'portrait_{k}.webp','character'); print('up',k,flush=True)
for k in NM:
    if 'j_'+k not in urls: urls['j_'+k]=up(A+f'join/{k}.webp',f'join_{k}.webp','background'); print('up join',k,flush=True)
if 'dongzhuo2' not in urls: urls['dongzhuo2']=up(A+'boss_posters/dongzhuo.webp','boss_poster_dongzhuo_v2.webp','background')
json.dump(urls,open(A+'portrait_urls.json','w'),indent=1)
CS_WALK={"url":"https://pub-4b20b43f5acf4dfaa3f6ab842daa51cf.r2.dev/2d3b0242-9a6d-4051-9825-46aa4efd064a/larch/project-e35e734b-478d-458b-9221-294f81398b59/1790873415348_musou_walk_chengsu.png","width":96,"height":136,"frames":3,"rows":1,"offsetX":0,"offsetY":0,"idleFrame":0,"scale":1.4,"faces":"right"}   # 地圖上成素原本的小人
# 1. 資料庫：五人頭像＋成素（npc）
_,d=req('GET','/rpg-database'); db=d['database']
for a in db['actors']:
    if a['id'] in NM: a['portrait']=urls['p_'+a['id']]
cs=[a for a in db['actors'] if a['id']=='chengsu']
base={"id":"chengsu","name":"成素","title":"呂布的女親兵","profile":"成廉的妹妹，營地的軍師。","role":"npc","walk":CS_WALK,"portrait":urls['p_chengsu'],"kit":"none"}
if cs: cs[0].update(portrait=urls['p_chengsu'])
else: db['actors'].append(base)
req('PUT','/rpg-database',{"summary":"五人頭像＋成素立繪","database":db},str(d['revision']))
_,d2=req('GET','/rpg-database'); print('db portraits',[(a['id'],bool(a.get('portrait'))) for a in d2['database']['actors']])
# 2. 白板：五張加入卡、董卓海報換新版
et,j=req('GET','/boards/board-main'); b=j['board']
os.makedirs('snapshots',exist_ok=True); json.dump(b,open(f'snapshots/board_{int(time.time())}.json','w'),ensure_ascii=False)
b['nodes']=[n for n in b['nodes'] if not n['id'].startswith('join-')]
for i,k in enumerate(NM):
    t=f'{NM[k]}趕到了！'
    b['nodes'].append({"id":f"join-{k}","position":{"x":2200+i*320,"y":-1000},"data":{"type":"dialogue","title":f"隊友加入：{NM[k]}","speaker":"","text":t,"background":urls['j_'+k],"dialogueLines":[{"id":"l1","speaker":"","text":t}]}})
for n in b['nodes']:
    if n['id'].startswith('poster-dongzhuo-'): n['data']['background']=urls['dongzhuo2']
et,_=req('PUT','/boards/board-main',{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"隊友加入圖、董卓海報新版"},et)
# 3. 地圖：招募選項先跳加入卡；成素結算改立繪
r=urllib.request.urlopen(urllib.request.Request(P+'/boards/board-main',headers={'Authorization':'Bearer '+K}),timeout=300); rev=int(r.headers.get('X-Larch-Revision'))
b=json.loads(r.read())['board']; m=json.loads([x for x in b['nodes'] if x['id']=='map-arena'][0]['data']['pluginValues']['map']); ev={e['id']:copy.deepcopy(e) for e in m['events']}
z=lambda **k:{"text":"","cardId":"","itemId":"","itemName":"","amount":1,"variable":"","value":"",**k}
ops=[]
def addjoin(acts,pid):
    acts[:]=[a for a in acts if not a['id'].endswith('-jc')]
    for a in list(acts):
        if a['kind']=='choice':
            for o in a['choice']['options']:
                k=o['id'].rsplit('-o-',1)[1]; o['actions']=[x for x in o['actions'] if not x['id'].endswith('-jc')]
                o['actions'].insert(0,z(id=f"{o['id']}-jc",kind="dialogue",cardId=f"join-{k}",presentation="text"))
        elif a['kind']=='party' and a.get('party')=='follow' and not any(c['kind']=='choice' for c in acts):
            i=acts.index(a); acts.insert(i,z(id=f"{pid}-{a['value']}-jc",kind="dialogue",cardId=f"join-{a['value']}",presentation="text")); break
for k in range(1,5):
    e=ev[f'rec-{k}']
    for pg in e['pages']: addjoin(pg['actions'],pg['id'])
    ops.append({"kind":"event","id":f'rec-{k}',"patch":{"pages":e['pages']}})
e=ev['reaper']
def portrait(acts):
    for a in acts:
        if a['kind'] in ('dialogue','choice'): a['presentation']='portrait'; a.setdefault('speaker','')
portrait(e['actions'])
for pg in e['pages']: pg['actorId']='chengsu'; portrait(pg['actions'])
ops.append({"kind":"event","id":"reaper","patch":{"actorId":"chengsu","actions":e['actions'],"pages":e['pages']}})
res=mcp("larch_rpg_edit",{"projectId":PID,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"招募時跳隊友加入圖；成素結算用立繪","operations":ops})
t=json.dumps(res,ensure_ascii=False); print(t[:1200] if ('isError' in t or 'rror' in t[:400]) else 'map ok')
