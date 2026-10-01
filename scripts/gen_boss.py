import base64,json,os,io,urllib.request,sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
T=os.path.expanduser("~/larch-taoyuan/")
def ref(f):
    im=Image.open(T+f).convert("RGBA"); bg=Image.new("RGBA",im.size,(128,128,128,255)); bg.alpha_composite(im)
    b=io.BytesIO(); bg.convert("RGB").save(b,"PNG"); return base64.b64encode(b.getvalue()).decode()
sty=base64.b64encode(open("sd/lubu_raw.png","rb").read()).decode()
POSE=("Pose: three-quarter side view, the whole figure turned about 45 degrees toward the RIGHT side of the image: face, eyes, chest, hips AND BOTH FEET point right; "
 "both boots' toes point to the RIGHT, never left; walking toward the right. Whole body visible with feet, centered, fills about 80% of the image height. "
 "Background: one flat solid pure magenta #FF00FF everywhere, no ground shadow, no other objects, no text.")
C={
 "liubei":("cast/v_劉備-戰甲_user_norm.webp","Liu Bei from image 1: a petite young WOMAN, black shoulder-length hair in a low ponytail with straight bangs, gentle face. Outfit: small fitted green-and-gold short armor over a white skirt, FLAT-soled green battle boots (no heels). Holds a pair of straight double swords, one in each hand."),
 "guanyu":("cast/v_關羽-戰甲_user_norm.webp","Guan Yu from image 1: a tall WOMAN, long black hair in a long braid, calm stern face. Outfit: green and gold armor, long dark red cape, FLAT-soled black battle boots (no heels). Holds a long guandao (crescent blade glaive) upright."),
 "zhangfei":("cast/v_張飛-戰甲_user_norm.webp","Zhang Fei from image 1: a muscular WOMAN, wild brown hair in a high ponytail tied with a red ribbon, big grin. Outfit: black leather short armor, FLAT-soled black battle boots (no heels). Holds a long snake spear with a wavy blade and red tassel."),
 "dongzhuo":("cast/npc3/董卓_cut.webp","Dong Zhuo from image 1: a huge fat middle-aged MAN, thick black beard, fierce scowl, top-knot. Outfit: dark brown lamellar armor, fur-collared dark red cloak, heavy boots. Very wide round body."),
 "caocao":("buchan/cg_v/anchor_caocao_1_v2.webp","Cao Cao from image 1: a middle-aged MAN with a thin moustache and small beard, sharp clever eyes, black official cap. Outfit: black lamellar armor with a long black cloak. Holds a straight sword at his side. He is clearly seen from the side-front, his nose and face pointing to the right edge of the image, striding to the right."),
 "jiling":("buchan/cg_v/anchor_jiling_3_v2.webp","Ji Ling from image 1: a sturdy MAN with a short beard, hair in a top-knot. Outfit: iron scale armor over a mustard-yellow robe, brown trousers and boots. Holds a long three-pointed blade polearm (sanjian dao) with a red tassel."),
}
def job(k):
    f,desc=C[k]; out=f"sd/boss_{k}_raw.png"
    if os.path.exists(out): return k,"skip"
    body={"contents":[{"role":"user","parts":[{"inlineData":{"mimeType":"image/png","data":ref(f)}},{"inlineData":{"mimeType":"image/png","data":sty}},
      {"text":"Image 1 is the character to draw (identity, face, hair, outfit). Image 2 is ONLY the art style reference: copy its chunky pixel-art style, its 2-heads-tall super-deformed chibi proportions (the head is as big as the whole body), its outline and shading. Do not copy image 2's character. "+desc+" Pixel art game sprite, super-deformed chibi, crisp hard pixel edges, limited palette, 1-pixel dark outline. "+POSE}]}],
      "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(out,"wb").write(base64.b64decode(d["data"])); print(k,"OK",flush=True); return k,"ok"
            print(k,"no image",flush=True)
        except Exception as e: print(k,"ERR",e,flush=True)
    return k,"fail"
ks=sys.argv[1:] or list(C)
with ThreadPoolExecutor(3) as ex: print(list(ex.map(job,ks)))
