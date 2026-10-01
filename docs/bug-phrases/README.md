# RPG 設定：線上快捷語（online.phrases）每存一次就被截短一次

## 現象

`online.phrases` 裡的第 i 句（從 0 開始數）會被截成 i 個字。第 0 句截完是空字串，直接被濾掉。

就算請求根本沒送 `phrases`，只改了別的線上設定（例如頻道名稱），存檔時快捷語還是會被截一次。存越多次，句子越短。

## 證據

| 檔案 | 內容 |
|---|---|
| `before.json`、`before.headers.txt` | 改之前讀到的設定。快捷語是 `["一","等我","好喔","哈哈哈","加油！","掰掰～"]`，其實先前已經被截過幾輪了 |
| `req1_channel_only.json` | 第一次請求：只送 `online.channelList`，沒有送 `phrases` |
| `resp1.json` | HTTP 200，revision 143，時間 2026-10-02 00:59:43（UTC+8）。快捷語變成 `["哈","加油","掰掰～"]` |
| `req2_phrases.json` | 第二次請求：送六句一樣長的 `["aaaaa","bbbbb","ccccc","ddddd","eeeee","fffff"]` |
| `resp2.json` | HTTP 400，時間 00:59:55。伺服器自己說會變成 `["b","cc","ddd","eeee","fffff"]` |
| `after_repro.json` | 重現後再讀一次，確認結果和 resp1 相同 |
| `node_repro.txt` | 照前端原始碼的寫法在 Node 裡重跑一次，結果和伺服器回的一模一樣 |

## 原因

前端 bundle `Preview-*.js` 裡是這樣寫的：

```js
phrases: s.phrases === void 0 ? a.phrases : md(s.phrases, xf, bf).map(Fo).filter(Boolean)
```

`Fo` 是從 `RpgOnlineLookCanvas-*.js` 匯入的 `h`，原本的定義是：

```js
function As(t, e = tn) { return L(String(t ?? "")...trim()).slice(0, e).join("").trim() }
```

第二個參數 `e` 是長度上限。`.map(Fo)` 呼叫時會把陣列索引當第二個參數傳進去，所以第 i 句就被 `slice(0, i)` 截掉了。伺服器端的驗證看起來也是同一段程式，所以才會在請求沒送 phrases 的時候也照樣截一次。

## 建議修法

```js
.map((x) => Fo(x))
```

`node_repro.txt` 裡有改前改後的對照。
