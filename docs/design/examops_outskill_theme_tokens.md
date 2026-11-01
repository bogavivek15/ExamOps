# ExamOps Design System: Outskill Theme Tokens

**Version:** 2.0.0  
**Status:** Canonical Design Token Specification  
**Brand Foundation:** Derived directly from live reference audit of Outskill (`https://www.outskill.com/` and `/outs.svg`)  
**Design Principle:** High-density enterprise operations platform embodying Outskill's dark obsidian canvas, precision geometric radii, subtle borders, crisp white typography, and signature Electric Lime (`#B8EF43`) accent.

---

## 1. Brand Tokens

These tokens are directly extracted from Outskill's official SVG branding and computed styles:

| Token Name | CSS Custom Property | Normalized Value | Purpose / Usage | Source Evidence |
|---|---|---|---|---|
| **Brand Primary (Lime)** | `--brand-primary` | `#B8EF43` (`rgb(184, 239, 67)`) | Primary buttons, active tabs, scheduled KPIs, progress bars | `outs.svg`, `button.bg-[#B8EF43]` |
| **Brand Primary Hover** | `--brand-primary-hover` | `#BEF264` (`rgb(190, 242, 100)`) | Hover state for primary action buttons (`lime-300`) | `button.hover:bg-lime-300` |
| **Brand Primary Active** | `--brand-primary-active` | `#A6DF30` (`rgb(166, 223, 48)`) | Mouse down / active press state on primary actions | Product-Derived from `#B8EF43` |
| **Brand Primary Subtle** | `--brand-primary-subtle` | `rgba(184, 239, 67, 0.12)` | Pill backgrounds, active table row highlights | Outskill badge opacity pattern |
| **Brand Primary Muted** | `--brand-primary-muted` | `rgba(184, 239, 67, 0.24)` | Focus rings, border glow, selected indicators | Outskill hover boundary |
| **Brand Cream White** | `--brand-cream` | `#FCF7F3` (`rgb(252, 247, 243)`) | Secondary brand mark accents, warm highlights | `outs.svg` sparkle star |
| **Brand Pure White** | `--brand-white` | `#FFFFFF` (`rgb(255, 255, 255)`) | Inverted action buttons (`bg-white text-black`), logo text | `outs.svg`, `button.bg-white` |
| **Brand Deep Black** | `--brand-black` | `#000000` (`rgb(0, 0, 0)`) | Inverted button text, icon button surfaces | `outskill.com` |

---

## 2. Surface & Layout Tokens

Outskill's canvas uses a disciplined dark architectural progression from obsidian canvas to elevated cards:

| Token Name | CSS Custom Property | Normalized Value | Usage in ExamOps | Reference Observation |
|---|---|---|---|---|
| **Canvas Background** | `--surface-bg` | `#08090A` (`rgb(8, 9, 10)`) | Root application viewport background | `div.bg-[#08090A]` |
| **Sidebar Surface** | `--surface-sidebar` | `#0D0E10` (`rgb(13, 14, 16)`) | Fixed left navigation sidebar background | Calibrated from `#08090A` |
| **Card / Table Surface** | `--surface-card` | `#121212` (`rgb(18, 18, 18)`) | Primary data cards, data table container, forms | `div.bg-[#121212]` |
| **Elevated Surface** | `--surface-elevated` | `#1C1C1C` (`rgb(28, 28, 28)`) | Table headers, modal dialogs, flyout drawers, dropdowns | `div.bg-[#1c1c1c]` |
| **Intermediate Surface**| `--surface-panel` | `#141414` (`rgb(20, 20, 20)`) | Filter bars, search input background, secondary panels | `div.bg-[#141414]` |
| **Icon Box Surface** | `--surface-iconbox` | `#343535` (`rgb(52, 53, 53)`) | Stat card icon badge containers, tool headers | `div.icon-box.bg-[#343535]` |
| **Hover Surface** | `--surface-hover` | `rgba(255, 255, 255, 0.05)` | Table row hover, menu item hover | `hover:bg-white/10` |
| **Active Nav Surface** | `--surface-nav-active` | `rgba(184, 239, 67, 0.10)` | Selected sidebar navigation pill | Outskill active item treatment |

---

## 3. Typography Tokens

Outskill couples crisp pure white with calibrated opacity tiers to achieve visual hierarchy without introducing muddy gray tints:

