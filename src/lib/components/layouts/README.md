# Pulsai Non-Uniform Layouts

Modern, dynamic layout components for a visually engaging UI experience.

---

## Components

### 1. AsymmetricGrid

Creates dynamic, non-uniform grid layouts with varying sizes.

**Features:**
- Variable column spans (1-2 columns)
- Variable row spans (1-2 rows)
- Hover animations
- Responsive (adapts to mobile)

**Usage:**
```svelte
<AsymmetricGrid items={myItems} columns={3} gap={16} animated={true}>
  <svelte:fragment slot="default" let:item let:index>
    <div>
      <h3>{item.title}</h3>
      <p>{item.content}</p>
    </div>
  </svelte:fragment>
</AsymmetricGrid>
```

**Props:**
- `items`: Array of items to display
- `columns`: Number of columns (default: 3)
- `gap`: Gap between items in pixels (default: 16)
- `minItemHeight`: Minimum item height in pixels (default: 200)
- `animated`: Enable staggered animations (default: true)

---

### 2. MasonryGrid

Pinterest-style masonry layout with dynamic item heights.

**Features:**
- Items flow naturally to fill space
- Balanced column distribution
- Auto-reflow on resize
- Smooth animations

**Usage:**
```svelte
<MasonryGrid items={myItems} columnCount={3} gap={16} animated={true}>
  <svelte:fragment slot="default" let:item let:index>
    <div class="masonry-item">
      <img src={item.image} alt={item.title} />
      <h4>{item.title}</h4>
    </div>
  </svelte:fragment>
</MasonryGrid>
```

**Props:**
- `items`: Array of items
- `columnCount`: Number of columns (default: 3)
- `gap`: Gap in pixels (default: 16)
- `animated`: Enable animations (default: true)

---

### 3. StaggeredList

Visually interesting list with staggered offsets and animations.

**Features:**
- Alternating or directional offsets
- Cascading entrance animations
- Configurable stagger delay
- Responsive (removes offsets on mobile)

**Usage:**
```svelte
<StaggeredList 
  items={myItems} 
  direction="alternate" 
  staggerDelay={50}
  offsetAmount={20}
>
  <svelte:fragment slot="default" let:item let:index>
    <div>{item.content}</div>
  </svelte:fragment>
</StaggeredList>
```

**Props:**
- `items`: Array of items
- `direction`: 'left' | 'right' | 'alternate' (default: 'alternate')
- `staggerDelay`: Delay between items in ms (default: 50)
- `offsetAmount`: Offset in pixels (default: 20)
- `animated`: Enable animations (default: true)

---

### 4. BentoBox

Japanese-inspired bento box layout with distinct sections.

**Features:**
- Pre-defined size variants (small, medium, large, wide, tall)
- Gradient backgrounds
- Top border accent on hover
- Responsive grid

**Usage:**
```svelte
<BentoBox sections={bentoSections} animated={true}>
  <svelte:fragment slot="section-1">
    <h3>Quick Stats</h3>
    <p>123 active users</p>
  </svelte:fragment>
  <svelte:fragment slot="section-2">
    <h3>Recent Activity</h3>
  </svelte:fragment>
</BentoBox>
```

**Section Object:**
```typescript
{
  id: string;
  size: 'small' | 'medium' | 'large' | 'wide' | 'tall';
  content: any;
}
```

**Size Guide:**
- `small`: 1 column × 1 row
- `medium`: 2 columns × 1 row
- `large`: 2 columns × 2 rows
- `wide`: 3 columns × 1 row
- `tall`: 1 column × 2 rows

---

### 5. AnimatedCard

Card component with ReactBits effects (gradient text, iridescence).

**Features:**
- Optional gradient text (Pulsai colors)
- Optional iridescent background on hover
- Icon support
- Smooth scale animations
- Clickable with proper a11y

**Usage:**
```svelte
<AnimatedCard
  title="Analytics"
  subtitle="Track your performance"
  icon="📊"
  gradient={true}
  iridescent={true}
  delay={100}
  clickable={true}
  on:click={handleClick}
>
  <p>Card content goes here</p>
</AnimatedCard>
```

