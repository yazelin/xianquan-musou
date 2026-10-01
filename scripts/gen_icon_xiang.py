import base64, json, os, urllib.request, sys, time
from concurrent.futures import ThreadPoolExecutor
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
ICON=("Square game skill icon, pixel art, 32x32 pixel style upscaled with crisp hard pixel edges, limited palette, 1-pixel dark outline, "
 "a single bold symbol centered, readable at small size, no text, no letters, no border frame. Background: one flat solid pure green #00FF00 everywhere.")
WPN=("Single weapon item sprite for an RPG, pixel art, crisp hard pixel edges, limited palette, 1-pixel dark outline, the whole weapon visible, "
 "drawn diagonally from bottom-left to top-right, centered, nothing else. Background: one flat solid pure green #00FF00 everywhere, no shadow, no text.")
J={
 # skills
 "sw-whirl":(ICON,"A whirling steel saber slash forming a circle with white wind streaks; colors steel grey and pale yellow."),
 "sw-quake":(ICON,"A saber striking the ground, cracked earth bursting upward with golden holy light."),
 "sw-musou":(ICON,"Many crossing saber slashes in a burst, falling purple-red meteors behind, intense, ochre and crimson."),
 "bw-pierce":(ICON,"An ice-blue arrow piercing through a cloud, frost trail."),
 "bw-thunder":(ICON,"A glowing arrow wrapped in yellow lightning."),
 "bw-rain":(ICON,"Many arrows raining down from the sky in a fan, purple meteor glow."),
 "mg-fire":(ICON,"A purple-and-orange fireball with flames."),
 "mg-frost":(ICON,"A pale blue ice crystal burst radiating outward in a ring."),
 "mg-meteor":(ICON,"A large purple meteor crashing down with a fiery tail."),
 "s-heal":(ICON,"A soft green leaf with a glowing green cross of healing light and sparkles."),
 "lb-thrust":(ICON,"The crescent blade of a Chinese fangtian halberd thrusting forward, golden holy streak, red tassel."),
 "lb-sweep":(ICON,"A fangtian halberd spinning in a circle, red tassels flying, yellow spark arc."),
 "lb-musou":(ICON,"A fangtian halberd with an enormous red and gold energy beam blasting forward, red tassels, dramatic."),
 "xs-cut":(ICON,"Open black iron tailor's scissors surrounded by many small flying cut marks in a ring, steel blue."),
 "xs-fly":(ICON,"Black iron tailor's scissors flying forward spinning, ice-blue speed lines."),
 "xs-bloom":(ICON,"Black iron scissors among a whirl of falling pink and white flower petals, golden glow."),
 # items
 "potion":(ICON,"A small round glass bottle of bright red healing potion with a cork, highlight on the glass."),
 "medal":(ICON,"A gold military merit medal with a red ribbon, Chinese ancient style, shiny."),
 # weapons
 "w-weixu":(WPN,"An ancient Chinese ring-pommel straight saber (huanshou dao), iron blade, dark wooden grip, iron ring at the pommel."),
 "w-lubu":(WPN,"An ancient Chinese fangtian halberd: long dark red shaft, spear tip with crescent side blade, red tassel below the blade."),
 "w-quan":(WPN,"A small child's wooden short bow with a light green grip wrap and a bowstring."),
 "w-diaochan":(WPN,"A small purple jade magic talisman charm on a lavender silk cord with a tassel, softly glowing purple."),
}
def job(k):
    pre,desc=J[k]; out=f"icons/{k}_raw.png"
    if os.path.exists(out): return k,"skip"
    body={"contents":[{"role":"user","parts":[{"text":desc+" "+pre}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(out,"wb").write(base64.b64decode(d["data"])); print(k,"OK",flush=True); return k,"ok"
        except Exception as e: print(k,"ERR",e,flush=True); time.sleep(10)
    return k,"fail"
J["w-xiang"]=(WPN,"A large pair of plain black iron tailor's scissors, ancient Chinese style, blades slightly open.")
print(job("w-xiang"))
