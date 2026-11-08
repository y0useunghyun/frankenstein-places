# 사진 바깥 흰 여백·대지·테두리선 잘라내기 → trim/*.jpg + trim.json(잘린 크기)
# 바깥에서 안쪽으로, 여백 줄(아주 밝음 / 어둡고 고름)이면 계속 깎고, 그림이 시작되면 멈춘 뒤 조금 더 안쪽으로(테두리선 건너뛰기).
# ponytail: 밝기 문턱 휴리스틱. 하늘이 아주 밝은 사진은 위쪽이 조금 더 깎일 수 있음 → INSET·LIGHT 조정
import json, os
from PIL import Image, ImageOps, ImageStat

LIGHT = 212          # 이보다 밝은 줄 = 여백
DARK, FLAT = 90, 14  # 이보다 어둡고 고른 줄 = 검은 스캔 테두리
INSET = 0.015        # 멈춘 뒤 더 안쪽으로 (테두리선 건너뛰기)
MAX_CUT = 0.3        # 한 변에서 최대 30%까지만


def is_margin(st):
    """여백 줄: 아주 밝거나(대지·흰 여백, 캡션 글씨 섞여도) / 어둡고 고른(검은 스캔 바탕·테두리)"""
    mean, std = st.mean[0], st.stddev[0]
    return mean > LIGHT or (mean < DARK and std < FLAT)


def edge(g, side):
    W, H = g.size
    n = H if side in 'tb' else W
    for i in range(int(n * MAX_CUT)):
        k = i if side in 'tl' else n - 1 - i
        box = (0, k, W, k + 1) if side in 'tb' else (k, 0, k + 1, H)
        if not is_margin(ImageStat.Stat(g.crop(box))):
            return i
    return int(n * MAX_CUT)


def trim(key):
    im = Image.open(f'photos/{key}.jpg').convert('RGB')
    g = ImageOps.grayscale(im)
    W, H = im.size
    box = (0, 0, W, H)
    for _ in range(3):                             # 검은 바탕 → 테두리선 → 흰 대지 순으로 벗겨지도록 몇 번 반복
        x0, y0, x1, y1 = box
        sub = g.crop(box)
        sw, sh = sub.size
        t, b, l, r = (edge(sub, s) for s in 'tblr')
        dx, dy = int(sw * INSET), int(sh * INSET)
        box = (x0 + l + dx, y0 + t + dy, x1 - r - dx, y1 - b - dy)
    out = im.crop(box)
    out.save(f'trim/{key}.jpg', quality=88)
    return out.size


if __name__ == '__main__':
    os.makedirs('trim', exist_ok=True)
    keys = [p['key'] for p in json.load(open('places.json'))]
    sizes = {k: trim(k) for k in keys}
    json.dump(sizes, open('trim.json', 'w'))
    print(len(sizes), 'trimmed')
