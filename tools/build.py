"""루비워크샵 쉬몰케 사이트 빌드.

index.src.html(한국어 원본)에서
  1) 사이즈 표(핸들바, 시트포스트, 휠셋)를 채워 index.html(한국어)을 만들고
  2) i18n/en.json, i18n/ja.json 번역으로 en/index.html, ja/index.html을 만들고
  3) sitemap.xml을 다시 씁니다.

사용법: python3 tools/build.py
문구를 고친 뒤에는 python3 i18n/extract.py 로 ko.json을 갱신하고,
새로 생긴 문장만 en.json / ja.json에 추가한 다음 빌드합니다.
"""
import json, re, sys, pathlib, datetime
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'i18n'))
from extract import HANGUL  # noqa: E402

SITE = 'https://schmolke.rubiworkshop.com/'

# ---------------------------------------------------------------- fit tables
# 쉬몰케 공식 사양(schmolke-carbon.com, 2026-11 기준). 무게는 제조사 기준.
BARS = [
  # 모델, 무게, 폭, 리치, 드롭, 플레어, 스템, 최대 하중
  ('Roadbar Evo TLO', '130 ~ 150g', '400 / 420 / 440mm', '73 / 78mm', '125 / 126mm', '-', '별도 스템', '110kg'),
  ('Roadbar Cockpit TLO', '222g (420 x 100)', '400 / 420 / 440mm', '73 / 78mm', '125 / 126mm', '6°', '90 / 100 / 110mm, -6°', '110kg'),
  ('Roadbar Cockpit Aero TLO', '250g (420 x 100)', '380 / 400 / 420mm', '77mm', '119mm', '6°', '100 / 110 / 120mm, -6°', '110kg'),
]
POSTS = [
  # 모델, 무게, 지름, 길이, 셋백, 레일, 최대 체중
  ('Seatpost TLO', '95g (27.2 x 350)', '27.2 / 30.9 / 31.6 / 34.9mm', '로드 200 ~ 350mm, 그래블 · MTB 250 ~ 450mm', '0mm', '원형, 오벌 8 x 12mm까지', '110kg'),
  ('Seatpost TLO Setback', '110g (27.2 x 350)', '27.2 / 30.9 / 31.6 / 34.9mm', '로드 200 ~ 350mm, 그래블 · MTB 250 ~ 450mm', '10mm', '원형, 오벌 8 x 12mm까지', '110kg'),
  ('Seatpost SL', '105g (27.2 x 350)', '27.2 / 30.9 / 31.6 / 34.9mm', '로드 200 ~ 350mm, 그래블 · MTB 300 ~ 450mm', '-', '원형, 오벌 8 x 12mm까지', '110kg'),
  ('Seatpost TLO 폴딩 바이크', '159g (31.8 x 600)', '31.8 / 34.9mm', '500 / 550 / 600mm', '-', '원형, 오벌 8 x 12mm까지', '체중에 맞춰 제작'),
]
WHEELS = [
  # 모델, 무게, 림 높이, 림 폭, 스포크, 허브, 최대 총중량
  ('TLO 37 TLR Disc 2nd Gen.', '840g', '37mm', '25 / 32.5mm', '카본 24개', 'Extralite, NONPLUS (DT Swiss 180은 970g)', '100kg'),
  ('TLO 50 TLR Disc', '940g', '50mm', '25 / 32.5mm', '카본 24개', 'Extralite, NONPLUS (DT Swiss 180은 1,025g)', '115kg'),
  ('TLO Gravel PI ROPE', '1,170g', '35mm', '25 / 31mm', 'PI ROPE 텍스타일 24개', 'NONPLUS 센터락', '110kg'),
]

def table(head, rows):
    h = '<table class="size fit"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead><tbody>'
    for r in rows:
        h += f'<tr><th>{r[0]}</th>' + ''.join(f'<td>{v}</td>' for v in r[1:]) + '</tr>'
    return h + '</tbody></table>'

TABLES = {
  '{{BAR_TABLE}}': lambda: table(['모델', '무게', '폭', '리치', '드롭', '플레어', '스템', '최대 하중'], BARS),
  '{{POST_TABLE}}': lambda: table(['모델', '무게', '지름', '길이', '셋백', '안장 레일', '최대 체중'], POSTS),
  '{{WHEEL_TABLE}}': lambda: table(['모델', '무게', '림 높이', '림 폭', '스포크', '허브', '최대 총중량'], WHEELS),
}

def build_ko():
    s = (ROOT / 'index.src.html').read_text()
    for k, f in TABLES.items():
        s = s.replace(k, f())
    assert '{{' not in s
    assert '—' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'em dash in Korean page'
    (ROOT / 'index.html').write_text(s)
    return s

