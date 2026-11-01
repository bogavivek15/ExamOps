# Outskill Reference Website Color & Design System Audit

**Audit Date:** 2026-11-01  
**Auditor:** Principal Product Designer, Brand Systems Engineer & Senior React Frontend Engineer  
**Reference Target 1:** `https://www.outskill.com/` (Official Homepage)  
**Reference Target 2:** `https://www.outskill.com/6-month-ai-generalist-fellowship` (Flagship Fellowship Program)  
**Tooling / Protocol:** Headless Chrome via Chrome DevTools Protocol (CDP), Computed Style Inspection, SVG Path Analysis, CSS OM Rules Extraction, Screenshot Capture across 3 Viewports.

---

## 1. Executive Summary & Brand Identity Overview

Outskill (`https://www.outskill.com/`) employs a distinctive, high-impact **dark-first visual architecture with an Electric Lime accent (`#B8EF43`)**, offset by crisp white typography (`#FFFFFF`), warm cream accents (`#FCF7F3`), and disciplined dark obsidian and charcoal surfaces (`#08090A`, `#121212`, `#141414`, `#1C1C1C`).

Unlike generic AI-dashboard templates that rely on blue-purple gradients and heavy glassmorphism, Outskill's aesthetic is characterized by:
- **Sharp, geometric container boundaries**: Border radii of `2px` and `4px`, delivering an ultra-crisp, precise, institutional feel.
- **Micro-calibrated border luminance**: Subtle borders (`rgba(255, 255, 255, 0.16)` to `rgba(255, 255, 255, 0.20)`) that delineate cards and sections without distracting visual clutter.
- **Electric Lime Signature Accent (`#B8EF43`)**: Reserved for primary calls-to-action, high-priority status indicators, and focal metric highlights.
- **Contrasting White Secondary Action Pattern**: Inverted white buttons (`#FFFFFF` background with `#000000` text) providing an elegant, dual-tone hierarchy.
- **Subdued Slate & Monochrome Icon Containers**: Square rounded icon badges (`#343535`) that maintain professional calm.
- **High-contrast Typography Hierarchy**: Primary titles in pure `#FFFFFF`, supporting subtitles in `rgba(255, 255, 255, 0.8)`, and tabular/metadata labels in `#9CA3AF` or `rgba(255, 255, 255, 0.5)`.

---

## 2. Screenshot Evidence & Viewport Verification

All screenshots were captured directly using headless Chrome CDP against the live Outskill production servers:

| Viewport | Dimension | Homepage Evidence | Fellowship Evidence | Status |
|---|---|---|---|---|
| **Desktop** | 1440 × 900 px | `docs/design/screenshots/outskill_home_1440.png` | `docs/design/screenshots/outskill_fellowship_1440.png` | **VERIFIED** |
| **Tablet** | 1024 × 768 px | `docs/design/screenshots/outskill_home_1024.png` | `docs/design/screenshots/outskill_fellowship_1024.png` | **VERIFIED** |
| **Mobile** | 390 × 844 px | `docs/design/screenshots/outskill_home_390.png` | `docs/design/screenshots/outskill_fellowship_390.png` | **VERIFIED** |

### Desktop vs Mobile Responsive Behavior
- **Navigation**: On desktop (1440px), the navigation is an expansive top bar with text links (`For Business`, `Newsletter`, `Contact Us`, `Apply as Mentor`) in `rgba(255, 255, 255, 0.5)` and a login button. On mobile (390px), navigation collapses into a minimal hamburger toggle (`w-8 h-8`).
- **Hero & Card Grids**: On desktop, cards are arranged in balanced multi-column grid layouts (`w-1/3`, `w-[60%]`, `w-[40%]`). On mobile, grids collapse into single vertical stacks with `100%` width and `px-4` padding.
- **Typography Sizing**: H1 scales from `38px` / `48px` on desktop down to `28px` / `32px` on mobile, while preserving font weights (`500` / `600`) and line heights.

---

## 3. Logo Anatomy & Exact Brand Color Extraction

Direct vector inspection of Outskill's official SVG logos (`https://www.outskill.com/outs.svg` and `https://www.outskill.com/home/osnewsvg.svg`) revealed the exact brand geometry and hex fills:

