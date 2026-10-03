from html import escape as esc
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from theme import skala

from .flow import prep_manca

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
VIDEO_EXT = (".mp4", ".webm", ".mov", ".m4v")
GAMBAR = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")

CSS = """<style>
.block-container{position:relative;z-index:1}
.st-key-bgvideo{position:fixed!important;inset:0;width:100vw!important;height:100vh!important;z-index:-2;
  pointer-events:none;margin:0!important;padding:0!important}
.st-key-bgvideo div,.st-key-bgvideo [data-testid="stVideo"]{width:100vw!important;height:100vh!important;margin:0!important;padding:0!important}
.st-key-bgvideo video{width:100vw!important;height:100vh!important;object-fit:cover;pointer-events:none;display:block}
.st-key-bgvideo video::-webkit-media-controls,.st-key-bgvideo video::-webkit-media-controls-enclosure{display:none!important}
.bg-shade{position:fixed;inset:0;z-index:-1;pointer-events:none;
  background:linear-gradient(180deg,rgba(8,20,45,.45) 0%,rgba(8,20,45,.25) 40%,rgba(8,20,45,.78) 100%)}
.brand{background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-radius:999px;padding:6px 8px 6px 14px;
  width:fit-content;max-width:100%;box-shadow:0 10px 26px -14px rgba(0,0,0,.45)}
.brand .tag{display:none}
.brand{padding-right:18px!important}
</style>"""

HERO = """<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:transparent;font-family:'Plus Jakarta Sans',system-ui,sans-serif}
.hero{height:100%;min-height:420px;color:#fff;padding:clamp(6px,2vh,20px) clamp(4px,1vw,12px) clamp(34px,8vh,72px);
 display:flex;flex-direction:column;justify-content:space-between}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:flex-start}
.eb{display:inline-block;font-size:.74rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;padding:7px 15px;border-radius:999px;
 background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);backdrop-filter:blur(6px)}
h1{margin:22px 0 16px;font-size:clamp(2.2rem,min(7.6vw,14vh),6.4rem);line-height:1.02;font-weight:800;letter-spacing:-.035em;max-width:1150px;
 text-shadow:0 6px 34px rgba(0,0,0,.55)}
h1 em{font-style:normal;background:linear-gradient(90deg,#FCD34D,#F59E0B);-webkit-background-clip:text;background-clip:text;color:transparent;
 filter:drop-shadow(0 4px 18px rgba(0,0,0,.45))}
.lead{margin:0;max-width:640px;font-size:clamp(1rem,1.5vw,1.2rem);line-height:1.6;color:rgba(255,255,255,.92);text-shadow:0 2px 14px rgba(0,0,0,.55)}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}
button{font:inherit;font-weight:800;font-size:.95rem;border-radius:999px;padding:14px 26px;cursor:pointer;border:0;transition:all .2s}
.b1{background:linear-gradient(90deg,#FCD34D,#F59E0B);color:#0B1B3A;box-shadow:0 14px 28px -12px rgba(245,158,11,.8)}
.b2{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.45);backdrop-filter:blur(6px)}
button:hover{transform:translateY(-2px)}.b2:hover{background:rgba(255,255,255,.26)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}
.st{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);backdrop-filter:blur(12px);border-radius:18px;padding:14px 18px}
.n{font-size:clamp(1.4rem,2.4vw,2rem);font-weight:800;letter-spacing:-.02em}.l{font-size:.8rem;color:rgba(255,255,255,.85);margin-top:2px}
.src{margin:12px 0 4px;font-size:.74rem;color:rgba(255,255,255,.75);text-shadow:0 1px 8px rgba(0,0,0,.6)}
@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}.lead{display:none}
 button{padding:11px 18px;font-size:.85rem}.st{padding:10px 14px}}
@media(max-height:700px){.lead{display:none}.src{display:none}.cta{margin-top:16px}h1{margin:14px 0 6px}.stats{margin-top:12px}.st{padding:9px 16px}button{padding:11px 22px}}
__FALLBACK__
</style></head><body><div class="hero">
<div class="main"><span class="eb">Dasbor visualisasi data · BPS</span>
<h1>Menjelajah <em>pariwisata Indonesia</em> lewat data</h1>
<p class="lead">Dari mana wisatawan datang, ke mana mereka bepergian, dan bagaimana akomodasi tersebar di 38 provinsi.</p>
<div class="cta"><button class="b1" onclick="go(1)">Mulai menjelajah →</button>
<button class="b2" onclick="go(1)">🌊 Aliran</button><button class="b2" onclick="go(2)">🧭 Multivariat</button>
<button class="b2" onclick="go(3)">🌳 Hierarki</button></div></div>
<div><div class="stats">__STATS__</div><div class="src">Sumber: BPS · diolah untuk UAS Visualisasi Data dan Informasi, Politeknik Statistika STIS 2026__CREDIT__</div></div>
</div>
<script>
const ease=t=>1-Math.pow(1-t,4);
document.querySelectorAll('.n').forEach(el=>{const to=+el.dataset.to,dec=+el.dataset.dec,suf=el.dataset.suf||'',t0=performance.now();
 (function f(t){const p=Math.min((t-t0)/1600,1);
  el.textContent=(to*ease(p)).toLocaleString('id-ID',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suf;
  if(p<1)requestAnimationFrame(f)})(t0)});
function fit(){try{const f=window.frameElement,P=parent.window,m=P.document.querySelector('[data-testid="stMain"]');
 const set=h=>{f.style.height=h+'px';f.setAttribute('height',h);const p=f.parentElement;if(p){p.style.height=h+'px';p.style.minHeight=h+'px'}};
 const top=f.getBoundingClientRect().top+(m?m.scrollTop:0);let h=Math.max(420,P.innerHeight-top-28);set(h);
 const ex=m?m.scrollHeight-m.clientHeight:0;if(ex>0&&h-ex>=420)set(h-ex)}catch(e){}}
function go(i){try{const t=parent.document.querySelectorAll('[role="tablist"]')[0].querySelectorAll('[role="tab"]');
 t[i].click();parent.document.querySelector('[data-testid="stMain"]').scrollTo({top:0,behavior:'smooth'})}catch(e){}}
try{const v=parent.document.querySelector('.st-key-bgvideo video');if(v){v.muted=true;v.play().catch(()=>{})}}catch(e){}
fit();setTimeout(fit,300);setTimeout(fit,1200);try{parent.addEventListener('resize',fit)}catch(e){}
</script></body></html>"""

