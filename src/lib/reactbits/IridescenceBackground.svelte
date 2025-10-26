<script lang="ts">
	/**
	 * IridescenceBackground - Animated iridescent background for dark mode
	 * Simplified CSS version using Pulsai colors
	 * Original uses WebGL, this is a performant CSS alternative
	 */
	
	import { onMount } from 'svelte';
	
	export let opacity: number = 0.15; // Light opacity for readability
	export let speed: number = 20; // Animation duration in seconds
	export let colors: string[] = ['#FA4616', '#FAC090', '#2751E3', '#43635A']; // Pulsai colors
	export let className: string = '';
	
	let containerRef: HTMLDivElement;
	
	$: gradientColors = colors.join(', ');
</script>

<div
	bind:this={containerRef}
	class="iridescence-container {className}"
	style="
		--iridescence-opacity: {opacity};
		--animation-speed: {speed}s;
		--gradient-colors: {gradientColors};
	"
>
	<div class="iridescence-layer iridescence-1" />
	<div class="iridescence-layer iridescence-2" />
	<div class="iridescence-layer iridescence-3" />
</div>

<style>
	.iridescence-container {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		overflow: hidden;
		pointer-events: none;
		opacity: var(--iridescence-opacity);
		z-index: 0;
	}
	
	.iridescence-layer {
		position: absolute;
		width: 200%;
		height: 200%;
		background: conic-gradient(
			from 0deg,
			#FA4616,
			#FAC090,
			#2751E3,
			#43635A,
			#00B050,
			#FA4616
		);
		filter: blur(80px);
		opacity: 0.6;
	}
	
	.iridescence-1 {
		top: -50%;
		left: -50%;
		animation: iridescence-rotate var(--animation-speed, 20s) linear infinite;
	}
	
	.iridescence-2 {
		top: -50%;
		left: -50%;
		animation: iridescence-rotate var(--animation-speed, 20s) linear infinite reverse;
		animation-delay: -6.67s;
	}
	
	.iridescence-3 {
		top: -50%;
		left: -50%;
		animation: iridescence-pulse calc(var(--animation-speed, 20s) / 2) ease-in-out infinite;
		transform-origin: center;
	}
	
	@keyframes iridescence-rotate {
		from {
			transform: rotate(0deg) scale(1);
		}
		50% {
			transform: rotate(180deg) scale(1.1);
		}
		to {
			transform: rotate(360deg) scale(1);
		}
	}
	
	@keyframes iridescence-pulse {
		0%, 100% {
			opacity: 0.6;
			transform: scale(1);
		}
		50% {
			opacity: 0.8;
			transform: scale(1.05);
		}
	}
	
	/* Only show in dark mode */
	:global(.light) .iridescence-container {
		display: none;
	}
</style>