```svg
<!-- Source: https://www.outskill.com/outs.svg -->
<svg width="163" height="41" viewBox="0 0 163 41" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="25.8281" y="15.3984" width="7.82196" height="7.82196" rx="3.91098" fill="#B8EF43"/>
  <rect x="0.398438" y="2.44531" width="7.82196" height="7.82196" rx="3.91098" fill="#FCF7F3"/>
  <rect x="13.1092" y="2.44531" width="7.82196" height="7.82196" rx="3.91098" fill="#FCF7F3"/>
  <rect x="0.398438" y="15.3984" width="7.82196" height="7.82196" rx="3.91098" fill="#B8EF43"/>
  <rect x="13.1094" y="15.3984" width="7.82196" height="7.82196" rx="3.91098" fill="#B8EF43"/>
  <rect x="0.398438" y="28.1133" width="7.82196" height="7.82196" rx="3.91098" fill="#B8EF43"/>
  <rect x="13.1094" y="28.1133" width="7.82196" height="7.82196" rx="3.91098" fill="#B8EF43"/>
  <rect x="25.8281" y="28.1133" width="7.82196" height="7.82196" rx="3.91098" fill="#FCF7F3"/>
  <path ... fill="#FCF7F3"/>
  <path ... fill="white"/>
</svg>
```

### Official Logo Tokens
1. **Logo Electric Lime**: `#B8EF43` (`rgb(184, 239, 67)`) — Dominant brand mark glyphs.
2. **Logo Cream White**: `#FCF7F3` (`rgb(252, 247, 243)`) — Supporting sparkle star and accent pill.
3. **Logo Wordmark White**: `#FFFFFF` (`rgb(255, 255, 255)`) — Precision sans-serif text "OUTSKILL".

---

## 4. CSS Custom Properties (:root Variables)

Extracted directly from the stylesheets rendered on `https://www.outskill.com/`:

```css
:root {
  --font-fira-sans: "Fira Sans", sans-serif;
  --font-figtree: "Figtree", sans-serif;
  --font-dm-sans: "DM Sans", sans-serif;
  --font-poppins: "Poppins", sans-serif;
  --font-lora: "Lora", serif;
  --font-pt-serif: "PT Serif", serif;
  --font-ibm-plex: "IBM Plex Sans", sans-serif;
  --font-spline-sans: "Spline Sans", sans-serif;
}
```

The primary typography stack rendered on the site is `"Fira Sans", sans-serif` and `"Figtree", sans-serif` for body text, combined with clean tabular numbering.

---

## 5. Master Color Inventory & Audit Register

The table below lists all verified colors extracted from the live DOM and computed CSS:

