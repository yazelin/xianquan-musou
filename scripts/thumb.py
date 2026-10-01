import os,subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
subprocess.run(['python3','cover3_param.py'],env={**os.environ,'DX':os.environ.get('DX','20'),'OUT':'cover/thumb_base.png'},check=True)
fp='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
im=Image.open('cover/thumb_base.png').convert('RGBA')
ov=Image.new('RGBA',im.size,(0,0,0,0))
big=ImageFont.truetype(fp,140,index=3); mid=ImageFont.truetype(fp,230,index=3); small=ImageFont.truetype(fp,44,index=3)
def txt(xy,s,font,fill):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((xy[0]+5,xy[1]+7),s,font=font,fill=(0,0,0,210)); ov.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(ov).text(xy,s,font=font,fill=fill)
x,y=90,230
txt((x,y),"仙泉·香布纏",big,(246,232,200,255))
txt((x-8,y+165),"無雙",mid,(232,190,90,255))
txt((x+4,y+445),"湘、布、蟬、荃、魏續，同一片戰場",small,(236,226,206,255))
im.alpha_composite(ov); im.convert('RGB').save('cover/thumb.png'); im.convert('RGB').resize((960,540)).save('cover/thumb_prev.png')
