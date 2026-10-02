# 改 Boss 戰鬥卡的招式名稱：讀整個白板 → 改每張 boss-* 的 data.pluginValues.battle → 整個白板 PUT 一次 → 讀回來逐張比對
# （2026-10-02：rpg-battle 接口一次一張又不能覆蓋 create；upsert_nodes 會把 pluginValues 放到卡片外層，兩條都不能用）
import json,urllib.request,os,time,http.client
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
REN={'仁德':'桃園之誓','青龍斬':'溫酒斬','燕人連突':'燕人張翼德','暴怒':'焚洛陽','堅守':'典韋護駕','重整':'郭嘉獻策','決戰':'縛虎急'}
def req(m,path,body=None,et=None):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        try:
            r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
            with urllib.request.urlopen(r,timeout=600) as x: return x.headers.get('ETag') or x.headers.get('X-Larch-Revision'),json.loads(x.read() or b'{}')
        except http.client.IncompleteRead: time.sleep(10)
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503,504): time.sleep(30); continue
            print(e.code,e.read()[:300]); raise
et,j=req('GET','/boards/board-main'); b=j['board']
os.makedirs('snapshots',exist_ok=True); json.dump(b,open(f'snapshots/board_{int(time.time())}.json','w'),ensure_ascii=False)
want={}
for n in b['nodes']:
    if not n['id'].startswith('boss-'): continue
    for junk in ('pluginValues','type','measured'):   # 試 upsert_nodes 時塞到外層的欄位
        if junk in n and junk!='type' or (junk=='type' and n.get('type')=='story' and 'pluginId' in n['data']): n.pop(junk,None)
    bt=json.loads(n['data']['pluginValues']['battle'])
    for e in bt['enemies']:
        for s in e.get('specials',[]): s['name']=REN.get(s['name'],s['name'])
    n['data']['pluginValues']['battle']=json.dumps(bt,ensure_ascii=False); want[n['id']]=bt
et,_=req('PUT','/boards/board-main',{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":f"Boss 招式改名（{len(want)} 張）"},et)
_,j=req('GET','/boards/board-main'); g={n['id']:n for n in j['board']['nodes']}
bad=[k for k,bt in want.items() if json.loads(g[k]['data']['pluginValues']['battle'])!=bt or 'pluginValues' in g[k]]
print('cards',len(want),'bad',bad,'nodes before/after',len(b['nodes']),len(g))
