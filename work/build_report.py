from pathlib import Path
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
fonts = Path('C:/Windows/Fonts')
for name, file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf'),('Arial-BoldItalic','arialbi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fonts/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-BoldItalic')

BURGUNDY = colors.HexColor('#450000')
TEXT = colors.HexColor('#252525')
GREY = colors.HexColor('#646464')
LIGHT = colors.HexColor('#F7F2F0')
LINE = colors.HexColor('#D9D9D9')
ST = {
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10.3,leading=14.2,textColor=TEXT,spaceAfter=8),
 'h1':ParagraphStyle('h1',fontName='Arial-Bold',fontSize=21,leading=26,textColor=colors.black,spaceAfter=17),
 'h2':ParagraphStyle('h2',fontName='Arial-Bold',fontSize=12.7,leading=17,textColor=colors.black,spaceAfter=10,spaceBefore=3),
 'bullet':ParagraphStyle('bullet',fontName='Arial',fontSize=10.3,leading=14.2,textColor=TEXT,leftIndent=12,firstLineIndent=-10,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9.4,leading=12.5,textColor=TEXT),
 'th':ParagraphStyle('th',fontName='Arial-Bold',fontSize=9.4,leading=12.5,textColor=colors.white),
 'cover':ParagraphStyle('cover',fontName='Arial-Bold',fontSize=32,leading=38,textColor=BURGUNDY,spaceAfter=14),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=9,leading=12,textColor=GREY,spaceAfter=10)
}

def inline(t):
    t = escape(t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:f'<link href="{m.group(2)}" color="#7D263A">{m.group(1)}</link>', t)
    t = re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t)
    return t

def widths(header,w):
    n=len(header)
    if n==2: return [w*.63,w*.37]
    if n==3:
        if 'Sản phẩm mẫu' in header[0]: return [w*.46,w*.27,w*.27]
        return [w*.23,w*.40,w*.37]
    if n==4:
        if 'Thời gian' in header[0]: return [w*.19,w*.35,w*.22,w*.24]
        if 'Đối thủ' in header[0]: return [w*.16,w*.25,w*.25,w*.34]
        if 'Ứng viên' in header[0]: return [w*.18,w*.21,w*.29,w*.32]
        return [w*.19,w*.26,w*.27,w*.28]
    if n==5:return [w*.10,w*.24,w*.22,w*.22,w*.22]
    return [w/n]*n

def blocks(section,cover=False):
    lines=section.strip().splitlines(); result=[]; i=0
    while i<len(lines):
        s=lines[i].strip()
        if not s: i+=1;continue
        if s.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.match(r'^:?-+:?$',x) for x in row): rows.append(row)
                i+=1
            data=[[Paragraph(inline(x),ST['th' if r==0 else 'cell']) for x in row] for r,row in enumerate(rows)]
            t=Table(data,colWidths=widths(rows[0],A4[0]-88),repeatRows=1,hAlign='LEFT')
            cmds=[('BACKGROUND',(0,0),(-1,0),BURGUNDY),('GRID',(0,0),(-1,-1),.45,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
            for row in range(1,len(rows)):
                if row%2:cmds.append(('BACKGROUND',(0,row),(-1,row),LIGHT))
            t.setStyle(TableStyle(cmds));result.extend([t,Spacer(1,12)]);continue
        if s.startswith('# '):
            style='cover' if cover else 'h1'; result.append(Paragraph(inline(s[2:]),ST[style]));i+=1;continue
        if s.startswith('## '):result.append(Paragraph(inline(s[3:]),ST['h2']));i+=1;continue
        if s.startswith('- '):result.append(Paragraph('• '+inline(s[2:]),ST['bullet']));i+=1;continue
        if re.match(r'^\d+\. ',s):result.append(Paragraph(inline(s),ST['bullet']));i+=1;continue
        para=[s];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||- |\d+\. )',lines[i].strip()):para.append(lines[i].strip());i+=1
        result.append(Paragraph(inline(' '.join(para)),ST['body']))
    return result

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFont('Arial',8)
    canvas.setFillColor(GREY)
    if doc.page>1:canvas.drawString(44,A4[1]-30,'L’AMME  /  BRAND AND BUSINESS AUDIT  /  Q4 2026')
    canvas.drawString(44,24,'23/10/2026 • Đánh giá bên ngoài và đề xuất quản trị')
    canvas.drawRightString(A4[0]-44,24,str(doc.page))
    canvas.restoreState()

source=OUT/'LAMME_Audit_CMO_Q4_2026.md'
sections=source.read_text(encoding='utf-8').split('<!-- PAGE -->')
story=[]
for i,sec in enumerate(sections):
    if i:story.append(PageBreak())
    story.extend(blocks(sec,cover=i==0))
pdf=OUT/'LAMME_Audit_CMO_Q4_2026.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=52,bottomMargin=43,title='L’AMME Brand and Business Audit Q4 2026',author='Nghiên cứu hỗ trợ đề xuất CMO',allowSplitting=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(str(pdf))
for i,p in enumerate(r.pages):
    txt=p.extract_text()
    print(i+1, len(txt),txt.splitlines()[1:3])
print('SECTIONS',len(sections),'PAGES',len(r.pages),'LINKS',sum(len(p.get('/Annots',[])) for p in r.pages))
