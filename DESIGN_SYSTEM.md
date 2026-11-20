# Kewargen UI Design System Guide for AI Agents

> **Purpose**: This guide is the authoritative design reference for AI agents building, modifying, or extending user interfaces in the **Kewargen** ecosystem (including standalone HTML apps like `index.html` and embedded server-side Web UIs like `scripts/vcf_qr_generator.py`).
>
> **Core Tenet**: All Kewargen UIs are **zero-build, zero-dependency, self-contained, and portable**. They rely exclusively on modern semantic HTML5, modern standard CSS, and vanilla JavaScript with inline SVGs. Do not introduce Tailwind, React, Vite, Webpack, Bootstrap, or external icon libraries.
>
> **Modern Web Standards**: Incorporates best practices from the **Modern Web Guidance** (standard CSS scrollbars, `:user-invalid` validation, `text-wrap: balance/pretty`, `color-scheme`, `accent-color`, dynamic viewport units `dvh`, and accessible tap targets).

---

## 1. Architectural & Platform Principles

1. **Self-Contained & Dependency-Free**:
   - Every UI must work by simply opening an `.html` file or serving a static HTML string from a Python script (`INDEX_HTML = """..."""`).
   - Use native modern CSS (CSS custom properties, Flexbox, CSS Grid, container queries, gradients, keyframes) and vanilla JavaScript.
2. **Warm, Crafted Aesthetic**:
   - Avoid generic sterile gray/blue enterprise palettes. Kewargen uses a distinct **Warm Amber & Stone Neutral** palette with subtle amber ambient glows, tactile cards, and refined typography.
3. **Responsive by Default**:
   - Mobile-first or desktop-down with seamless adaptability across small phones (<640px), tablets (640px–768px), and desktop displays (>1024px).
   - Use dynamic viewport units (`100dvh`) to prevent layout clipping when mobile address bars expand or contract.
4. **Accessible & Agent-Friendly**:
   - Maintain full semantic markup (`<form>`, `<fieldset>`, `<legend>`, `<label for="...">`).
   - Preserve keyboard navigation, explicit `:focus-visible` styling, screen-reader support (`.visually-hidden`), and minimum 48px tap targets.
   - Clear semantic structures ensure that both human users and autonomous AI agents (such as browser-based subagents or WebMCP tools) can reliably inspect, interact with, and submit forms.

---

## 2. Document Setup & Meta Configuration

