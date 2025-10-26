# Pulsai ReactBits Components

Svelte adaptations of ReactBits components customized with Pulsai's color palette.

## Components

### 1. GradientText

Animated gradient text with customizable colors and animation speed.

**Usage:**
```svelte
<script>
	import { GradientText, PULSAI_GRADIENTS } from '$lib/reactbits';
</script>

<!-- Simple usage with default Pulsai orange gradient -->
<GradientText>
	<h1>Welcome to Pulsai</h1>
</GradientText>

<!-- Custom gradient colors -->
<GradientText colors={PULSAI_GRADIENTS.blueGreen} animationSpeed={12}>
	<span class="text-4xl font-bold">Model Selector</span>
</GradientText>

<!-- With border -->
<GradientText showBorder={true} colors={PULSAI_GRADIENTS.accent}>
	<button>Click Me</button>
</GradientText>
```

**Props:**
- `colors`: string[] - Array of color stops (default: Pulsai orange gradient)
- `animationSpeed`: number - Animation duration in seconds (default: 8)
- `showBorder`: boolean - Show animated border (default: false)
- `className`: string - Additional CSS classes

**Predefined Gradients:**
- `PULSAI_GRADIENTS.orange` - Primary orange gradient
- `PULSAI_GRADIENTS.blueGreen` - Blue to green gradient
- `PULSAI_GRADIENTS.accent` - Accent green gradient
- `PULSAI_GRADIENTS.full` - Full color spectrum

### 2. IridescenceBackground

Animated iridescent background effect for dark mode. Automatically hidden in light mode.

**Usage:**
```svelte
<script>
	import { IridescenceBackground } from '$lib/reactbits';
</script>

<!-- In your main chat container -->
<div class="relative min-h-screen bg-gray-900 dark:bg-black">
	<IridescenceBackground opacity={0.15} speed={20} />
	
	<div class="relative z-10">
		<!-- Your content here -->
		<h1>Chat Interface</h1>
	</div>
</div>
```

**Props:**
- `opacity`: number - Background opacity (default: 0.15, recommended: 0.10-0.20 for readability)
- `speed`: number - Animation duration in seconds (default: 20)
- `colors`: string[] - Array of colors for gradient (default: Pulsai palette)
- `className`: string - Additional CSS classes

**Notes:**
- Only visible in dark mode (automatically hidden in light mode)
- Uses CSS animations (no WebGL, better performance)
- Uses Pulsai colors by default: #FA4616, #FAC090, #2751E3, #43635A

## Pulsai Color Palette

```typescript
const PULSAI_COLORS = {
	primary: '#FA4616',       // Orange foncé - Primary accent
	primaryLight: '#FAC090',  // Orange clair - Secondary accent
	success: '#00B050',       // Vert - Success/validation
	error: '#FF0000',         // Rouge - Error/warning
	info: '#2751E3',          // Bleu foncé - Links/info
	dark: '#000000',          // Noir - Dark background
	dark2: '#EAEAEA',         // Gris foncé - Dark text
	light: '#FFFFFF',         // Blanc - Light background
	light2: '#F5F5F5',        // Gris clair - Light text
	accent: '#43635A'         // Vert foncé - Subtle highlight
};
```

## Tailwind CSS Integration

The following utilities are available after importing the updated `tailwind.config.js`:

### Colors
```html
<div class="bg-pulsai-primary text-pulsai-light">Primary Button</div>
<div class="border-pulsai-success">Success Border</div>
```

### Font Sizes
```html
<nav class="text-nav">Navigation Item</nav>
<h2 class="text-section">Section Header</h2>
<span class="text-nav-sub">Submenu Item</span>
```

### Animations
```html
<div class="animate-gradient">Animated Gradient</div>
<div class="animate-fade-in">Fade In</div>
<div class="animate-slide-in">Slide In</div>
```

### Gradients
```html
<div class="bg-pulsai-gradient-orange">Orange Gradient</div>
<div class="bg-pulsai-gradient-blue-green">Blue-Green Gradient</div>
```

## CSS Variables

Use these CSS variables in custom styles:

```css
.custom-button {
	background: var(--pulsai-gradient-orange);
	color: var(--pulsai-light);
	border: 2px solid var(--pulsai-primary);
}

.custom-text {
	color: var(--pulsai-info);
}

/* Responsive iridescence */
.chat-container {
	--pulsai-iridescence-opacity: 0.15; /* Override default */
}
```

## Application Examples

### Chat Interface with Iridescence

```svelte
<script>
	import { IridescenceBackground } from '$lib/reactbits';
</script>

<div class="relative min-h-screen dark:bg-gray-950">
	<!-- Background effect (dark mode only) -->
	<IridescenceBackground />
	
	<!-- Main content -->
	<div class="relative z-10 container mx-auto p-4">
		<div class="chat-messages space-y-4">
			<!-- Chat messages -->
		</div>
	</div>
</div>
```

### Model Selector with Gradient Text

```svelte
<script>
	import { GradientText, PULSAI_GRADIENTS } from '$lib/reactbits';
	
	let models = ['GPT-4', 'Claude', 'Llama'];
</script>

<div class="model-selector">
	<GradientText colors={PULSAI_GRADIENTS.blueGreen}>
		<h2 class="text-2xl font-bold">Select Model</h2>
	</GradientText>
	
	<div class="model-list mt-4">
		{#each models as model}
			<button class="model-button">
				<GradientText animationSpeed={10}>
					{model}
				</GradientText>
			</button>
		{/each}
	</div>
</div>
```

### Settings Section Headers

```svelte
<script>
	import { GradientText } from '$lib/reactbits';
</script>

<section class="settings-section">
	<GradientText>
		<h2 class="section-header">MCP Servers</h2>
	</GradientText>
	
	<div class="settings-content">
		<!-- Settings form -->
	</div>
</section>

<style>
	.section-header {
		font-size: 20px;
		font-weight: 700;
	}
</style>
```

## Performance Considerations

1. **IridescenceBackground**: Uses CSS animations (no WebGL), very performant
2. **GradientText**: Lightweight CSS gradient animation
3. **Dark Mode Only**: Iridescence automatically disabled in light mode
4. **Opacity**: Keep iridescence opacity between 0.10-0.20 for best readability

## Browser Compatibility

- ✅ Chrome/Edge (100+)
- ✅ Firefox (100+)
- ✅ Safari (15.4+)
- ✅ Mobile browsers (iOS Safari 15.4+, Chrome Android 100+)

## Migration from Pulsai

These components are drop-in replacements with Pulsai branding. Simply import and use:

```svelte
// Before
<h1 class="text-xl">Pulsai</h1>

// After
<GradientText>
	<h1 class="text-xl">Pulsai</h1>
</GradientText>
```

## Next Steps

1. Apply `IridescenceBackground` to main chat container
2. Use `GradientText` for:
   - App title/logo
   - Section headers in settings
   - Model selector labels
   - Button text for primary actions
3. Update menu font sizes using Tailwind classes (`text-nav`, `text-nav-sub`, `text-section`)
4. Apply Pulsai color classes throughout the app

## Support

For issues or questions about these components, refer to:
- ReactBits original docs: https://reactbits.dev/
- Pulsai documentation: (your docs path)
- Tailwind CSS docs: https://tailwindcss.com/docs

