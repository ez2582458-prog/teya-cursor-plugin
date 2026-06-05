---
name: aurora-team-conversion
description: Aurora Team Conversion — формы, CTA, consent, anti-spam, SMTP, Telegram/WhatsApp, Metrika/GA4 goals.
---

# Aurora Team Conversion

## Выход

`teya-memory/wp/conversion-tracking-map.md`

## Обязательно

- CTA map for header, hero, service blocks, footer and mobile.
- Read `teya-memory/design/AURA_VISUAL_INVENTORY.json` and `AURA_ASSET_REGISTRY.json` for form-side visuals, CTA callouts and conversion-section visuals.
- If AURA marks a form-side visual/callout as required, include it in `conversion-tracking-map.md`; do not allow Aurora to replace it with a plain form card.
- Lead form fields and validation.
- Success/error states.
- Standard “Политика конфиденциальности” page.
- Standard “Политика cookies” page.
- Privacy and personal data consent.
- Cookie banner is always required on production sites.
- Cookie accept button: `Принять cookies` / `Принять`, with consent stored in first-party cookie/localStorage.
- Cookie banner links to both privacy and cookies policies.
- Anti-spam: nonce, honeypot, rate limit recommendation.
- SMTP/delivery requirements.
- Analytics events for form submit, phone, email, messenger, CTA clicks.
- Yandex Metrika and GA4 naming.
- Thank-you page usually `noindex, follow`.

## Blockers

Status cannot be `✅` if privacy page, cookies page, cookie banner, accept button, form consent links, or required conversion visual zones are missing.