Every Kewargen HTML document must include these standard `<head>` tags to prevent FOUC (flash of un-themed content), enable browser-level theme adaptation, and load the brand typography:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <!-- Informs browser of supported color schemes to prevent FOUC -->
  <meta name="color-scheme" content="light" />
  <title>Kewargen</title>

  <!-- Google Fonts: Recursive Variable Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Recursive:slnt,wght,CASL,CRSV,MONO@-15..0,300..1000,0..1,0..1,0..1&display=swap" rel="stylesheet" />

  <style>
    /* Global Root Defaults */
    :root {
      color-scheme: light;
      accent-color: #d97706; /* Native checkboxes, radios, ranges match brand */
    }

    * {
      box-sizing: border-box;
      font-family: "Recursive", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Branded Text Selection */
    ::selection {
      background: rgba(217, 119, 6, 0.2);
      color: #1c1917;
    }
  </style>
</head>
```

---

## 3. Typography & Text Balancing

### 3.1 Font Family & Rules
- **Primary Font**: `Recursive` with variable axes (`slnt,wght,CASL,CRSV,MONO`).
- **Fallbacks**: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
- **Prevent Mobile Zoom**: All `<input>`, `<select>`, and `<textarea>` controls must have `font-size: max(1rem, 1em)` or at least `16px` on mobile viewports so iOS Safari does not auto-zoom on focus.

### 3.2 Modern Text Layout & Legibility
Modern web standards improve reading quality and prevent awkward line-wrapping:
- **`text-wrap: balance`**: Apply to titles and headings (`.app-title`, `.panel-title`, `h1`-`h3`) to ensure symmetrical line lengths and prevent lonely words.
- **`text-wrap: pretty`**: Apply to paragraphs, descriptions, and warning notes (`.app-subtitle`, `.download-note`, `p`) to eliminate orphaned runts on the last line.

```css
.app-title,
.panel-title,
h1, h2, h3 {
  text-wrap: balance;
}

.app-subtitle,
.download-note,
.status,
p {
  text-wrap: pretty;
}
```

### 3.3 Typography Scale

| Element | CSS Class | Size (Mobile / Desktop) | Weight | Color | Line Height / Tracking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **App Title** | `.app-title`, `.panel-title` | `1.25rem` / `1.5rem` | `700` | `#1c1917` (Stone 900) | `letter-spacing: -0.02em` |
| **App Subtitle** | `.app-subtitle` | `0.875rem` | `400` | `#78716c` (Stone 500) | `1.4` |
| **Section Label** | `.section-label` | `0.8125rem` (13px) | `500` | `#57534e` (Stone 600) | `margin-bottom: 0.375rem` |
| **Input & Body** | `.field-input`, body | `0.875rem` – `1rem` | `400` | `#1c1917` | `1.5` |
| **Pill / Radio Chip** | `.radio-chip-label` | `0.6875rem` / `0.75rem` | `500` | `#57534e` (Active: `#ffffff`) | `1.2` |
| **Action Button** | `.generate-btn` | `0.9375rem` (15px) | `600` | `#ffffff` | `1.2` |
| **Secondary Button**| `.btn-secondary`, `.download-btn` | `0.75rem` – `0.8125rem` | `500` / `600` | `#57534e` / `#44403c` | `1.2` |
| **Captions / Notes**| `.download-note`, `.dropzone-sub` | `0.6875rem` (11px) – `0.8125rem` | `400` | `#a8a29e` (Stone 400) | `1.6` |

---

## 4. Color Tokens & Contrast

Kewargen's palette is grounded in **Stone** warm neutrals with **Amber** accents, fully meeting **WCAG 1.4.3** (Text Contrast ≥4.5:1) and **WCAG 1.4.11** (Non-text Contrast ≥3:1).

### 4.1 Background & Canvas
- **Page Canvas Background**:
  ```css
  background: linear-gradient(135deg, #fffbeb 0%, #fafaf9 40%, rgba(253, 230, 138, 0.35) 100%);
  ```
- **Card Surface**: `#ffffff` (Pure White)
- **Secondary Panel Surface (Preview Panel)**: `rgba(250, 250, 249, 0.5)`
- **Input & Inactive Control Surface**: `#fafaf9` (Stone 50)
- **Hover Surface**: `#f5f5f4` (Stone 100)

### 4.2 Borders & Dividers
- **Card Outer Border**: `1px solid rgba(231, 229, 228, 0.6)`
- **Input / Component Border**: `1px solid #e7e5e4` (Stone 200)
- **Interactive Border Hover**: `#d6d3d1` (Stone 300)
- **Dashed Dropzone Border**: `2px dashed #d6d3d1`

### 4.3 Accent & Action (Warm Amber)
- **Primary CTA Button Gradient**:
  ```css
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%); /* Amber 600 to Amber 700 */
  ```
- **Primary Button Top Gloss**:
  ```css
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
  ```
- **Active Pill / Chip**: `#78350f` (Amber 900)
- **Focus Rings**:
  ```css
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.12);
  ```
- **Dropzone Active Dragover**:
  ```css
  border-color: #d97706;
  background: rgba(253, 230, 138, 0.15);
  ```

### 4.4 Feedback & Status
- **Information**:
  - Background: `#fffbeb` (Amber 50)
  - Border: `1px solid #fde68a` (Amber 200)
  - Text: `#92400e` (Amber 800)
- **Error / Danger**:
  - Background: `#fef2f2` (Red 50)
  - Border: `1px solid #fecaca` (Red 200)
  - Text: `#b91c1c` (Red 700)
- **Success**:
  - Background: `#f0fdf4` (Green 50)
  - Border: `1px solid #bbf7d0` (Green 200)
  - Text: `#166534` (Green 800)

---

## 5. Elevation, Shadows & Radii

### 5.1 Border Radii
- **Full Pill**: `9999px` (Filter chips, selection pills)
- **Container Card**: `1.25rem` (20px) on desktop (`0` on full-bleed mobile modal view)
- **Secondary Containers**: `0.875rem` (14px) – `1rem` (16px) (Dropzones, preview canvas)
- **CTA Buttons**: `0.75rem` (12px)
- **Inputs & Secondary Buttons**: `0.5rem` (8px)

### 5.2 Shadows
- **Card Floating Elevation**:
  ```css
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 8px 10px -6px rgba(0, 0, 0, 0.1),
              0 4px 12px rgba(120, 53, 15, 0.08); /* Amber ambient tint */
  ```
- **Primary CTA Button**:
  ```css
  box-shadow: 0 2px 8px rgba(180, 83, 9, 0.3);
  ```
  *Hover*: `box-shadow: 0 4px 16px rgba(180, 83, 9, 0.35); transform: translateY(-1px);`  
  *Active*: `box-shadow: 0 1px 4px rgba(180, 83, 9, 0.3); transform: translateY(0);`
- **Secondary / Download Button Hover**:
  ```css
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  ```

---

## 6. Standard Scrollbars & Browser Theming

Follow the standard CSS properties `scrollbar-color` and `scrollbar-width` instead of relying only on deprecated WebKit prefixes.

> [!IMPORTANT]
> **WebKit Animation Bug**: Never animate or add `transition` to `scrollbar-color`. A known WebKit bug causes the entire scrollbar to flicker whenever `scrollbar-color` transitions.

```css
/* Custom Scrollbars with Modern Standard & WebKit Fallback */
.controls-panel,
.preview-panel,
.scroll-container {
  --scrollbar-thumb: rgba(168, 162, 158, 0.4);
  --scrollbar-track: transparent;

  scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  scrollbar-width: thin;
}

/* Fallback for older WebKit browsers that do not support scrollbar-color */
@supports not (scrollbar-color: auto) {
  .controls-panel,
  .preview-panel,
  .scroll-container {
    scrollbar-width: auto;
  }
  .controls-panel::-webkit-scrollbar,
  .preview-panel::-webkit-scrollbar,
  .scroll-container::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  .controls-panel::-webkit-scrollbar-track,
  .preview-panel::-webkit-scrollbar-track,
  .scroll-container::-webkit-scrollbar-track {
    background: transparent;
  }
  .controls-panel::-webkit-scrollbar-thumb,
  .preview-panel::-webkit-scrollbar-thumb,
  .scroll-container::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 3px;
  }
  .controls-panel::-webkit-scrollbar-thumb:hover,
  .preview-panel::-webkit-scrollbar-thumb:hover,
  .scroll-container::-webkit-scrollbar-thumb:hover {
    background: rgba(168, 162, 158, 0.6);
  }
}
```

---

## 7. Forms, Validation & Input Hints

To ensure superior UX and compatibility with mobile keyboards and AI agents:

### 7.1 Modern Validation Timing
Do not use raw `:invalid` for visual borders—it marks required empty fields as red before the user has even touched them.
- Use **`:user-invalid`** instead:
  ```css
  .field-input:user-invalid {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
  }
  ```
- **Validation Event Flow**:
  - `input`: Clear errors as the user edits.
  - `blur`: Validate when the user leaves the field.
  - `submit`: Final gatekeeper; block submission and shift focus to the first invalid field.

### 7.2 Non-Prose Input Attributes
Turn off aggressive OS autocapitalization, autocorrect, and spellchecking on non-prose inputs (usernames, emails, URLs, filenames, codes):
```html
<input
  type="text"
  id="filename"
  name="filename"
  class="field-input"
  autocomplete="off"
  autocorrect="off"
  autocapitalize="none"
  spellcheck="false"
  enterkeyhint="done"
/>
```

### 7.3 Minimum Tap Targets
All interactive controls (buttons, chips, file labels) must provide an accessible tap target of at least **`48px`** (or `min-height: 48px;`) on touch devices (`@media (pointer: coarse)` or mobile).

---

## 8. Layout Archetypes

Kewargen has two standard structural layouts:

### Archetype 1: Split-Panel Studio (Input Left, Live Output Right)
*Best for*: Interactive generators, live previews, configurable items (e.g. `index.html`).

```html
<div class="page-wrapper">
  <div class="qr-card">
    <div class="layout-grid">
      <!-- Left Panel: Controls -->
      <div class="controls-panel">
        <h1 class="panel-title">Kewargen</h1>
        <!-- Form Controls -->
      </div>
      <!-- Right Panel: Output & Preview -->
      <div class="preview-panel">
        <!-- Empty State or Live Render Box -->
      </div>
    </div>
  </div>
</div>
```

```css
.page-wrapper {
  min-height: 100dvh;
  background: linear-gradient(135deg, #fffbeb 0%, #fafaf9 40%, rgba(253, 230, 138, 0.35) 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 1.5rem;
    align-items: center;
  }
}
@media (min-width: 1024px) {
  .page-wrapper {
    padding: 2rem;
  }
}

.qr-card {
  width: 100%;
  max-width: 1536px;
  background: #fff;
  border-radius: 0;
  box-shadow: none;
  border: none;
  overflow: hidden;
  animation: cardUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
@media (min-width: 640px) {
  .qr-card {
    border-radius: 1.25rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                0 8px 10px -6px rgba(0, 0, 0, 0.1),
                0 4px 12px rgba(120, 53, 15, 0.08);
    border: 1px solid rgba(231, 229, 228, 0.6);
  }
}
@media (min-width: 768px) {
  .qr-card {
    height: calc(100dvh - 48px);
    max-height: 740px;
  }
}
@media (min-width: 1024px) {
  .qr-card {
    height: calc(100dvh - 64px);
    max-height: 800px;
  }
}

.layout-grid {
  display: flex;
  flex-direction: column;
  height: auto;
}
@media (min-width: 768px) {
  .layout-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100%;
  }
}
@media (min-width: 1024px) {
  .layout-grid {
    grid-template-columns: 1.1fr 0.9fr;
  }
}

.controls-panel {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-bottom: 1px solid rgba(231, 229, 228, 0.6);
  overflow-y: auto;
}
@media (min-width: 640px) {
  .controls-panel {
    padding: 1.75rem 2rem;
    gap: 1.25rem;
  }
}
@media (min-width: 768px) {
  .controls-panel {
    border-bottom: none;
    border-right: 1px solid rgba(231, 229, 228, 0.6);
    height: 100%;
  }
}

.preview-panel {
  padding: 2rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  background: rgba(250, 250, 249, 0.5);
  overflow-y: auto;
}
@media (min-width: 768px) {
  .preview-panel {
    height: 100%;
  }
}
```

---

### Archetype 2: Centered Task Card (Modal / Workflow)
*Best for*: Dedicated single-purpose utilities, batch converters, upload portals (e.g. `vcf_qr_generator.py`).

```html
<div class="card">
  <div class="card-header">
    <div>
      <h1 class="app-title">Kewargen Batch QR</h1>
      <p class="app-subtitle">Convert contacts CSV into SVG VCF QR codes</p>
    </div>
    <a href="#" class="btn-secondary">Action</a>
  </div>
  <!-- Task controls, Dropzone, and Actions -->
  <button class="generate-btn">Execute Action</button>
  <div class="status info">Status message</div>
</div>
```

```css
.card {
  width: 100%;
  max-width: 580px;
  background: #ffffff;
  border-radius: 1.25rem;
  border: 1px solid rgba(231, 229, 228, 0.6);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 8px 10px -6px rgba(0, 0, 0, 0.1),
              0 4px 12px rgba(120, 53, 15, 0.08);
  padding: 2rem;
  animation: cardUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
```

---

## 9. Component Library & Code Specifications

### 9.1 Primary Action Button (Signature CTA)
```html
<button type="button" class="generate-btn">
  Generate QR Code
</button>
```
```css
.generate-btn {
  width: 100%;
  min-height: 48px;
  padding: 0.75rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(180, 83, 9, 0.3);
  position: relative;
  overflow: hidden;
  font-family: inherit;
  -webkit-tap-highlight-color: transparent;
}

.generate-btn::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
  pointer-events: none;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(180, 83, 9, 0.35);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(180, 83, 9, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

---

### 9.2 Secondary & Download Buttons
```html
<button type="button" class="btn-secondary">
  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
  </svg>
  Action Name
</button>
```
```css
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.5rem;
  border: 1px solid #e7e5e4;
  color: #57534e;
  background: #fafaf9;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f5f5f4;
  border-color: #d6d3d1;
  color: #1c1917;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.btn-secondary:active {
  transform: scale(0.97);
}
```

---

### 9.3 Text Inputs & Form Fields
```html
<div>
  <label for="urlInput" class="section-label">Target URL</label>
  <input
    id="urlInput"
    name="url"
    type="url"
    class="field-input"
    placeholder="https://example.com"
    autocomplete="url"
    autocorrect="off"
    autocapitalize="none"
    spellcheck="false"
  />
