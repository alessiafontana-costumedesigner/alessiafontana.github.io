# alessiafontana.github.io

Portfolio website of Alessia Fontana, costume designer.
It's a plain static site (HTML, CSS and a little JavaScript), with no frameworks and nothing to install beyond Python 3, which comes with macOS.

```
index.html, about.html, contact.html, 404.html     generated pages (don't edit by hand)
projects/*.html                                    generated project pages
assets/css/style.css                               all styling (colors, fonts, spacing)
assets/js/main.js                                  image viewer + fade-in on scroll
assets/img/                                        web-sized photos (generated)
assets/video/                                      web-sized video
tools/build_pages.py                               ALL the site's text + page templates
tools/optimize_media.py                            makes web-sized photos from media/
tools/serve.py                                     local preview server
media/                                             original full-size photos (not uploaded)
```

---

## 1. Edit the website

### Change text (bio, credits, email, Instagram…)

All the text lives at the top of **`tools/build_pages.py`**:

- `EMAIL`, `INSTAGRAM_HANDLE`, `INSTAGRAM_URL`, `CITY`: contact details (also used in the footer)
- `ABOUT_LEAD`, `ABOUT_PARAGRAPHS`, `SELECTED_PROJECTS`, `EDUCATION`: the About page
- `PROJECTS`: every project's title, description (`intro`), credits (director, year…), cover image and layout

Anything written in `[square brackets]` is a **placeholder**. It appears on the site with a light blue dashed highlight so it's easy to spot. Replace it with real text and remove the brackets.
Wrap a title in `*asterisks*` to set it in italics.

After editing, rebuild the pages by running this from the project folder:

```sh
python3 tools/build_pages.py
```

> Don't edit the `.html` files directly. They are overwritten every time you run the build.

### Add or change photos

1. Put the original photos in the right folder inside `media/`.
   The folders each project uses are listed in `PROJECTS` at the top of `tools/optimize_media.py`.
2. Make the web-sized copies (about 2000px and 900px versions, a few hundred KB each):
   ```sh
   python3 tools/optimize_media.py
   ```
3. Rebuild the pages:
   ```sh
   python3 tools/build_pages.py
   ```

Photos appear in alphabetical order by original file name.

### Add a new project

1. Create a folder for it in `media/` with its photos (plus a sub-folder for backstage photos if you have them).
2. In `tools/optimize_media.py`, add a line to `PROJECTS`, for example `"new-project": {"gallery": "MY FOLDER", "backstage": "MY FOLDER/Backstage"},`
3. In `tools/build_pages.py`, add a matching entry to `PROJECTS`.
   Copy an existing one and change `slug` (it must match the name used in step 2), `title`, `kind`, `cover`, `intro`, `credits` and `layouts`.
4. Run both commands from the section above.

### Change the look

Colors and fonts are defined at the top of `assets/css/style.css` (`--paper`, `--ink`, `--accent`, …).
No rebuild is needed after CSS changes; just refresh the browser.

---

## 2. See the website on your computer (localhost)

From the project folder, start the preview server:

```sh
python3 tools/serve.py
```

Then open **http://localhost:8000** in your browser. 
Refresh the page after each change (and after running `build_pages.py`). Press `Ctrl + C` in the terminal to stop the server.

> Use `tools/serve.py` rather than `python3 -m http.server`. Python's built-in server can't stream video
> (the clip on *The End* never loads in Chrome), and with it browsers cache pages, which hides your changes.
> To use a different port: `python3 tools/serve.py 8080`.

---

## 3. Publish online (GitHub Pages)

The site is hosted for free by GitHub Pages at
**https://alessiafontana-costumedesigner.github.io/alessiafontana.github.io/**.

### First time only

1. The repository is `alessiafontana.github.io` on the GitHub account `alessiafontana-costumedesigner`.
   For the shorter address **https://alessiafontana-costumedesigner.github.io**, rename the repository
   to `alessiafontana-costumedesigner.github.io` (Settings → General), then update `SITE_URL` in
   `tools/build_pages.py` and rebuild.
2. Push the code (see below).
3. On GitHub, open the repository and go to **Settings → Pages**.
   Under *Build and deployment*, choose **Source: Deploy from a branch**, **Branch: `main`**, folder **`/ (root)`**, then **Save**.
4. After a minute or two the site is live. The address is shown at the top of the Pages settings.

### Every time you make changes

```sh
python3 tools/build_pages.py        # if you changed text or photos
git add -A
git commit -m "Describe what you changed"
git push
```

GitHub republishes the site automatically within a minute or two. 
If you don't see the change, do a hard refresh (`Cmd + Shift + R`).

### Notes

- `media/` (the full-size originals, about 400MB) is listed in `.gitignore` and is **never uploaded**:
  GitHub rejects files over 100MB, and the originals would make the site very slow. 
  Keep a backup of that folder somewhere safe (it only exists on this computer).
- `.nojekyll` tells GitHub to serve the files as they are, without processing them.
- To use a custom domain (e.g. `alessiafontana.com`), add it under **Settings → Pages → Custom domain** and follow GitHub's DNS instructions.
