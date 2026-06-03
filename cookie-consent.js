/**
 * The Cultural Brief (SA) — Cookie & Privacy Consent
 * POPIA-compliant consent banner for static GitHub Pages site.
 * Uses localStorage (no server, no tracking cookies of our own).
 * v1.0 — April 2026
 */
(function () {
  'use strict';

  var CONSENT_KEY = 'tcbsa_consent_v1';
  var CONSENT_DATE_KEY = 'tcbsa_consent_date';

  // Inject styles
  var style = document.createElement('style');
  style.textContent = [
    '#tcb-cookie{position:fixed;bottom:0;left:0;right:0;z-index:9999;',
    'background:#1a1714;color:#f5f2ec;',
    'font-family:"EB Garamond",Georgia,serif;font-size:0.88rem;line-height:1.6;',
    'padding:1.2rem 1.6rem;',
    'display:flex;align-items:center;justify-content:space-between;',
    'gap:1.2rem;flex-wrap:wrap;',
    'border-top:2px solid #7a7167;',
    'transform:translateY(100%);transition:transform 0.4s ease;',
    '}',
    '#tcb-cookie.visible{transform:translateY(0);}',
    '#tcb-cookie p{margin:0;flex:1;min-width:200px;color:#c9c3b8;}',
    '#tcb-cookie a{color:#f5f2ec;text-decoration:none;border-bottom:1px solid #7a7167;}',
    '#tcb-cookie a:hover{border-bottom-color:#f5f2ec;}',
    '#tcb-cookie-actions{display:flex;gap:0.8rem;flex-shrink:0;flex-wrap:wrap;}',
    '#tcb-accept{background:#f5f2ec;color:#1a1714;border:none;',
    'font-family:"EB Garamond",Georgia,serif;font-size:0.75rem;',
    'letter-spacing:0.18em;text-transform:uppercase;',
    'padding:0.55rem 1.2rem;cursor:pointer;transition:background 0.2s;}',
    '#tcb-accept:hover{background:#e8e4dc;}',
    '#tcb-decline{background:transparent;color:#7a7167;border:1px solid #7a7167;',
    'font-family:"EB Garamond",Georgia,serif;font-size:0.75rem;',
    'letter-spacing:0.18em;text-transform:uppercase;',
    'padding:0.55rem 1.2rem;cursor:pointer;transition:all 0.2s;}',
    '#tcb-decline:hover{color:#f5f2ec;border-color:#f5f2ec;}',
    '@media(max-width:480px){',
    '#tcb-cookie{padding:1rem 1.2rem;}',
    '#tcb-cookie-actions{width:100%;justify-content:flex-end;}',
    '}'
  ].join('');
  document.head.appendChild(style);

  function hasConsent() {
    try {
      return localStorage.getItem(CONSENT_KEY) !== null;
    } catch (e) { return true; } // If storage unavailable, don't show banner
  }

  function setConsent(accepted) {
    try {
      localStorage.setItem(CONSENT_KEY, accepted ? 'accepted' : 'declined');
      localStorage.setItem(CONSENT_DATE_KEY, new Date().toISOString());
    } catch (e) {}
  }

  function dismiss() {
    var el = document.getElementById('tcb-cookie');
    if (el) {
      el.style.transform = 'translateY(100%)';
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 450);
    }
  }

  function showBanner() {
    var banner = document.createElement('div');
    banner.id = 'tcb-cookie';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie and privacy notice');

    banner.innerHTML = '<p>This site uses Google Fonts (loaded from Google\'s servers) and Substack for newsletter delivery. ' +
      'No tracking or advertising cookies are set by this site. ' +
      'By continuing to browse you acknowledge our <a href="' + privacyUrl() + '">Privacy &amp; Cookie Policy</a>.</p>' +
      '<div id="tcb-cookie-actions">' +
      '<button id="tcb-decline" type="button">Decline optional</button>' +
      '<button id="tcb-accept" type="button">Accept &amp; continue</button>' +
      '</div>';

    document.body.appendChild(banner);

    // Animate in after a tick
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        banner.classList.add('visible');
      });
    });

    document.getElementById('tcb-accept').addEventListener('click', function () {
      setConsent(true);
      dismiss();
    });

    document.getElementById('tcb-decline').addEventListener('click', function () {
      setConsent(false);
      dismiss();
    });
  }

  function privacyUrl() {
    // Resolve relative to current page location
    var path = window.location.pathname;
    if (path.indexOf('/editions/') !== -1) {
      return '../privacy.html';
    }
    return 'privacy.html';
  }

  // Only show if no consent recorded yet
  function init() {
    if (hasConsent()) return;
    // Small delay so page content renders first
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        setTimeout(showBanner, 600);
      });
    } else {
      setTimeout(showBanner, 600);
    }
  }

  init();
})();
