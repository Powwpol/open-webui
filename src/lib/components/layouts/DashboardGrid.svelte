<script lang="ts">
	/**
	 * Dashboard Grid Layout
	 * 
	 * Combines multiple layout types for a dynamic dashboard experience.
	 * Showcases Pulsai's modern, non-uniform UI design.
	 */
	
	import AsymmetricGrid from './AsymmetricGrid.svelte';
	import MasonryGrid from './MasonryGrid.svelte';
	import BentoBox from './BentoBox.svelte';
	import AnimatedCard from './AnimatedCard.svelte';
	
	export let layoutType: 'asymmetric' | 'masonry' | 'bento' = 'bento';
	export let items: any[] = [];
	export let animated: boolean = true;
</script>

<div class="dashboard-grid">
	{#if layoutType === 'asymmetric'}
		<AsymmetricGrid {items} {animated}>
			<svelte:fragment slot="default" let:item let:index>
				<AnimatedCard
					title={item.title}
					subtitle={item.subtitle}
					icon={item.icon}
					gradient={index % 3 === 0}
					iridescent={index % 2 === 0}
					delay={index * 50}
				>
					{#if item.content}
						<div class="item-content">
							{@html item.content}
						</div>
					{/if}
				</AnimatedCard>
			</svelte:fragment>
		</AsymmetricGrid>
	
	{:else if layoutType === 'masonry'}
		<MasonryGrid {items} {animated}>
			<svelte:fragment slot="default" let:item let:index>
				<AnimatedCard
					title={item.title}
					subtitle={item.subtitle}
					icon={item.icon}
					gradient={index % 4 === 0}
					delay={index * 30}
				>
					{#if item.content}
						<div class="item-content">
							{@html item.content}
						</div>
					{/if}
				</AnimatedCard>
			</svelte:fragment>
		</MasonryGrid>
	
	{:else if layoutType === 'bento'}
		<BentoBox sections={items} {animated}>
			{#each items as section}
				<svelte:fragment slot={section.id}>
					<AnimatedCard
						title={section.title || ''}
						subtitle={section.subtitle || ''}
						icon={section.icon || ''}
						gradient={section.gradient !== false}
						iridescent={section.iridescent !== false}
					>
						{#if section.content}
							<div class="item-content">
								{@html section.content}
							</div>
						{/if}
					</AnimatedCard>
				</svelte:fragment>
			{/each}
		</BentoBox>
	{/if}
</div>

<style>
	.dashboard-grid {
		width: 100%;
		min-height: 100vh;
	}
	
	.item-content {
		padding: 1rem 0;
		font-size: 0.95rem;
		line-height: 1.6;
		color: var(--color-text-primary, #333);
	}
	
	:global(.dark) .item-content {
		color: var(--color-text-primary-dark, #ddd);
	}
</style>

