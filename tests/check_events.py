"""照 Larch 引擎規則靜態檢查地圖事件。用法：python3 tests/check_events.py [project.json]
不給檔案就抓線上專案。發現問題印出來並以退出碼 1 結束。"""
import json,sys,os,urllib.request,re
PID='project-e35e734b-478d-458b-9221-294f81398b59'
def load():
    if len(sys.argv)>1:
        d=json.load(open(sys.argv[1])); return d.get('project',d)
    K=open(os.path.expanduser('~/.config/larch/key')).read().strip()
    d=json.loads(urllib.request.urlopen(urllib.request.Request(f'https://larch.ink/api/agent/projects/{PID}',headers={'Authorization':'Bearer '+K}),timeout=300).read())
    return d.get('project',d)
pr=load(); board=[b for b in pr['boards'] if b['id']=='board-main'][0]
nodes={n['id']:n for n in board['nodes']}
m=json.loads(nodes['map-arena']['data']['pluginValues']['map']); ev={e['id']:e for e in m['events']}
errs=[]; ok=[]
def E(msg): errs.append(msg)
def flat(acts):
    for a in acts:
        yield a
        if a['kind']=='choice':
            for o in a['choice']['options']: yield from flat(o['actions'])
        if a['kind']=='random':
            for o in a['random']['options']: yield from flat(o['actions'])
def pages(e):
    yield ('base',e.get('trigger'),e.get('conditions',[]),e.get('actions',[]))
    for p in e.get('pages',[]): yield (p['id'],p.get('trigger',e.get('trigger')),p.get('conditions',[]),p.get('actions',[]))

# 1. 對話卡連結：存在、是對話卡、內容包在 data、有台詞；海報卡要有 http 背景
for e in m['events']:
    for pid,_,_,acts in pages(e):
        for a in flat(acts):
            if a['kind']=='dialogue' and a.get('cardId'):
                n=nodes.get(a['cardId'])
                if not n: E(f"{e['id']}/{pid}: 連到不存在的卡 {a['cardId']}"); continue
                d=n.get('data',{})
                if d.get('type')!='dialogue': E(f"{a['cardId']}: 不是包在 data 裡的對話卡"); continue
                if not (d.get('dialogueLines') or d.get('text')): E(f"{a['cardId']}: 沒有台詞")
                if a['cardId'].startswith(('poster-','join-')) and not str(d.get('background','')).startswith('http'): E(f"{a['cardId']}: 背景不是網址")
ok.append('對話卡連結')

# 2. 平行事件：觸發條件用到的變數，不能在「還有非變數步驟」之前就被改掉
for e in m['events']:
    for pid,trig,conds,acts in pages(e):
        if trig!='parallel' or pid!='base': continue   # 分頁型的平行事件（招募）實測不受影響，只查基本頁
        cv={c['variable'] for c in conds if c.get('kind')=='variable'}
        top=acts
        for i,a in enumerate(top):
            if a['kind']=='variable' and a.get('variable') in cv:
                later=[x['kind'] for x in top[i+1:] if x['kind'] not in ('variable',)]
                if later: E(f"{e['id']}/{pid}: 第 {i+1} 步就改觸發條件 {a['variable']}，後面的 {later} 會被跳過")
                break
        for a in top:
            if a['kind']=='random':
                for o in a['random']['options']:
                    sub=o['actions']
                    for i,x in enumerate(sub):
                        if x['kind']=='variable' and x.get('variable') in cv and any(y['kind']!='variable' for y in sub[i+1:]):
                            E(f"{e['id']}/{pid}/{o['id']}: 分支裡先改觸發條件 {x['variable']}，後面會被跳過")
ok.append('平行事件步驟順序')

# 3. 王的階段鏈：dir-N（stage N-1→N）出場 → 王事件（stage N 存在）打倒 → stage N+1
stage_set={}
for e in m['events']:
    for pid,trig,conds,acts in pages(e):
        for a in flat(acts):
            if a['kind']=='variable' and a.get('variable')=='boss_stage':
                stage_set.setdefault(e['id'],[]).append((pid,a.get('op','set'),a.get('value')))
