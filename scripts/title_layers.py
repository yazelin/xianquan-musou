# 改標題畫面的封面與按鈕位置（百分比）。用法：python3 title_layers.py <start_x> <start_y> [間距]
import json,urllib.request,os,time,sys
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
def req(m,path='',body=None,et=None):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:
            with urllib.request.urlopen(r,timeout=600) as x: return x.headers.get('ETag'),json.loads(x.read() or b'{}')
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(30); continue
            print(e.code,e.read()[:300]); raise
x,y=float(sys.argv[1]),float(sys.argv[2]); gap=float(sys.argv[3]) if len(sys.argv)>3 else 6.5
canon=lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True)
et,p=req('GET'); p=p.get('project',p)
os.makedirs('snapshots',exist_ok=True); json.dump(p,open(f'snapshots/titlescreen_{int(time.time())}.json','w'),ensure_ascii=False)
s=p['settings']; boards=json.loads(json.dumps(p['boards']))
keep={k:canon(p.get(k)) for k in ('characters','variables','languages','name','description')}; pl=canon(s.get('plugins'))
s['titleCoverImage']=s['projectThumbnail']   # 封面跟縮圖同一張（2026-10-02 作者決定）
L={l['id']:l for l in s['titleScreen']['layers']}
s['titleScreen']['layers']=[{**L['action-start'],'x':x,'y':y},{**L['action-continue'],'x':x,'y':y+gap},{**L['languages'],'x':x,'y':y+2*gap}]
et,_=req('PUT','',{"project":p,"summary":f"標題畫面按鈕移到 ({x},{y})"},et)
for b in boards: et,_=req('PUT','/boards/'+b['id'],{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"改標題畫面後把版子原樣推回"},et)
_,q=req('GET'); q=q.get('project',q); g={b['id']:b for b in q['boards']}
for b in boards: assert canon(g[b['id']]['nodes'])==canon(b['nodes']) and canon(g[b['id']]['edges'])==canon(b['edges']),b['id']
for k,v in keep.items(): assert canon(q.get(k))==v,k
assert canon(q['settings'].get('plugins'))==pl
print('OK',[(l['id'],l['x'],l['y']) for l in q['settings']['titleScreen']['layers']])
