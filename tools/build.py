#!/usr/bin/env python3
"""Build the website into _site/ from the content/ files.

    python tools/build.py

Text and image choices live in content/*.yml (edited through Pages CMS).
Photos live in images/, videos in videos/. This script:
  - resizes every photo the site uses (max 2000px, plus a 900px thumbnail),
    converting PNG/HEIC/WebP to JPEG and fixing phone-camera rotation,
  - generates every HTML page,
  - copies CSS, JS and videos.
The result in _site/ is what GitHub Pages publishes. GitHub runs this
automatically on every change (see .github/workflows/deploy.yml).

Text conventions (useful for the editor):
  *Title*          -> italics
  [anything]       -> highlighted on the site as a placeholder still to fill in
"""
import os
import re
import shutil
import sys
import unicodedata
from html import escape
from pathlib import Path
from urllib.parse import quote

import yaml
from PIL import Image, ImageOps

try:  # iPhone photos (.heic)
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
# Public address of the site, no trailing slash. In GitHub Actions it comes from
# the Pages settings; the fallback is used for local builds.
SITE_URL = os.environ.get(
    "SITE_URL", "https://alessiafontana-costumedesigner.github.io/alessiafontana.github.io"
).rstrip("/")

FULL_SIZE, THUMB_SIZE = 2000, 900

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@400;500&display=swap" rel="stylesheet">')

LAYOUTS = {"one": "stack", "two": "grid-2", "three": "grid-3"}
FOCUS = {"top": "50% 20%", "center": "50% 50%", "bottom": "50% 80%"}
SIZES = {"stack": "(max-width: 1440px) 100vw, 1340px",
         "grid-2": "(max-width: 560px) 100vw, 50vw",
         "grid-3": "(max-width: 560px) 100vw, (max-width: 900px) 50vw, 33vw",
         "masonry-3": "(max-width: 560px) 100vw, (max-width: 900px) 50vw, 33vw"}

warnings = []


def warn(msg):
    warnings.append(msg)
    print("WARNING:", msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Content helpers
# ---------------------------------------------------------------------------

def load(name):
    data = yaml.safe_load((ROOT / "content" / f"{name}.yml").read_text(encoding="utf-8")) or {}
    return data


def s(value):
    """Any YAML value as a trimmed string ('' for empty)."""
    return "" if value is None else str(value).strip()


def as_list(value):
    if not value:
        return []
    return [v for v in (value if isinstance(value, list) else [value]) if s(v)]


def text(value):
    """Escape text, set *x* in italics, highlight [placeholders]."""
    out = escape(s(value))
    out = re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)
    return re.sub(r"(\[.+?\])", r'<span class="placeholder">\1</span>', out)


def plain(value):
    """Text without markup, for attributes and alt text."""
    return re.sub(r"[*\[\]]", "", s(value))


def is_placeholder(value):
    return s(value).startswith("[")


