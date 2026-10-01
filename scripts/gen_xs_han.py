import base64,json,os,urllib.request,sys
from concurrent.futures import ThreadPoolExecutor
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
ref=base64.b64encode(open("han_scissors.png","rb").read()).decode()
SC=("ancient Han-dynasty iron spring shears exactly like image 1: two long straight pointed iron blades joined ONLY at the back end by one single round iron loop (the spring), brown cord wrapped where the loop meets the blades; NO pivot screw, NO finger holes, NO second ring: there is exactly ONE round loop in the whole picture, at the back end, and the two blades meet in front of it with nothing round in the middle")
ICON=("Square game skill icon, pixel art, 32x32 pixel style upscaled with crisp hard pixel edges, limited palette, 1-pixel dark outline, a single bold symbol centered, readable at small size, no text, no letters, no border frame. Background: one flat solid pure green #00FF00 everywhere.")
J={"xs-cut":"The "+SC+", blades slightly open, surrounded by many small flying cut marks in a ring, steel blue glow.",
   "xs-fly":"The "+SC+", flying forward diagonally to the upper right while spinning, ice-blue speed lines trailing behind.",
   "xs-bloom":"The "+SC+", among a whirl of falling pink and white flower petals, golden glow."}
def job(k):
    body={"contents":[{"role":"user","parts":[{"inlineData":{"mimeType":"image/png","data":ref}},{"text":J[k]+" "+ICON}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(f"icons/{k}_han_raw.png","wb").write(base64.b64decode(d["data"])); print(k,"OK",flush=True); return
        except Exception as e: print(k,"ERR",e,flush=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(job,sys.argv[1:] or J))
