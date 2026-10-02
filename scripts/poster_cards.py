# 王出場海報：每位王兩張對話卡（第一輪的出場旁白、無雙輪的出場旁白），卡片背景＝海報；出場事件的旁白改連到卡片
import json,os,copy,urllib.request
from mcp_call import call as mcp
P='project-e35e734b-478d-458b-9221-294f81398b59'
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
U=json.load(open('../assets/boss_posters/urls.json'))
FIRST={'sanying':('dir-1','虎牢關前，劉備、關羽、張飛三人一起殺到。'),'dongzhuo':('dir-3','董卓現身。'),
       'caocao_puyang':('dir-5','曹操領兵來到濮陽。'),'jiling':('dir-7','紀靈率袁術軍殺到。'),'caocao_xiapi':('dir-9','下邳城外，曹操親自來了。')}
MUSOU=['sanying','dongzhuo','caocao_puyang','jiling','caocao_xiapi']   # dm-o0..o4 的順序
NM={'sanying':'劉備、關羽、張飛','dongzhuo':'董卓','caocao_puyang':'曹操','jiling':'紀靈','caocao_xiapi':'下邳的曹操'}
nodes=[]
for i,k in enumerate(MUSOU):
    for kind,text in (('first',FIRST[k][1]),('musou',f'無雙！{NM[k]}殺到，比上一位更強。')):
        nodes.append({"id":f"poster-{k}-{kind}","type":"dialogue","title":f"王出場：{NM[k]}（{'第一輪' if kind=='first' else '無雙'}）",
            "position":{"x":2200+i*320,"y":-700+(0 if kind=='first' else 260)},"speaker":"","text":text,"background":U[k],
            "dialogueLines":[{"id":"l1","speaker":"","text":text}]})
r=mcp("larch_upsert_nodes",{"projectId":P,"boardId":"board-main","summary":"王出場海報對話卡（十張）","nodes":nodes})
print('cards', 'isError' not in json.dumps(r)[:2000])
# 地圖事件
_r=urllib.request.urlopen(urllib.request.Request(f'https://larch.ink/api/agent/projects/{P}/boards/board-main',headers={'Authorization':'Bearer '+K}),timeout=300); rev=int(_r.headers.get('X-Larch-Revision')); b=json.loads(_r.read())
b=b.get('board',b); node=[n for n in b['nodes'] if n['id']=='map-arena'][0]
m=json.loads(node['data']['pluginValues']['map']); ev={e['id']:e for e in m['events']}
def link(a,card):
    a['cardId']=card; a['text']=''; a['presentation']='text'; a.pop('hideBackground',None)
ops=[]
for k,(eid,_) in FIRST.items():
    e=copy.deepcopy(ev[eid]); [link(a,f'poster-{k}-first') for a in e['actions'] if a['id']==eid+'-say']
    ops.append({"kind":"event","id":eid,"patch":{"actions":e['actions']}})
e=copy.deepcopy(ev['dir-musou'])
for a in e['actions']:
    if a['kind']=='random':
        for i,o in enumerate(a['random']['options']):
            for x in o['actions']:
                if x['kind']=='dialogue': link(x,f'poster-{MUSOU[i]}-musou')
ops.append({"kind":"event","id":"dir-musou","patch":{"actions":e['actions']}})
res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"王出場旁白改連海報對話卡","operations":ops})
t=json.dumps(res,ensure_ascii=False); print(t[:800] if 'isError' in t or 'rror' in t[:300] else 'map ok')