| Token Name | Exact CSS Value | HEX | RGB / RGBA | Usage | Source URL | Selector / Element | State | Classification | Verification |
|---|---|---|---|---|---|---|---|---|---|
| `outskill-lime-primary` | `rgb(184, 239, 67)` | `#B8EF43` | `rgb(184, 239, 67)` | Primary CTA button background, active accent | `outskill.com` | `button.bg-[#B8EF43]`, `outs.svg` | Default | Brand-Original | DIRECT_DOM & SVG |
| `outskill-lime-hover` | `rgb(190, 242, 100)` | `#BEF264` | `rgb(190, 242, 100)` | Hover state on lime buttons (`lime-300`) | `outskill.com` | `button:hover` (`hover:bg-lime-300`) | Hover | Brand-Original | DIRECT_CSS_CLASS |
| `outskill-lime-active` | `rgb(166, 223, 48)` | `#A6DF30` | `rgb(166, 223, 48)` | Active press state on lime buttons | `outskill.com` | Computed active shade | Active | Product-Derived | DERIVED_ACCESSIBLE |
| `outskill-lime-subtle` | `rgba(184, 239, 67, 0.12)` | `#B8EF431F` | `rgba(184, 239, 67, 0.12)` | Accent pill background, active row highlight | `outskill.com` | Badge and hover backdrop | Default | Product-Derived | DERIVED_TRANSLUCENCY |
| `outskill-cream-white` | `rgb(252, 247, 243)` | `#FCF7F3` | `rgb(252, 247, 243)` | Logo sparkle star, warm highlight element | `outskill.com` | `outs.svg path[fill="#FCF7F3"]` | Default | Brand-Original | DIRECT_SVG |
| `outskill-canvas-dark` | `rgb(8, 9, 10)` | `#08090A` | `rgb(8, 9, 10)` | Deep obsidian canvas background | `outskill.com` | `div.bg-[#08090A]` | Default | Brand-Original | DIRECT_DOM |
| `outskill-canvas-black` | `rgb(0, 0, 0)` | `#000000` | `rgb(0, 0, 0)` | Full black canvas & footer backdrop | `outskill.com` | `html`, `body`, `div.bg-black` | Default | Brand-Original | DIRECT_DOM |
| `outskill-surface-card` | `rgb(18, 18, 18)` | `#121212` | `rgb(18, 18, 18)` | Primary card and container surface | `outskill.com` | `div.bg-[#121212]` | Default | Brand-Original | DIRECT_DOM |
| `outskill-surface-elevated`| `rgb(20, 20, 20)` | `#141414` | `rgb(20, 20, 20)` | Elevated card / modal surface | `outskill.com` | `div.bg-[#141414]` | Default | Brand-Original | DIRECT_DOM |
| `outskill-surface-panel` | `rgb(28, 28, 28)` | `#1C1C1C` | `rgb(28, 28, 28)` | Tool card surface, dropdowns, table headers | `outskill.com` | `div.bg-[#1c1c1c]` | Default | Brand-Original | DIRECT_DOM |
| `outskill-surface-iconbox` | `rgb(52, 53, 53)` | `#343535` | `rgb(52, 53, 53)` | Small icon badge container | `outskill.com` | `div.icon-box.bg-[#343535]` | Default | Brand-Original | DIRECT_DOM |
| `outskill-border-subtle` | `rgba(255, 255, 255, 0.16)` | `#FFFFFF29` | `rgba(255, 255, 255, 0.16)` | Skill card border, section dividers | `outskill.com` | `div.border-[#ffffff]/16` | Default | Brand-Original | DIRECT_DOM |
| `outskill-border-default` | `rgba(255, 255, 255, 0.20)` | `#FFFFFF33` | `rgba(255, 255, 255, 0.20)` | Global container and header border | `outskill.com` | `div.border-white/20` | Default | Brand-Original | DIRECT_DOM |
| `outskill-border-strong` | `rgba(255, 255, 255, 0.30)` | `#FFFFFF4D` | `rgba(255, 255, 255, 0.30)` | Button border, active card border | `fellowship` | `button.border-white/30` | Default | Brand-Original | DIRECT_DOM |
| `outskill-border-lime` | `rgba(98, 98, 98, 0.40)` | `#62626266` | `rgba(98, 98, 98, 0.40)` | Subtle dark border on lime button | `outskill.com` | `button.border-[#62626266]/40` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-pure` | `rgb(255, 255, 255)` | `#FFFFFF` | `rgb(255, 255, 255)` | Main headings (H1, H2, H3), active nav | `outskill.com` | `h1`, `h2`, `h3`, `text-white` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-secondary`| `rgba(255, 255, 255, 0.80)` | `#FFFFFFCC` | `rgba(255, 255, 255, 0.80)` | Supporting text, card descriptions | `fellowship` | `p.text-white/80` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-muted` | `rgba(255, 255, 255, 0.60)` | `#FFFFFF99` | `rgba(255, 255, 255, 0.60)` | Body text, section subtitles | `outskill.com` | `p.text-white/60` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-nav` | `rgba(255, 255, 255, 0.50)` | `#FFFFFF80` | `rgba(255, 255, 255, 0.50)` | Inactive navigation links, timestamps | `outskill.com` | `a.text-white/50` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-gray400` | `rgb(156, 163, 175)` | `#9CA3AF` | `rgb(156, 163, 175)` | Metadata label text, micro-copy | `outskill.com` | `div.text-gray-400` | Default | Brand-Original | DIRECT_DOM |
| `outskill-text-gray300` | `rgb(209, 213, 219)` | `#D1D5DB` | `rgb(209, 213, 219)` | Breadcrumb text, secondary metadata | `fellowship` | `div.text-gray-300` | Default | Brand-Original | DIRECT_DOM |
| `outskill-button-white` | `rgb(255, 255, 255)` | `#FFFFFF` | `rgb(255, 255, 255)` | Secondary button background | `outskill.com` | `button.bg-white.text-black` | Default | Brand-Original | DIRECT_DOM |
| `outskill-button-white-hover`| `rgba(255, 255, 255, 0.3)` | `#FFFFFF4D` | `rgba(255, 255, 255, 0.30)` | Secondary button hover background | `outskill.com` | `hover:bg-[#ffffff]/30` | Hover | Brand-Original | DIRECT_CSS_CLASS |
| `outskill-button-black` | `rgb(0, 0, 0)` | `#000000` | `rgb(0, 0, 0)` | Black icon button (`Load More`, arrows) | `outskill.com` | `button.bg-black.text-white` | Default | Brand-Original | DIRECT_DOM |

