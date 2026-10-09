#!/usr/bin/env python3
"""Generate every HTML page of the site.

All the site's text lives in this file. Edit it, then run:

    python3 tools/build_pages.py

Do not edit the .html files directly: they are overwritten on every build.
Any text written inside [square brackets] is shown highlighted on the site
as a placeholder that still needs real content.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "assets/img/manifest.json").read_text())
# Public address of the site (no trailing slash). Update it if the repository or account is renamed.
SITE_URL = "https://alessiafontana-costumedesigner.github.io/alessiafontana.github.io"

# ---------------------------------------------------------------------------
# CONTACT DETAILS (used in the footer of every page and on the Contact page)
# ---------------------------------------------------------------------------
EMAIL = "[hello@example.com]"
INSTAGRAM_HANDLE = "[@username]"
INSTAGRAM_URL = "https://www.instagram.com/"
CITY = "[City, Italy]"
CONTACT_INTRO = "For collaborations, commissions and enquiries about costume design for film, theatre and fashion."

# ---------------------------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------------------------
ABOUT_LEAD = "[One or two sentences introducing Alessia: costume designer working between film and fashion, based in …]"
ABOUT_PARAGRAPHS = [
    "[A longer paragraph about her background and training, the kind of projects she works on, and her approach to building characters through clothing: research, fabrics, hand techniques such as embroidery and knitwear.]",
    "[Optional: collaborations, awards, languages, availability for new projects.]",
]
# (year, description) — use *asterisks* around a title to set it in italics.
SELECTED_PROJECTS = [
    ("2024", "*The End*, short film. Costume design"),
    ("2024", "*Anime Giovani*, short film. Costume design"),
    ("2022", "Fashion Graduate Italia, Milan. Runway collection"),
    ("[Year]", "*Échec et Mat*, costume concept"),
]
EDUCATION = [
    ("[Year]", "[Degree, Institution, City]"),
]
# Image on the About page: (project slug, image name from assets/img/<slug>/), caption
ABOUT_IMAGE = ("site", "about-01")
ABOUT_IMAGE_ALT = "Runway look from Fashion Graduate Italia: red damask jacket and culottes over a blue velvet corset, with a beaded blue bonnet"
ABOUT_CAPTION = "Fashion Graduate Italia, Milan, 2022."

# ---------------------------------------------------------------------------
# PROJECTS — order here is the order on the home page.
#   slug     folder name in assets/img/ and the page's file name
#   cover    (image name, focal point) for the home page tile
#   layouts  how each section is laid out:
#              "stack"     one large image per row
#              "grid-2"    two per row   | "grid-3"   three per row
#              "masonry-3" three columns, for mixed portrait/landscape photos
#   video    optional short MP4 clip (plays silently on a loop), shown above backstage
# ---------------------------------------------------------------------------

PROJECTS = [
    dict(slug="fashion-graduate-italia", title="Fashion Graduate Italia", kind="Fashion",
         cover=("gallery-16", "50% 22%"),
         eyebrow="Runway collection · Milan",
         intro="[Short description of the collection shown at Fashion Graduate Italia: concept, damask and velvet, lace collars, knitted bonnets.]",
         credits=[("Role", "Designer"), ("Event", "Fashion Graduate Italia"), ("Year", "2022")],
         layouts={"gallery": "grid-3"},
         alt="Look from the Fashion Graduate Italia runway"),
    dict(slug="echec-et-mat", title="Échec et Mat", kind="Concept",
         cover=("gallery-01", "50% 40%"),
         eyebrow="Costume concept · Thesis project",
         intro="[Short description of the project: the idea behind the costumes, references (Vermeer, Dutch Golden Age), materials and techniques such as embroidery.]",
         credits=[("Role", "Costume Designer"), ("Year", "[Year]"), ("School", "[Institution]")],
         layouts={"gallery": "stack"}),
    dict(slug="anime-giovani", title="Anime Giovani", kind="Short film",
         cover=("gallery-05", "50% 40%"),
         eyebrow="Short film · Costume design",
         intro="[Short description of the film and the costume approach: characters, palette, period.]",
         credits=[("Role", "Costume Designer"), ("Director", "[Director name]"), ("Production", "[Production]"), ("Year", "2024")],
         layouts={"gallery": "grid-2", "backstage": "masonry-3"},
         alt="Still from Anime Giovani"),
    dict(slug="the-end", title="The End", kind="Short film",
         cover=("gallery-04", "50% 50%"),
         eyebrow="Short film · Costume design",
         intro="[Short description of the film and the costume approach: the fairy-tale characters, fabrics, how the costumes were sourced or made.]",
         credits=[("Role", "Costume Designer"), ("Director", "[Director name]"), ("Production", "[Production]"), ("Year", "2024")],
         layouts={"gallery": "grid-2", "backstage": "masonry-3"},
         video="assets/video/the-end.mp4",
         alt="Still from The End"),
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@400;500&display=swap" rel="stylesheet">')


# ---------------------------------------------------------------------------
# Templates (no need to edit below this line)
# ---------------------------------------------------------------------------

def text(s):
    """Escape text, set *x* in italics, highlight [placeholders]."""
    s = escape(s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return re.sub(r"(\[.+?\])", r'<span class="placeholder">\1</span>', s)


def bare(s):
    """Plain value for use inside attributes (mailto:, etc.)."""
    return s.strip("[]")


def page(title, desc, body, current, prefix="", og_image="assets/img/echec-et-mat/gallery-01-thumb.jpg"):
    def nav(name, href):
        cur = ' aria-current="page"' if current == name else ""
        return f'<a href="{prefix}{href}"{cur}>{name}</a>'
    full_title = "Alessia Fontana — Costume Designer" if not title else f"{title} — Alessia Fontana"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(full_title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta property="og:title" content="{escape(full_title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{SITE_URL}/{og_image}">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  {FONTS}
  <link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-name">Alessia Fontana</span>
        <span class="brand-role">Costume Designer</span>
      </a>
      <nav class="nav" aria-label="Main">
        {nav("Work", "index.html")}
        {nav("About", "about.html")}
        {nav("Contact", "contact.html")}
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <span>&copy; <span id="year">2026</span> Alessia Fontana</span>
      <a href="{INSTAGRAM_URL}" rel="noopener" target="_blank">Instagram</a>
      <a href="mailto:{escape(bare(EMAIL))}">Email</a>
      <a class="top" href="#top" onclick="window.scrollTo({{top:0}});return false;">Back to top &uarr;</a>
    </div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
  <script src="{prefix}assets/js/main.js" defer></script>
</body>
</html>
"""


