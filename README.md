# Schmolke · Rubi Workshop

schmolke.rubiworkshop.com 원페이지 정적 사이트. quoc.rubiworkshop.com, thm.rubiworkshop.com과 같은 구조와 디자인(레이아웃, 서체, 빌드 방식)입니다.

- `index.html` 한국어 원페이지 (Schmolke · Range · Cockpit · Seatpost · Saddle · Wheels · Folding · Fit · Story · Showroom)
- 디자인은 QUOC 사이트와 같은 rubi.kr 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- THM 사이트와 다른 점: 쉬몰케 공식 제품 사진은 흰 배경의 정사각형 스튜디오 컷이라, 제품 컷(`.shots`, `figure.prod`)은 1:1 비율에 흰 바탕, 잘림 없이(contain) 보여 줍니다. 라벨과 아이브로우는 원문 대소문자 그대로 씁니다. 포인트 컬러는 쉬몰케 레드(#c8102e)이며 포커스 표시에만 씁니다.
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `index.src.html` 편집용 한국어 원본. 사이즈 표는 `{{BAR_TABLE}}`, `{{POST_TABLE}}`, `{{WHEEL_TABLE}}` 자리에 빌드 시 채워집니다 (`tools/build.py` 안의 수치).
- `i18n/` 번역 사전 (`ko.json` 원문 목록, `en.json` · `ja.json` 원문→번역, `tr_source.py` 번역 원본)
- `tools/build.py` 한국어 페이지, 번역 페이지, sitemap.xml을 한 번에 생성
- `404.html` 하위 주소(/cockpit, /stem, /seatpost, /saddle, /wheels, /tlo37, /brompton, /fit, /dealers 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `brand`, `cockpit`, `roadbar`, `stem`, `seatpost`, `saddle`, `wheels`, `folding`, `parts`)
- `.github/image-manifest.txt` + `fetch-images.yml` 쉬몰케 공식 사이트(schmolke-carbon.com) 이미지 이전용 워크플로. 원본이 2560~5500px로 커서 받은 뒤 히어로는 2400px, 나머지는 1600px로 줄입니다.

## 처음 올릴 때
1. 저장소 `sereno-kwon/schmolke`를 만들고 이 폴더를 main에 푸시합니다.
2. 푸시하면 `fetch-images.yml`이 매니페스트의 이미지 59장을 schmolke-carbon.com에서 받아 줄인 뒤 `images/`에 커밋합니다. Actions → Fetch images from Schmolke에서 FAIL이 있으면 해당 줄의 URL을 바꿔 다시 푸시합니다.
3. 배포: GitHub Pages(Settings → Pages → main / root) 또는 Cloudflare Pages(저장소 연결, 빌드 명령 없음, 출력 폴더 `/`) 중 하나를 씁니다.
4. 도메인 DNS에 `schmolke` CNAME 레코드를 추가합니다 (GitHub Pages는 `sereno-kwon.github.io`, Cloudflare Pages는 `<프로젝트>.pages.dev`). CNAME 파일은 이미 들어 있습니다.
5. 파비콘은 별도로 넣어야 합니다: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px), `images/logo-512.png`.
6. 로고(`images/logo.svg`)는 쉬몰케 공식 사이트 헤더 로고(SVG)를 받아 옵니다. CSS에서 헤더는 검정, 다크모드는 흰색으로 칠해집니다.

## 이미지
매니페스트를 수정해 main에 푸시하면 Actions가 이미지를 받아 `images/`에 커밋합니다.
이미 받은 파일은 건너뛰므로, 이미지를 교체할 때는 해당 파일을 지우거나 새 파일명으로 추가합니다.
루비에서 직접 촬영한 사진으로 바꿀 때는 같은 경로에 덮어쓰면 됩니다.

- 히어로 02(TLO 37 휠셋)는 공식 사이트 배너 원본이라 아래쪽 가운데에 매거진 테스트 로고가 들어 있습니다. 거슬리면 `images/wheels/01.jpg` 등 다른 컷이나 루비 촬영 사진으로 바꾸세요.
- 히어로 03(스템), 04(폴딩 바이크)는 1000px 정사각형이라 오른쪽에 붙는 `fit-stage` 배치로 씁니다.
- 인물 사진(창업자, 앰배서더)은 쓰지 않았습니다.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` 로 한국어 페이지를 만들고, `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 새로 생기거나 바뀐 한국어 문장을 `en.json` · `ja.json`에 같은 키로 추가합니다 (또는 `i18n/tr_source.py`의 목록을 같은 순서로 고친 뒤 `python3 i18n/tr_source.py`). HTML 태그는 원문과 똑같이 유지합니다.
4. 다시 `python3 tools/build.py` 를 실행하면 번역되지 않은 문장이 있을 때 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다 (`pip install beautifulsoup4`).

## 링크
- 헤더 SHOP, 각 제품의 "루비워크샵에서 보기" 버튼: `https://rubiworkshop.com/schmolke`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 INSTAGRAM: `https://www.instagram.com/rubi.workshop`, THM Korea: `https://thm.rubiworkshop.com/`
- 쇼룸 운영시간: 월~금 12:00~19:00, 토 10:00~15:30
- 사이트 표기: 운영 주체는 "루비워크샵"(사이트 이름, og:site_name, 구조화 데이터, 저작권 표기), 루비컴퍼니는 쉬몰케의 한국 공식 디스트리뷰터로 표기

## 한글 표기
쉬몰케(Schmolke), 슈테판 쉬몰케(Stefan Schmolke), 콘스탄츠(Konstanz), 보덴호(Bodensee), 로드바 에보(Roadbar Evo), 콕핏(Cockpit), 레게리시마(Leggerissima), 에어로우(Aerrow), 인피니티(Infinity), 익스트라라이트(Extralite), 논플러스(NONPLUS), 브롬톤 T 라인(Brompton T Line), 얀 울리히(Jan Ullrich)

## 수치 출처
쉬몰케 공식 사이트 schmolke-carbon.com 제품별 사양과 회사 소개(Story: 34 Years of Success, The Team, Product Tests), 2026-11 확인. 무게는 제조사 기준.
