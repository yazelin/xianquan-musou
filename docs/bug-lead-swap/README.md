# RPG 動作地圖：Q 換人帶隊只換外觀，血量、MP、技能沒有跟著換

## 現象

隊伍裡有同行的隊友時，玩家按 Q（或點畫面上的隊友頭像、選單「同行的夥伴」裡的「帶隊」），帶隊的人會換成那位隊友：走路圖和普攻類型會換，但下面這些仍然照原本的主角算：

- 血量上限
- MP 上限
- 等級顯示
- 1～4 的技能

作者實際遇到的情況：用貂蟬（法器）開局，招到呂布（長槍）以後按 Q 換呂布帶隊，按 1 放出來的還是貂蟬的火球術，血量上限也還是貂蟬的。

## 重現步驟

1. RPG 資料庫放兩個角色 A、B，各自有不同的 growth 與 skills。
2. 主角是 A，用 party 步驟讓 B 加入（`party: "follow"`）。
3. 在動作地圖上按 Q，換 B 帶隊。
4. 看左上的血量上限，按 1 放技能：都還是 A 的。

## 原因（rpg-engine-B2Jm4cvJ.js，2026-10-02 線上版）

10-01 回報時的版本是 `rpg-engine-CVycXasz.js`（換人函式當時叫 `Ks`）。10-02 更新後函式改了名字，行為沒變。

換人帶隊的函式只換了外觀和位置：

```js
function rl(e){const t=Bt[e];if(!t)return;const a=t.id.slice(6),
  n={x:u.x,y:u.y,direction:u.direction},i={name:u.name,sprite:u.sprite};
  dt.delete(t.id),Object.assign(u,{x:t.x,y:t.y,direction:t.direction,name:t.name,sprite:t.sprite}),
  Object.assign(t,n,i,{id:"party-"+Lt}),Lt=a,Bt.push(...Bt.splice(e,1))}
```

血量上限、MP 上限、等級顯示、1～4 技能都是讀 `_e.heroId`（資料庫的主角），不是讀帶隊的人 `Lt`：

```js
function Ft(){return Wn(_e?.heroId||"")?.hp||W.hp}                    // 血量上限
const wi=()=>(Wn(_e?.heroId||"")?.mp??20)+le.statsFor(...,"hero").mp   // MP 上限
function o(){const e=Nn(_e?.heroId||"");return e?"Lv "+e+" · ":""}    // 等級顯示
function Mr(){return Sr(_e?.heroId||"","hero")}                        // 技能
```

10-02 新加的角色能力（`abilities`）和走路速度（`speed`）則是讀帶隊的人：

```js
function Ni(){const e=_e?.actors.find(t=>t.id===ja(Lt))?.abilities;...}  // 能力
function tt(){const e=Number(_e?.actors.find(t=>t.id===ja(Lt))?.speed)||1;...}  // 速度
```

所以按 Q 換呂布帶隊以後，普攻、能力、速度變成呂布的，血量、MP、等級、技能還是貂蟬的。新功能讓兩邊對不起來的範圍比 10-01 更大。

Q 鍵綁在玩家的按鍵設定裡（`xe.member`），玩家可以改成別的鍵但不能清空；角色能力的按鍵規定不能用 q，也蓋不掉它。按下去不會觸發任何事件，所以作者這邊補不了。

## 對照：hero 步驟是完整換人

事件的 hero 步驟（新版 `function ai`）會換 `_e.heroId`、記住每個人各自的血量、把裝備存回各自身上，換完血量上限和技能都正確。本作目前用 C 鍵（一個 hotkey 道具）觸發事件、再用 hero 步驟換人來繞過，但 Q 還是在。

## 建議

兩個做法擇一：

1. 讓 Q 換人時走跟 hero 步驟一樣的路（換 heroId、套用該角色的等級、血量、MP、技能）。
2. 給作者一個開關（例如 RPG 設定裡關掉「隊友帶隊」），關掉時 Q、隊友頭像、選單的「帶隊」都不出現。
