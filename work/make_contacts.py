from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path('work/rendered')
files=sorted(root.glob('page-*.png'))
for start in range(0,len(files),4):
    canvas=Image.new('RGB',(1200,1740),'#d9d9d9')
    for j,p in enumerate(files[start:start+4]):
        im=Image.open(p).convert('RGB'); im.thumbnail((580,820))
        x=(j%2)*600+10;y=(j//2)*870+30
        canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x,y-20),p.stem,fill='black')
    canvas.save(root/f'contact-{start//4+1}.png')
print(len(files), 'pages rendered')
