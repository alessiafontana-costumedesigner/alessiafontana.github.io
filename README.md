# alessiafontana.github.io

Portfolio website of Alessia Fontana, costume designer.

**Live site:** https://alessiafontana-costumedesigner.github.io/alessiafontana.github.io/

- **Part 1** is for Alessia: how to change texts and photos from the browser, with no code.
- **Part 2** is the technical side: how the site is built, local preview, one-time setup.

---

## Part 1: Editing the website (no code needed)

All changes are made at **[app.pagescms.org](https://app.pagescms.org)**, a free editor that works in the browser.

### Open the editor

1. Go to **https://app.pagescms.org**.
2. Click **Sign in with GitHub** and log in with the `alessiafontana-costumedesigner` account.
3. Click the **alessiafontana.github.io** repository.

In the left menu there are three sections:

| Section | What you can change |
| --- | --- |
| **Projects** | Every project: title, year, description, cover, photos, video, backstage photos, order on the home page |
| **About page** | Introduction, biography, photo, selected projects, education |
| **Contact & site info** | Email, Instagram, city, contact text, the name and role at the top of each page |

### Save and publish

Click **Save** at the top right after making changes. The site updates automatically after
**about 2 minutes**. Refresh the website to see them (on a computer: `Cmd + Shift + R`;
on a phone: close and reopen the page).

### Change a text

Open the section, click the field, type, then **Save**.

- To write a title in *italics*, put asterisks around it: `*The End*, short film`.
- Text written inside `[square brackets]` shows up on the site with a light blue highlight. It marks
  something still to fill in. Replace it with the real text and remove the brackets.
- In the biography, leave an **empty line** between paragraphs.
- Leaving a field empty hides it on the site (for example the Instagram row or the year).

### Add photos to a project

1. **Projects** → click the project to open it.
2. Under **Gallery photos** (or **Backstage photos**), click **Add** and upload the photos from your
   computer or phone. Photos straight from the phone are fine: they are resized automatically.
3. Drag the photos to change their order.
4. **Save**.

To **remove** a photo from a project, delete it from the list and **Save**. This hides it from the
site; the file itself stays in the **Media** library in case you want it again.

### Add a new project

1. **Projects** → **Add an entry** at the bottom of the list.
2. Fill in **Title**, **Category** (e.g. *Short film*), **Subtitle**, **Year**, **Description**.
3. Upload the **Gallery photos** and choose a **Cover photo** (the image shown on the home page).
4. Choose a **Gallery layout**:
   - *One large photo per row*: for wide images or pages of a book
   - *Two photos per row*: for film stills
   - *Three photos per row*: for portrait photos, e.g. runway looks
5. **Save**.

### Change the order of projects on the home page

**Projects** → drag the projects up or down. The first one appears at the top left. **Save**.

### Change the cover crop

On the home page, covers are cropped to a landscape shape. If a face or detail gets cut off,
change **Cover framing** in that project (*Keep the top* works well for portrait photos).

### Add a video

Videos must be **MP4** files, short (a few seconds to a minute) and ideally under 50 MB.
Upload it in the project's **Video clip** field. It plays silently on a loop, after the photos.

### If something goes wrong

- **The change doesn't appear:** wait 2–3 minutes and refresh the page.
- **Undo a mistake:** every save is kept in the history, so an older version can always be restored.
  Ask Niccolò.
- **The site still shows the old version after 10 minutes:** a photo may be in an unsupported format.
  Ask Niccolò to check the **Actions** tab on GitHub.

---

## Part 2: Technical notes

### How it works

```
content/projects.yml, about.yml, site.yml   all texts and photo choices (edited by Pages CMS)
images/                                      photos, organized by project
videos/                                      video clips (MP4)
assets/css/style.css, assets/js/main.js      design and behavior (image viewer, fade-in)
tools/build.py                               builds the site into _site/ (resizes photos, writes HTML)
tools/serve.py                               local preview server
.pages.yml                                   defines the Pages CMS editing forms
.github/workflows/deploy.yml                 builds and publishes on every push to main
media/                                       original full-size photos (local only, not uploaded)
```

Every push to `main` (including each **Save** in Pages CMS) triggers the GitHub Action, which runs
`tools/build.py` and publishes `_site/` to GitHub Pages. The generated HTML is not committed.

The build resizes photos to at most 2000px plus a 900px thumbnail, converts PNG, HEIC and WebP
to JPEG, and fixes phone-camera rotation. A missing or unreadable photo is skipped with a warning
in the Action log, so one bad file doesn't take the site down.

### One-time setup

1. **Publish with GitHub Actions.** Repository **Settings → Pages → Build and deployment → Source**:
   choose **GitHub Actions**. This needs an admin of the repository (the
   `alessiafontana-costumedesigner` account).
2. **Install Pages CMS.** Sign in at https://app.pagescms.org with the
   `alessiafontana-costumedesigner` account. When asked, install the **Pages CMS GitHub App** and
   give it access to the `alessiafontana.github.io` repository.

### Preview locally

You need Python 3 (included with macOS). The first time only, from the project folder:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then, every time:

```sh
.venv/bin/python tools/build.py     # build the site into _site/
python3 tools/serve.py              # serve it at http://localhost:8000
```

Run `build.py` again after each change, then refresh the browser. Press `Ctrl + C` to stop the server.
If Alessia has made changes in Pages CMS, run `git pull` first.

> Use `tools/serve.py` rather than `python3 -m http.server`. Python's built-in server can't stream video,
> so the clip on *The End* never loads in Chrome, and with it browsers cache pages, which hides your changes.
> To use a different port: `python3 tools/serve.py 8080`.

### Change the look

Colors and fonts are defined at the top of `assets/css/style.css` (`--paper`, `--ink`, `--accent`, …).
Page structure is in the templates inside `tools/build.py`.

### Notes

- If the repository is renamed, the address changes too. The build picks up the new address
  automatically from the Pages settings.
- `media/` (the full-size originals, about 400MB) is listed in `.gitignore` and is **never uploaded**.
  Keep a backup of that folder somewhere safe (it only exists on this computer).
- To use a custom domain (e.g. `alessiafontana.com`), add it under **Settings → Pages → Custom domain**
  and follow GitHub's DNS instructions.
