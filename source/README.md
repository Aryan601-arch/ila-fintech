# Ila Fintech website: source

The finished website is built from these files.

| File | What it holds |
| --- | --- |
| `site-config.json` | Company details: name, phone, email, address, hours, social links, WhatsApp, form settings, logo, domain |
| `build.py` | Page text and layout for every page |
| `base.css`, `extra.css` | Styles (joined into `css/styles.css`) |
| `main.js` | Menu, slider, animations and form sending |
| `images/` | Photos (see `images/CREDITS.txt`). `images/brand/` holds the logo and browser-tab icons |

## Change something

On GitHub: open the file, click the pencil icon, make the change and click **Commit changes**.
The website rebuilds and goes live by itself within a few minutes (progress is under the **Actions** tab).

On your own computer: run `python3 build.py`. The website is written to `../site/`, and the build
lists any details that are still placeholders. Pillow (`pip install pillow`) is only needed to redraw the PNG icons.

## Forms

Contact, quote, callback and job forms send through FormSubmit to `form_email` (or `email` if empty).
The first message sent after launch triggers an activation email to that address. Click the link once.
Job applications go to `careers_email`, which needs its own one-time activation.
To use Web3Forms instead, paste a free access key from web3forms.com into `web3forms_key`.
If sending fails, visitors see your email address and phone number instead.

## Your own domain

Set `domain` to your address (for example `https://www.ilafintech.com`). The build then adds the
`CNAME` file GitHub Pages needs. Point your domain's DNS at GitHub Pages (a `CNAME` record for `www`
pointing to `aryan601-arch.github.io`), then tick **Enforce HTTPS** under Settings → Pages.
