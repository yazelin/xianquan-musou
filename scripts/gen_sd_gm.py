import base64, json, os, urllib.request, io, threading, sys
from PIL import Image
exec(open('gen_sd.py').read().split('def job')[0].split('def call')[0])  # STYLE, C, CG, ref imports
src=open('gen_sd.py').read()
ns={}; exec(src.split('def job')[0].replace('KEY=[','_K=['),ns)
STYLE,C,ref=ns['STYLE'],ns['C'],ns['ref']
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
def job(k):
    f,desc=C[k]
    body={"contents":[{"role":"user","parts":[{"inlineData":{"mimeType":"image/png","data":ref(f)}},{"text":desc+" Keep the same identity, face and hair as the reference image, but redraw it as: "+STYLE}]}],
          "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(f"sd/{k}_raw.png","wb").write(base64.b64decode(d["data"])); print(k,"OK",flush=True); return
            print(k,"no image",str(j)[:300],flush=True)
        except Exception as e: print(k,"ERR",e,flush=True)
ks=sys.argv[1:] or list(C)
ts=[threading.Thread(target=job,args=(k,)) for k in ks]; [t.start() for t in ts]; [t.join() for t in ts]
