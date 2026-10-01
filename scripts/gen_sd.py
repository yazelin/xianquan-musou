import base64, json, os, time, urllib.request, io, threading
from PIL import Image
BASE="https://ching-tech.ddns.net/codex-image"
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc"),encoding="utf-8") if "CODEX_IMAGE_KEY=" in l][0]
CG=os.path.expanduser("~/larch-taoyuan/buchan/cg_v/")
def call(m,p,b=None):
    r=urllib.request.Request(BASE+p,data=json.dumps(b).encode() if b else None,method=m,headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=120) as x: return json.loads(x.read())
def ref(f):
    im=Image.open(CG+f).convert("RGBA"); bg=Image.new("RGBA",im.size,(128,128,128,255)); bg.alpha_composite(im)
    bio=io.BytesIO(); bg.convert("RGB").save(bio,"PNG"); return base64.b64encode(bio.getvalue()).decode()
STYLE=("Pixel art game sprite, super-deformed chibi, exactly 2 heads tall: a very big round head and a tiny body, "
 "clean crisp pixel art like a 32x32 RPG character upscaled with hard pixel edges, limited palette, 1-pixel dark outline, "
 "front-facing standing pose, whole body visible with feet, centered, character fills about 80% of the image height. "
 "Background: one flat solid pure green #00FF00 everywhere, no ground shadow, no other objects, no text, no frame.")
C={
 "weixu":("qa_weixu_1_v2.webp","Wei Xu from image 1: a young man, dark brown eyes, short messy dark hair tied up, square face. Outfit: dull iron scale armor over an earthy ochre / mustard-yellow cloth robe; main color earthy yellow. Holds a straight ring-pommel saber (huanshou dao) in his right hand."),
 "diaochan":("qa_diaochan_1_v2.webp","Diaochan from image 1: a young woman, near-black eyes, black hair in an elegant bun with hair ornaments. Outfit: flowing pale purple and white hanfu dress with lavender ribbons; main color purple. Holds a small glowing purple magic charm in her hands."),
 "quan":("qa_quan10_4_v2.webp","Lu Quan from image 1: a little girl about ten years old, amber eyes, dark brown high ponytail. Outfit: light green and white short tunic, brown trousers, boots; main color green. Holds a small wooden bow, a quiver on her back."),
 "lubu":("qa_lubu_armor_1_v2.webp","Lu Bu from image 1: an adult WOMAN (female), red eyes, very long black hair with dark red sheen, golden crown with two long red tassel cords. Outfit: black and gold armor with crimson red cape and red skirt; main color red. Holds a tall fangtian halberd (long spear with crescent blade) upright."),
 "xiang":("qa_xiang_2_v2.webp","Yan Xiang from image 1: an adult woman, tea-brown eyes, dark brown hair in a bun with a wooden hairpin. Outfit: simple cross-collar robe dyed steel blue with a darker blue skirt; main color blue. Holds a big pair of plain black iron tailor's scissors in her right hand, ready to fight."),
}
def job(k):
    f,desc=C[k]
    body={"prompt":desc+" Keep the same identity, face and hair as image 1, but redraw it as: "+STYLE,"size":"1024x1024","quality":"high","count":1,"reference_images_base64":[ref(f)]}
    for t in range(3):
        try:
            j=call("POST","/v1/images/jobs",body); jid=j["id"]; print(k,"job",jid,flush=True)
            while True:
                time.sleep(15); s=call("GET",f"/v1/images/jobs/{jid}")
                if s.get("status")=="succeeded":
                    data=urllib.request.urlopen(s["images"][0]["url"]).read(); open(f"sd/{k}_raw.png","wb").write(data); print(k,"OK",flush=True); return
                if s.get("status") in ("failed","error"): print(k,"FAIL",s.get("error"),flush=True); break
        except Exception as e: print(k,"ERR",e,flush=True); time.sleep(20)
ts=[threading.Thread(target=job,args=(k,)) for k in C]
[t.start() for t in ts]; [t.join() for t in ts]