</div>
```
```css
.section-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #57534e;
  margin-bottom: 0.375rem;
}

.field-input {
  display: block;
  width: 100%;
  min-height: 42px;
  padding: 0.5rem 0.75rem;
  font-size: max(1rem, 1em); /* Prevents iOS auto-zoom */
  border: 1px solid #e7e5e4;
  border-radius: 0.5rem;
  background: #fafaf9;
  color: #1c1917;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

@media (min-width: 640px) {
  .field-input {
    font-size: 0.875rem;
  }
}

.field-input:focus {
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.12);
}

.field-input:user-invalid {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.field-input::placeholder {
  color: #a8a29e;
}
```

---

### 9.4 Accessible Radio Pill Selector (Chips)
Uses modern CSS `:has()` for clean child-state styling:

```html
<fieldset class="type-fieldset">
  <legend class="section-label">Data type</legend>
  <div class="type-radios">
    <label class="radio-chip">
      <input type="radio" name="dataType" value="link" checked />
      <span class="radio-chip-label">Link</span>
    </label>
    <label class="radio-chip">
      <input type="radio" name="dataType" value="vcard" />
      <span class="radio-chip-label">vCard</span>
    </label>
  </div>
</fieldset>
```
```css
.type-fieldset {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  border: none;
  padding: 0;
  margin: 0;
}

.type-radios {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}
@media (min-width: 640px) {
  .type-radios {
    gap: 0.5rem;
  }
}

.radio-chip {
  cursor: pointer;
}

.radio-chip input {
  position: absolute;
  clip-path: inset(50%);
  overflow: hidden;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  border: 0;
  white-space: nowrap;
}

.radio-chip-label {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border-radius: 9999px;
  border: 1px solid #e7e5e4;
  color: #57534e;
  background: #fafaf9;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;
}
@media (min-width: 640px) {
  .radio-chip-label {
    padding: 0.3rem 0.75rem;
    font-size: 0.75rem;
  }
}

.radio-chip:hover .radio-chip-label {
  border-color: #d6d3d1;
  background: #f5f5f4;
}

.radio-chip:has(:checked) .radio-chip-label {
  background: #78350f;
  color: #fff;
  border-color: #78350f;
  box-shadow: 0 1px 4px rgba(120, 53, 15, 0.25);
}

.radio-chip:has(:focus-visible) .radio-chip-label {
  outline: 2px solid #d97706;
  outline-offset: 2px;
}
```

---

### 9.5 Drag-and-Drop File Zone
```html
<div class="dropzone" id="dropzone" tabindex="0" role="button" aria-label="Upload CSV contacts file">
  <div class="dropzone-icon-wrap">
    <svg fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
    </svg>
  </div>
  <p class="dropzone-title" id="dropTitle">Drag & drop your contacts <strong>.csv</strong> here</p>
  <p class="dropzone-sub" id="dropSub">or click to browse your files</p>
  <input type="file" id="fileInput" accept=".csv,text/csv" class="visually-hidden">
</div>
```
```css
.dropzone {
  border: 2px dashed #d6d3d1;
  border-radius: 0.875rem;
  background: #fafaf9;
  padding: 3rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  outline: none;
}

.dropzone:hover,
.dropzone.dragover {
  border-color: #d97706;
  background: rgba(253, 230, 138, 0.15);
}

.dropzone:focus-visible {
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.12);
}