for N,boss in [(1,'boss-liubei'),(3,'boss-dongzhuo'),(5,'boss-caocao1'),(7,'boss-jiling'),(9,'boss-caocao2')]:
    d=ev[f'dir-{N}']; conds={c['variable']:c['value'] for c in d['conditions'] if c.get('kind')=='variable'}
    if conds.get('boss_stage')!=str(N-1): E(f"dir-{N}: 觸發條件 boss_stage 應是 {N-1}，是 {conds.get('boss_stage')}")
    sets=[s for s in stage_set.get(f'dir-{N}',[]) if s[0]=='base']
    if sets!=[('base','set',str(N))]: E(f"dir-{N}: 應把 boss_stage 設成 {N}，實際 {sets}")
    b=ev[boss]; bc={c['variable']:c['value'] for c in b['conditions'] if c.get('kind')=='variable'}
    if bc.get('boss_stage')!=str(N): E(f"{boss}: 出現條件 boss_stage 應是 {N}，是 {bc.get('boss_stage')}")
    for pid,trig,conds,acts in pages(b):
        ks=[a['kind'] for a in acts]
        if 'battle' not in ks:
            if pid.endswith('-down'): continue   # 三英各自倒下後的「已倒下」頁，本來就沒有戰鬥
            E(f"{boss}/{pid}: 沒有戰鬥步驟")
        else:
            i=ks.index('battle')
            if N!=1 and not (len(ks)>i+2 and ks[i+1]=='music' and ks[i+2]=='weather'): E(f"{boss}/{pid}: 打倒後沒有立刻換回音樂與天氣 {ks}")
        for cid in [a.get('cardId') for a in acts if a['kind']=='battle']:
            if cid not in nodes: E(f"{boss}/{pid}: 戰鬥卡 {cid} 不存在")
    # 出場事件的音樂、海報
    ks=[a['kind'] for a in d['actions']]
    if 'music' not in ks: E(f"dir-{N}: 沒有換戰鬥曲")
    if N!=1 and 'weather' not in ks: E(f"dir-{N}: 沒有換天氣")
ok.append('王的階段鏈')

# 4. 三英全倒換回音樂；無雙隨機五個分支都有海報與正確 stage
ks=[a['kind'] for a in ev['dir-sy']['actions']]
if ks[:2]!=['music','weather']: E(f"dir-sy: 三英全倒沒有先換回音樂天氣 {ks}")
rnd=[a for a in ev['dir-musou']['actions'] if a['kind']=='random'][0]
for o,st in zip(rnd['random']['options'],[1,3,5,7,9]):
    vs=[a for a in o['actions'] if a['kind']=='variable' and a['variable']=='boss_stage']
    if not vs or vs[0]['value']!=str(st): E(f"dir-musou/{o['id']}: boss_stage 應設 {st}")
    if not any(a['kind']=='dialogue' and str(a.get('cardId','')).startswith('poster-') for a in o['actions']): E(f"dir-musou/{o['id']}: 沒有海報卡")
ok.append('無雙隨機出王')

# 5. 招募：每頁的每個選項都先跳加入圖再入隊
for k in range(1,5):
    for p in ev[f'rec-{k}']['pages']:
        acts=p['actions']; ch=[a for a in acts if a['kind']=='choice']
        if ch:
            for o in ch[0]['choice']['options']:
                if not (o['actions'] and o['actions'][0]['kind']=='dialogue' and o['actions'][0]['cardId'].startswith('join-')): E(f"rec-{k}/{p['id']}/{o['id']}: 沒有先跳加入圖")
        else:
            ks=[a['kind'] for a in acts]
            if 'dialogue' not in ks or ks.index('dialogue')>ks.index('party'): E(f"rec-{k}/{p['id']}: 最後一位沒有先跳加入圖")
ok.append('招募加入圖')

# 6. 成素：所有非旁白對話都用立繪，演員資料庫有 chengsu
r=ev['reaper']
for pid,_,_,acts in pages(r):
    for a in flat(acts):
        if a['kind'] in('dialogue','choice') and a.get('speaker')!='narrator' and a.get('presentation')!='portrait': E(f"reaper/{pid}: {a['id']} 沒用立繪")
if r.get('actorId')!='chengsu': E('reaper 沒有連到成素演員')
ok.append('成素立繪')

print('通過：','、'.join(c for c in ok))
if errs:
    print(f'\n發現 {len(errs)} 個問題：'); [print(' -',x) for x in errs[:60]]; sys.exit(1)
print('沒有問題')
