<script lang="ts">
	/**
	 * Masonry Grid Layout
	 * 
	 * Pinterest-style masonry layout with dynamic item heights.
	 * Items flow naturally to fill available space.
	 */
	
	import { onMount, afterUpdate } from 'svelte';
	import { fade } from 'svelte/transition';
	
	export let items: any[] = [];
	export let columnCount: number = 3;
	export let gap: number = 16;
	export let animated: boolean = true;
	
	let containerEl: HTMLDivElement;
	let columnWrappers: HTMLDivElement[] = [];
	
	// Distribute items across columns
	function distributeItems() {
		if (!containerEl) return;
		
		const columns: any[][] = Array.from({ length: columnCount }, () => []);
		const columnHeights: number[] = Array(columnCount).fill(0);
		
		// Place each item in the shortest column
		items.forEach((item, index) => {
			const shortestColumnIndex = columnHeights.indexOf(Math.min(...columnHeights));
			columns[shortestColumnIndex].push({ ...item, originalIndex: index });
			
			// Estimate height (will be recalculated after render)
			columnHeights[shortestColumnIndex] += 300; // Rough estimate
		});
		
		return columns;
	}
	
	$: columns = distributeItems();
	
	// Recalculate on resize
	let resizeTimeout: number;
	function handleResize() {
		clearTimeout(resizeTimeout);
		resizeTimeout = setTimeout(() => {
			columns = distributeItems();
		}, 200);
	}
	
	onMount(() => {
		window.addEventListener('resize', handleResize);
		return () => window.removeEventListener('resize', handleResize);
	});
</script>

<div 
	class="masonry-container" 
	bind:this={containerEl}
	style="--column-count: {columnCount}; --gap: {gap}px;"
>
	{#if columns}
		{#each columns as column, colIndex}
			<div class="masonry-column" bind:this={columnWrappers[colIndex]}>
				{#each column as item, itemIndex (item.id || item.originalIndex)}
					<div 
						class="masonry-item"
						in:fade={{ duration: 300, delay: animated ? item.originalIndex * 30 : 0 }}
					>
						<slot {item} index={item.originalIndex} />
					</div>
				{/each}
			</div>
		{/each}
	{/if}
</div>

<style>
	.masonry-container {
		display: flex;
		gap: var(--gap);
		width: 100%;
		padding: 1rem;
	}
	
	.masonry-column {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: var(--gap);
	}
	
	.masonry-item {
		position: relative;
		border-radius: 12px;
		background: var(--color-bg-secondary, #f5f5f5);
		overflow: hidden;
		transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
		            box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.masonry-item:hover {
		transform: translateY(-4px) scale(1.02);
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
		z-index: 10;
	}
	
	:global(.dark) .masonry-item {
		background: var(--color-bg-secondary-dark, #1a1a1a);
	}
	
	:global(.dark) .masonry-item:hover {
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
	}
	
	/* Responsive */
	@media (max-width: 1024px) {
		.masonry-container {
			--column-count: 2;
		}
	}
	
	@media (max-width: 640px) {
		.masonry-container {
			flex-direction: column;
		}
		
		.masonry-column {
			width: 100%;
		}
	}
</style>

