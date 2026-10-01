import json,urllib.request,io,os
from PIL import Image
m=json.load(open('live_map.json')); W,H=m['width'],m['height']
ts={}
for t in m['tilesets']:
    p=f"cover/{t['id']}.png"
    if not os.path.exists(p): open(p,'wb').write(urllib.request.urlopen(urllib.request.Request(t['url'],headers={'User-Agent':'Mozilla/5.0'})).read())
    ts[t['id']]=(Image.open(p).convert('RGBA'),t['tileSize'],t['columns'])
img=Image.new('RGBA',(W*16,H*16),(0,0,0,255))
for L in m['layers']:
    if not L.get('visible',True): continue
    for i,t in enumerate(L['tiles']):
        if not t: continue
        sid,idx=t.rsplit(':',1); im,s,c=ts[sid]; idx=int(idx)
        tile=im.crop(((idx%c)*s,(idx//c)*s,(idx%c)*s+s,(idx//c)*s+s)).resize((16,16),Image.NEAREST)
        img.alpha_composite(tile,((i%W)*16,(i//W)*16))
img.save('map_render.png'); img.resize((W*10,H*10),Image.NEAREST).save('map_render_small.png')
