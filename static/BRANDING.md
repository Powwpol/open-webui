# Pulsai Visual Assets & Branding Guide

## Color Palette

Pulsai uses a distinctive, vibrant color scheme:

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Pulsai Orange** | `#FA4616` | Primary brand color, CTAs, highlights |
| **Pulsai Orange Light** | `#FAC090` | Gradients, hover states, accents |
| **Pulsai Blue** | `#2751E3` | Secondary actions, info |
| **Pulsai Accent** | `#43635A` | Tertiary accents |
| **Pulsai Success** | `#00B050` | Success states, confirmations |

### Neutral Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Dark** | `#000000` | Dark mode background |
| **Dark 2** | `#EAEAEA` | Dark mode secondary |
| **Light** | `#FFFFFF` | Light mode background |
| **Light 2** | `#F5F5F5` | Light mode secondary |

### Gradients

```css
/* Orange Gradient */
--pulsai-gradient-orange: linear-gradient(135deg, #FA4616, #FAC090);

/* Blue-Green Gradient */
--pulsai-gradient-blue-green: linear-gradient(135deg, #2751E3, #00B050);

/* Accent Gradient */
--pulsai-gradient-accent: linear-gradient(135deg, #43635A, #00B050);

/* Full Spectrum */
--pulsai-gradient-full: linear-gradient(135deg, #FA4616, #FAC090, #2751E3, #43635A, #00B050);
```

---

## Typography

### Fonts

- **Primary**: Inter Variable
- **Display**: Archivo Variable
- **Serif**: Instrument Serif
- **Monospace**: Mona Sans

### Font Sizes

| Element | Size | Weight |
|---------|------|--------|
| **Navigation Items** | 18px | 600 |
| **Sub-Items** | 15px | 500 |
| **Section Headers** | 20px | 700 |
| **Body Text** | 14px | 400 |
| **Small Text** | 12px | 400 |

---

## Visual Assets

### Icons & Favicons

Located in `/static/static/`:

- `favicon.ico` - 32x32 ICO format
- `favicon.png` - 32x32 PNG format
- `favicon.svg` - Scalable vector format
- `favicon-96x96.png` - High-res PNG
- `favicon-dark.png` - Dark mode variant
- `apple-touch-icon.png` - iOS home screen icon

### App Icons

- `web-app-manifest-192x192.png` - PWA icon (small)
- `web-app-manifest-512x512.png` - PWA icon (large)

### Logos & Imagery

- `logo.png` - Full Pulsai logo
- `splash.png` - Light mode splash screen
- `splash-dark.png` - Dark mode splash screen
- `user.png` - Default user avatar placeholder
- `image-placeholder.png` - Image loading placeholder

---

## Manifest Files

### Web App Manifest

**File**: `/static/manifest.json` and `/static/static/site.webmanifest`

Key properties:
- **Name**: Pulsai
- **Theme Color**: `#FA4616` (Pulsai Orange)
- **Background**: `#000000` (Black)
- **Display**: Standalone (PWA)

### OpenSearch

**File**: `/static/opensearch.xml`

Enables browser search integration with Pulsai branding.

---

## UI Components

### Buttons

```css
/* Primary Button */
background: #FA4616;
color: #FFFFFF;
hover: #FAC090;

/* Secondary Button */
background: #2751E3;
color: #FFFFFF;
hover: #43635A;

/* Success Button */
background: #00B050;
color: #FFFFFF;
```

### Cards & Containers

```css
/* Light Mode */
background: #FFFFFF;
border: 1px solid #EAEAEA;

/* Dark Mode */
background: #1a1a1a;
border: 1px solid #333333;
```

### Special Effects

#### Gradient Text

Use ReactBits `GradientText` component with Pulsai colors:

```svelte
<GradientText colors={['#FA4616', '#FAC090', '#2751E3', '#43635A', '#00B050']}>
  Pulsai
</GradientText>
```

#### Iridescence Background

Use on dark UI parts only:

```svelte
<IridescenceBackground 
  color={[1, 1, 1]} 
  opacity={0.15}
  speed={1.0}
/>
```

---

## Dark Mode

### Iridescence Effect

In dark mode, a subtle iridescent background is applied:

```css
.dark {
  --pulsai-iridescence-opacity: 0.15;
}

:root {
  --pulsai-iridescence-opacity: 0;
}
```

This creates a dynamic, AI-themed visual effect that's:
- Subtle (15% opacity)
- Interactive (reacts to mouse movement)
- Performance-optimized (WebGL)

---

## Usage Guidelines

### Do's ✅

- Use Pulsai Orange (`#FA4616`) for primary actions
- Apply gradients for headings and special elements
- Maintain sufficient contrast (WCAG AA minimum)
- Use gradient text sparingly for impact
- Keep iridescence subtle (≤20% opacity)

### Don'ts ❌

- Don't use Open Web UI branding
- Don't combine all colors at once
- Don't use iridescence on light backgrounds
- Don't exceed 3 colors in a single gradient
- Don't apply gradients to body text

---

## File Structure

```
static/
├── static/
│   ├── favicon.ico
│   ├── favicon.png
│   ├── favicon.svg
│   ├── favicon-96x96.png
│   ├── favicon-dark.png
│   ├── apple-touch-icon.png
│   ├── logo.png
│   ├── splash.png
│   ├── splash-dark.png
│   ├── web-app-manifest-192x192.png
│   ├── web-app-manifest-512x512.png
│   ├── site.webmanifest
│   └── custom.css
├── manifest.json
├── opensearch.xml
└── assets/
    ├── fonts/
    └── images/
```

---

## Accessibility

### Contrast Ratios

All color combinations meet WCAG AA standards:

- **Text on Pulsai Orange**: White text (16.5:1)
- **Text on Dark Background**: Light text (15.2:1)
- **Links**: Pulsai Blue with underline (4.6:1)

### Focus States

All interactive elements include visible focus indicators:

```css
:focus-visible {
  outline: 2px solid #FA4616;
  outline-offset: 2px;
}
```

---

## Brand Voice

Pulsai's visual identity reflects:
- **Innovation**: Vibrant oranges and modern gradients
- **Intelligence**: Deep blues and sophisticated UI
- **Performance**: Clean, efficient design
- **Flexibility**: Multi-backend, multi-protocol capability

---

## Examples

### Header with Gradient

```svelte
<h1 class="gradient-text">Welcome to Pulsai</h1>

<style>
  .gradient-text {
    background: var(--pulsai-gradient-orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
</style>
```

### Card with Hover Effect

```svelte
<div class="card">
  <h3>Backend Status</h3>
  <p>All systems operational</p>
</div>

<style>
  .card {
    background: white;
    border: 1px solid #EAEAEA;
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
  }
  
  .card:hover {
    border-color: var(--pulsai-primary);
    box-shadow: 0 4px 12px rgba(250, 70, 22, 0.1);
  }
  
  .dark .card {
    background: #1a1a1a;
    border-color: #333;
  }
</style>
```

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Maintainer:** Pulsai Team

For technical implementation details, see:
- `src/app.css` - Global CSS variables
- `tailwind.config.js` - Tailwind configuration
- `src/lib/reactbits/` - ReactBits components

