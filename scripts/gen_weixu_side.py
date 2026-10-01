import base64,json,os,urllib.request,threading
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.bashrc")) if "GEMINI_IMAGE_KEY=" in l][0]
URL="https://ching-tech.ddns.net/gemini-web/v1beta/models/gemini-3.1-flash-image-preview:generateContent"
ref=base64.b64encode(open("sd/weixu_raw.png","rb").read()).decode()
P=("Image 1 is Wei Xu, a chibi pixel-art game sprite. Redraw the SAME character in the SAME chunky pixel-art style, same 2-heads-tall proportions, "
 "same face, hair, ochre robe, iron scale armor and ring-pommel saber, but change the pose to a three-quarter side view: "
 "his whole figure is turned about 45 degrees toward the RIGHT side of the image: face, eyes, chest, hips AND BOTH FEET all point to the right. Both boots' toes point to the RIGHT side of the image, never to the left. He is walking toward the right, the front foot (closer to the right edge) steps forward to the right. "
 "The saber is held in his right hand pointing down. Whole body visible with feet, centered, fills about 80% of the image height. "
 "Background: one flat solid pure green #00FF00 everywhere, no ground shadow, no other objects, no text.")
def job(i):
    body={"contents":[{"role":"user","parts":[{"inlineData":{"mimeType":"image/png","data":ref}},{"text":P}]}],
          "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
    for t in range(3):
        try:
            r=urllib.request.Request(URL,data=json.dumps(body).encode(),method="POST",headers={"x-goog-api-key":KEY,"Content-Type":"application/json"})
            j=json.loads(urllib.request.urlopen(r,timeout=450).read())
            for p in j["candidates"][0]["content"]["parts"]:
                d=p.get("inlineData") or p.get("inline_data")
                if d: open(f"sd/weixu_side{i}b_raw.png","wb").write(base64.b64decode(d["data"])); print(i,"OK",flush=True); return
            print(i,"no image",str(j)[:300],flush=True)
        except Exception as e: print(i,"ERR",e,flush=True)
ts=[threading.Thread(target=job,args=(i,)) for i in (1,2)]; [t.start() for t in ts]; [t.join() for t in ts]
