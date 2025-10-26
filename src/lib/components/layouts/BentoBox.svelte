<script lang="ts">
	/**
	 * Bento Box Layout
	 * 
	 * Japanese-inspired bento box layout with distinct sections.
	 * Popular in modern dashboard designs (Apple, Notion, Linear).
	 */
	
	import { fade, scale } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	
	export let sections: Array<{
		id: string;
		size: 'small' | 'medium' | 'large' | 'wide' | 'tall';
		content: any;
	}> = [];
	export let animated: boolean = true;
	
	// Map sizes to grid spans
	const sizeMap = {
		small: { cols: 1, rows: 1 },
		medium: { cols: 2, rows: 1 },
		large: { cols: 2, rows: 2 },
		wide: { cols: 3, rows: 1 },
		tall: { cols: 1, rows: 2 }
	};
	
	function getGridStyle(size: typeof sections[0]['size']) {
		const { cols, rows } = sizeMap[size];
		return `grid-column: span ${cols}; grid-row: span ${rows};`;
	}
</script>

<div class="bento-container">
	{#each sections as section, index (section.id)}
		<div
			class="bento-box bento-{section.size}"
			style={getGridStyle(section.size)}
			in:scale={{ 
				duration: 400, 
				delay: animated ? index * 60 : 0, 
				easing: cubicOut,
				start: 0.9
			}}
		>
			<slot name={section.id} content={section.content} {index}>
				<div class="bento-content">
					{@html section.content || ''}
				</div>
			</slot>
		</div>
	{/each}
</div>

<style>
	.bento-container {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		grid-auto-rows: 200px;
		gap: 1rem;
		padding: 1rem;
		width: 100%;
	}
	
	.bento-box {
		position: relative;
		border-radius: 16px;
		background: linear-gradient(135deg, 
			var(--color-bg-secondary, #f5f5f5) 0%, 
			var(--color-bg-tertiary, #e0e0e0) 100%
		);
		padding: 1.5rem;
		overflow: hidden;
		transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
		            box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		
		/* Subtle border */
		border: 1px solid rgba(0, 0, 0, 0.05);
	}
	
	.bento-box:hover {
		transform: translateY(-4px);
		box-shadow: 0 16px 32px rgba(0, 0, 0, 0.12);
		border-color: var(--pulsai-primary, #FA4616);
	}
	
	.bento-box::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: var(--pulsai-gradient-orange, linear-gradient(90deg, #FA4616, #FAC090));
		opacity: 0;
		transition: opacity 0.3s ease;
	}
	
	.bento-box:hover::before {
		opacity: 1;
	}
	
	.bento-content {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	/* Dark mode */
	:global(.dark) .bento-box {
		background: linear-gradient(135deg, 
			var(--color-bg-secondary-dark, #1a1a1a) 0%, 
			var(--color-bg-tertiary-dark, #252525) 100%
		);
		border-color: rgba(255, 255, 255, 0.1);
	}
	
	:global(.dark) .bento-box:hover {
		box-shadow: 0 16px 32px rgba(0, 0, 0, 0.5);
		border-color: var(--pulsai-primary, #FA4616);
	}
	
	/* Responsive */
	@media (max-width: 1024px) {
		.bento-container {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.bento-wide {
			grid-column: span 2 !important;
		}
	}
	
	@media (max-width: 640px) {
		.bento-container {
			grid-template-columns: 1fr;
			grid-auto-rows: 180px;
		}
		
		.bento-box {
			grid-column: span 1 !important;
			grid-row: span 1 !important;
		}
	}
</style>

