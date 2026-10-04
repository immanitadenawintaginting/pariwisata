import base64
import mimetypes
from functools import lru_cache
from html import escape as esc
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

FONT_PLOT = "Plus Jakarta Sans, Inter, system-ui, sans-serif"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--ink:#0F172A;--muted:#64748B;--line:#E2E8F0;--bg:#F4F7FB}
.stApp{background:
  radial-gradient(900px 520px at 6% -6%,rgba(0,114,178,.11),transparent 60%),
  radial-gradient(800px 480px at 100% 0%,rgba(230,159,0,.11),transparent 55%),var(--bg)}
.stApp,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,
.stApp button,.stApp input,.stMarkdown{font-family:'Plus Jakarta Sans',system-ui,sans-serif}
[data-testid="stHeader"]{background:transparent}
footer,#MainMenu{visibility:hidden}
.block-container{max-width:1240px;padding:1.1rem 1.4rem 4rem}
html,[data-testid="stMain"]{scroll-behavior:smooth}
[data-testid="stMain"]{scroll-snap-type:y proximity}

.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.05rem;color:var(--ink);margin:2px 0 10px}
.brand .dot{width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#0072B2,#E69F00)}
.brand .tag{margin-left:auto;font-size:.72rem;font-weight:600;color:var(--muted);border:1px solid var(--line);
  border-radius:999px;padding:3px 10px;background:#fff}
[role="tablist"],div[data-baseweb="tab-list"]{gap:6px!important;background:#fff;border:1px solid var(--line);
  border-radius:999px;padding:6px!important;width:fit-content;max-width:100%;
  box-shadow:0 12px 30px -12px rgba(15,23,42,.30)}
[role="tablist"]::after{display:none!important}
[data-testid="stTab"],button[data-baseweb="tab"]{height:auto!important;padding:11px 28px!important;
  border-radius:999px!important;background:transparent;transition:all .2s}
[data-testid="stTab"] p,button[data-baseweb="tab"] p{font-size:1.05rem;font-weight:700;color:var(--muted);margin:0}
[data-testid="stTab"]:hover,button[data-baseweb="tab"]:hover{background:#EEF2F7}
[data-testid="stTab"][aria-selected="true"],[data-testid="stTab"][data-selected],
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,#0F172A,#1E4A7A)!important;
  box-shadow:0 10px 20px -8px rgba(15,23,42,.65)}
[data-testid="stTab"][aria-selected="true"] p,[data-testid="stTab"][data-selected] p,
button[data-baseweb="tab"][aria-selected="true"] p{color:#fff!important}
.react-aria-SelectionIndicator,div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{display:none!important}

.nav{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px}
.nav a{text-decoration:none;color:var(--ink);font-weight:700;font-size:.92rem;background:#fff;
  border:1px solid var(--line);border-radius:999px;padding:9px 20px;transition:all .2s;
  box-shadow:0 8px 20px -12px rgba(15,23,42,.35)}
.nav a:hover{background:var(--ink);color:#fff;transform:translateY(-1px)}

.ch{display:flex;gap:16px;align-items:flex-start;margin:26px 0 6px;scroll-margin-top:12px;scroll-snap-align:start}
.ch-no{flex:0 0 auto;font-size:3.6rem;font-weight:800;line-height:.9;letter-spacing:-2px;
  background:linear-gradient(160deg,var(--c),transparent 125%);-webkit-background-clip:text;
  background-clip:text;color:transparent}
.ch-eb{font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px}
.ch h2{margin:0;padding:0;font-size:1.75rem;letter-spacing:-.02em;font-weight:800;line-height:1.15;color:var(--ink)}
.ch p{margin:4px 0 0;max-width:980px;font-size:.93rem;line-height:1.5;color:#475569}

[class*="st-key-card_"]{background:#fff;border:1px solid var(--line);border-radius:20px;padding:10px 14px 4px;
  box-shadow:0 1px 2px rgba(15,23,42,.04),0 16px 36px -16px rgba(15,23,42,.16);transition:box-shadow .25s,transform .25s}
[class*="st-key-card_"]:hover{box-shadow:0 1px 2px rgba(15,23,42,.05),0 22px 44px -14px rgba(15,23,42,.22)}
[class*="st-key-panel_"]{background:rgba(255,255,255,.72);backdrop-filter:blur(10px);border:1px solid var(--line);
  border-radius:22px;padding:14px 20px 8px}
.panel-t{font-weight:800;font-size:.95rem;color:var(--ink);margin-bottom:2px}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:16px;background:#fff}

.kpi{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:20px;
  padding:14px 16px;height:100%;box-shadow:0 12px 28px -18px rgba(15,23,42,.25);transition:transform .2s}
.kpi:hover{transform:translateY(-3px)}
.kpi-ic{flex:0 0 auto;width:46px;height:46px;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:1.35rem}
.kpi-l{font-size:.78rem;font-weight:700;color:var(--muted)}
.kpi-v{font-size:1.45rem;font-weight:800;line-height:1.2;color:var(--ink)}
.kpi-s{font-size:.8rem;color:var(--muted)}

.tile{background:#fff;border:1px solid var(--line);border-radius:14px;padding:8px 14px;margin-bottom:8px;font-size:.86rem;line-height:1.4;
  box-shadow:0 10px 24px -18px rgba(15,23,42,.3)}
.tile b i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px}
.tile small{color:var(--muted);font-size:.74rem;line-height:1.3;display:block;margin-top:2px}

.chip{display:inline-flex;align-items:center;gap:7px;background:#F1F5F9;border-radius:999px;
  padding:4px 12px;margin:2px 6px 2px 0;font-size:.82rem;font-weight:600;color:#334155;white-space:nowrap}
.chip i{display:inline-block;width:11px;height:11px;border-radius:50%}
.insight{display:flex;gap:12px;align-items:flex-start;margin:8px 0 0;padding:9px 16px;font-size:.92rem;line-height:1.45;border-radius:16px;
  background:linear-gradient(120deg,rgba(230,159,0,.14),rgba(230,159,0,.04));border:1px solid rgba(230,159,0,.35)}
.insight .ic{font-size:1.3rem;line-height:1.3}
.insight b.h{display:block;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:#B45309;margin-bottom:2px}

@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@supports (animation-timeline:view()){
  .ch,.insight,[class*="st-key-card_"]{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 40%}}
@supports not (animation-timeline:view()){
  .ch,.insight,[class*="st-key-card_"]{animation:rise .7s ease both}}

.brand img.logo{height:52px;width:auto;display:block}
.sec{margin:54px 0 16px;scroll-margin-top:70px}
.sec .eb{font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#0072B2;margin-bottom:4px}
.sec h2{margin:0;padding:0;font-size:2.1rem;letter-spacing:-.02em;font-weight:800;line-height:1.2;color:var(--ink)}
.sec p{margin:8px 0 0;max-width:780px;font-size:1.04rem;line-height:1.6;color:#475569}
.step{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:20px;
  padding:16px 18px;height:100%;box-shadow:0 12px 28px -18px rgba(15,23,42,.25)}
.step .n{flex:0 0 auto;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-weight:800;color:#fff;background:linear-gradient(135deg,#0072B2,#009E73)}
.step b{display:block;color:var(--ink);margin-bottom:2px}.step span{font-size:.9rem;color:#475569;line-height:1.5}
.foot{margin-top:46px;padding:22px 26px;border-radius:24px;color:#CBD5E1;font-size:.9rem;line-height:1.6;
  background:linear-gradient(125deg,#0B1B3A,#0F3D6B)}
.foot b{color:#fff}.foot a{color:#FCD34D}

@media(max-width:700px){
  .sec h2{font-size:1.5rem}.brand img.logo{height:40px}
  .block-container{padding:.8rem .8rem 3rem}
  .ch{flex-direction:column;gap:2px;margin-top:24px}.ch-no{font-size:2.4rem}.ch h2{font-size:1.35rem}
  .brand .tag{display:none}}
[data-testid="stHeader"]{display:none}
.stApp [id]{scroll-margin-top:88px}
[data-testid="stLayoutWrapper"]:has(> .st-key-brandbar){position:sticky;top:8px;z-index:1000;height:0;overflow:visible;margin-bottom:-1rem;pointer-events:none}
.st-key-brandbar{margin:0;pointer-events:none}
.st-key-brandbar .brand{pointer-events:auto;margin:0;min-height:58px;box-sizing:border-box;width:fit-content;background:#fff;border:1px solid var(--line);border-radius:999px;
  padding:4px 20px 4px 12px;box-shadow:0 12px 30px -12px rgba(15,23,42,.30)}
.st-key-brandbar .brand img.logo{height:44px}
.st-key-nav [role="tablist"]:not([role="tabpanel"] *){position:sticky;top:8px;z-index:999;margin-left:auto}
.st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *){padding:10px 20px!important}
.st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *) p{font-size:.95rem}
@media(max-width:1100px){
  [data-testid="stLayoutWrapper"]:has(> .st-key-brandbar){position:static;height:auto;margin-bottom:0}
  .st-key-nav [role="tablist"]:not([role="tabpanel"] *){margin-left:0;width:100%;overflow-x:auto;
    scrollbar-width:none;justify-content:space-between}
  .st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *){padding:9px 12px!important}
  .st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *) p{font-size:.85rem}}
@media(max-width:480px){
  .st-key-nav [role="tablist"]:not([role="tabpanel"] *){gap:2px!important;padding:4px!important}
  .st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *){padding:8px 8px!important}
  .st-key-nav [data-testid="stTab"]:not([role="tabpanel"] *) p{font-size:.78rem}}
</style>
"""

HERO = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}body{margin:0;font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:transparent}
.hero{position:relative;overflow:hidden;border-radius:28px;padding:34px 36px 30px;color:#fff;min-height:__H__px;
  background:linear-gradient(125deg,#0B1B3A 0%,#0F3D6B 55%,#0E7490 100%);
  box-shadow:0 30px 60px -28px rgba(11,27,58,.7)}
.hero:before{content:"";position:absolute;width:520px;height:520px;right:-140px;top:-220px;border-radius:50%;
  background:radial-gradient(circle,rgba(230,159,0,.38),transparent 65%);animation:float 9s ease-in-out infinite}
@keyframes float{50%{transform:translate(-30px,26px)}}
svg.bg{position:absolute;inset:0;width:100%;height:100%;opacity:.9}
svg.bg path{fill:none;stroke-width:1.6;stroke-dasharray:4 12;animation:dash 7s linear infinite}
@keyframes dash{to{stroke-dashoffset:-160}}
.in{position:relative;z-index:2}
.eb{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;
  padding:5px 12px;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25)}
h1{margin:0 0 10px;font-size:3rem;line-height:1.1;font-weight:800;letter-spacing:-.02em;max-width:860px}
h1 em{font-style:normal;background:linear-gradient(90deg,#FCD34D,#F59E0B);-webkit-background-clip:text;
  background-clip:text;color:transparent}
.lead{margin:0;max-width:680px;font-size:1.02rem;line-height:1.6;color:rgba(255,255,255,.82)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:26px}
.st{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);backdrop-filter:blur(8px);
  border-radius:18px;padding:14px 16px}
.n{font-size:1.75rem;font-weight:800;letter-spacing:-.02em}
.l{font-size:.78rem;color:rgba(255,255,255,.75);margin-top:2px}
.hint{margin-top:16px;font-size:.78rem;color:rgba(255,255,255,.6)}
@media(max-width:640px){.hero{padding:24px 20px}h1{font-size:1.9rem}.lead{display:none}
  .stats{grid-template-columns:repeat(2,1fr)}.n{font-size:1.4rem}}
</style></head><body><div class="hero">
<svg class="bg" viewBox="0 0 1200 420" preserveAspectRatio="none">
 <path id="p1" d="M-20 330 C 250 60, 520 400, 820 140 S 1150 120, 1230 40" stroke="#56B4E9"/>
 <path id="p2" d="M-20 380 C 300 230, 600 420, 900 250 S 1150 260, 1230 200" stroke="#E69F00"/>
 <path id="p3" d="M-20 200 C 220 330, 560 60, 840 300 S 1100 330, 1230 300" stroke="#CC79A7"/>
 <circle r="4" fill="#FCD34D"><animateMotion dur="9s" repeatCount="indefinite"><mpath href="#p1"/></animateMotion></circle>
 <circle r="4" fill="#fff"><animateMotion dur="12s" repeatCount="indefinite"><mpath href="#p2"/></animateMotion></circle>
 <circle r="4" fill="#56B4E9"><animateMotion dur="10s" repeatCount="indefinite"><mpath href="#p3"/></animateMotion></circle>
</svg>
<div class="in">__EYEBROW__<h1>__TITLE__</h1><p class="lead">__LEAD__</p>
<div class="stats">__STATS__</div></div></div>
<script>
const ease=t=>1-Math.pow(1-t,4);
document.querySelectorAll('.n').forEach(el=>{const to=+el.dataset.to,dec=+el.dataset.dec,suf=el.dataset.suf||'',t0=performance.now();
 (function f(t){const p=Math.min((t-t0)/1600,1);
  el.textContent=(to*ease(p)).toLocaleString('id-ID',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suf;
  if(p<1)requestAnimationFrame(f)})(t0)});
</script></body></html>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


@lru_cache(maxsize=None)
def data_uri(path):
    p = Path(path)
    if not p.exists():
        return None
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def brand_bar(nama="Pariwisata Indonesia", tag="Sumber: BPS", logo=None):
    mark = f'<img class="logo" src="{logo}" alt="Logo {esc(nama)}">' if logo else '<span class="dot"></span>'
    teks = "" if logo else esc(nama)
    with st.container(key="brandbar"):
        st.markdown(f'<div class="brand">{mark}{teks}'
                    f'<span class="tag">{esc(tag)}</span></div>', unsafe_allow_html=True)


def section_title(eyebrow, title, lead="", anchor=""):
    a = f' id="{anchor}"' if anchor else ""
    p = f"<p>{lead}</p>" if lead else ""
    st.markdown(f'<div class="sec"{a}><div class="eb">{esc(eyebrow)}</div><h2>{esc(title)}</h2>{p}</div>',
                unsafe_allow_html=True)


def skala(v):
    if v >= 1e9:
        return v / 1e9, 1, " miliar"
    if v >= 1e6:
        return v / 1e6, 1, " jt"
    return v, 0, ""


def hero(eyebrow, title, lead, stats, height=400):
    cells = ""
    for v, label in stats:
        n, dec, suf = skala(v)
        cells += (f'<div class="st"><div class="n" data-to="{n:.4f}" data-dec="{dec}" '
                  f'data-suf="{esc(suf)}">0</div><div class="l">{esc(label)}</div></div>')
    html = (HERO.replace("__H__", str(height - 40)).replace("__EYEBROW__", f'<span class="eb">{esc(eyebrow)}</span>' if eyebrow else "")
            .replace("__TITLE__", title).replace("__LEAD__", esc(lead)).replace("__STATS__", cells))
    components.html(html, height=height)


def story_nav(items):
    st.markdown('<div class="nav">' + "".join(f'<a href="#{a}">{esc(t)}</a>' for a, t in items) + "</div>",
                unsafe_allow_html=True)


def chapter(no, anchor, eyebrow, title, lead, color="#0072B2"):
    st.markdown(
        f'<div class="ch" id="{anchor}"><div class="ch-no" style="--c:{color}">{no:02d}</div><div>'
        f'<div class="ch-eb" style="color:{color}">Bab {no} · {esc(eyebrow)}</div>'
        f'<h2>{esc(title)}</h2><p>{lead}</p></div></div>', unsafe_allow_html=True)


def card(nama):
    return st.container(key=f"card_{nama}")


def panel(nama, judul=""):
    box = st.container(key=f"panel_{nama}")
    if judul:
        box.markdown(f'<div class="panel-t">{esc(judul)}</div>', unsafe_allow_html=True)
    return box


def kpi_card(col, ikon, label, value, sub, color):
    col.markdown(
        f'<div class="kpi"><div class="kpi-ic" style="background:{color}22">{ikon}</div><div>'
        f'<div class="kpi-l">{esc(label)}</div><div class="kpi-v">{esc(value)}</div>'
        f'<div class="kpi-s">{esc(sub)}</div></div></div>', unsafe_allow_html=True)


def chips(items):
    st.markdown("".join('<span class="chip">' + (f'<i style="background:{c}"></i>' if c else "") + esc(t)
                        + "</span>" for c, t in items), unsafe_allow_html=True)


def insight(teks):
    st.markdown(f'<div class="insight"><div class="ic">💡</div><div><b class="h">Temuan</b>{teks}</div></div>',
                unsafe_allow_html=True)


def polish(fig):
    fig.update_layout(
        font=dict(family=FONT_PLOT, color="#0F172A"), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", title_font=dict(size=15),
        hoverlabel=dict(bgcolor="#0F172A", bordercolor="#0F172A",
                        font=dict(color="#fff", family=FONT_PLOT, size=12)))
    return fig