def slugify(value):
    value = unicodedata.normalize("NFKD", s(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "project"


def url(path):
    return quote(path.as_posix() if isinstance(path, Path) else path)


# ---------------------------------------------------------------------------
# Images and videos
# ---------------------------------------------------------------------------

_images = {}


def image(ref):
    """Resize a photo from the repo into _site; return its info, or None if missing."""
    ref = s(ref).lstrip("/")
    if not ref:
        return None
    if ref in _images:
        return _images[ref]
    src = ROOT / ref
    if not src.is_file():
        warn(f"photo not found: {ref}")
        _images[ref] = None
        return None
    rel = Path(ref).with_suffix(".jpg")
    full, thumb = OUT / rel, OUT / "thumbs" / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    thumb.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(src) as im:
            rotated = im.getexif().get(0x0112, 1) not in (0, 1)
            im = ImageOps.exif_transpose(im).convert("RGB")
            small_jpeg = (src.suffix.lower() in (".jpg", ".jpeg") and not rotated
                          and max(im.size) <= FULL_SIZE and src.stat().st_size < 1_200_000)
            if small_jpeg:  # already web-sized: copy untouched to avoid recompression
                shutil.copy2(src, full)
                w, h = im.size
            else:
                big = im.copy()
                big.thumbnail((FULL_SIZE, FULL_SIZE), Image.LANCZOS)
                big.save(full, "JPEG", quality=82, optimize=True, progressive=True)
                w, h = big.size
            im.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            im.save(thumb, "JPEG", quality=76, optimize=True, progressive=True)
            tw = im.size[0]
    except Exception as e:  # unreadable file: skip it rather than break the site
        warn(f"could not read photo {ref}: {e}")
        _images[ref] = None
        return None
    info = {"full": url(rel), "thumb": url(Path("thumbs") / rel), "w": w, "h": h, "tw": tw}
    _images[ref] = info
    return info


def video(ref):
    ref = s(ref).lstrip("/")
    if not ref:
        return None
    src = ROOT / ref
    if not src.is_file():
        warn(f"video not found: {ref}")
        return None
    dst = OUT / ref
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return url(ref)


def img_tag(info, prefix, alt, lazy=True, sizes="(max-width: 720px) 100vw, 50vw", style=""):
    attrs = ' loading="lazy"' if lazy else ""
    if style:
        attrs += f' style="{style}"'
    srcset = ""
    if info["tw"] < info["w"]:
        srcset = (f' srcset="{prefix}{info["thumb"]} {info["tw"]}w, {prefix}{info["full"]} {info["w"]}w"'
                  f' sizes="{sizes}"')
    return (f'<img src="{prefix}{info["thumb"]}"{srcset} '
            f'width="{info["w"]}" height="{info["h"]}" alt="{escape(alt)}"{attrs} decoding="async">')


# ---------------------------------------------------------------------------
# Page template
# ---------------------------------------------------------------------------

def page(site, title, desc, body, current, prefix="", og_image=None):
    def nav(name, href):
        cur = ' aria-current="page"' if current == name else ""
        return f'<a href="{prefix}{href}"{cur}>{name}</a>'
    name, role = plain(site.get("name")) or "Alessia Fontana", plain(site.get("role"))
    full_title = f"{name} — {role}" if not title else f"{title} — {name}"
    og = f'\n  <meta property="og:image" content="{SITE_URL}/{og_image}">' if og_image else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(full_title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta property="og:title" content="{escape(full_title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:type" content="website">{og}
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  {FONTS}
  <link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-name">{escape(name)}</span>
        <span class="brand-role">{escape(role)}</span>
      </a>
      <nav class="nav" aria-label="Main">
        {nav("Portfolio", "index.html")}
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
      <span>&copy; <span id="year">2026</span> {escape(name)}</span>
{footer_links(site)}
      <a class="top" href="#top" onclick="window.scrollTo({{top:0}});return false;">Back to top &uarr;</a>
    </div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
  <script src="{prefix}assets/js/main.js" defer></script>
</body>
</html>
"""


def instagram_url(site):
    handle = s(site.get("instagram"))
    if not handle or is_placeholder(handle):
        return None
    handle = re.sub(r"^(https?://)?(www\.)?instagram\.com/", "", handle).strip("/@ ")
    return f"https://www.instagram.com/{quote(handle)}/"


def footer_links(site):
    links = []
    if instagram_url(site):
        links.append(f'      <a href="{instagram_url(site)}" rel="noopener" target="_blank">Instagram</a>')
    email = s(site.get("email"))
    if email and not is_placeholder(email):
        links.append(f'      <a href="mailto:{escape(email)}">Email</a>')
    return "\n".join(links)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def build_home(site, projects):
    tiles = []
    for n, p in enumerate(projects):
        cover = p["cover_info"]
        if cover:
            im = img_tag(cover, "", plain(p["title"]), lazy=n > 1,
                         style=f"object-position:{FOCUS.get(s(p.get('cover_focus')), FOCUS['center'])}")
        else:
            im = ""
        tiles.append(f"""        <li class="reveal">
          <a class="tile" href="projects/{p['slug']}.html">
            <div class="tile-media">{im}</div>
            <div class="tile-caption">
              <span class="tile-title">{text(p['title'])}</span>
              <span class="tile-kind">{text(p.get('category'))}</span>
            </div>
          </a>
        </li>""")
    body = f"""    <div class="wrap">
      <h1 class="sr-only">Selected work</h1>
      <ul class="work-grid">
{chr(10).join(tiles)}
      </ul>
    </div>"""
    og = projects[0]["cover_info"]["thumb"] if projects and projects[0]["cover_info"] else None
    desc = f"Portfolio of {plain(site.get('name'))}, {plain(site.get('role')).lower()} for film and fashion."
    (OUT / "index.html").write_text(page(site, None, desc, body, "Portfolio", og_image=og), encoding="utf-8")


def gallery(items, layout, alt_base):
    lis = []
    for i, info in enumerate(items, 1):
        lis.append(f'        <li class="reveal"><button type="button" data-full="../{info["full"]}" '
                   f'aria-label="View image {i} larger">'
                   + img_tag(info, "../", f"{alt_base} — image {i}", lazy=i > 2, sizes=SIZES[layout])
                   + "</button></li>")
    return f'\n      <ul class="gallery {layout}">\n' + "\n".join(lis) + "\n      </ul>"


def build_project(site, projects, n):
    p = projects[n]
    prev_p, next_p = projects[n - 1], projects[(n + 1) % len(projects)]
    title = plain(p["title"])
    year = s(p.get("year"))
    intro = f'\n          <p class="project-intro">{text(p.get("description"))}</p>' if s(p.get("description")) else ""
    credits = (f'\n          <dl class="credits">\n          <dt>Year</dt><dd>{text(year)}</dd>\n          </dl>'
               if year else "")
    parts = [f"""    <div class="wrap">
      <article>
      <header class="project-head">
        <div>
          <p class="eyebrow">{text(p.get('subtitle'))}</p>
          <h1 class="project-title">{text(p['title'])}</h1>
        </div>
        <div>{intro}{credits}
        </div>
      </header>"""]
    items = [i for i in (image(r) for r in as_list(p.get("images"))) if i]
    if items:
        parts.append(gallery(items, LAYOUTS.get(s(p.get("layout")), "grid-2"), title))
    clip = video(p.get("video"))
    if clip:
        parts.append(f"""
      <div class="section-label" aria-hidden="true"></div>
      <video class="film reveal" autoplay muted loop playsinline preload="metadata" aria-label="Clip from {escape(title)}">
        <source src="../{clip}" type="video/mp4">
      </video>""")
    backstage = [i for i in (image(r) for r in as_list(p.get("backstage"))) if i]
    if backstage:
        parts.append('\n      <h2 class="section-label">Backstage</h2>')
        parts.append(gallery(backstage, "masonry-3", f"Backstage, {title}"))
    nav = ""
    if len(projects) > 1:
        nav = f"""
      <nav class="project-nav" aria-label="More projects">
        <a class="prev" href="{prev_p['slug']}.html"><span class="dir">&larr; Previous</span><span class="name">{text(prev_p['title'])}</span></a>
        <a class="next" href="{next_p['slug']}.html"><span class="dir">Next &rarr;</span><span class="name">{text(next_p['title'])}</span></a>
      </nav>"""
    parts.append(f"""
      </article>{nav}
    </div>""")
    og = p["cover_info"]["thumb"] if p["cover_info"] else None
    desc = f"{title} — {plain(p.get('subtitle'))}. Costumes by {plain(site.get('name'))}."
    (OUT / "projects" / f"{p['slug']}.html").write_text(
        page(site, title, desc, "".join(parts), "Portfolio", prefix="../", og_image=og), encoding="utf-8")


def rows(items):
    return "\n".join(f'          <li><span class="yr">{text(r.get("year"))}</span><span>{text(r.get("description"))}</span></li>'
                     for r in items or [] if isinstance(r, dict) and (s(r.get("year")) or s(r.get("description"))))


def build_about(site, about):
    paras = "\n".join(f"        <p>{text(t)}</p>" for t in re.split(r"\n\s*\n", s(about.get("text"))) if t.strip())
    photo = image(about.get("photo"))
    figure = ""
    if photo:
        caption = f"\n        <figcaption>{text(about.get('photo_caption'))}</figcaption>" if s(about.get("photo_caption")) else ""
        alt = plain(about.get("photo_caption")) or f"Photo of {plain(site.get('name'))}"
        figure = f"""
      <figure class="about-photo reveal">
        {img_tag(photo, "", alt, lazy=False, sizes="(max-width: 820px) 100vw, 45vw")}{caption}
      </figure>"""
    cv = ""
    for heading, key in (("Selected projects", "selected_projects"), ("Education", "education")):
        r = rows(about.get(key))
        if r:
            cv += f"\n        <h2>{heading}</h2>\n        <ul>\n{r}\n        </ul>"
    lead = f'\n        <p class="lead">{text(about.get("intro"))}</p>' if s(about.get("intro")) else ""
    body = f"""    <div class="wrap about">
      <div class="prose about-text">
        <h1 class="page-title">About</h1>{lead}
{paras}
      </div>{figure}
      <div class="prose cv">{cv}
      </div>
    </div>"""
    desc = f"About {plain(site.get('name'))}, {plain(site.get('role')).lower()} for film and fashion."
    (OUT / "about.html").write_text(page(site, "About", desc, body, "About"), encoding="utf-8")


def build_contact(site):
    items = []
    email = s(site.get("email"))
    if email:
        link = f'<a href="mailto:{escape(email)}">{text(email)}</a>' if not is_placeholder(email) else f'<span class="contact-value">{text(email)}</span>'
        items.append(f'        <li><span class="label">Email</span>{link}</li>')
    handle = s(site.get("instagram"))
    if handle:
        ig = instagram_url(site)
        shown = text(handle if is_placeholder(handle) or handle.startswith("@") else "@" + handle.split("/")[-1].lstrip("@"))
        link = f'<a href="{ig}" rel="noopener" target="_blank">{shown}</a>' if ig else f'<span class="contact-value">{shown}</span>'
        items.append(f'        <li><span class="label">Instagram</span>{link}</li>')
    if s(site.get("city")):
        items.append(f'        <li><span class="label">Based in</span><span class="contact-value">{text(site.get("city"))}</span></li>')
    intro = f'\n        <p class="lead">{text(site.get("contact_intro"))}</p>' if s(site.get("contact_intro")) else ""
    body = f"""    <div class="wrap split">
      <div>
        <h1 class="page-title">Contact</h1>{intro}
      </div>
      <ul class="contact-list">
{chr(10).join(items)}
      </ul>
    </div>"""
    desc = f"Contact {plain(site.get('name'))}, {plain(site.get('role')).lower()}."
    (OUT / "contact.html").write_text(page(site, "Contact", desc, body, "Contact"), encoding="utf-8")


def build_404(site):
    body = f"""    <div class="wrap">
      <h1 class="page-title">Page not found</h1>
      <p><a class="link" href="{SITE_URL}/index.html">Back to the portfolio</a></p>
    </div>"""
    (OUT / "404.html").write_text(page(site, "Not found", "Page not found.", body, None, prefix=SITE_URL + "/"),
                                  encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "projects").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")

    site, about = load("site"), load("about")
    projects, seen = [], set()
    for p in load("projects").get("projects") or []:
        if not isinstance(p, dict) or not s(p.get("title")):
            continue
        slug = base = slugify(plain(p["title"]))
        n = 2
        while slug in seen:  # two projects with the same title
            slug, n = f"{base}-{n}", n + 1
        seen.add(slug)
        p["slug"] = slug
        p["cover_info"] = image(p.get("cover")) or next(
            (i for i in (image(r) for r in as_list(p.get("images"))) if i), None)
        projects.append(p)

    build_home(site, projects)
    for n in range(len(projects)):
        build_project(site, projects, n)
    build_about(site, about)
    build_contact(site)
    build_404(site)
    print(f"Built {len(projects)} projects, {sum(1 for v in _images.values() if v)} photos into {OUT.relative_to(ROOT)}/"
          + (f" with {len(warnings)} warning(s)" if warnings else ""))


if __name__ == "__main__":
    main()
