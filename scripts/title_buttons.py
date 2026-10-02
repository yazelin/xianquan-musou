# 標題畫面按鈕加底板（作者 2026-10-02：白字壓在畫面上看不清楚，不知道去哪裡按開始）
import json,urllib.request,os,time,http.client
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
def req(m,path='',body=None,et=None):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        try:
            r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
            with urllib.request.urlopen(r,timeout=600) as x: return x.headers.get('ETag'),json.loads(x.read() or b'{}')
        except http.client.IncompleteRead: time.sleep(10)
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503,504): time.sleep(30); continue
            print(e.code,e.read()[:400]); raise
SKIN={"mode":"color","faces":{"normal":{"background":"#1a0e08e6","border":"#c9a14a","text":"#f6e7c4"},
                              "hover":{"background":"#7a1c14f0","border":"#f0c96a","text":"#fff6dc"},
                              "press":{"background":"#4a100cf5","border":"#c9a14a","text":"#fff6dc"}}}
canon=lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True)
et,p=req('GET'); p=p.get('project',p)
os.makedirs('snapshots',exist_ok=True); json.dump(p,open(f'snapshots/titlebtn_{int(time.time())}.json','w'),ensure_ascii=False)
boards=json.loads(json.dumps(p['boards'])); keep={k:canon(p.get(k)) for k in ('characters','variables','languages','name','description')}; pl=canon(p['settings'].get('plugins'))
for l in p['settings']['titleScreen']['layers']:
    if l['kind']=='button': l['skin']=SKIN; l['width']=18; l['x']=79; l['size']=1.7
    if l['kind']=='language': l['x']=79
    l['y']={'action-start':74,'action-continue':83,'languages':92}.get(l['id'],l.get('y'))   # 作者 10-02：兩顆按鈕疊在一起
et,_=req('PUT','',{"project":p,"summary":"標題按鈕加黑金底板"},et)
for b in boards: et,_=req('PUT','/boards/'+b['id'],{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"改標題畫面後把版子原樣推回"},et)
_,q=req('GET'); q=q.get('project',q); g={b['id']:b for b in q['boards']}
for b in boards: assert canon(g[b['id']]['nodes'])==canon(b['nodes']) and canon(g[b['id']]['edges'])==canon(b['edges']),b['id']
for k,v in keep.items(): assert canon(q.get(k))==v,k
assert canon(q['settings'].get('plugins'))==pl
print('OK',[(l['id'],l.get('skin',{}).get('mode')) for l in q['settings']['titleScreen']['layers']])
