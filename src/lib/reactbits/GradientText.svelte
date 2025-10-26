<script lang="ts">
	/**
	 * GradientText - Animated gradient text component adapted from ReactBits
	 * Customized with Pulsai color palette
	 */
	
	export let colors: string[] = ['#FA4616', '#FAC090', '#FA4616']; // Pulsai orange gradient
	export let animationSpeed: number = 8; // seconds
	export let showBorder: boolean = false;
	export let className: string = '';
	
	$: gradientStyle = `
		background-image: linear-gradient(to right, ${colors.join(', ')});
		animation-duration: ${animationSpeed}s;
		background-size: 300% 100%;
	`;
</script>

<div
	class="relative mx-auto flex max-w-fit flex-row items-center justify-center rounded-[1.25rem] font-medium backdrop-blur transition-shadow duration-500 overflow-hidden cursor-pointer {className}"
>
	{#if showBorder}
		<div
			class="absolute inset-0 bg-cover z-0 pointer-events-none animate-gradient"
			style={gradientStyle}
		>
			<div
				class="absolute inset-0 bg-black rounded-[1.25rem] z-[-1]"
				style="width: calc(100% - 2px); height: calc(100% - 2px); left: 50%; top: 50%; transform: translate(-50%, -50%);"
			/>
		</div>
	{/if}
	<div
		class="inline-block relative z-2 text-transparent bg-cover animate-gradient"
		style="{gradientStyle} background-clip: text; -webkit-background-clip: text;"
	>
		<slot />
	</div>
</div>

<style>
	/* Additional Svelte-specific styles if needed */
</style>

