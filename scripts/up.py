import json,urllib.request,os,base64,time
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/project-e35e734b-478d-458b-9221-294f81398b59'
res={}
for k in ['weixu','diaochan','quan','lubu','xiang']:
    data=base64.b64encode(open(f'chars/{k}.png','rb').read()).decode()
    body={"name":f"musou_{k}.png","mimeType":"image/png","category":"character","base64":data}
    for t in range(10):
        try:
            r=urllib.request.Request(base+'/media',method='POST',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+K,'Content-Type':'application/json'})
            j=json.loads(urllib.request.urlopen(r).read()); res[k]=j['asset']['url']; print(k,res[k],flush=True); break
        except urllib.error.HTTPError as e:
            print(k,e.code,e.read()[:200]); time.sleep(30)
    time.sleep(5)
json.dump(res,open('char_urls.json','w'),indent=1)
