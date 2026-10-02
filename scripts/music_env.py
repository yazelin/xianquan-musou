# 王出場換曲＋天氣、打倒／陣亡換回；地圖黃昏光影（2026-10-02 作者要畫面豐富）
# 地圖天氣只能整張地圖一起換，沒有分區；所以改成「王出場時換天氣、打倒或陣亡時換回晴天」
import json,urllib.request,os,copy,time,base64
from mcp_call import call as mcp
P='project-e35e734b-478d-458b-9221-294f81398b59'; K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
base='https://larch.ink/api/agent/projects/'+P
U=json.load(open('../assets/music_urls.json'))
MAPBGM="https://pub-4b20b43f5acf4dfaa3f6ab842daa51cf.r2.dev/2d3b0242-9a6d-4051-9825-46aa4efd064a/larch/built-in-assets/packs/larch-rpg-kingdom/music/1790630749185_battle.mp3"
z=lambda **k:{"text":"","cardId":"","itemId":"","itemName":"","amount":1,"variable":"","value":"",**k}
MUS=lambda i,url,vol: z(id=i,kind="music",audio={"url":url,"volume":vol,"loop":True})
WX=lambda i,kind,inten,dark: z(id=i,kind="weather",weather={"kind":kind,"intensity":inten,"darkness":dark})
BOSS_IN=lambda p: MUS(p+'-bgm',U['boss'],0.55)
BACK=lambda p:[MUS(p+'-bgmb',MAPBGM,0.35),WX(p+'-wxb','clear',0,0)]
# 每位王出場的天氣（第一輪 dir-N 與無雙隨機的選項順序一致）
WEATHER={'dir-1':None,'dir-3':('clear',0,0.45),'dir-5':('clear',0,0.65),'dir-7':('storm',0.5,0.25),'dir-9':('rain',0.85,0.4)}   # 10-02 實測 0.18 看不出來，調重
MUSOU=['dir-1','dir-3','dir-5','dir-7','dir-9']
r=urllib.request.urlopen(urllib.request.Request(base+'/boards/board-main',headers={'Authorization':'Bearer '+K}),timeout=300); rev=int(r.headers.get('X-Larch-Revision'))
b=json.loads(r.read())['board']; m=json.loads([x for x in b['nodes'] if x['id']=='map-arena'][0]['data']['pluginValues']['map'])
ev={e['id']:copy.deepcopy(e) for e in m['events']}
def clean(acts,suffixes=('-bgm','-bgmb','-wx','-wxb')): return [a for a in acts if not a['id'].endswith(suffixes)]
ops=[]
def entrance(acts,p,wx):
    acts[:]=clean(acts); i=[j for j,a in enumerate(acts) if a['kind']=='dialogue'][0]
    ins=[BOSS_IN(p)]+([WX(p+'-wx',*wx)] if wx else []); acts[i:i]=ins
for d,wx in WEATHER.items():
    e=ev[d]; entrance(e['actions'],d,wx); ops.append({"kind":"event","id":d,"patch":{"actions":e['actions']}})
e=ev['dir-musou']
for a in e['actions']:
    if a['kind']=='random':
        for i,o in enumerate(a['random']['options']): entrance(o['actions'],f'dm{i}',WEATHER[MUSOU[i]])
ops.append({"kind":"event","id":"dir-musou","patch":{"actions":e['actions']}})
def after_battle(acts,p):
    acts[:]=clean(acts); i=[j for j,a in enumerate(acts) if a['kind']=='battle'][0]; acts[i+1:i+1]=BACK(p)
for bid in ['boss-dongzhuo','boss-caocao1','boss-jiling','boss-caocao2']:
    e=ev[bid]; after_battle(e['actions'],bid+'-0')
    for pg in e.get('pages',[]): after_battle(pg['actions'],bid+'-'+pg['id'])
    ops.append({"kind":"event","id":bid,"patch":{"actions":e['actions'],"pages":e.get('pages',[])}})
e=ev['dir-sy']; e['actions']=clean(e['actions'])+BACK('dsy'); ops.append({"kind":"event","id":"dir-sy","patch":{"actions":e['actions']}})
e=ev['reaper']
def before_jump(acts,p):
    acts[:]=clean(acts); js=[j for j,a in enumerate(acts) if a['kind']=='jump']
    i=js[0] if js else len(acts); acts[i:i]=BACK(p)
before_jump(e['actions'],'rp0')
for pg in e.get('pages',[]): before_jump(pg['actions'],'rp'+pg['id'][3:])
ops.append({"kind":"event","id":"reaper","patch":{"actions":e['actions'],"pages":e.get('pages',[])}})
ops.append({"kind":"settings","patch":{"environment":{"weather":"clear","intensity":0,"darkness":0.08,"shake":0,"lights":[],
  "ambience":{"particles":"embers","density":0.3,"rays":0.35,"clouds":0.3,"vignette":0.35,"tint":"#ff9a4a","tintStrength":0.16}}}})
print(len(ops),'ops')
if os.environ.get('GO'):
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"王出場換曲與天氣、打倒或陣亡換回；地圖黃昏光影","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:1200] if ('isError' in t or 'rror' in t[:400]) else 'ok')
