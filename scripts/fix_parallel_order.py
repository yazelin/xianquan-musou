# 平行事件每一步前都會重查觸發條件，條件不成立就中止（引擎 ve() 的 be() 檢查）。
# 王出場等事件第一步就改 boss_stage，後面的吼聲、震動、換曲、海報全被跳過。這支把改條件變數的步驟移到最後。
import json,urllib.request,os,copy
from mcp_call import call as mcp
P='project-e35e734b-478d-458b-9221-294f81398b59'; K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
r=urllib.request.urlopen(urllib.request.Request(f'https://larch.ink/api/agent/projects/{P}/boards/board-main',headers={'Authorization':'Bearer '+K}),timeout=300); rev=int(r.headers.get('X-Larch-Revision'))
b=json.loads(r.read())['board']; m=json.loads([x for x in b['nodes'] if x['id']=='map-arena'][0]['data']['pluginValues']['map']); ev={e['id']:copy.deepcopy(e) for e in m['events']}
def vars_last(acts):
    v=[a for a in acts if a['kind']=='variable']; o=[a for a in acts if a['kind']!='variable']; acts[:]=o+v
ops=[]
for d in ['dir-1','dir-3','dir-5','dir-7','dir-9','dir-loop','dir-sy']:
    e=ev[d]; vars_last(e['actions']); ops.append({"kind":"event","id":d,"patch":{"actions":e['actions']}}); print(d,[a['kind'] for a in e['actions']])
e=ev['dir-musou']; acts=e['actions']
rnd=[a for a in acts if a['kind']=='random'][0]
for o in rnd['random']['options']: vars_last(o['actions'])
e['actions']=[a for a in acts if a['kind']!='random']+[rnd]   # 吼聲、震動放在擲骰之前
ops.append({"kind":"event","id":"dir-musou","patch":{"actions":e['actions']}})
print('dir-musou',[a['kind'] for a in e['actions']],[x['kind'] for x in rnd['random']['options'][0]['actions']])
if os.environ.get('GO'):
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"王出場等平行事件：改條件變數的步驟移到最後（否則後面步驟會被跳過）","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:1000] if ('isError' in t or 'rror' in t[:400]) else 'map ok')
