import base64,json,os,urllib.request
from concurrent.futures import ThreadPoolExecutor
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
b64=lambda f: base64.b64encode(open(f,"rb").read()).decode()
SC=("ancient Han-dynasty iron spring shears exactly like image 2: two long straight pointed iron blades that are joined ONLY at the back end by one single round iron loop bent from the same bar (the loop is the spring), "
    "brown cord wrapped where the loop meets the blades; NO pivot screw in the middle, NO finger holes, NO two rings.")
JOBS={
 "xiang_han":(["sd/xiang_raw.png","han_scissors.png","sd/weixu_side1b_raw.png"],
   "Image 1 is Yan Xiang, a chibi pixel-art game sprite: redraw the SAME woman in the SAME chunky pixel-art style and 2-heads-tall proportions, same face, tea-brown eyes, dark brown hair bun with a wooden hairpin, steel-blue cross-collar robe and darker blue skirt. "
   "Change only two things. (1) She holds in her right hand "+SC+" The blades point forward and down. "
   "(2) Pose: copy the POSE and facing of image 3 exactly (image 3 is only a pose reference, do not copy that man): three-quarter side view, her nose and face pointing to the right edge of the image, her whole figure turned about 45 degrees toward the RIGHT side of the image: face, eyes, chest, hips AND BOTH FEET point right; both shoes' toes point to the RIGHT, never left; walking toward the right. "
   "Whole body visible with feet, centered, fills about 80% of the image height. Background: one flat solid pure green #00FF00 everywhere, no ground shadow, no other objects, no text."),
 "w-xiang_han":(["han_scissors.png"],
   "Single weapon item sprite for an RPG, pixel art, crisp hard pixel edges, limited palette, 1-pixel dark outline: "+SC+
   " Drawn diagonally: the pointed blade tips at the TOP-RIGHT, the round loop at the BOTTOM-LEFT. The whole tool visible, centered, nothing else. Background: one flat solid pure green #00FF00 everywhere, no shadow, no text."),
}
def job(k):
    refs,txt=JOBS[k]
    parts=[{"inlineData":{"mimeType":"image/png","data":b64(f)}} for f in refs]+[{"text":txt}]
    body={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(f"sd/{k}_raw.png","wb").write(base64.b64decode(d["data"])); print(k,"OK",flush=True); return
            print(k,"no image",flush=True)
        except Exception as e: print(k,"ERR",e,flush=True)
import sys
with ThreadPoolExecutor(2) as ex: list(ex.map(job,sys.argv[1:] or JOBS))