FALLBACK = (".hero{border-radius:30px;padding:clamp(18px,4vh,48px) clamp(20px,4vw,48px);"
            "background:linear-gradient(125deg,#0B1B3A 0%,#0F3D6B 55%,#0E7490 100%)}")


def _cari_video():
    if not ASSETS.exists():
        return None
    kand = [p for p in sorted(ASSETS.iterdir())
            if p.is_file() and not p.name.lower().endswith(GAMBAR)
            and (any(e in p.name.lower() for e in VIDEO_EXT) or p.name.lower().startswith("video"))]
    kand.sort(key=lambda p: not p.name.lower().startswith("beranda"))
    return kand[0] if kand else None


def render(load, load_sheet):
    m, _ = prep_manca(load_sheet("Flow"))
    c = load("chord.csv")
    neg = m[m["Kategori"] == "Negara"]
    nonself = c[c["Asal"] != c["Tujuan"]]
    stats = [(float(m["Value"].sum()), "kunjungan wisman"), (neg["Asal"].nunique(), "negara asal"),
             (c["Asal"].nunique(), "provinsi (nusantara)"), (float(nonself["Value"].sum()), "perjalanan antarprovinsi")]
    cells = ""
    for v, label in stats:
        n, dec, suf = skala(v)
        cells += (f'<div class="st"><div class="n" data-to="{n:.4f}" data-dec="{dec}" '
                  f'data-suf="{esc(suf)}">0</div><div class="l">{esc(label)}</div></div>')

    st.markdown(CSS + "<style>.block-container{padding-bottom:.6rem!important}</style>", unsafe_allow_html=True)
    video = _cari_video()
    if video:
        with st.container(key="bgvideo"):
            st.video(str(video), loop=True, autoplay=True, muted=True)
        st.markdown('<div class="bg-shade"></div>', unsafe_allow_html=True)
    html = (HERO.replace("__STATS__", cells).replace("__FALLBACK__", "" if video else FALLBACK)
            .replace("__CREDIT__", " · Video: YouTube" if video else ""))
    components.html(html, height=640)