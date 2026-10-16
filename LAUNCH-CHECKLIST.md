# Ila Fintech website: launch checklist

The site is live at https://aryan601-arch.github.io/ila-fintech/ and every page, button and form works.
These items still need your real details.

## 1. Your details
Edit `source/site-config.json` on GitHub (pencil icon, then **Commit changes**). The site updates by itself.
- [ ] Phone number (`phone` and `phone_link`)
- [ ] Email addresses (`email`, `careers_email`)
- [ ] Office address, map search text and office hours
- [ ] WhatsApp number (shows a chat button when filled in)
- [ ] Facebook, Instagram, LinkedIn and other profile links (hidden until filled in)
- [x] Your logo (added). If your designer has the original file (SVG or a large PNG), replace the files in `source/images/brand/` for a sharper logo

## 2. Words and photos to check
- [ ] Company story on the Home and About pages
- [ ] Promises you are happy to keep: free first consultation, quote within two working days, reply within one working day, fixed prices
- [ ] Services, solutions and budget ranges on the quote form
- [ ] Replace stock photos with your own team, office and project photos where you can
- [ ] Add real projects and client reviews once you have permission (left out so nothing is invented)
- [ ] Have someone review the Privacy Policy and Terms of Use

## 3. Forms
- [ ] After your real email is in, send a test message from the Contact page and click the FormSubmit activation email
- [ ] Do the same from the Careers page for the careers address

## 4. Your own domain (optional)
- [ ] Get a domain: .com from any registrar, or a free .com.np (such as ilafintech.com.np) for Nepali businesses at register.com.np
- [ ] Set `domain` in `source/site-config.json` to it, e.g. https://www.ilafintech.com
- [ ] In your domain's DNS, add a `CNAME` record for `www` pointing to `aryan601-arch.github.io`
- [ ] In the repository, go to Settings → Pages and tick **Enforce HTTPS**

## 5. After launch
- [ ] Add the site to Google Search Console and submit `sitemap.xml`
- [ ] Add the website link to your Google Business Profile and Facebook page
