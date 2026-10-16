/* Site script: menu, slider, scroll animations, forms. */
(function () {
  'use strict';
  var SITE = /*CONFIG*/{};
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* mobile menu */
  var toggle = $('#toggle'), menu = $('#menu');
  if (toggle && menu) {
    var setOpen = function (open) {
      menu.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? '✕ Close' : '☰ Menu';
    };
    toggle.addEventListener('click', function () { setOpen(!menu.classList.contains('open')); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.classList.contains('open')) { setOpen(false); toggle.focus(); } });
    document.addEventListener('click', function (e) { if (menu.classList.contains('open') && !menu.contains(e.target) && e.target !== toggle) setOpen(false); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
  }

  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* hero slider */
  function rotator(items, dotsEl, ms) {
    if (items.length < 2 || !dotsEl) return;
    var i = 0, timer = null;
    var dots = items.map(function (_, k) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Show slide ' + (k + 1));
      b.addEventListener('click', function () { go(k); restart(); });
      dotsEl.appendChild(b);
      return b;
    });
    function go(k) {
      items[i].hidden = true; dots[i].classList.remove('on'); dots[i].removeAttribute('aria-current');
      i = k;
      items[i].hidden = false; dots[i].classList.add('on'); dots[i].setAttribute('aria-current', 'true');
    }
    function restart() { clearInterval(timer); if (!reduce) timer = setInterval(function () { go((i + 1) % items.length); }, ms); }
    var host = dotsEl.parentNode;
    host.addEventListener('mouseenter', function () { clearInterval(timer); });
    host.addEventListener('mouseleave', restart);
    host.addEventListener('focusin', function () { clearInterval(timer); });
    dots[0].classList.add('on'); dots[0].setAttribute('aria-current', 'true');
    restart();
  }
  rotator($$('.slide'), $('#dots'), 6500);
  /* fetch the other slide photos once the page has loaded, so switching slides never shows a blank frame */
  addEventListener('load', function () { $$('.slide img[loading="lazy"]').forEach(function (i) { i.loading = 'eager'; }); });

  /* scroll fade-up and counters */
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.remove('wait'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    $$('.aos').forEach(function (el, k) {
      if (el.getBoundingClientRect().top > innerHeight) {
        el.classList.add('wait'); el.style.transitionDelay = (k % 3) * 100 + 'ms'; io.observe(el);
      }
    });
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, end = +el.dataset.count, suf = el.dataset.suffix || '', t0 = performance.now();
        (function tick(n) {
          var k = Math.min(1, Math.max(0, (n - t0) / 1400));
          el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))) + suf;
          if (k < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: 0.6 });
    $$('[data-count]').forEach(function (el) { co.observe(el); });
  }

  /* back to top */
  var top = $('#totop');
  if (top) {
    addEventListener('scroll', function () { top.classList.toggle('show', scrollY > 600); }, { passive: true });
    top.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
  }

  /* contact page: "Get a quote for X" links arrive as #quote-<service> */
  var quote = $('#quote');
  if (quote) {
    var m = /^#quote-([a-z]+)$/.exec(location.hash);
    var sel = $('#q-service');
    if (m && sel) {
      var opt = $$('option', sel).filter(function (o) { return o.dataset.key === m[1]; })[0];
      if (opt) sel.value = opt.value;
    }
    if (m) setTimeout(function () { quote.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 50);
  }

  /* forms */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  function validate(form) {
    var first = null;
    $$('input, select, textarea', form).forEach(function (f) {
      if (f.name === 'botcheck' || f.type === 'hidden') return;
      var v = f.value.trim(), bad = false;
      if (f.required && !v) bad = true;
      else if (v && f.type === 'email' && !EMAIL_RE.test(v)) bad = true;
      else if (v && f.type === 'tel' && v.replace(/\D/g, '').length < 7) bad = true;
      else if (v && f.type === 'url' && !/^https?:\/\/\S+\.\S+/.test(v)) bad = true;
      var wrap = f.closest('.field');
      if (wrap) wrap.classList.toggle('invalid', bad);
      f.setAttribute('aria-invalid', String(bad));
      if (bad && !first) first = f;
    });
    return first;
  }

  function send(form, data) {
    var subject = (form.dataset.subject || 'Website enquiry') + (data.name ? ' from ' + data.name : '');
    var url, body;
    if (SITE.web3formsKey) {
      url = 'https://api.web3forms.com/submit';
      body = Object.assign({ access_key: SITE.web3formsKey, subject: subject, from_name: SITE.name + ' website' }, data);
    } else {
      url = 'https://formsubmit.co/ajax/' + encodeURIComponent(form.dataset.to || SITE.formEmail);
      body = Object.assign({ _subject: subject, _template: 'table', _captcha: 'false' }, data);
    }
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok || !(j.success === true || j.success === 'true')) throw new Error(j.message || 'Send failed');
      });
    });
  }

  $$('form[data-form]').forEach(function (form) {
    var status = $('.form-status', form) || $('#' + form.dataset.status);
    var btn = $('button[type=submit]', form);
    var label = btn ? btn.textContent : '';
    var show = function (cls, html) { if (!status) return; status.className = status.className.replace(/\b(ok|err)\b/g, '').trim() + ' ' + cls; status.innerHTML = html; };

    form.addEventListener('input', function (e) {
      var w = e.target.closest && e.target.closest('.field.invalid');
      if (w) { w.classList.remove('invalid'); e.target.setAttribute('aria-invalid', 'false'); }
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = validate(form);
      if (bad) {
        show('err', 'Please check the highlighted field' + ($$('.invalid', form).length > 1 ? 's' : '') + '.');
        bad.focus();
        return;
      }
      var fd = new FormData(form), data = {};
      fd.forEach(function (v, k) { data[k] = typeof v === 'string' ? v.trim() : v; });
      if (data.botcheck) { form.reset(); show('ok', 'Thank you. Your message has been sent.'); return; }
      delete data.botcheck;
      data.page = document.title;
      var who = data.name ? ', ' + esc(data.name.split(' ')[0]) : '';
      var to = form.dataset.to || SITE.email;

      if (SITE.preview) {
        show('ok', 'Preview only: nothing was sent. On the live website this message goes straight to <b>' + esc(to) + '</b>.');
        return;
      }
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      show('', '');
      send(form, data).then(function () {
        form.reset();
        show('ok', 'Thank you' + who + '. Your message has been sent and we will reply within one working day.');
      }).catch(function () {
        show('err', 'Sorry, your message could not be sent. Please email us at <a href="mailto:' + esc(to) + '">' + esc(to) + '</a> or call <a href="tel:' + esc(SITE.phoneLink) + '">' + esc(SITE.phone) + '</a>.');
      }).then(function () {
        if (btn) { btn.disabled = false; btn.textContent = label; }
      });
    });
  });
})();
