// 3D: 글자 지면을 눕히고, 장소 이름 자리에 사진을 세움. 배는 화면 가운데서 글자 바다를 타고 감.
// text.tpl.html의 전역 변수(book, x, y, s, vx, grab)를 그대로 씀
const TILT = 55, PERSPECTIVE = 1100, STAND_H = 150, SHIP_W = 340;
document.head.insertAdjacentHTML('beforeend', `<style>
  body { perspective: ${PERSPECTIVE}px; }
  #tilt { position: fixed; inset: 0; transform: rotateX(${TILT}deg); transform-style: preserve-3d; }
  #book { transform-style: preserve-3d; }
  a.pl { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
  .stand, #ship { position: absolute; left: 0; top: 0; transform-origin: 50% 100%; }
  .stand { height: ${STAND_H}px; transform: translate(-50%, -100%) rotateX(-90deg); }
  .stand img { height: 100%; display: block; box-shadow: 0 2px 6px rgba(0,0,0,.25); }
  #ship { width: ${SHIP_W}px; pointer-events: none; }
</style>`);

const tilt = document.createElement('div');
tilt.id = 'tilt'; book.before(tilt); tilt.append(book);

for (const a of book.querySelectorAll('a.pl')) {   // 이름 자리(가운데·윗줄)에 사진 세우기
  const st = document.createElement('a');
  st.className = 'stand'; st.href = a.href; st.target = '_blank'; st.rel = 'noopener'; st.title = a.title;
  st.style.left = a.offsetLeft + a.offsetWidth / 2 + 'px'; st.style.top = a.offsetTop + 'px';
  st.innerHTML = `<img src="${a.dataset.img}" alt="">`;
  st.firstChild.alt = a.title;
  book.append(st);
}

const ship = new Image();
ship.id = 'ship'; ship.src = 'ship.png'; ship.alt = '정기여객선'; book.append(ship);
(function sail(t) {   // 화면 가운데에 고정 → 글자가 배 밑으로 흘러감. 가는 방향 따라 뱃머리 돌림
  const cx = x + innerWidth / s / 2, cy = y + innerHeight / s / 2;
  ship.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -100%) rotateX(-90deg)` +
    ` rotate(${Math.sin(t / 650) * 2.5}deg) scaleX(${vx > 0 ? -1 : 1})`;
  requestAnimationFrame(sail);
})(0);

// 끌다가 링크 위에서 놓으면 열지 않음 / 링크 클릭은 멈춤 토글 안 함
let dragged = false;
addEventListener('pointerup', e => {
  dragged = !!(grab && grab.moved);
  if (grab && e.target.closest('a')) grab.moved = true;
}, true);
addEventListener('click', e => { if (dragged && e.target.closest('a')) e.preventDefault(); }, true);
