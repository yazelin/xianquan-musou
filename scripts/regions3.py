import json
from collections import deque
from mcp_call import call as mcp
from regions import board, P
rev,m=board(); W,H=m['width'],m['height']
blk=lambda x,y: any(L.get('collision') and L['tiles'][y*W+x] for L in m['layers'])
seen={(28,21)}; q=deque([(28,21)])
while q:
    x,y=q.popleft()
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
        X,Y=x+dx,y+dy
        if 0<=X<W and 0<=Y<H and (X,Y) not in seen and not blk(X,Y): seen.add((X,Y)); q.append((X,Y))
area={"width":W,"cells":''.join('1' if (x,y) in seen and not (x<10 and y<8) else '0' for y in range(H) for x in range(W))}
occ={(e['x'],e['y']) for e in m['events']}
ops=[]
bad=[e['id'] for e in m['events'] if not e['id'].startswith(('sp-','dir-','init','intro','hero','reaper')) and e['actor']!='none' and ((e['x'],e['y']) not in seen)]
print('events not reachable:',bad)
def near(x,y,me):
    for d in range(12):
        for dx in range(-d,d+1):
            for dy in range(-d,d+1):
                c=(x+dx,y+dy)
                if c in seen and (c not in occ or c==me) and not (c[0]<10 and c[1]<8): occ.add(c); return c
ev={e['id']:e for e in m['events']}
for eid,(x,y) in {'boss-liubei':(30,30),'boss-guanyu':(33,31),'boss-zhangfei':(30,33),'boss-dongzhuo':(51,17),'boss-caocao1':(44,36),'boss-jiling':(10,40),'boss-caocao2':(46,55)}.items():
    me=(ev[eid]['x'],ev[eid]['y']); occ.discard(me); c=near(x,y,me); ops.append({"kind":"event","id":eid,"patch":{"x":c[0],"y":c[1]}}); print(eid,c)
for e in m['events']:
    acts=e['actions']; ch=False
    for a in acts:
        if a['kind']=='spawn' and a['spawn'].get('at')=='area': a['spawn']['area']=area; ch=True
    if ch: ops.append({"kind":"event","id":e['id'],"patch":{"actions":acts}}); print('area ->',e['id'])
res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"Boss 搬到各自區域；生怪範圍改成 64×64 可走到的格子","operations":ops})
t=json.dumps(res,ensure_ascii=False); print(t[:600] if 'isError' in t else 'ok')
rev,m=board(); json.dump(m,open('live_map.json','w'),ensure_ascii=False); print('rev',rev, 'reachable cells',area['cells'].count('1'))