# ---------------------------------------------------------------- translate
LANG = {
 'en': {'locale': 'en_US', 'path': 'en/'},
 'ja': {'locale': 'ja_JP', 'path': 'ja/'},
}

def translate(ko_html, lang):
    tr = json.loads((ROOT / f'i18n/{lang}.json').read_text())
    missing = set()
    def t(s):
        k = s.strip()
        if not HANGUL.search(k):
            return s
        if k in tr:
            return s.replace(k, tr[k])
        missing.add(k)
        return s

    soup = BeautifulSoup(ko_html, 'html.parser')
    soup.html['lang'] = lang
    if soup.title:
        soup.title.string = t(soup.title.string)
    for m in soup.find_all('meta'):
        if m.has_attr('content'):
            m['content'] = t(m['content'])
    for sc in soup.find_all('script', type='application/ld+json'):
        data = json.loads(sc.string)
        def walk(o):
            if isinstance(o, dict):
                return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(v) for v in o]
            if isinstance(o, str):
                return t(o)
            return o
        data = walk(data)
        for node in data.get('@graph', []):
            if node.get('@type') == 'WebSite':
                node['url'] = SITE + LANG[lang]['path']
                node['inLanguage'] = lang
        sc.string = '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for el in soup.body.find_all(True):
        for a in ('alt', 'aria-label', 'title'):
            if el.has_attr(a):
                el[a] = t(el[a])

    def visit(el):
        if el.name in ('script', 'style'):
            return
        direct = any(isinstance(c, NavigableString) and not isinstance(c, Comment) and HANGUL.search(c) for c in el.children)
        if direct:
            k = el.decode_contents().strip()
            if k in tr:
                el.clear()
                frag = BeautifulSoup(tr[k], 'html.parser')
                for c in list(frag.contents):
                    el.append(c)
            else:
                missing.add(k)
            return
        for c in list(el.children):
            if getattr(c, 'name', None):
                visit(c)
    visit(soup.body)

    # canonical, og, hreflang self, language switcher
    soup.find('link', rel='canonical')['href'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:url')['content'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:locale')['content'] = LANG[lang]['locale']
    for a in soup.select('nav.lang a'):
        code = a['hreflang']
        a['href'] = '../' if code == 'ko' else ('./' if code == lang else f'../{code}/')
        if code == lang:
            a['class'] = ['on']; a['aria-current'] = 'page'
        else:
            a.attrs.pop('class', None); a.attrs.pop('aria-current', None)
    if lang == 'ja':
        # 일본어는 한글 서체(에스코어 드림) 대신 Noto Sans JP로 통일 (영문·숫자는 Pretendard 유지)
        style = soup.find('style')
        for tag in BeautifulSoup('<link rel="preconnect" href="https://fonts.googleapis.com">'
                                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                                 '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
                                 '<style>:root{--font:"RubiLatin","Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif}</style>',
                                 'html.parser').contents[:]:
            style.insert_after(tag) if tag.name == 'style' else style.insert_before(tag)

    out = str(soup)
    # 하위 폴더에서 이미지 경로 보정
    out = out.replace('src="images/', 'src="../images/').replace('url(images/', 'url(../images/').replace('href="images/', 'href="../images/')
    left = [k for k in missing]
    return out, left

def sitemap(html):
    imgs = sorted(set(re.findall(r'images/[\w/.-]+\.(?:jpg|png|webp)', html)))
    imgs = [i for i in imgs if not re.search(r'logo|favicon|apple-touch', i)]
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{SITE}{p}"/>' for h, p in [('ko', ''), ('en', 'en/'), ('ja', 'ja/'), ('x-default', '')])
    urls = []
    for p in ['', 'en/', 'ja/']:
        u = f'  <url>\n    <loc>{SITE}{p}</loc>{alts}\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if not p else "0.8"}</priority>'
        if not p:
            u += ''.join(f'\n    <image:image><image:loc>{SITE}{i}</image:loc></image:image>' for i in imgs)
        urls.append(u + '\n  </url>')
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
         + '\n'.join(urls) + '\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(x)

if __name__ == '__main__':
    ko = build_ko()
    print('ko  index.html', len(ko))
    for lang in LANG:
        if not (ROOT / f'i18n/{lang}.json').exists():
            print(lang, 'skipped (no translation file)'); continue
        out, left = translate(ko, lang)
        d = ROOT / LANG[lang]['path']; d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(out)
        hangul = len(HANGUL.findall(re.sub(r'<script(?![^>]*ld\+json).*?</script>', '', out, flags=re.S)))
        print(lang, f'{d.name}/index.html', len(out), 'untranslated units:', len(left), 'hangul chars left:', hangul)
        for k in left[:20]:
            print('   -', k[:90])
    sitemap(ko)
