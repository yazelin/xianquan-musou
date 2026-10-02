# 遊戲選單配色（黑金紅）＋標題畫面音樂（香布纏的 bgm_prologue）
import json,urllib.request,os,time,http.client
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
U=json.load(open('../assets/music_urls.json'))
def req(m,path,body=None,et=None):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        try:
            r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
            with urllib.request.urlopen(r,timeout=600) as x: return x.headers.get('ETag'),json.loads(x.read() or b'{}')
        except http.client.IncompleteRead: time.sleep(10)
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503,504): time.sleep(30); continue
            print(e.code,e.read()[:300]); raise
_,s=req('GET','/rpg-settings')
mu=dict(s['menuUi']); mu.update(preset="night",accent="#c9a14a")
req('PUT','/rpg-settings',{"summary":"選單改成黑金配色","menuUi":mu},str(s['revision']))
_,s2=req('GET','/rpg-settings'); print('menuUi',s2['menuUi'])
canon=lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True)
et,p=req('GET',''); p=p.get('project',p)
os.makedirs('snapshots',exist_ok=True); json.dump(p,open(f'snapshots/ui_{int(time.time())}.json','w'),ensure_ascii=False)
boards=json.loads(json.dumps(p['boards'])); keep={k:canon(p.get(k)) for k in ('characters','variables','languages','name','description')}; pl=canon(p['settings'].get('plugins'))
p['settings']['titleScreen']['bgm']=U['title']
et,_=req('PUT','',{"project":p,"summary":"標題畫面音樂"},et)
for b in boards: et,_=req('PUT','/boards/'+b['id'],{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"改設定後把版子原樣推回"},et)
_,q=req('GET',''); q=q.get('project',q); g={b['id']:b for b in q['boards']}
for b in boards: assert canon(g[b['id']]['nodes'])==canon(b['nodes']) and canon(g[b['id']]['edges'])==canon(b['edges']),b['id']
for k,v in keep.items(): assert canon(q.get(k))==v,k
assert canon(q['settings'].get('plugins'))==pl
print('title bgm',q['settings']['titleScreen'].get('bgm','')[-30:])