def img_tag(item, prefix, alt, lazy=True, sizes="(max-width: 720px) 100vw, 50vw"):
    l = ' loading="lazy"' if lazy else ""
    return (f'<img src="{prefix}assets/img/{item["thumb"]}" '
            f'srcset="{prefix}assets/img/{item["thumb"]} 900w, {prefix}assets/img/{item["src"]} {item["w"]}w" '
            f'sizes="{sizes}" width="{item["w"]}" height="{item["h"]}" alt="{escape(alt)}"{l} decoding="async">')


def find(slug, key):
    sec, _ = key.rsplit("-", 1)
    return next(i for i in M[slug][sec] if i["src"].endswith(f"/{key}.jpg"))


# ---------- index ----------
tiles = []
for n, p in enumerate(PROJECTS, 1):
    item = find(p["slug"], p["cover"][0])
    im = img_tag(item, "", p["title"], lazy=n > 2).replace("<img ", f'<img style="object-position:{p["cover"][1]}" ')
    tiles.append(f"""        <li class="reveal">
          <a class="tile" href="projects/{p['slug']}.html">
            <div class="tile-media">{im}</div>
            <div class="tile-caption">
              <span class="tile-title">{escape(p['title'])}</span>
              <span class="tile-kind">{escape(p['kind'])}</span>
            </div>
          </a>
        </li>""")
body = f"""    <div class="wrap">
      <h1 class="sr-only">Selected work</h1>
      <ul class="work-grid">
{chr(10).join(tiles)}
      </ul>
    </div>"""
(ROOT / "index.html").write_text(page(None, "Portfolio of Alessia Fontana, costume designer for film and fashion.", body, "Work"))

# ---------- project pages ----------
SIZES = {"stack": "(max-width: 1440px) 100vw, 1340px",
         "grid-2": "(max-width: 560px) 100vw, 50vw",
         "grid-3": "(max-width: 560px) 100vw, (max-width: 900px) 50vw, 33vw",
         "masonry-3": "(max-width: 560px) 100vw, (max-width: 900px) 50vw, 33vw"}