**Props:**
- `title`: Card title (string)
- `subtitle`: Card subtitle (string)
- `icon`: Icon HTML or emoji (string)
- `gradient`: Use gradient text for title (default: false)
- `iridescent`: Show iridescent background on hover (default: false)
- `delay`: Animation delay in ms (default: 0)
- `clickable`: Make card clickable (default: true)

---

### 6. DashboardGrid

Combines multiple layout types for a complete dashboard experience.

**Features:**
- Switches between asymmetric, masonry, and bento layouts
- Auto-wraps items in AnimatedCards
- Distributes gradient and iridescence effects
- Fully responsive

**Usage:**
```svelte
<DashboardGrid
  layoutType="bento"
  items={dashboardItems}
  animated={true}
/>
```

**Props:**
- `layoutType`: 'asymmetric' | 'masonry' | 'bento' (default: 'bento')
- `items`: Array of dashboard items
- `animated`: Enable animations (default: true)

**Item Object:**
```typescript
{
  id: string;
  title: string;
  subtitle?: string;
  icon?: string;
  content?: string;
  size?: 'small' | 'medium' | 'large' | 'wide' | 'tall'; // For bento
  gradient?: boolean; // Override gradient setting
  iridescent?: boolean; // Override iridescent setting
}
```

---

## Pulsai Color Palette

All layouts use Pulsai's custom color scheme:

```css
--pulsai-primary: #FA4616;       /* Orange */
--pulsai-primary-light: #FAC090; /* Light Orange */
--pulsai-success: #00B050;       /* Green */
--pulsai-info: #2751E3;          /* Blue */
--pulsai-accent: #43635A;        /* Teal */
```

**Gradients:**
```css
--pulsai-gradient-orange: linear-gradient(135deg, #FA4616, #FAC090);
--pulsai-gradient-blue-green: linear-gradient(135deg, #2751E3, #00B050);
--pulsai-gradient-full: linear-gradient(135deg, #FA4616, #FAC090, #2751E3, #43635A, #00B050);
```

---

## Responsive Design

All layouts are fully responsive:

- **Desktop** (> 1024px): Full layouts
- **Tablet** (640px - 1024px): 2 columns
- **Mobile** (< 640px): Single column, simplified layouts

---

## Animations

Powered by Svelte transitions and ReactBits:

- **Scale**: Entrance animations
- **Fade**: Subtle content reveals
- **Fly**: Directional entrances
- **Stagger**: Cascading effects

**Animation Easing:**
- `cubicOut`: Smooth, natural deceleration

**Performance:**
- CSS transforms (GPU-accelerated)
- RequestAnimationFrame for complex effects
- Lazy loading ready

---

## Dark Mode

All components support dark mode via CSS custom properties:

```css
:global(.dark) .component {
  background: var(--color-bg-secondary-dark, #1a1a1a);
  color: var(--color-text-primary-dark, #fff);
}
```

**Dark Mode Classes:**
- `.dark` on root element
- Automatic theme detection
- Smooth transitions

---

## Examples

### Modern Dashboard
```svelte
<DashboardGrid
  layoutType="bento"
  items={[
    { id: '1', title: 'Total Users', content: '1,234', size: 'small', gradient: true },
    { id: '2', title: 'Revenue', content: '$45,678', size: 'medium', iridescent: true },
    { id: '3', title: 'Activity Feed', size: 'tall' },
    { id: '4', title: 'Quick Actions', size: 'wide', gradient: true }
  ]}
/>
```

### Image Gallery
```svelte
<MasonryGrid items={photos}>
  <svelte:fragment slot="default" let:item>
    <img src={item.url} alt={item.title} class="gallery-image" />
  </svelte:fragment>
</MasonryGrid>
```

### Feature List
```svelte
<StaggeredList items={features} direction="alternate">
  <svelte:fragment slot="default" let:item>
    <AnimatedCard
      title={item.name}
      subtitle={item.description}
      icon={item.icon}
      gradient={true}
    />
  </svelte:fragment>
</StaggeredList>
```

---

## Best Practices

1. **Use semantic HTML** inside slots
2. **Limit items** for performance (< 100 items per layout)
3. **Test responsiveness** on all breakpoints
4. **Enable animations** selectively (disable on mobile if needed)
5. **Combine layouts** for visual hierarchy

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Required Features:**
- CSS Grid
- CSS Custom Properties
- CSS Transitions
- Intersection Observer (for lazy loading)

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Part of:** Pulsai UI System

