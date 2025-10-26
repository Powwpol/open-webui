<script lang="ts">
	/**
	 * Asymmetric Grid Layout
	 * 
	 * Creates dynamic, non-uniform grid layouts with varying sizes.
	 * Inspired by modern dashboard designs (Pinterest, Notion, etc.)
	 */
	
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	
	export let items: any[] = [];
	export let columns: number = 3;
	export let gap: number = 16;
	export let minItemHeight: number = 200;
	export let animated: boolean = true;
	
	// Grid patterns for asymmetric layouts
	const patterns = [
		{ span: 1, height: 1 }, // Small
		{ span: 2, height: 1 }, // Wide
		{ span: 1, height: 2 }, // Tall
		{ span: 2, height: 2 }, // Large
		{ span: 1, height: 1 }, // Small
		{ span: 1, height: 1 }, // Small
	];
	
	let gridItems: Array<{ item: any; pattern: typeof patterns[0]; delay: number }> = [];
	
	$: {
		// Assign patterns to items dynamically
		gridItems = items.map((item, index) => ({
			item,
			pattern: patterns[index % patterns.length],
			delay: animated ? index * 50 : 0
		}));
	}
	
	$: gridStyle = `
		display: grid;
		grid-template-columns: repeat(${columns}, 1fr);
		gap: ${gap}px;
		grid-auto-rows: ${minItemHeight}px;
	`;
</script>

<div class="asymmetric-grid" style={gridStyle}>
	{#each gridItems as { item, pattern, delay }, i (item.id || i)}
		<div
			class="grid-item"
			style="
				grid-column: span {pattern.span};
				grid-row: span {pattern.height};
			"
			in:scale={{ duration: 300, delay, easing: cubicOut }}
		>
			<slot {item} index={i} />
		</div>
	{/each}
</div>

<style>
	.asymmetric-grid {
		width: 100%;
		padding: 1rem;
	}
	
	.grid-item {
		position: relative;
		overflow: hidden;
		border-radius: 12px;
		background: var(--color-bg-secondary, #f5f5f5);
		transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
		            box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.grid-item:hover {
		transform: translateY(-4px);
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
	}
	
	:global(.dark) .grid-item {
		background: var(--color-bg-secondary-dark, #1a1a1a);
	}
	
	:global(.dark) .grid-item:hover {
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
	}
	
	/* Responsive */
	@media (max-width: 1024px) {
		.asymmetric-grid {
			grid-template-columns: repeat(2, 1fr) !important;
		}
	}
	
	@media (max-width: 640px) {
		.asymmetric-grid {
			grid-template-columns: 1fr !important;
		}
		
		.grid-item {
			grid-column: span 1 !important;
			grid-row: span 1 !important;
		}
	}
</style>

