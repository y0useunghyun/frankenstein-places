# 정기여객선 그림에서 배만 손으로 딴 다각형으로 오려 냄 → ship.png (투명 배경)
from PIL import Image, ImageDraw, ImageFilter
im = Image.open('collect/a140.jpg').convert('L')
POLY = [(352,165),(360,190),(490,185),(522,140),(538,170),(520,190),(540,200),(600,235),(630,240),(640,300),(665,345),
        (690,470),(688,490),(670,520),(255,526),(215,485),(170,455),(65,415),(130,390),(215,320),(265,265),(320,200)]
mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon(POLY, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(2))
out = Image.merge('LA', (im, mask)).crop(mask.getbbox())
out.save('ship.png'); print(out.size)
