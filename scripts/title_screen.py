# 標題畫面：封面＝沒有字的主視覺，狂草標題＝獨立圖片圖層（手機直向時平台會把圖層排成一欄，標題才不會被裁掉）
import json,urllib.request,os,time,base64,io,http.client
from PIL import Image
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
def req(m,path='',body=None,et=None):
    h={'Authorization':'Bearer '+K,'Content-Type':'application/json'}
    if et: h['If-Match']=et
    for t in range(8):
        r=urllib.request.Request(P+path,method=m,data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:
            with urllib.request.urlopen(r,timeout=600) as x: return x.headers.get('ETag'),json.loads(x.read() or b'{}')
        except http.client.IncompleteRead: time.sleep(10); continue
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503,504): time.sleep(30); continue
            print(e.code,e.read()[:300]); raise
def upload(path,name,fmt):
    bio=io.BytesIO(); Image.open(path).save(bio,fmt,**({'quality':90} if fmt=='WEBP' else {}))
    _,j=req('POST','/media',{"name":name,"mimeType":"image/"+fmt.lower(),"category":"ui","base64":base64.b64encode(bio.getvalue()).decode()}); time.sleep(3); print('uploaded',name,j['asset']['url'],flush=True); return j['asset']['url']
A='../assets/cover/'
cover=os.environ.get('COVER') or upload(A+'cover_v5.webp','musou_cover_v5.webp','WEBP')
title=os.environ.get('TITLE') or upload(A+'title_layer.png','musou_title_layer.webp','WEBP')
canon=lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True)
et,p=req('GET'); p=p.get('project',p)
os.makedirs('snapshots',exist_ok=True); json.dump(p,open(f'snapshots/titlescreen_{int(time.time())}.json','w'),ensure_ascii=False)
s=p['settings']; boards=json.loads(json.dumps(p['boards']))
keep={k:canon(p.get(k)) for k in ('characters','variables','languages','name','description')}; pl=canon(s.get('plugins'))
s['titleCoverImage']=cover; s['titleCoverPositionX']=50; s['titleCoverShade']=0.1
L={l['id']:l for l in s['titleScreen']['layers']}
s['titleScreen']['layers']=[
  {"id":"title-art","kind":"image","url":title,"x":0,"y":53,"width":45,"align":"left"},
  {**L['action-start'],'x':84,'y':79},{**L['action-continue'],'x':84,'y':85.5},{**L['languages'],'x':84,'y':92}]
et,_=req('PUT','',{"project":p,"summary":"標題畫面：封面無字版＋狂草標題圖層"},et)
for b in boards: et,_=req('PUT','/boards/'+b['id'],{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"改標題畫面後把版子原樣推回"},et)
_,q=req('GET'); q=q.get('project',q); g={b['id']:b for b in q['boards']}
for b in boards: assert canon(g[b['id']]['nodes'])==canon(b['nodes']) and canon(g[b['id']]['edges'])==canon(b['edges']),b['id']
for k,v in keep.items(): assert canon(q.get(k))==v,k
assert canon(q['settings'].get('plugins'))==pl
print('OK',q['settings']['titleCoverImage'][-24:],[(l['id'],l.get('x'),l.get('y')) for l in q['settings']['titleScreen']['layers']])
