<script lang="ts">
	/**
	 * Animated Card with ReactBits Effects
	 * 
	 * Card component with gradient text, iridescence background, and smooth animations.
	 */
	
	import { GradientText, IridescenceBackground } from '$lib/reactbits';
	import { scale, fade } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	
	export let title: string = '';
	export let subtitle: string = '';
	export let icon: string = '';
	export let gradient: boolean = false;
	export let iridescent: boolean = false;
	export let delay: number = 0;
	export let clickable: boolean = true;
	
	let isHovered = false;
</script>

<div
	class="animated-card"
	class:clickable
	class:hovered={isHovered}
	in:scale={{ duration: 400, delay, easing: cubicOut, start: 0.9 }}
	on:mouseenter={() => isHovered = true}
	on:mouseleave={() => isHovered = false}
	role={clickable ? 'button' : undefined}
	tabindex={clickable ? 0 : undefined}
	on:click
	on:keydown
>
	{#if iridescent}
		<div class="iridescence-layer">
			<IridescenceBackground opacity={0.15} speed={1.0} />
		</div>
	{/if}
	
	<div class="card-content">
		{#if icon}
			<div class="card-icon" in:scale={{ duration: 300, delay: delay + 100 }}>
				{@html icon}
			</div>
		{/if}
		
		{#if title}
			<div class="card-title">
				{#if gradient}
					<GradientText 
						colors={['#FA4616', '#FAC090', '#2751E3', '#43635A', '#00B050']}
						animationSpeed={8}
					>
						{title}
					</GradientText>
				{:else}
					<h3>{title}</h3>
				{/if}
			</div>
		{/if}
		
		{#if subtitle}
			<div class="card-subtitle" in:fade={{ duration: 300, delay: delay + 200 }}>
				<p>{subtitle}</p>
			</div>
		{/if}
		
		<div class="card-slot">
			<slot />
		</div>
	</div>
</div>

<style>
	.animated-card {
		position: relative;
		border-radius: 16px;
		background: white;
		padding: 1.5rem;
		overflow: hidden;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		border: 1px solid rgba(0, 0, 0, 0.08);
	}
	
	.animated-card.clickable {
		cursor: pointer;
	}
	
	.animated-card:hover,
	.animated-card.hovered {
		transform: translateY(-4px);
		box-shadow: 0 16px 32px rgba(0, 0, 0, 0.12);
		border-color: var(--pulsai-primary, #FA4616);
	}
	
	.iridescence-layer {
		position: absolute;
		inset: 0;
		pointer-events: none;
		opacity: 0;
		transition: opacity 0.5s ease;
		z-index: 0;
	}
	
	.animated-card:hover .iridescence-layer,
	.animated-card.hovered .iridescence-layer {
		opacity: 1;
	}
	
	.card-content {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	
	.card-icon {
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--pulsai-gradient-orange, linear-gradient(135deg, #FA4616, #FAC090));
		border-radius: 12px;
		color: white;
	}
	
	.card-title h3 {
		font-size: 1.25rem;
		font-weight: 700;
		margin: 0;
		color: var(--color-text-primary, #000);
	}
	
	.card-subtitle p {
		font-size: 0.875rem;
		color: var(--color-text-secondary, #666);
		margin: 0;
		line-height: 1.5;
	}
	
	.card-slot {
		margin-top: 0.5rem;
	}
	
	/* Dark mode */
	:global(.dark) .animated-card {
		background: var(--color-bg-secondary-dark, #1a1a1a);
		border-color: rgba(255, 255, 255, 0.1);
	}
	
	:global(.dark) .animated-card:hover,
	:global(.dark) .animated-card.hovered {
		box-shadow: 0 16px 32px rgba(0, 0, 0, 0.5);
		border-color: var(--pulsai-primary, #FA4616);
	}
	
	:global(.dark) .card-title h3 {
		color: var(--color-text-primary-dark, #fff);
	}
	
	:global(.dark) .card-subtitle p {
		color: var(--color-text-secondary-dark, #aaa);
	}
</style>

