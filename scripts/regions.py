import json,urllib.request,os
from mcp_call import call as mcp
K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
P='project-e35e734b-478d-458b-9221-294f81398b59'; base='https://larch.ink/api/agent/projects/'+P
def board():
    r=urllib.request.urlopen(urllib.request.Request(base+'/boards/board-main',headers={'Authorization':'Bearer '+K})); rev=int(r.headers.get('X-Larch-Revision'))
    b=json.loads(r.read())['board']; n=[x for x in b['nodes'] if x['id']=='map-arena'][0]; m=n['data']['pluginValues']['map']; return rev,(json.loads(m) if isinstance(m,str) else m)
if __name__=="__main__":
    rev,m=board(); W=m['width']
    pen=[L for L in m['layers'] if L['id']=='pen-wall'][0]
    er=[{"kind":"paint","layerId":"pen-wall","tool":"eraser","tile":None,"from":[i%W,i//W]} for i,t in enumerate(pen['tiles']) if t and (i%W>=50 or i//W>=34)]
    ops_t=[
     {"op":"clear","x":53,"y":0,"w":11,"h":40},{"op":"clear","x":0,"y":36,"w":64,"h":28},
     {"op":"area","ground":"grass","shape":"rect","x":53,"y":0,"w":11,"h":64},{"op":"area","ground":"grass","shape":"rect","x":0,"y":36,"w":64,"h":28},
     # west wasteland (五原荒原)
     {"op":"area","ground":"dirt","shape":"blob","x":2,"y":22,"w":17,"h":34},
     {"op":"scatter","object":"rock","x":3,"y":24,"w":15,"h":30,"count":9},{"op":"scatter","object":"dead-tree","x":3,"y":24,"w":15,"h":30,"count":6},
     {"op":"decorate","kind":"stones","x":3,"y":24,"w":15,"h":30},
     # NE town (長安/下邳)
     {"op":"area","ground":"cobble","shape":"rect","x":42,"y":3,"w":18,"h":17},
     {"op":"village","x":42,"y":3,"w":18,"h":17,"houses":5},
     {"op":"path","ground":"cobble","points":[[36,11],[60,11]],"width":2},{"op":"path","ground":"cobble","points":[[51,3],[51,22]],"width":2},
     # south river (泗水) with three fords
     {"op":"path","ground":"water","points":[[18,49],[30,51],[44,48],[61,50]],"width":3},
     {"op":"path","ground":"dirt","points":[[24,45],[24,56]],"width":2},{"op":"path","ground":"dirt","points":[[39,44],[39,55]],"width":2},{"op":"path","ground":"dirt","points":[[55,45],[55,56]],"width":2},
     {"op":"farm","x":28,"y":55,"w":9,"h":5,"crop":"wheat"},
     # new outer border
     {"op":"forest","kind":"green","x":62,"y":0,"w":2,"h":64},{"op":"forest","kind":"green","x":0,"y":62,"w":64,"h":2},{"op":"forest","kind":"green","x":0,"y":38,"w":2,"h":24},
    ]
    ops=er+[{"kind":"terrain","plan":{"mode":"edit","ops":ops_t},"connect":True}]
    print(len(er),'pen erase')
    res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"四區地形：西荒原、東北城鎮、南河道、中央草原，外圈新邊界","operations":ops})
    t=json.dumps(res,ensure_ascii=False); print(t[:600] if 'isError' in t else 'ok')
    rev,m=board(); json.dump(m,open('live_map.json','w'),ensure_ascii=False); print('rev',rev)
