# Ila Fintech website

**Live site:** https://aryan601-arch.github.io/ila-fintech/

The company website for Ila Fintech, an IT company in Kathmandu, Nepal. It has 13 pages:
Home, About, Services, Solutions, Blog (3 articles), Contact, Careers, Privacy Policy, Terms of Use and a page-not-found page.

## Update the website

1. Open [`source/site-config.json`](source/site-config.json) and click the pencil icon.
2. Change your phone number, email, address, social links or anything else.
3. Click **Commit changes**.

The website rebuilds and goes live by itself within a few minutes. You can follow it under the **Actions** tab.
Page text lives in [`source/build.py`](source/build.py). See [`source/README.md`](source/README.md) for details.

Before launch, work through [LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md).

## Open it in VS Code

1. Install Python 3 from python.org. On Windows, tick **Add python.exe to PATH** in the installer.
2. In VS Code, choose **File → Open Folder** and pick the `ila-fintech` folder.
3. Open a terminal (**Terminal → New Terminal**) and run `pip install pillow` once. It is optional, but it
   clears the yellow underline VS Code shows on `build.py` and sets the logo's exact size.
4. Run `python source/build.py` (on a Mac, `python3 source/build.py`). The website is written to `site/`.
5. Open `site/index.html` in your browser, or right-click it and choose **Open with Live Server** if you have
   the Live Server extension.

The `site/` folder stays on your computer and is not uploaded. GitHub builds its own copy from `source/`.

## How it is published

| Branch | Holds |
| --- | --- |
| `main` | The source files you edit |
| `gh-pages` | The finished website, rebuilt automatically from `main`. Do not edit it by hand. |

GitHub Pages serves the `gh-pages` branch. To host somewhere else, such as cPanel, download the
`gh-pages` branch as a ZIP and upload its contents to `public_html`.
