# Ila Infotech website

**Live site:** https://aryan601-arch.github.io/ila-fintech/

The company website for Ila Infotech, an IT company in Kathmandu, Nepal. It has 13 pages:
Home, About, Services, Solutions, Blog (3 articles), Contact, Careers, Privacy Policy, Terms of Use and a page-not-found page.

## Update the website

1. Open [`source/site-config.json`](source/site-config.json) and click the pencil icon.
2. Change your phone number, email, address, social links or anything else.
3. Click **Commit changes**.

The website rebuilds and goes live by itself within a few minutes. You can follow it under the **Actions** tab.
Page text lives in [`source/build.py`](source/build.py). See [`source/README.md`](source/README.md) for details.

Before launch, work through [LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md).

## How it is published

| Branch | Holds |
| --- | --- |
| `main` | The source files you edit |
| `gh-pages` | The finished website, rebuilt automatically from `main`. Do not edit it by hand. |

GitHub Pages serves the `gh-pages` branch. To host somewhere else, such as cPanel, download the
`gh-pages` branch as a ZIP and upload its contents to `public_html`.
