import json
from mcp_call import call as mcp
from regions import board, P
rev,m=board()
ops_t=[
 {"op":"area","ground":"grass","shape":"rect","x":17,"y":43,"w":45,"h":15},
 {"op":"area","ground":"water","shape":"rect","x":17,"y":48,"w":45,"h":3},
 {"op":"area","ground":"dirt","shape":"rect","x":25,"y":47,"w":2,"h":5},{"op":"area","ground":"dirt","shape":"rect","x":39,"y":47,"w":2,"h":5},{"op":"area","ground":"dirt","shape":"rect","x":53,"y":47,"w":2,"h":5},
 {"op":"scatter","object":"barrel","x":42,"y":3,"w":18,"h":17,"count":4},{"op":"scatter","object":"crate","x":42,"y":3,"w":18,"h":17,"count":3},
 {"op":"place","object":"well","x":50,"y":14},{"op":"place","object":"flag-red","x":44,"y":20},{"op":"place","object":"flag-red","x":58,"y":20},
]
res=mcp("larch_rpg_edit",{"projectId":P,"boardId":"board-main","nodeId":"map-arena","expectedRevision":rev,"summary":"河道改成連續一條、三處淺灘；城鎮加道具","operations":[{"kind":"terrain","plan":{"mode":"edit","ops":ops_t},"connect":True}]})
t=json.dumps(res,ensure_ascii=False); print(t[:600] if 'isError' in t else 'ok')
rev,m=board(); json.dump(m,open('live_map.json','w'),ensure_ascii=False); print('rev',rev)
