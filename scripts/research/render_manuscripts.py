"""Render current PDFs for human layout review; no manuscript edits."""
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / "build/research/rendered"
out.mkdir(parents=True, exist_ok=True)
for language, folder in (("en", "paper"), ("ru", "paper-ru")):
    doc = pdfium.PdfDocument(ROOT / folder / "main.pdf")
    thumbs = []
    for index in range(len(doc)):
        image = doc[index].render(scale=1.25).to_pil().convert("RGB")
        image.save(out / f"{language}-{index+1:02d}.png")
        image.thumbnail((300, 420))
        thumb = Image.new("RGB", (320, 450), "white")
        thumb.paste(image, ((320-image.width)//2, 22))
        ImageDraw.Draw(thumb).text((12, 4), f"{language.upper()} {index+1}", fill="black")
        thumbs.append(thumb)
    for start in range(0, len(thumbs), 8):
        batch = thumbs[start:start+8]
        sheet = Image.new("RGB", (320*4, 450*((len(batch)+3)//4)), "#cccccc")
        for index, thumb in enumerate(batch):
            sheet.paste(thumb, ((index%4)*320, (index//4)*450))
        sheet.save(out / f"{language}-contact-{start//8+1}.png")
    print(f"{language}: {len(doc)} pages rendered to {out}")