| Token Name | CSS Custom Property | Normalized Value | Usage in ExamOps |
|---|---|---|---|
| **Text Primary** | `--text-primary` | `#FFFFFF` (`rgb(255, 255, 255)`) | Page titles, KPI metrics, table headings, active items |
| **Text Secondary** | `--text-secondary` | `rgba(255, 255, 255, 0.82)` | Section subtitles, card body text, form labels |
| **Text Muted** | `--text-muted` | `#9CA3AF` (`rgb(156, 163, 175)`) | Secondary table cells, captions, input placeholders |
| **Text Subdued / Nav** | `--text-nav` | `rgba(255, 255, 255, 0.50)` | Inactive nav links, breadcrumb dividers, timestamps |
| **Text Accent** | `--text-accent` | `#B8EF43` (`rgb(184, 239, 67)`) | Active metric highlights, success indicators, primary links |
| **Text Inverse** | `--text-inverse` | `#000000` (`rgb(0, 0, 0)`) | Text inside Lime CTA buttons (`bg-[#B8EF43]`) and White buttons |

---

## 4. Borders, Rings & Dividers

Outskill avoids heavy borders, using fine micro-borders with explicit white transparency:

| Token Name | CSS Custom Property | Normalized Value | Usage in ExamOps |
|---|---|---|---|
| **Border Subtle** | `--border-subtle` | `rgba(255, 255, 255, 0.12)` | Table row dividers, card inner separators |
| **Border Default** | `--border-default` | `rgba(255, 255, 255, 0.18)` | Standard card borders, top navigation border, table borders |
| **Border Strong** | `--border-strong` | `rgba(255, 255, 255, 0.28)` | Modal borders, input active borders, button outlines |
| **Border Accent** | `--border-accent` | `#B8EF43` | Active tab border, selected card outline |
| **Focus Ring** | `--focus-ring` | `0 0 0 2px rgba(184, 239, 67, 0.40)` | Accessible keyboard focus state |

---

## 5. Semantic Status System (Enterprise Operations)

Strictly classified between Outskill-original and Product-derived:

| Status | Background | Text / Border | Purpose | Classification |
|---|---|---|---|---|
| **SCHEDULED** | `rgba(184, 239, 67, 0.12)` | `#B8EF43` | Examination scheduled with full resource allocation | **Outskill-Based** |
| **PUBLISHED** | `rgba(184, 239, 67, 0.16)` | `#B8EF43` | Schedule approved and published to students | **Outskill-Based** |
| **ACTIVE / READY** | `rgba(184, 239, 67, 0.12)` | `#B8EF43` | Active academic period, room available | **Outskill-Based** |
| **DRAFT** | `rgba(255, 255, 255, 0.08)` | `#D1D5DB` | Preliminary scheduling run in progress | **Outskill-Based** |
| **WARNING** | `rgba(232, 182, 109, 0.12)` | `#E8B66D` | High room utilization (>90%), tight turnaround | **Product-Derived** |
| **CONFLICT / DANGER**| `rgba(255, 107, 107, 0.12)`| `#FF6B6B` | Unassigned exam, hard constraint failure | **Product-Derived** |
| **INFO / ACCOMMODATION**| `rgba(124, 170, 229, 0.12)`| `#7CAAE5` | Special accommodation note, system notification | **Product-Derived** |

---

## 6. Visualization & Chart Tokens (Recharts)

| Visualization Token | Hex Value | Semantic Usage |
|---|---|---|
| `--chart-lime` | `#B8EF43` | Scheduled exams, high-capacity rooms |
| `--chart-cream` | `#FCF7F3` | Baseline targets, enrolled students |
| `--chart-slate` | `#9CA3AF` | Inactive/unassigned capacity |
| `--chart-amber` | `#E8B66D` | Utilization warnings |
| `--chart-rose` | `#FF6B6B` | Conflicted exams |
| `--chart-blue` | `#7CAAE5` | Invigilator shifts |
| `--chart-grid` | `rgba(255, 255, 255, 0.08)`| Cartesian chart grid lines |
| `--chart-tooltip-bg`| `#1C1C1C` | Tooltip popup background |
| `--chart-tooltip-border`| `rgba(255, 255, 255, 0.20)`| Tooltip popup border |

---

## 7. Geometric & Spacing Standards

- **Border Radius**:
  - Buttons: `2px` (`rounded-[2px]`) or `4px` (`rounded`)
  - Cards, Tables, Drawers: `4px` (`rounded-[4px]`) to `6px`
  - Modals: `8px` (`rounded-lg`)
  - Badges / Pills: `4px` or `rounded-full`
- **Typography Hierarchy**:
  - H1 / Page Hero: `24px` - `28px`, font-weight `600`, tracking tight
  - H2 / Section Title: `18px` - `20px`, font-weight `600`
  - H3 / Card Title: `14px` - `16px`, font-weight `500`
  - Body Text: `14px`, line-height `1.5`
  - Monospace Data / IDs / Counts: `12px` - `13px`, font-weight `500` (JetBrains Mono / Consolas)