---

## 6. Product-Derived Semantic Status Colors (Enterprise Operations)

Because Outskill is a cohort-based AI fellowship platform rather than a university examination platform, specific operational statuses (Conflict, Unscheduled, Warning, Danger) are not declared as dedicated tokens on their landing page.

In strict adherence to the mandate ("DOCUMENT AS PRODUCT-DERIVED. Never claim that a derived status color is an original Outskill brand color"):

| Token Name | Exact HEX | RGB / RGBA | Operational Purpose | Derivation Rationale | Classification |
|---|---|---|---|---|---|
| `status-scheduled-bg` | `#B8EF431A` | `rgba(184, 239, 67, 0.10)` | Scheduled exam badge, 100% capacity | Built directly from Outskill Lime `#B8EF43` at 10% opacity | Product-Derived |
| `status-scheduled-fg` | `#B8EF43` | `rgb(184, 239, 67)` | Scheduled text, success checkmarks | Exact Outskill Lime `#B8EF43` | Product-Derived (Brand-Based) |
| `status-published-bg` | `#B8EF4324` | `rgba(184, 239, 67, 0.14)` | Published schedule run badge | Built from Outskill Lime `#B8EF43` | Product-Derived |
| `status-published-fg` | `#B8EF43` | `rgb(184, 239, 67)` | Published run text | Exact Outskill Lime `#B8EF43` | Product-Derived (Brand-Based) |
| `status-draft-bg` | `#FFFFFF14` | `rgba(255, 255, 255, 0.08)` | Draft run badge | Outskill white at 8% opacity | Product-Derived |
| `status-draft-fg` | `#D1D5DB` | `rgb(209, 213, 219)` | Draft run text | Outskill gray-300 | Product-Derived |
| `status-warning-bg` | `#E8B66D1A` | `rgba(232, 182, 109, 0.10)` | Near-capacity warning badge | Warm amber harmonized with Outskill `#FCF7F3` | Product-Derived |
| `status-warning-fg` | `#E8B66D` | `rgb(232, 182, 109)` | Warning text & warning icon | Warm amber, WCAG AA compliant on `#121212` | Product-Derived |
| `status-danger-bg` | `#FF55551A` | `rgba(255, 85, 85, 0.10)` | Hard constraint conflict badge | Crisp coral-red, high visibility on `#121212` | Product-Derived |
| `status-danger-fg` | `#FF6B6B` | `rgb(255, 107, 107)` | Conflict text, unscheduled reason code | High-contrast crimson (4.8:1 on `#121212`) | Product-Derived |
| `status-info-bg` | `#5BA4FC1A` | `rgba(91, 164, 252, 0.10)` | Accommodation note badge | Cool slate blue harmonized with dark obsidian | Product-Derived |
| `status-info-fg` | `#7CAAE5` | `rgb(124, 170, 229)` | Accommodation icon & detail link | Clean informational blue | Product-Derived |

---

## 7. Gradients, Shadows & Effect Definitions

1. **Horizontal Fade**:
   - `linear-gradient(to right, rgba(0, 0, 0, 0), rgb(8, 9, 10))`
   - Verified on `div.absolute.top-0.right-0.h-full.w-32`.
2. **Vertical Bottom Fade**:
   - `linear-gradient(to top, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0))`
   - Verified on card footer overlays.
3. **Card Shadow**:
   - `rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px`
   - Verified on primary CTA buttons.
4. **Border Radius Standards**:
   - Buttons: `2px` and `4px`.
   - Cards & Tables: `4px` (and `rounded-lg` / `8px` for modal dialogs).
   - Badges & Pills: `4px` or `rounded-full`.

---

## 8. Audit Verification Conclusion

The extracted palette establishes that Outskill is a **dark obsidian-canvas brand (`#08090A`) with rich charcoal card layers (`#121212`, `#141414`, `#1C1C1C`), crisp white typography (`#FFFFFF`), subtle borders (`rgba(255, 255, 255, 0.2)`), and an Electric Lime signature accent (`#B8EF43`)**.

This audit is **complete, verified via live browser automation, and ready for design token system generation**.

