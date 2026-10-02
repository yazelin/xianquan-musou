// 全自動回歸：每個情境各開一局本機預覽，把遊戲進度設到王出場前，截圖海報與出場後的地圖。
// 用法：cd ~/larch-preview && node ~/xianquan-musou/tests/run_all.mjs  （輸出到 ~/xianquan-musou/docs/test-2026-10-02/auto/）
import { chromium } from '/home/ct/larch-preview/node_modules/playwright-core/index.mjs';
import { spawn, execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
const HOME=process.env.HOME, PJ=`${HOME}/larch-preview/larch-project-e35e734b-478d-458b-9221-294f81398b59/project.json`;
const OUT=`${HOME}/xianquan-musou/docs/test-2026-10-02/auto`; mkdirSync(OUT,{recursive:true});
const CHROME=['/opt/google/chrome/chrome','/usr/bin/google-chrome'].find(existsSync);
// 情境：名稱、開局 boss_stage、boss_round、預期海報卡
const CASES=[['1_三英','0','1','虎牢關前'],['2_董卓','2','1','董卓現身'],['3_濮陽曹操','4','1','濮陽'],['4_紀靈','6','1','紀靈率'],['5_下邳曹操','8','1','下邳城外'],['6_無雙隨機','0','2','無雙！']];
const ORIG=readFileSync(PJ,'utf8');
function seed(stage,round){
  const d=JSON.parse(ORIG), pr=d.project||d, nodes=pr.boards.find(b=>b.id==='board-main').nodes;
  for(const n of nodes){ const pv=n.data?.pluginValues; if(pv?.battle){ const bt=JSON.parse(pv.battle); for(const e of bt.enemies){ e.attack=1; e.specials=[]; } pv.battle=JSON.stringify(bt);} }
  const mn=nodes.find(n=>n.id==='map-arena'), m=JSON.parse(mn.data.pluginValues.map), ev=Object.fromEntries(m.events.map(e=>[e.id,e]));
  for(const a of ev['init-score'].actions){ if(a.variable==='boss_stage') a.value=stage; if(a.variable==='boss_round') a.value=round; }
  for(const e of m.events) if(e.id.startsWith('dir-')) for(const c of e.conditions) if(c.variable==='bk') c.value='0';
  mn.data.pluginValues.map=JSON.stringify(m); writeFileSync(PJ,JSON.stringify(d));
}
const server=spawn('python3',['serve.py',PJ,'--port','0'],{cwd:`${HOME}/larch-preview`,stdio:['ignore','pipe','inherit']});
const BASE=await new Promise((ok,bad)=>{server.stdout.on('data',d=>{const m=d.toString().match(/預覽：(http:\/\/127\.0\.0\.1:\d+)/); if(m) ok(m[1]);}); server.on('exit',c=>bad(new Error('serve '+c)));});
const browser=await chromium.launch({executablePath:CHROME,headless:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const results=[];
for(const [name,stage,round,line] of CASES){
  seed(stage,round); await sleep(1500);
  const page=await (await browser.newContext({viewport:{width:1280,height:720},locale:'zh-TW'})).newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(e.message));
  try{
    await page.goto(BASE+'/?card=map-arena'); await sleep(7000);
    const f=page.frameLocator('#player');
    const start=f.getByRole('button',{name:/開始遊戲/}); if(await start.count()) { await start.first().click(); await sleep(5000); }
    // 取名→開場說明→選呂布→說明；每次按 Enter 並偵測海報（對話框上方出現大圖背景）
    const keys=['Enter','Enter','4','Enter','Enter','Enter','Enter','Enter'];
    let got=null;
    for(let i=0;i<keys.length+6 && !got;i++){
      await page.keyboard.press(keys[i]||'Enter'); await sleep(1800);
      const txt=await page.screenshot({path:`${OUT}/${name}_step${i}.png`});
      for(const fr of page.frames()){ const t=await fr.evaluate(()=>document.body?.innerText||'').catch(()=>''); if(t.includes(line)){ got=t.split('\n').find(x=>x.includes(line)); break; } }
      if(got){ await page.screenshot({path:`${OUT}/${name}_海報.png`}); }
    }
    if(got){ await page.keyboard.press('Enter'); await sleep(3500); await page.screenshot({path:`${OUT}/${name}_出場後地圖.png`}); }
    results.push({name, 出場旁白: got||'沒有出現', errors: errs.slice(0,3)});
  }catch(e){ results.push({name,error:String(e).slice(0,200)}); }
  await page.context().close();
}
writeFileSync(PJ,ORIG); await browser.close(); server.kill();
writeFileSync(`${OUT}/results.json`,JSON.stringify(results,null,1)); console.log(JSON.stringify(results,null,1));
