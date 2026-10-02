# 成素結算：選項分支裡的對話也用立繪（10-02 實測：選了「換某人」之後那句沒有立繪）
import json,urllib.request,os,copy
from mcp_call import call as mcp
P='project-e35e734b-478d-458b-9221-294f81398b59'; K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
r=urllib.request.urlopen(urllib.request.Request(f'https://larch.ink/api/agent/projects/{P}/boards/board-main',headers={'Authorization':'Bearer '+K}),timeout=300); rev=int(r.headers.get('X-Larch-Revision'))
b=json.loads(r.read())['board']; m=json.loads([x for x in b['nodes'] if x['id']=='map-arena'][0]['data']['pluginValues']['map'])
e=copy.deepcopy([x for x in m['events'] if x['id']=='reaper'][0]); n=[0]
def walk(acts):
    for a in acts:
        if a['kind'] in ('dialogue','choice') and a.get('speaker','')!='narrator':
            if a.get('presentation')!='portrait': n[0]+=1
            a['presentation']='portrait'
        if a['kind']=='choice':
            for o in a['choice']['options']: walk(o['actions'])
walk(e['actions'])
for pg in e['pages']: walk(pg['actions'])
print('changed',n[0])
res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"成素結算：選項分支裡的對話也用立繪","operations":[{"kind":"event","id":"reaper","patch":{"actions":e['actions'],"pages":e['pages']}}]})
t=json.dumps(res,ensure_ascii=False); print(t[:800] if ('isError' in t or 'rror' in t[:400]) else 'map ok')