.dropzone-icon-wrap {
  width: 3.75rem;
  height: 3.75rem;
  aspect-ratio: 1 / 1;
  border-radius: 0.875rem;
  background: #ffffff;
  border: 1px solid #e7e5e4;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.875rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.dropzone-icon-wrap svg {
  width: 1.75rem;
  height: 1.75rem;
  stroke: #d97706;
}

.dropzone-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #1c1917;
  margin: 0;
}

.dropzone-sub {
  font-size: 0.8125rem;
  color: #a8a29e;
  margin-top: 0.35rem;
}
```

---

### 9.6 Canonical Accessible Screen-Reader Class
Always use `clip-path: inset(50%)` to ensure elements stay completely in the accessibility tree:

```css
.visually-hidden,
.sr-only {
  position: absolute;
  clip-path: inset(50%);
  overflow: hidden;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  border: 0;
  white-space: nowrap;
}

.hidden {
  display: none !important;
}

.flex {
  display: flex !important;
}
```

---

## 10. AI Agent Pre-Flight Checklist

Before saving, executing, or presenting any newly created or refactored UI in Kewargen, verify each criterion:

- [ ] **Zero build tools**: Is the code 100% executable directly by any browser without bundling or compilation?
- [ ] **`<meta name="color-scheme" content="light">` present**: Is the color-scheme declared in the HTML head?
- [ ] **Global `accent-color: #d97706` declared**: Do native controls pick up the amber theme automatically?
- [ ] **Standard scrollbars**: Does the scrollbar use `scrollbar-color` and `scrollbar-width: thin` with non-animated styling?
- [ ] **Text balance & pretty wrapping**: Are titles wrapped with `text-wrap: balance` and body/notes with `text-wrap: pretty`?
- [ ] **`:user-invalid` validation**: Are errors styled with `:user-invalid` instead of premature `:invalid`?
- [ ] **Touch target size**: Are buttons and interactive elements at least `48px` in height on touch devices?
- [ ] **Non-prose hints enabled**: Are `autocorrect="off"`, `autocapitalize="none"`, and `spellcheck="false"` on technical inputs?
- [ ] **Canonical `.visually-hidden` used**: Does hidden-input accessibility use `clip-path: inset(50%)`?
- [ ] **Ambient amber shadow applied**: Does the main container card feature `rgba(120, 53, 15, 0.08)` warm ambient elevation?
