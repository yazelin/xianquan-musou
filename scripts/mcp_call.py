import json,urllib.request,os,sys
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
U='https://larch.ink/mcp'
H={'Authorization':'Bearer '+K,'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
def post(body,sid=None):
    h=dict(H); 
    if sid: h['Mcp-Session-Id']=sid
    r=urllib.request.urlopen(urllib.request.Request(U,data=json.dumps(body).encode(),headers=h,method='POST'),timeout=300)
    raw=r.read().decode(); sid2=r.headers.get('Mcp-Session-Id') or sid
    if raw.lstrip().startswith('event:') or 'data:' in raw[:20]:
        raw='\n'.join(l[5:] for l in raw.splitlines() if l.startswith('data:'))
    return (json.loads(raw) if raw.strip() else None),sid2
def call(name,args):
    j,sid=post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"py","version":"1"}}})
    post({"jsonrpc":"2.0","method":"notifications/initialized"},sid)
    j,_=post({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":name,"arguments":args}},sid)
    return j
if __name__=='__main__':
    print(json.dumps(call(sys.argv[1],json.load(open(sys.argv[2]))),ensure_ascii=False)[:3000])
