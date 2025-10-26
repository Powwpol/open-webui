<script lang="ts">
	/**
	 * Staggered List Layout
	 * 
	 * Creates a visually interesting list with staggered animations and offsets.
	 * Items appear in a cascading effect.
	 */
	
	import { fade, fly } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	
	export let items: any[] = [];
	export let direction: 'left' | 'right' | 'alternate' = 'alternate';
	export let staggerDelay: number = 50;
	export let offsetAmount: number = 20;
	export let animated: boolean = true;
	
	function getOffset(index: number): number {
		if (direction === 'alternate') {
			return index % 2 === 0 ? offsetAmount : -offsetAmount;
		}
		return direction === 'right' ? offsetAmount : -offsetAmount;
	}
	
	function getDelay(index: number): number {
		return animated ? index * staggerDelay : 0;
	}
</script>

<div class="staggered-list">
	{#each items as item, index (item.id || index)}
		<div
			class="staggered-item"
			class:offset-right={getOffset(index) > 0}
			class:offset-left={getOffset(index) < 0}
			style="--offset: {Math.abs(getOffset(index))}px;"
			in:fly={{ 
				x: -getOffset(index) * 2, 
				y: 20,
				duration: 400, 
				delay: getDelay(index), 
				easing: cubicOut 
			}}
		>
			<slot {item} {index} />
		</div>
	{/each}
</div>

<style>
	.staggered-list {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		padding: 1rem;
		width: 100%;
	}
	
	.staggered-item {
		position: relative;
		padding: 1.5rem;
		border-radius: 12px;
		background: var(--color-bg-secondary, #f5f5f5);
		transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
		            box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.staggered-item.offset-right {
		margin-left: var(--offset);
	}
	
	.staggered-item.offset-left {
		margin-right: var(--offset);
	}
	
	.staggered-item:hover {
		transform: translateX(calc(var(--offset) * 0.5)) translateY(-4px);
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
	}
	
	.staggered-item.offset-left:hover {
		transform: translateX(calc(var(--offset) * -0.5)) translateY(-4px);
	}
	
	:global(.dark) .staggered-item {
		background: var(--color-bg-secondary-dark, #1a1a1a);
	}
	
	:global(.dark) .staggered-item:hover {
		box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.staggered-item {
			margin-left: 0 !important;
			margin-right: 0 !important;
		}
		
		.staggered-item:hover {
			transform: translateY(-4px);
		}
	}
</style>