for n, p in enumerate(PROJECTS):
    prev_p, next_p = PROJECTS[n - 1], PROJECTS[(n + 1) % len(PROJECTS)]
    credits = "\n".join(f"          <dt>{escape(k)}</dt><dd>{text(v)}</dd>" for k, v in p["credits"])
    parts = [f"""    <div class="wrap">
      <article>
      <header class="project-head">
        <div>
          <p class="eyebrow">{escape(p['eyebrow'])}</p>
          <h1 class="project-title">{escape(p['title'])}</h1>
        </div>
        <div>
          <p class="project-intro">{text(p['intro'])}</p>
          <dl class="credits">
{credits}
          </dl>
        </div>
      </header>"""]
    for sec, layout in p["layouts"].items():
        if sec == "backstage":
            if p.get("video"):
                parts.append(f"""
      <h2 class="section-label">Film</h2>
      <video class="film reveal" autoplay muted loop playsinline preload="metadata" aria-label="Clip from {escape(p['title'])}">
        <source src="../{p['video']}" type="video/mp4">
      </video>""")
            parts.append('\n      <h2 class="section-label">Backstage</h2>')
        alt_base = "Backstage, " + p["title"] if sec == "backstage" else p.get("alt", p["title"])
        items = M[p["slug"]][sec]
        lis = []
        for i, item in enumerate(items, 1):
            lis.append(f'        <li class="reveal"><button type="button" data-full="../assets/img/{item["src"]}" '
                       f'aria-label="View image {i} larger">'
                       + img_tag(item, "../", f"{alt_base} — image {i}", lazy=i > 2, sizes=SIZES[layout])
                       + "</button></li>")
        parts.append(f'\n      <ul class="gallery {layout}">\n' + "\n".join(lis) + "\n      </ul>")
    parts.append(f"""
      </article>
      <nav class="project-nav" aria-label="More projects">
        <a class="prev" href="{prev_p['slug']}.html"><span class="dir">&larr; Previous</span><span class="name">{escape(prev_p['title'])}</span></a>
        <a class="next" href="{next_p['slug']}.html"><span class="dir">Next &rarr;</span><span class="name">{escape(next_p['title'])}</span></a>
      </nav>
    </div>""")
    cover = find(p["slug"], p["cover"][0])
    (ROOT / "projects").mkdir(exist_ok=True)
    (ROOT / "projects" / f"{p['slug']}.html").write_text(
        page(p["title"], f"{p['title']} — {p['eyebrow']}. Costumes by Alessia Fontana.", "".join(parts), "Work",
             prefix="../", og_image=f"assets/img/{cover['thumb']}"))

# ---------- about ----------
def rows(items):
    return "\n".join(f'            <li><span class="yr">{text(y)}</span><span>{text(d)}</span></li>' for y, d in items)


portrait = find(*ABOUT_IMAGE)
paras = "\n".join(f"        <p>{text(t)}</p>" for t in ABOUT_PARAGRAPHS)
body = f"""    <div class="wrap split">
      <figure class="reveal">
        {img_tag(portrait, "", ABOUT_IMAGE_ALT, lazy=False, sizes="(max-width: 820px) 100vw, 45vw")}
        <figcaption>{text(ABOUT_CAPTION)}</figcaption>
      </figure>
      <div class="prose">
        <h1 class="page-title">About</h1>
        <p class="lead">{text(ABOUT_LEAD)}</p>
{paras}

        <div class="cv">
          <h2>Selected projects</h2>
          <ul>
{rows(SELECTED_PROJECTS)}
          </ul>
          <h2>Education</h2>
          <ul>
{rows(EDUCATION)}
          </ul>
        </div>
      </div>
    </div>"""
(ROOT / "about.html").write_text(page("About", "About Alessia Fontana, costume designer for film and fashion.", body, "About"))

# ---------- contact ----------
body = f"""    <div class="wrap split">
      <div>
        <h1 class="page-title">Contact</h1>
        <p class="lead">{text(CONTACT_INTRO)}</p>
      </div>
      <ul class="contact-list">
        <li><span class="label">Email</span><a href="mailto:{escape(bare(EMAIL))}">{text(EMAIL)}</a></li>
        <li><span class="label">Instagram</span><a href="{escape(INSTAGRAM_URL)}" rel="noopener" target="_blank">{text(INSTAGRAM_HANDLE)}</a></li>
        <li><span class="label">Based in</span><span class="contact-value">{text(CITY)}</span></li>
      </ul>
    </div>"""
(ROOT / "contact.html").write_text(page("Contact", "Contact Alessia Fontana, costume designer.", body, "Contact"))

# ---------- 404 ----------
body = f"""    <div class="wrap">
      <h1 class="page-title">Page not found</h1>
      <p><a class="link" href="{SITE_URL}/index.html">Back to the work</a></p>
    </div>"""
(ROOT / "404.html").write_text(page("Not found", "Page not found.", body, None, prefix=SITE_URL + "/"))
print("Built index, about, contact, 404 and", len(PROJECTS), "project pages.")
