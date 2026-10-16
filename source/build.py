#!/usr/bin/env python3
"""Build the company website.

    python3 build.py                 # writes the finished site to ../site
                                     # (on GitHub this runs by itself on every change)
    python3 build.py --out DIR       # writes it somewhere else
    python3 build.py --preview DIR   # preview copy for the claude.ai artifact (forms do not send)

All company details (phone, email, address, social links, form settings) come from
site-config.json. Page text lives in this file; edit it here and rebuild.
"""
import argparse
import datetime
import html
import json
import re
import shutil
import urllib.parse
from pathlib import Path

SRC = Path(__file__).resolve().parent
BRAND = SRC / 'images' / 'brand'  # optional: your own favicon-32.png, apple-touch-icon.png and icon-512.png
BRAND_ICONS = (BRAND / 'favicon-32.png').exists()
TODAY = datetime.date.today()


def e(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- icons
ICON_PATHS = {
    'web': '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M3 9h18"/>',
    'apps': '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    'software': '<path d="m8 7-5 5 5 5M16 7l5 5-5 5"/>',
    'ecommerce': '<path d="M6 6h15l-2 9H8L6 3H3"/><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/>',
    'design': '<path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.6 7.6"/><circle cx="11" cy="11" r="2"/>',
    'marketing': '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    'person': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    'headset': '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="2" y="14" width="5" height="7" rx="2"/><rect x="17" y="14" width="5" height="7" rx="2"/>',
    'trend': '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    'monitor': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    'star': '<path d="M12 2l3 6 6 1-4.5 4 1 6-5.5-3-5.5 3 1-6L3 9l6-1z"/>',
    'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    'pin': '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    'eye': '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    'heart': '<path d="M12 20s-8-4.5-8-11a5 5 0 0 1 8-4 5 5 0 0 1 8 4c0 6.5-8 11-8 11z"/>',
    'cap': '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
}


def icon(name, size=24):
    return (f'<svg width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" aria-hidden="true">{ICON_PATHS[name]}</svg>')


WHATSAPP_SVG = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>')

# ---------------------------------------------------------------- content
SERVICES = [
    dict(id='web', name='Web Development', icon='web', img='hero-code.jpg', alt='Website code on a developer screen',
         short='Professional, fast-loading websites that work on every device and show up on Google.',
         intro='Your website is often the first place a customer meets your business. We design and build fast, secure websites that work on every phone, are easy for your staff to update, and are set up to be found on Google.',
         ticks=['Custom design that matches your brand', 'Mobile-friendly pages that load quickly', 'Easy content editing for your team',
                'Contact forms, maps and WhatsApp chat buttons', 'Basic SEO and Google Business Profile setup', 'Domain, hosting and SSL certificate setup'],
         good='companies, schools, clinics, hotels, NGOs and startups.'),
    dict(id='apps', name='App Development', icon='apps', img='service-app.jpg', alt='A smartphone lying on a yellow desk',
         short='Android and iOS apps for bookings, orders, school updates and more.',
         intro='Apps that let your customers book, order, pay or stay updated from their phone. We take care of design, development, testing and publishing to the Play Store and App Store.',
         ticks=['Android and iOS apps from one codebase', 'Push notifications for offers and alerts', 'eSewa, Khalti and card payments',
                'Admin panel to manage content and users', 'Play Store and App Store publishing', 'Updates and fixes after launch'],
         good='schools, restaurants, delivery services, clinics and membership businesses.'),
    dict(id='software', name='Software Development', icon='software', img='project-hospital.jpg', alt='A person working on business software at a laptop',
         short='Billing, inventory, HR and hospital systems designed around how you work.',
         intro='Custom systems for the work your team does every day: billing, stock, staff, patients or students. We study how you work first, then build the software around it instead of forcing you into a template.',
         ticks=['Billing, invoicing and accounts', 'Inventory and purchase management', 'HR, attendance and payroll',
                'Hospital, clinic and school systems', 'Separate access levels for each staff role', 'Reports you can export to Excel and PDF'],
         good='growing businesses that have outgrown spreadsheets.'),
    dict(id='ecommerce', name='eCommerce Solutions', icon='ecommerce', img='project-store.jpg', alt='A laptop on a desk ready for online shopping',
         short='Online stores with eSewa, Khalti and card payments, plus stock management.',
         intro='Online stores that are simple for customers to buy from and simple for you to run. Take payments by eSewa, Khalti, card or cash on delivery, and manage orders and stock in one place.',
         ticks=['Product catalogue with sizes, colours and stock', 'eSewa, Khalti, card and cash on delivery', 'Order tracking with SMS or email updates',
                'Discount codes and seasonal offers', 'Delivery charges by area', 'Daily and monthly sales reports'],
         good='shops, brands, wholesalers and home businesses selling online.'),
    dict(id='design', name='Graphic Design', icon='design', img='service-design.jpg', alt='Branding and print design samples laid out on a wooden table',
         short='Logos, brand identity, social media posts and print materials.',
         intro='A clear, consistent brand makes a business look established. We design logos, brand guides, social media posts and print materials that look right wherever you use them.',
         ticks=['Logo and brand identity', 'Brand colours and font guide', 'Social media posts and ad designs',
                'Brochures, flyers and banners', 'Business cards and letterheads', 'Website and app interface design (UI/UX)'],
         good='new businesses, rebrands and marketing teams.'),
    dict(id='marketing', name='Digital Marketing', icon='marketing', img='blog-seo.jpg', alt='A person planning a marketing campaign on a laptop',
         short='SEO, Facebook and Google ads that bring real enquiries to your business.',
         intro='We help people find you online and turn visits into enquiries, with SEO, Google and Facebook ads and social media management. Each month you get a plain report of what was spent and what it brought in.',
         ticks=['Search engine optimisation (SEO)', 'Google Ads and Facebook & Instagram ads', 'Social media content and page management',
                'Google Business Profile setup and reviews', 'Email and SMS campaigns', 'A monthly results report'],
         good='businesses that want more calls, messages and walk-in customers.'),
]
SVC = {s['id']: s for s in SERVICES}

FEATURES = [
    ('person', 'Client-First Approach', 'You see progress every week and approve each step.'),
    ('headset', 'Quick Support', 'Real people answer when you call or message us.'),
    ('trend', 'After-Launch Care', 'Updates, backups and speed checks after you go live.'),
    ('monitor', 'Modern Technology', 'Built with tools that are fast, secure and easy to grow.'),
    ('star', 'Fair, Fixed Pricing', 'A clear quote before we start. No surprise bills.'),
]

SOLUTIONS = [
    dict(id='websites', cat='Web', title='Business Websites', img='blog-redesign.jpg', alt='A laptop showing a business website', svc='web',
         text='A professional website with your services, photos, contact form, map and WhatsApp button, which your staff can update themselves.',
         points=['Pages for services, team and gallery', 'Enquiry form and click-to-call', 'Google Maps and Business Profile', 'News or blog section']),
    dict(id='store', cat='eCommerce', title='Online Stores', img='project-store.jpg', alt='A laptop on a desk ready for online shopping', svc='ecommerce',
         text='Sell online with local payment options, delivery tracking and stock that updates itself as orders come in.',
         points=['Product catalogue and stock', 'eSewa, Khalti and card payments', 'Order and delivery tracking', 'Sales reports']),
    dict(id='school', cat='Education', title='School Management & Parent App', img='project-school.jpg', alt='A developer building a school app', svc='software',
         text='Attendance, fees, exam results and notices in one system, with an app that keeps parents informed.',
         points=['Student records and attendance', 'Fee billing and reminders', 'Exam results and report cards', 'Notices sent to parents\u2019 phones']),
    dict(id='hospital', cat='Healthcare', title='Hospital & Clinic Management', img='project-hospital.jpg', alt='A person using a laptop at work', svc='software',
         text='Patient records, appointments, billing, lab and pharmacy in one easy system for front desk and doctors.',
         points=['Patient registration and history', 'Appointments and queue display', 'Billing, lab and pharmacy', 'Daily and monthly reports']),
    dict(id='billing', cat='Retail & Wholesale', title='Billing & Inventory Software', img='blog-software.jpg', alt='An office team working at their screens', svc='software',
         text='Fast counter billing and stock control for shops, distributors and multi-branch businesses.',
         points=['Quick billing with barcode scanning', 'Low-stock alerts and purchase orders', 'Several branches or counters', 'Profit and sales reports']),
    dict(id='booking', cat='Hotels, Salons & Services', title='Booking & Appointment Systems', img='hero-office.jpg', alt='An office team at their desks', svc='web',
         text='Let customers book rooms, tables, classes or appointments online, and keep your staff schedule in one place.',
         points=['Online booking calendar', 'Deposit or full payment at booking', 'SMS and email reminders', 'Staff and room schedules']),
]

STEPS = [
    ('Free', 'Consultation', 'We listen to what you need, look at what you already have and suggest the simplest way to get there.'),
    ('Fixed price', 'Plan & Quote', 'You get a written scope, timeline and fixed price before any work starts.'),
    ('Weekly updates', 'Design & Build', 'We share progress every week so you can review, comment and approve each step.'),
    ('After launch', 'Launch & Support', 'We go live, train your team and stay on for updates, backups and fixes.'),
]

INDUSTRIES = ['Schools & Colleges', 'Hospitals & Clinics', 'Retail & eCommerce', 'Hotels & Travel', 'Restaurants & Cafés',
              'NGOs & INGOs', 'Cooperatives & Finance', 'Real Estate', 'Manufacturing', 'Startups']

POSTS = [
    dict(slug='blog-website-redesign', cat='Website Tips', mins=5, img='blog-redesign.jpg', alt='A laptop on a wooden desk', svc='web',
         title='5 signs your business website needs a redesign',
         summary='Slow loading, poor mobile view and no enquiries? Here is what to fix first.',
         body='''
<p>Your website should be working for you day and night. If it was built a few years ago, it may be quietly turning customers away instead. Here are five signs it is time for a refresh, and what to fix first.</p>
<h2>1. It is hard to use on a phone</h2>
<p>Most visitors will see your site on a phone. If they have to pinch and zoom, or the buttons are too small to tap, many will simply leave. Try this test: open your site on your own phone and see whether you can find your phone number in under ten seconds.</p>
<h2>2. It loads slowly</h2>
<p>Large photos, old plugins and cheap hosting all slow a site down. A page that takes more than a few seconds to appear loses visitors before they read a word. Free tools such as Google PageSpeed Insights show exactly what is holding your pages back.</p>
<h2>3. The information is out of date</h2>
<p>Old prices, a branch that has closed, staff who have left or a copyright line from years ago all tell visitors that nobody is looking after the business. People notice, and it makes them less likely to get in touch.</p>
<h2>4. It does not bring in enquiries</h2>
<p>A business website has one main job: making it easy to contact you. That means a clear phone number, a short form, a WhatsApp button and a map. If people visit but nobody calls, the path from reading to contacting you is probably not clear enough.</p>
<h2>5. You cannot update it yourself</h2>
<p>If changing a price or adding a photo means waiting days for a developer, the site will always fall behind. A modern website lets your own staff make everyday changes in a few minutes.</p>
<h2>What to fix first</h2>
<p>Start with mobile and speed, because they affect every visitor. Then make your contact options obvious on every page. Finally, update your text and photos so they match the business you run today. A redesign does not always mean starting from scratch; sometimes a new design on your existing content is enough.</p>
'''),
    dict(slug='blog-local-seo-nepal', cat='Digital Marketing', mins=6, img='blog-seo.jpg', alt='A person working at a laptop, seen from above', svc='marketing',
         title='How local businesses in Nepal can rank on Google',
         summary='Simple SEO steps any shop, clinic or school can start this week.',
         body='''
<p>When someone nearby searches for "dental clinic in Lalitpur" or "laptop repair in Putalisadak", Google shows a map with three businesses at the top. Getting into that list is called local SEO, and most of it is free. These are the steps we recommend to every local business.</p>
<h2>1. Claim your Google Business Profile</h2>
<p>Search for your business on Google Maps. If it is there, claim it; if not, add it. Fill in every field: category, phone number, opening hours, website and real photos of your shop or office. Many streets in Kathmandu Valley have no official name, so place the map pin carefully and mention a nearby landmark or chowk in your address.</p>
<h2>2. Ask happy customers for reviews</h2>
<p>Reviews are one of the strongest signals Google uses for local results. Ask satisfied customers to leave one, and send them a direct link so it takes less than a minute. Reply politely to every review, including the bad ones.</p>
<h2>3. Use the words your customers search for</h2>
<p>Think about how people actually search: the service plus the area. Use those phrases naturally in your page titles, headings and text. Some customers search in Nepali or in romanised Nepali, so it can help to include common terms in both.</p>
<h2>4. Keep your details the same everywhere</h2>
<p>Your business name, address and phone number should match exactly on your website, Google profile, Facebook page and any directories. Small differences confuse Google and customers alike.</p>
<h2>5. Make your website fast and mobile-friendly</h2>
<p>Google favours sites that work well on phones. A slow, hard-to-read site will struggle to rank, however good your business is.</p>
<h2>6. Keep posting</h2>
<p>Add updates, offers and photos to your Google profile, and publish useful articles on your website. Fresh activity shows Google that the business is open and active.</p>
<h2>How long does it take?</h2>
<p>Local SEO usually takes a few weeks to a few months to show results, depending on your area and competition. Be careful with anyone who promises the number one spot: nobody can guarantee it.</p>
'''),
    dict(slug='blog-custom-vs-ready-software', cat='Software', mins=5, img='blog-software.jpg', alt='An office team working at their screens', svc='software',
         title='Do you need custom software or a ready-made tool?',
         summary='A plain guide to choosing what fits your budget and your team.',
         body='''
<p>Sooner or later every growing business hits the limit of spreadsheets and paper registers. The next question is whether to buy a ready-made tool or have software built for you. Both can be the right answer.</p>
<h2>When a ready-made tool is the better choice</h2>
<ul>
<li>Your process is standard, such as basic accounting, email or team chat.</li>
<li>Your budget is small and you need something working this week.</li>
<li>A popular tool already does at least 80 percent of what you need.</li>
</ul>
<p>The trade-offs: monthly fees that are often charged in dollars, features you will never use, and gaps for local needs such as Bikram Sambat (BS) dates, Nepali VAT invoice formats or eSewa and Khalti payments.</p>
<h2>When custom software makes more sense</h2>
<ul>
<li>The way you work is part of what makes your business different.</li>
<li>Your staff copy the same data between several tools or spreadsheets.</li>
<li>You need BS dates, Nepali formats or local payment gateways built in.</li>
<li>You want to own the system and the data instead of renting them.</li>
</ul>
<h2>The middle path</h2>
<p>You do not have to choose one or the other. Many businesses use a ready-made tool for the standard parts and have a small custom system built for the part that is unique, connected so the data flows between them.</p>
<h2>Questions to ask before you decide</h2>
<ol>
<li>Which task costs your team the most time each week?</li>
<li>How many people will use the system, and on which devices?</li>
<li>What will it cost over three years, including subscriptions and training?</li>
<li>Who will you call when something stops working?</li>
</ol>
<p>Answer these honestly and the right choice usually becomes clear.</p>
'''),
]

NAV = [('index.html', 'Home'), ('about.html', 'About'), ('services.html', 'Services'),
       ('solutions.html', 'Solutions'), ('blog.html', 'Blog'), ('contact.html', 'Contact')]


# ---------------------------------------------------------------- builder
class Site:
    def __init__(self, cfg, preview):
        self.c = cfg
        self.preview = preview
        self.domain = cfg['domain'].rstrip('/')
        self.base_path = urllib.parse.urlparse(self.domain).path.rstrip('/') + '/'  # "/" on your own domain, "/repo/" on GitHub Pages
        self.form_email = cfg.get('form_email') or cfg['email']
        self.pages = []  # (filename, html, in_sitemap)

    # -- small pieces
    def tel(self, text=None):
        c = self.c
        return f'<a href="tel:{e(c["phone_link"])}">{e(text or c["phone"])}</a>'

    def mail(self, addr=None):
        addr = addr or self.c['email']
        return f'<a href="mailto:{e(addr)}">{e(addr)}</a>'

    def maps_url(self):
        return 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote_plus(self.c['map_query'])

    @staticmethod
    def img_size(src, height):
        """width/height attributes for an image shown at a fixed height, so the page doesn't jump while it loads."""
        try:
            from PIL import Image
            w, h = Image.open(SRC / src).size
            return f' width="{round(w * height / h)}" height="{height}"'
        except Exception:
            return f' height="{height}"'

    def logo(self, footer=False):
        c = self.c
        small_style = ' style="color:var(--on-dark)"' if footer else ''
        src = (c.get('logo_dark') or c.get('logo')) if footer else c.get('logo')
        if src:
            return f'<a href="index.html" class="logo"><img src="{e(src)}" alt="{e(c["name"])}"{self.img_size(src, 40 if footer else 44)}></a>'
        return (f'<a href="index.html" class="logo"><span class="mark" aria-hidden="true">IL</span>'
                f'<span>{e(c["name"])}<small{small_style}>{e(c["tagline"])}</small></span></a>')

    def social(self):
        labels = {'facebook': ('Facebook', 'f'), 'instagram': ('Instagram', 'ig'), 'linkedin': ('LinkedIn', 'in'),
                  'x': ('X (Twitter)', 'x'), 'youtube': ('YouTube', 'yt'), 'tiktok': ('TikTok', 'tt')}
        links = [f'<a href="{e(u)}" target="_blank" rel="noopener" aria-label="{labels[k][0]}">{labels[k][1]}</a>'
                 for k, u in self.c.get('social', {}).items() if u and k in labels]
        return f'<div class="social">{"".join(links)}</div>' if links else ''

    def org_jsonld(self):
        c = self.c
        data = {
            '@context': 'https://schema.org', '@type': 'ProfessionalService', 'name': c['name'],
            'url': self.domain + '/', 'image': self.domain + '/images/hero-team.jpg',
            'logo': self.domain + '/' + (c.get('logo') or 'apple-touch-icon.png'),
            'email': c['email'], 'telephone': c['phone_link'],
            'address': {'@type': 'PostalAddress', 'streetAddress': c['address'], 'addressLocality': c['city'], 'addressCountry': c['country']},
            'openingHours': c['opening_hours_schema'], 'areaServed': 'Nepal',
        }
        same = [u for u in c.get('social', {}).values() if u]
        if same:
            data['sameAs'] = same
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

    # -- layout
    def head(self, fn, title, desc, og_type='website', og_img='hero-team.jpg', extra=''):
        url = self.domain + '/' + ('' if fn == 'index.html' else fn)
        parts = []
        if not (self.preview and fn == 'index.html'):
            parts += ['<meta charset="utf-8">', '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">']
        if fn == '404.html' and not self.preview:
            parts.append(f'<base href="{e(self.base_path)}">')
        parts += [
            f'<title>{e(title)}</title>',
            f'<meta name="description" content="{e(desc)}">',
        ]
        if fn == '404.html':
            parts.append('<meta name="robots" content="noindex">')
        else:
            parts.append(f'<link rel="canonical" href="{e(url)}">')
        parts += [
            '<meta name="theme-color" content="#15191E">',
            f'<meta property="og:type" content="{og_type}">',
            f'<meta property="og:site_name" content="{e(self.c["name"])}">',
            f'<meta property="og:title" content="{e(title)}">',
            f'<meta property="og:description" content="{e(desc)}">',
            f'<meta property="og:url" content="{e(url)}">',
            f'<meta property="og:image" content="{e(self.domain)}/images/{og_img}">',
            '<meta name="twitter:card" content="summary_large_image">',
            *([] if BRAND_ICONS else ['<link rel="icon" href="favicon.svg" type="image/svg+xml">']),
            '<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">',
            '<link rel="apple-touch-icon" href="apple-touch-icon.png">',
        ]
        if not self.preview:
            parts.append('<link rel="manifest" href="site.webmanifest">')
        parts += [
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&amp;family=Open+Sans:wght@400;600&amp;display=swap">',
            '<link rel="stylesheet" href="css/styles.css">',
            '<script src="js/main.js" defer></script>',
        ]
        if extra:
            parts.append(extra)
        return '\n'.join(parts)

    def header(self, active):
        c = self.c
        items = []
        for href, label in NAV:
            on = href == active
            items.append(f'<li><a href="{href}"' + (' class="active" aria-current="page"' if on else '') + f'>{label}</a></li>')
        items.append('<li class="menu-cta"><a href="contact.html#quote">Get a Free Quote</a></li>')
        return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="container">
  <div class="left"><span>✉ {self.mail()}</span><span>☎ {self.tel()}</span></div>
  <div class="right"><span>{e(c["hours"])}</span><span>{e(c["city"])}, Nepal</span></div>
</div></div>

<header class="header">
  <nav class="container" style="position:relative" aria-label="Main">
    {self.logo()}
    <ul class="menu" id="menu">
      {"".join(items)}
    </ul>
    <a href="contact.html#quote" class="btn btn-accent">Get a Quote</a>
    <button class="toggle" id="toggle" type="button" aria-expanded="false" aria-controls="menu">☰ Menu</button>
  </nav>
</header>'''

    def footer(self):
        c = self.c
        svc_links = ''.join(f'<li><a href="services.html#{s["id"]}">{s["name"]}</a></li>' for s in SERVICES)
        wa = ''
        if c.get('whatsapp'):
            digits = re.sub(r'\D', '', c['whatsapp'])
            wa = f'\n<a class="wa" href="https://wa.me/{digits}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{WHATSAPP_SVG}</a>'
        return f'''<footer>
  <div class="container">
    <div class="f-grid">
      <div>{self.logo(footer=True)}<p>We help businesses grow with websites, apps and software built and supported by one local team.</p>{self.social()}</div>
      <div><h4>Services</h4><ul>{svc_links}</ul></div>
      <div><h4>Company</h4><ul><li><a href="about.html">About Us</a></li><li><a href="solutions.html">Solutions</a></li><li><a href="blog.html">Blog</a></li><li><a href="careers.html">Careers</a></li><li><a href="contact.html">Contact</a></li></ul></div>
      <div><h4>Contact Info</h4><ul><li><a href="{e(self.maps_url())}" target="_blank" rel="noopener">{e(c["address"])}</a></li><li>{self.tel()}</li><li>{self.mail()}</li><li>{e(c["hours"])}</li></ul></div>
    </div>
    <div class="copyright"><span>© <span data-year>{TODAY.year}</span> {e(c["name"])}. All rights reserved.</span><span class="f-bottom-links"><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Use</a></span></div>
  </div>
</footer>
<button class="totop" id="totop" type="button" aria-label="Back to top">↑</button>{wa}'''

    def page_head(self, title, lead, crumbs):
        trail = '<li><a href="index.html">Home</a></li>'
        for href, label in crumbs[:-1]:
            trail += f'<li><a href="{href}">{e(label)}</a></li>'
        trail += f'<li aria-current="page">{e(crumbs[-1][1])}</li>'
        return f'''<section class="page-head"><div class="container">
  <nav aria-label="Breadcrumb"><ol class="crumbs">{trail}</ol></nav>
  <h1>{e(title)}</h1>
  <p>{e(lead)}</p>
</div></section>'''

    def cta(self, heading="Have a project in mind? Let's talk about it.",
            text='Book a free consultation and get a clear plan and quote within two working days.',
            label='Book a Free Consultation', href='contact.html#quote'):
        return f'''<section class="cta" style="padding-block:70px">
  <div class="container">
    <div><h2>{e(heading)}</h2><p>{e(text)}</p></div>
    <div class="right"><a href="{href}" class="btn btn-accent">{e(label)}</a></div>
  </div>
</section>'''

    @staticmethod
    def wrap_labels(h):
        return re.sub(r'(<label class="field[^"]*" for="[^"]+">)(.*?)(<(?:input|select|textarea))', r'\1<span>\2</span>\3', h)

    def add(self, fn, title, desc, active, main, og_type='website', og_img='hero-team.jpg', extra_head='', sitemap=True):
        main = self.wrap_labels(main)
        head = self.head(fn, title, desc, og_type, og_img, extra_head)
        body = f'{self.header(active)}\n\n<main id="main">\n{main}\n</main>\n\n{self.footer()}'
        if self.preview and fn == 'index.html':
            doc = f'{head}\n\n{body}\n'
        else:
            doc = f'<!doctype html>\n<html lang="en">\n<head>\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'
        self.pages.append((fn, doc, sitemap))

    # -- reusable blocks
    def features(self, sub='', title=''):
        cards = ''.join(f'<div class="feat aos"><div class="icon">{icon(i)}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in FEATURES)
        top = f'<div class="center aos" style="margin-bottom:46px"><span class="sub">{sub}</span><h2 class="title">{title}</h2></div>' if title else ''
        return f'<section class="features"><div class="container">{top}<div class="feat-grid">{cards}</div></div></section>'

    def process(self):
        steps = ''.join(f'<div class="step aos"><span class="when">{w}</span><h3>{t}</h3><p>{d}</p></div>' for w, t, d in STEPS)
        return f'''<section class="process">
  <div class="container">
    <div class="center aos"><span class="sub">How We Work</span><h2 class="title">Four clear steps from idea to launch</h2>
    <p class="lead">You always know what is happening, what it costs and what comes next.</p></div>
    <div class="steps">{steps}</div>
  </div>
</section>'''

    def industries(self):
        chips = ''.join(f'<span class="chip">{e(x)}</span>' for x in INDUSTRIES)
        dup = ''.join(f'<span class="chip" aria-hidden="true">{e(x)}</span>' for x in INDUSTRIES)
        return f'''<div class="industries"><div class="container">
  <p class="center" style="font:600 .95rem var(--head);color:var(--ink);margin-bottom:18px">Industries we work with</p>
  <div class="wrap"><div class="track">{chips}{dup}</div></div>
</div></div>'''

    def post_card(self, p, lazy=True):
        lz = ' loading="lazy"' if lazy else ''
        return (f'<a class="post aos" href="{p["slug"]}.html"><div class="pic"><img class="photo" src="images/{p["img"]}" alt="{e(p["alt"])}"'
                f'{lz} width="800" height="600"></div><p class="meta">{e(p["cat"])} · {p["mins"]} min read</p>'
                f'<h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p></a>')

    def sol_card(self, s):
        return (f'<a class="proj aos" href="solutions.html#{s["id"]}"><div class="pic"><img class="photo" src="images/{s["img"]}" alt="{e(s["alt"])}" loading="lazy" width="800" height="600"></div>'
                f'<div class="body"><span class="cat">{e(s["cat"])}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p><span class="more">See what\u2019s included →</span></div></a>')

    # -- pages
    def build_home(self):
        c = self.c
        svc_cards = ''.join(
            f'<div class="svc aos"><div class="icon">{icon(s["icon"])}</div><h3>{s["name"]}</h3><p>{s["short"]}</p>'
            f'<a href="services.html#{s["id"]}" class="more">Learn More<span class="sr"> about {s["name"]}</span> →</a></div>' for s in SERVICES)
        sols = ''.join(self.sol_card(s) for s in SOLUTIONS if s['id'] in ('store', 'hospital', 'school'))
        posts = ''.join(self.post_card(p) for p in POSTS)
        main = f'''<section class="hero" style="padding:0" aria-label="Highlights">
  <div class="container">
    <div class="slide">
      <div class="copy">
        <span class="kicker">Welcome to {e(c["name"])}</span>
        <h1>We build software that helps your business <span>grow</span></h1>
        <p>Websites, mobile apps and custom software for businesses in Nepal and abroad. Planned, built and supported by one local team.</p>
        <div class="btns"><a href="contact.html#quote" class="btn btn-accent">Get Started</a><a class="call" href="tel:{e(c["phone_link"])}">☎<span>Call us anytime<b>{e(c["phone"])}</b></span></a></div>
      </div>
      <img class="photo" src="images/hero-team.jpg" alt="A software team working together on laptops" width="800" height="600" fetchpriority="high">
    </div>
    <div class="slide" hidden>
      <div class="copy">
        <span class="kicker">Web &amp; App Development</span>
        <h2 class="h1">Your business online, <span>done right</span></h2>
        <p>Fast, secure websites and apps that look great on every phone and bring you real customers.</p>
        <div class="btns"><a href="services.html" class="btn btn-accent">Our Services</a><a href="solutions.html" class="btn btn-outline">View Solutions</a></div>
      </div>
      <img class="photo" src="images/hero-code.jpg" alt="Website code on a developer screen" loading="lazy" width="800" height="600">
    </div>
    <div class="slide" hidden>
      <div class="copy">
        <span class="kicker">Support You Can Count On</span>
        <h2 class="h1">We stay with you <span>after launch</span></h2>
        <p>Hosting, updates and quick help whenever something needs fixing. One call and we're on it.</p>
        <div class="btns"><a href="contact.html" class="btn btn-accent">Talk to Us</a><a href="about.html" class="btn btn-outline">About Us</a></div>
      </div>
      <img class="photo" src="images/hero-office.jpg" alt="An office team at their desks" loading="lazy" width="800" height="600">
    </div>
  </div>
  <div class="dots" id="dots"></div>
</section>

{self.features()}

<section id="about">
  <div class="container about-grid">
    <div class="collage aos">
      <img class="photo big" src="images/about-team.jpg" alt="Team members working in a shared office" loading="lazy" width="800" height="600">
      <img class="photo small" src="images/about-office.jpg" alt="A modern open-plan office" loading="lazy" width="800" height="600">
      <div class="years"><b>Local</b>Team based in<br>{e(c["city"])}</div>
    </div>
    <div class="aos">
      <span class="sub">About Company</span>
      <h2 class="title">Your trusted IT partner for every stage of growth</h2>
      <p>{e(c["name"])} is a {e(c["city"])}-based IT company that builds websites, mobile apps and business software for startups, schools, hospitals, shops and agencies. We take your idea from first sketch to a working product, then keep it running smoothly.</p>
      <ul class="checks">
        <li>Developers and designers in one team</li>
        <li>Clear timelines and fixed quotes</li>
        <li>Secure, mobile-friendly work</li>
        <li>Training for your staff</li>
      </ul>
      <a href="about.html" class="btn btn-brand">More About Us</a>
    </div>
  </div>
</section>

<div class="stats">
  <div class="container">
    <div><b data-count="6">6</b><span>Core services under one roof</span></div>
    <div><b data-count="100" data-suffix="%">100%</b><span>Mobile-friendly websites</span></div>
    <div><b data-count="1">1</b><span>Team from idea to launch</span></div>
    <div><b>Free</b><span>First consultation</span></div>
  </div>
</div>

<section id="services">
  <div class="container">
    <div class="center aos">
      <span class="sub">Our Services</span>
      <h2 class="title">IT solutions built around your business</h2>
      <p class="lead">From a simple business website to a full management system, we handle design, development, hosting and support.</p>
    </div>
    <div class="svc-grid">{svc_cards}</div>
  </div>
</section>

{self.cta()}

<section id="solutions">
  <div class="container">
    <div class="center aos">
      <span class="sub">What We Build</span>
      <h2 class="title">Ready-to-tailor solutions</h2>
      <p class="lead">Proven starting points that we shape around your business, so you get working software sooner.</p>
    </div>
    <div class="proj-grid">{sols}</div>
    <div class="section-foot"><a href="solutions.html" class="btn btn-brand">See All Solutions</a></div>
  </div>
</section>

{self.process()}

{self.industries()}

<section id="blog">
  <div class="container">
    <div class="center aos"><span class="sub">Our Blog</span><h2 class="title">Latest news and tips</h2></div>
    <div class="blog-grid">{posts}</div>
    <div class="section-foot"><a href="blog.html" class="btn btn-brand">Read the Blog</a></div>
  </div>
</section>

<div class="news" id="contact">
  <div class="container">
    <div><h3>Let's work together</h3><p>Leave your email and we'll get back to you within one working day.</p></div>
    <form data-form data-subject="Callback request" data-status="newsNote" novalidate>
      <span class="field-inline field"><label for="news-email" class="sr">Email address</label><input id="news-email" name="email" type="email" autocomplete="email" placeholder="Your email address" required></span>
      <span class="hp" aria-hidden="true"><label for="news-bot">Leave empty</label><input id="news-bot" name="botcheck" tabindex="-1" autocomplete="off"></span>
      <button class="btn btn-dark" type="submit">Send</button>
    </form>
    <p class="note form-status" id="newsNote" role="status" aria-live="polite"></p>
  </div>
</div>'''
        title = f'{c["name"]} Website' if self.preview else f'{c["name"]} | Websites, Apps & Software in {c["city"]}, Nepal'
        self.add('index.html', title,
                 f'{c["name"]} builds websites, mobile apps and custom business software for companies, schools, hospitals and shops in {c["city"]} and across Nepal.',
                 'index.html', main, extra_head=self.org_jsonld())

    def build_about(self):
        c = self.c
        mv = [('target', 'Our Mission', 'Help businesses in Nepal work better and reach more customers with reliable, well-made software.'),
              ('eye', 'Our Vision', 'To be the technology partner local businesses trust and recommend to their friends.'),
              ('heart', 'Our Values', 'Clear communication, fair pricing, careful work, and staying with our clients after launch.')]
        cards = ''.join(f'<div class="card aos"><div class="icon">{icon(i)}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in mv)
        main = f'''{self.page_head("About Us", "A Kathmandu IT company that plans, builds and looks after websites, apps and business software.", [("about.html", "About Us")])}

<section>
  <div class="container about-grid">
    <div class="collage aos">
      <img class="photo big" src="images/about-team.jpg" alt="Team members working in a shared office" width="800" height="600">
      <img class="photo small" src="images/about-office.jpg" alt="A modern open-plan office" loading="lazy" width="800" height="600">
      <div class="years"><b>Local</b>Team based in<br>{e(c["city"])}</div>
    </div>
    <div class="aos">
      <span class="sub">Who We Are</span>
      <h2 class="title">Technology that fits the way you work</h2>
      <p>{e(c["name"])} is an IT company in {e(c["city"])}, Nepal. We build websites, mobile apps and business software for companies, schools, hospitals, shops and organisations, and we look after them once they are live.</p>
      <p style="margin-top:14px">We work closely with every client. You talk directly with the people building your project, get a fixed quote before work starts, and see progress every week. When you need a change or something goes wrong, you call us and we fix it.</p>
      <ul class="checks">
        <li>Design, development and marketing in one team</li>
        <li>Plain-language advice, no jargon</li>
        <li>Fixed quotes and clear timelines</li>
        <li>Support and training after launch</li>
      </ul>
      <a href="contact.html#quote" class="btn btn-brand">Start a Project</a>
    </div>
  </div>
</section>

{self.features("Why Choose Us", "What working with us is like")}

<section>
  <div class="container">
    <div class="center aos"><span class="sub">What Drives Us</span><h2 class="title">Mission, vision and values</h2></div>
    <div class="mv">{cards}</div>
  </div>
</section>

{self.process()}

{self.cta()}'''
        self.add('about.html', f'About Us | {c["name"]}',
                 f'Learn about {c["name"]}, a {c["city"]} IT company building websites, apps and business software, and how we work with our clients.',
                 'about.html', main)

    def build_services(self):
        c = self.c
        blocks = []
        for i, s in enumerate(SERVICES):
            ticks = ''.join(f'<li>{e(t)}</li>' for t in s['ticks'])
            lazy = '' if i == 0 else ' loading="lazy"'
            blocks.append(f'''<article class="svc-detail" id="{s["id"]}">
  <div class="media aos"><img class="photo" src="images/{s["img"]}" alt="{e(s["alt"])}"{lazy} width="800" height="600"><div class="icon">{icon(s["icon"], 28)}</div></div>
  <div class="aos">
    <span class="sub">Service</span>
    <h2>{s["name"]}</h2>
    <p>{e(s["intro"])}</p>
    <ul class="ticks">{ticks}</ul>
    <p class="good-for"><b>Good for:</b> {e(s["good"])}</p>
    <a href="contact.html#quote-{s["id"]}" class="btn btn-brand">Get a Quote for {s["name"]}</a>
  </div>
</article>''')
        jump = ''.join(f'<a class="chip" href="#{s["id"]}">{s["name"]}</a>' for s in SERVICES)
        main = f'''{self.page_head("Our Services", "Design, development, hosting and marketing for businesses of every size. Pick one service or let us handle everything.", [("services.html", "Services")])}

<section style="padding-bottom:20px">
  <div class="container">
    <nav class="jump" aria-label="Services on this page">{jump}</nav>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {"".join(blocks)}
  </div>
</section>

{self.process()}

{self.cta()}'''
        self.add('services.html', f'Services | {c["name"]}',
                 'Web development, mobile apps, custom software, eCommerce, graphic design and digital marketing from one local team in Kathmandu.',
                 'services.html', main)

    def build_solutions(self):
        c = self.c
        cards = []
        for s in SOLUTIONS:
            pts = ''.join(f'<li>{e(p)}</li>' for p in s['points'])
            cards.append(f'''<article class="sol aos" id="{s["id"]}" style="scroll-margin-top:100px">
  <img class="photo" src="images/{s["img"]}" alt="{e(s["alt"])}" loading="lazy" width="800" height="600">
  <div class="body">
    <span class="cat">{e(s["cat"])}</span>
    <h3>{e(s["title"])}</h3>
    <p>{e(s["text"])}</p>
    <ul>{pts}</ul>
    <a href="contact.html#quote-{s["svc"]}" class="more">Ask about this solution →</a>
  </div>
</article>''')
        main = f'''{self.page_head("Solutions", "Proven starting points for common business needs, tailored to the way your business works.", [("solutions.html", "Solutions")])}

<section>
  <div class="container">
    <div class="center aos">
      <span class="sub">What We Build</span>
      <h2 class="title">Solutions for schools, clinics, shops and more</h2>
      <p class="lead">Each solution is set up for your business, with your branding, your workflow and your data. Tell us what you need and we will show you how it would work for you.</p>
    </div>
    <div class="sol-grid">{"".join(cards)}</div>
  </div>
</section>

{self.industries()}

{self.cta("Need something that isn't listed here?", "Most of our work is custom. Tell us the problem and we'll suggest the simplest way to solve it.", "Tell Us What You Need")}'''
        self.add('solutions.html', f'Solutions | {c["name"]}',
                 'Business websites, online stores, school and hospital management systems, billing and booking software built for businesses in Nepal.',
                 'solutions.html', main)

    def build_blog(self):
        c = self.c
        posts = ''.join(self.post_card(p, lazy=False) for p in POSTS)
        main = f'''{self.page_head("Blog", "Practical tips on websites, software and digital marketing for businesses in Nepal.", [("blog.html", "Blog")])}

<section>
  <div class="container">
    <div class="blog-grid" style="margin-top:0">{posts}</div>
  </div>
</section>

{self.cta("Want help putting these tips into practice?", "Tell us about your business and we'll suggest where to start.", "Contact Us", "contact.html")}'''
        self.add('blog.html', f'Blog | {c["name"]}', f'Practical tips on websites, software and digital marketing for businesses in Nepal, from the {c["name"]} team.',
                 'blog.html', main)

        for p in POSTS:
            others = ''.join(f'<li><a href="{o["slug"]}.html">{e(o["title"])}</a></li>' for o in POSTS if o is not p)
            s = SVC[p['svc']]
            ld = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['summary'],
                  'image': f'{self.domain}/images/{p["img"]}', 'datePublished': TODAY.isoformat(),
                  'author': {'@type': 'Organization', 'name': c['name']}, 'publisher': {'@type': 'Organization', 'name': c['name']},
                  'mainEntityOfPage': f'{self.domain}/{p["slug"]}.html'}
            main = f'''{self.page_head(p["title"], p["summary"], [("blog.html", "Blog"), (p["slug"] + ".html", p["title"])])}

<section>
  <article class="prose">
    <p class="meta">{e(p["cat"])} · {p["mins"]} min read · By the {e(c["name"])} team</p>
    <img class="photo" src="images/{p["img"]}" alt="{e(p["alt"])}" width="800" height="600">
    {p["body"].strip()}
    <div class="post-cta">
      <h2>Need help with this?</h2>
      <p>Our {s["name"].lower()} team can look at your situation and tell you what we would do first.</p>
      <a class="btn btn-brand" href="contact.html#quote-{s["id"]}">Talk to Our Team</a>
    </div>
    <div class="related">
      <h2>More from the blog</h2>
      <ul>{others}</ul>
      <p style="margin-top:12px"><a href="blog.html">← Back to all articles</a></p>
    </div>
  </article>
</section>'''
            self.add(p['slug'] + '.html', f'{p["title"]} | {c["name"]}', p['summary'], 'blog.html', main,
                     og_type='article', og_img=p['img'], extra_head='<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')

    def build_contact(self):
        c = self.c
        opts = '<option value="General enquiry" data-key="general">General enquiry</option>'
        opts += ''.join(f'<option value="{s["name"]}" data-key="{s["id"]}">{s["name"]}</option>' for s in SERVICES)
        opts += '<option value="Something else" data-key="other">Something else</option>'
        budgets = ['Not sure yet', 'Under Rs. 50,000', 'Rs. 50,000 to 2,00,000', 'Rs. 2,00,000 to 5,00,000', 'Above Rs. 5,00,000']
        bopts = ''.join(f'<option>{e(b)}</option>' for b in budgets)
        main = f'''{self.page_head("Contact Us", "Call, email or send us a message. We reply to every enquiry within one working day.", [("contact.html", "Contact")])}

<section>
  <div class="container contact-grid">
    <div>
      <span class="sub">Get In Touch</span>
      <h2 class="title">We'd love to hear about your project</h2>
      <p style="margin-bottom:26px">Whether you need a new website, an app or help with existing software, start with a free, no-obligation conversation.</p>
      <div class="info-cards">
        <div class="info-card"><div class="icon">{icon("phone")}</div><div><h3>Call us</h3>{self.tel()}</div></div>
        <div class="info-card"><div class="icon">{icon("mail")}</div><div><h3>Email us</h3>{self.mail()}</div></div>
        <div class="info-card"><div class="icon">{icon("pin")}</div><div><h3>Visit our office</h3><p>{e(c["address"])}</p><a href="{e(self.maps_url())}" target="_blank" rel="noopener">Open in Google Maps →</a></div></div>
        <div class="info-card"><div class="icon">{icon("clock")}</div><div><h3>Office hours</h3><p>{e(c["hours"])}</p></div></div>
      </div>
    </div>

    <div class="form-card" id="quote" style="scroll-margin-top:100px">
      <h2>Request a free quote</h2>
      <p>Tell us a little about what you need. Fields marked <span style="color:var(--primary)">*</span> are required.</p>
      <form data-form data-subject="Quote request" novalidate>
        <div class="form-grid">
          <label class="field" for="q-name">Full name <span class="req">*</span><input id="q-name" name="name" autocomplete="name" required></label>
          <label class="field" for="q-email">Email <span class="req">*</span><input id="q-email" name="email" type="email" autocomplete="email" required></label>
          <label class="field" for="q-phone">Phone<input id="q-phone" name="phone" type="tel" autocomplete="tel" placeholder="98XXXXXXXX"></label>
          <label class="field" for="q-company">Company or organisation<input id="q-company" name="company" autocomplete="organization"></label>
          <label class="field" for="q-service">What do you need?<select id="q-service" name="service">{opts}</select></label>
          <label class="field" for="q-budget">Budget<select id="q-budget" name="budget">{bopts}</select></label>
          <label class="field full" for="q-message">Your message <span class="req">*</span><textarea id="q-message" name="message" required placeholder="A few lines about your business and what you'd like to build"></textarea></label>
          <span class="hp" aria-hidden="true"><label for="q-bot">Leave empty</label><input id="q-bot" name="botcheck" tabindex="-1" autocomplete="off"></span>
        </div>
        <p style="font-size:.85rem;margin-top:14px">By sending this form you agree to our <a href="privacy.html" style="color:var(--primary);text-decoration:underline">Privacy Policy</a>.</p>
        <button class="btn btn-brand" type="submit" style="margin-top:16px">Send Message</button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
  <div class="container">
    <div class="map-link" style="margin-top:48px">
      <div><h3 style="color:#fff;font-size:1.15rem">Find our office</h3><p>{e(c["address"])}</p></div>
      <a class="btn btn-accent" href="{e(self.maps_url())}" target="_blank" rel="noopener">Get Directions</a>
    </div>
  </div>
</section>'''
        self.add('contact.html', f'Contact Us | {c["name"]}',
                 f'Contact {c["name"]} in {c["city"]} for a free quote on websites, apps, software and digital marketing. Call {c["phone"]} or send us a message.',
                 'contact.html', main, extra_head=self.org_jsonld())

    def build_careers(self):
        c = self.c
        roles = [('software', 'Developers', 'Web, mobile and backend developers who write clean code and enjoy solving real problems.'),
                 ('design', 'Designers', 'UI/UX and graphic designers who care about how things look and how they work.'),
                 ('marketing', 'Digital Marketers', 'SEO, ads and content people who can show results in numbers.'),
                 ('cap', 'Interns', 'Students and fresh graduates from BSc CSIT, BIT, BCA, BE Computer and similar courses.')]
        cards = ''.join(f'<div class="svc aos"><div class="icon">{icon(i)}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in roles)
        ropts = ''.join(f'<option>{t}</option>' for t in ['Developer', 'Designer', 'Digital Marketer', 'Internship', 'Other'])
        main = f'''{self.page_head("Careers", "Help us build useful software for businesses across Nepal.", [("careers.html", "Careers")])}

<section>
  <div class="container about-grid">
    <div class="aos">
      <span class="sub">Work With Us</span>
      <h2 class="title">Grow your career on real projects</h2>
      <p>We are always glad to hear from people who enjoy building useful things. Send us your details and CV, and we will get in touch when a role opens that suits you.</p>
      <ul class="checks">
        <li>You care about quality</li>
        <li>You explain things clearly</li>
        <li>You keep learning new tools</li>
        <li>You like working in a team</li>
      </ul>
      <p>Prefer email? Send your CV to {self.mail(c["careers_email"])}.</p>
    </div>
    <img class="photo aos" src="images/hero-office.jpg" alt="An office team at their desks" width="800" height="600" style="aspect-ratio:4/3">
  </div>
</section>

<section class="process">
  <div class="container">
    <div class="center aos"><span class="sub">Who We Hire</span><h2 class="title">Roles we hire for</h2></div>
    <div class="svc-grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">{cards}</div>
  </div>
</section>

<section>
  <div class="container" style="max-width:820px">
    <div class="form-card" id="apply" style="scroll-margin-top:100px">
      <h2>Send us your details</h2>
      <p>Share a link to your CV or portfolio (Google Drive, GitHub, Behance or LinkedIn). Fields marked <span style="color:var(--primary)">*</span> are required.</p>
      <form data-form data-subject="Job application" data-to="{e(c["careers_email"])}" novalidate>
        <div class="form-grid">
          <label class="field" for="c-name">Full name <span class="req">*</span><input id="c-name" name="name" autocomplete="name" required></label>
          <label class="field" for="c-email">Email <span class="req">*</span><input id="c-email" name="email" type="email" autocomplete="email" required></label>
          <label class="field" for="c-phone">Phone <span class="req">*</span><input id="c-phone" name="phone" type="tel" autocomplete="tel" required placeholder="98XXXXXXXX"></label>
          <label class="field" for="c-role">Role you're interested in<select id="c-role" name="role">{ropts}</select></label>
          <label class="field full" for="c-link">Link to your CV or portfolio <span class="req">*</span><input id="c-link" name="cv_link" type="url" required placeholder="https://"></label>
          <label class="field full" for="c-message">Tell us about yourself<textarea id="c-message" name="message" placeholder="Your experience, skills and what you'd like to work on"></textarea></label>
          <span class="hp" aria-hidden="true"><label for="c-bot">Leave empty</label><input id="c-bot" name="botcheck" tabindex="-1" autocomplete="off"></span>
        </div>
        <p style="font-size:.85rem;margin-top:14px">By sending this form you agree to our <a href="privacy.html" style="color:var(--primary);text-decoration:underline">Privacy Policy</a>.</p>
        <button class="btn btn-brand" type="submit" style="margin-top:16px">Send Application</button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>'''
        self.add('careers.html', f'Careers | {c["name"]}',
                 f'Join {c["name"]} in {c["city"]}. We hire developers, designers, digital marketers and interns. Send us your CV.',
                 'careers.html', main)

    def build_legal(self):
        c = self.c
        updated = f'{TODAY.day} {TODAY:%B %Y}'
        privacy = f'''
<p class="meta">Last updated: {updated}</p>
<p>This policy explains what personal information {e(c["name"])} ("we", "us") collects through this website, how we use it and the choices you have.</p>
<h2>Information we collect</h2>
<ul>
<li><b>Contact and quote forms:</b> your name, email address, phone number, company, the service you are interested in, your budget range and your message.</li>
<li><b>Job applications:</b> your name, contact details, the role you are interested in, a link to your CV or portfolio and anything you tell us about yourself.</li>
<li><b>Technical information:</b> like most websites, our hosting provider may record basic data such as your IP address, browser type and the pages you visit, for security and to keep the site running.</li>
</ul>
<h2>How we use your information</h2>
<ul>
<li>To reply to your enquiry and prepare quotes.</li>
<li>To deliver and support the services you ask for.</li>
<li>To consider your job application.</li>
<li>To keep this website secure and working properly.</li>
</ul>
<p>We do not sell your personal information, and we do not send you marketing messages unless you ask us to.</p>
<h2>Services that help run this website</h2>
<p>Messages you send through our forms are delivered to our inbox by a form delivery service ({'Web3Forms' if c.get('web3forms_key') else 'FormSubmit'}), which processes the message only to deliver it. The website uses Google Fonts, which means your browser loads font files from Google's servers. Links to Google Maps and social media open those services, which have their own privacy policies.</p>
<h2>Cookies</h2>
<p>This website does not set its own cookies for tracking or advertising. If we add analytics in future, we will update this policy.</p>
<h2>How long we keep information</h2>
<p>We keep enquiry and project emails for as long as needed to serve you and to meet legal and accounting requirements. Job applications are kept for up to one year unless you ask us to delete them sooner.</p>
<h2>Your rights</h2>
<p>In line with the Individual Privacy Act, 2075 (2018) of Nepal, you can ask to see the personal information we hold about you, ask us to correct it, or ask us to delete it. To do this, email {self.mail()}.</p>
<h2>Security</h2>
<p>This website uses an encrypted (HTTPS) connection. We take reasonable steps to protect the information you send us, but no method of sending data over the internet is completely secure.</p>
<h2>Changes to this policy</h2>
<p>We may update this policy from time to time. The date at the top shows when it last changed.</p>
<h2>Contact</h2>
<p>{e(c["name"])}, {e(c["address"])}. Email {self.mail()} or call {self.tel()}.</p>'''
        terms = f'''
<p class="meta">Last updated: {updated}</p>
<p>These terms apply to your use of the {e(c["name"])} website. By using the website you agree to them.</p>
<h2>Using this website</h2>
<p>You may browse the website and share links to it. You must not misuse it, for example by trying to break its security, sending spam through its forms or copying large parts of it for another website.</p>
<h2>Content and ownership</h2>
<p>The text, design, logo and graphics on this website belong to {e(c["name"])} or are used with permission. Some photos are free stock images used under their licences. You may not reuse our content without written permission.</p>
<h2>Information on this website</h2>
<p>We work to keep the information on this website accurate and up to date, but it is provided for general information only. Service descriptions, timelines and prices on the website are not an offer. Every project is agreed in a written quote or contract, and those documents take priority over anything on this website.</p>
<h2>Links to other websites</h2>
<p>We link to other websites such as Google Maps and social media. We are not responsible for their content or how they handle your information.</p>
<h2>Limitation of liability</h2>
<p>To the extent allowed by law, {e(c["name"])} is not liable for any loss caused by using this website or relying on its content. Nothing in these terms limits liability that cannot be limited by law.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of Nepal, and any disputes will be handled by the courts of Kathmandu.</p>
<h2>Changes</h2>
<p>We may update these terms from time to time. The date at the top shows when they last changed.</p>
<h2>Contact</h2>
<p>Questions about these terms? Email {self.mail()}.</p>'''
        for fn, title, lead, body in [('privacy.html', 'Privacy Policy', 'How we collect, use and protect your personal information.', privacy),
                                      ('terms.html', 'Terms of Use', 'The rules for using this website.', terms)]:
            main = f'''{self.page_head(title, lead, [(fn, title)])}

<section>
  <article class="prose legal">{body}
  </article>
</section>'''
            self.add(fn, f'{title} | {c["name"]}', f'{title} for the {c["name"]} website.', '', main)

    def build_404(self):
        c = self.c
        main = f'''<section class="notfound">
  <div class="container">
    <p class="big">404</p>
    <h1 style="margin:16px 0 12px">Page not found</h1>
    <p style="max-width:520px;margin:0 auto 28px">The page you are looking for may have moved or no longer exists. Try one of these instead.</p>
    <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap">
      <a href="index.html" class="btn btn-brand">Go to Homepage</a>
      <a href="services.html" class="btn btn-dark">Our Services</a>
      <a href="contact.html" class="btn btn-dark">Contact Us</a>
    </div>
  </div>
</section>'''
        self.add('404.html', f'Page Not Found | {c["name"]}', 'This page could not be found.', '', main, sitemap=False)

    # -- output
    def write(self, out):
        out = Path(out)
        if out.exists():
            shutil.rmtree(out)
        (out / 'css').mkdir(parents=True)
        (out / 'js').mkdir()
        for fn, doc, _ in self.pages:
            (out / fn).write_text(doc, encoding='utf-8')

        css = (SRC / 'base.css').read_text(encoding='utf-8') + '\n' + (SRC / 'extra.css').read_text(encoding='utf-8')
        (out / 'css' / 'styles.css').write_text(css, encoding='utf-8')

        c = self.c
        js_cfg = {'name': c['name'], 'email': c['email'], 'formEmail': self.form_email, 'phone': c['phone'],
                  'phoneLink': c['phone_link'], 'web3formsKey': c.get('web3forms_key', ''), 'preview': self.preview}
        js = (SRC / 'main.js').read_text(encoding='utf-8').replace('/*CONFIG*/{}', json.dumps(js_cfg, ensure_ascii=False))
        (out / 'js' / 'main.js').write_text(js, encoding='utf-8')

        shutil.copytree(SRC / 'images', out / 'images', ignore=shutil.ignore_patterns('*.txt'))
        if c.get('logo') and not (out / c['logo']).exists():
            print(f'WARNING: logo file {c["logo"]} not found in images/')
        self.write_icons(out)

        if not self.preview:
            urls = ''.join(
                f'  <url><loc>{e(self.domain)}/{"" if fn == "index.html" else fn}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n'
                for fn, _, sm in self.pages if sm)
            (out / 'sitemap.xml').write_text(
                f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding='utf-8')
            (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {self.domain}/sitemap.xml\n', encoding='utf-8')
            (out / 'site.webmanifest').write_text(json.dumps({
                'name': c['name'], 'short_name': c['name'], 'start_url': self.base_path, 'display': 'browser',
                'background_color': '#FFFFFF', 'theme_color': '#15191E',
                'icons': [{'src': self.base_path + 'apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'},
                          {'src': self.base_path + 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'} if BRAND_ICONS else
                          {'src': self.base_path + 'favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}]}, indent=2), encoding='utf-8')
            (out / '.nojekyll').write_text('', encoding='utf-8')  # GitHub Pages: serve files as they are
            host = urllib.parse.urlparse(self.domain).hostname or ''
            if host and not host.endswith('.github.io'):
                (out / 'CNAME').write_text(host + '\n', encoding='utf-8')  # GitHub Pages custom domain
            (out / '.htaccess').write_text(
                f'# For Apache / cPanel hosting\nErrorDocument 404 {self.base_path}404.html\n\n'
                '<IfModule mod_rewrite.c>\n  RewriteEngine On\n  RewriteCond %{HTTPS} off\n  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]\n</IfModule>\n\n'
                '<IfModule mod_expires.c>\n  ExpiresActive On\n  ExpiresByType image/jpeg "access plus 1 month"\n  ExpiresByType image/png "access plus 1 month"\n'
                '  ExpiresByType image/svg+xml "access plus 1 month"\n  ExpiresByType text/css "access plus 1 week"\n  ExpiresByType application/javascript "access plus 1 week"\n</IfModule>\n',
                encoding='utf-8')
            shutil.copy(SRC / 'images' / 'CREDITS.txt', out / 'images' / 'CREDITS.txt')

    def write_icons(self, out):
        if BRAND_ICONS:  # your own icons in images/brand/ win over the generated letter mark
            for name in ('favicon-32.png', 'apple-touch-icon.png', 'icon-512.png'):
                if (BRAND / name).exists():
                    shutil.copy(BRAND / name, out / name)
            return
        (out / 'favicon.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#306CF2"/>'
            '<text x="32" y="43" font-family="Poppins,Arial,Helvetica,sans-serif" font-size="30" font-weight="700" fill="#fff" text-anchor="middle">IL</text></svg>\n',
            encoding='utf-8')
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print('Pillow not installed: skipping PNG icons (pip install pillow)')
            return
        font_path = next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf',
                                      '/Library/Fonts/Arial Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if Path(p).exists()), None)
        for name, size, radius in [('apple-touch-icon.png', 180, 0), ('favicon-32.png', 32, 6)]:
            scale = 4
            S = size * scale
            im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius * scale, fill=(48, 108, 242, 255))
            font = ImageFont.truetype(font_path, int(S * 0.46)) if font_path else ImageFont.load_default()
            d.text((S / 2, S / 2), 'IL', font=font, fill='white', anchor='mm')
            im.resize((size, size), Image.LANCZOS).save(out / name)

    def placeholders(self):
        c = self.c
        warn = []
        if 'XXXX' in c['phone'] or 'XXXX' in c['phone_link']:
            warn.append('phone / phone_link')
        if c['address'].lower().startswith('your'):
            warn.append('address')
        if not any(c.get('social', {}).values()):
            warn.append('social links (none set, icons are hidden)')
        if not c.get('logo'):
            warn.append('logo (using the IL letter mark)')
        return warn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=str(SRC.parent / 'site'))
    ap.add_argument('--preview', metavar='DIR', help='build the claude.ai preview copy into DIR')
    a = ap.parse_args()
    cfg = json.loads((SRC / 'site-config.json').read_text(encoding='utf-8'))
    site = Site(cfg, preview=bool(a.preview))
    for step in (site.build_home, site.build_about, site.build_services, site.build_solutions, site.build_blog,
                 site.build_contact, site.build_careers, site.build_legal, site.build_404):
        step()
    out = a.preview or a.out
    site.write(out)
    print(f'Built {len(site.pages)} pages into {out}')
    for w in site.placeholders():
        print('  still a placeholder:', w)


if __name__ == '__main__':
    main()
