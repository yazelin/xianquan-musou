import json
from collections import deque
m=json.load(open('live_map.json')); W,H=m['width'],m['height']
lay={L['id']:L for L in m['layers']}
ev={(e['x'],e['y']):e['id'] for e in m['events']}
blk=lambda i: any(L.get('collision') and L['tiles'][i] for L in m['layers'])
g=lay['t-ground']['tiles']
# reachability from hero/camp
start=(28,21)
seen={start}; q=deque([start])
while q:
    x,y=q.popleft()
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
        X,Y=x+dx,y+dy
        if 0<=X<W and 0<=Y<H and (X,Y) not in seen and not blk(Y*W+X): seen.add((X,Y)); q.append((X,Y))
rows=[]
for y in range(H):
    r=''
    for x in range(W):
        i=y*W+x; t=g[i] or ''
        c='?' if not t else '.'
        if lay.get('t-water') and lay['t-water']['tiles'][i]: c='~'
        if blk(i): c='#' if not (lay.get('t-water') and lay['t-water']['tiles'][i]) else '~'
        elif (x,y) not in seen: c='!'
        if (x,y) in ev: c='B' if ev[(x,y)].startswith('boss') else 'E'
        r+=c
    rows.append(r)
print('\n'.join(rows))
unreach=[(x,y) for y in range(H) for x in range(W) if not blk(y*W+x) and (x,y) not in seen]
print('unreachable walkable cells:',len(unreach),'empty ground:',sum(1 for t in g if not t))
