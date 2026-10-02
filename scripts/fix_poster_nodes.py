# 海報對話卡改成正確形狀：內容包進 data（upsert_nodes 收原始卡片結構，攤平送會被原樣存下，播放器讀不到）
import json,urllib.request,os,time,http.client
P='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
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
json.dump(b,open(f'snapshots/board_{int(time.time())}.json','w'),ensure_ascii=False)
fixed=[]
U=json.load(open('../assets/boss_posters/urls.json'))
for i,n in enumerate(b['nodes']):
    if n['id'].startswith('poster-') and 'data' not in n:
        data={k:v for k,v in n.items() if k not in ('id','position')}
        b['nodes'][i]={"id":n['id'],"position":n.get('position',{"x":0,"y":0}),"data":data}; n=b['nodes'][i]
    if n['id'].startswith('poster-'):
        n['data']['background']=U[n['id'][7:].rsplit('-',1)[0]]; fixed.append(n['id'])   # 背景換成 urls.json 裡的版本（16:9）
et,_=req('PUT','/boards/board-main',{"name":b['name'],"nodes":b['nodes'],"edges":b['edges'],"summary":"海報對話卡：正確形狀＋16:9 背景"},et)
_,j=req('GET','/boards/board-main'); g={n['id']:n for n in j['board']['nodes']}
print('fixed',len(fixed),'ok',all('data' in g[k] and g[k]['data'].get('background') for k in fixed),'nodes',len(g))
