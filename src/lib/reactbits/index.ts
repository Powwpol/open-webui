/**
 * ReactBits Components for Pulsai
 * 
 * Svelte adaptations of ReactBits components with Pulsai color palette integration
 */

export { default as GradientText } from './GradientText.svelte';
export { default as IridescenceBackground } from './IridescenceBackground.svelte';

// Pulsai Color Presets
export const PULSAI_COLORS = {
	primary: '#FA4616',
	primaryLight: '#FAC090',
	success: '#00B050',
	error: '#FF0000',
	info: '#2751E3',
	dark: '#000000',
	dark2: '#EAEAEA',
	light: '#FFFFFF',
	light2: '#F5F5F5',
	accent: '#43635A'
};

// Predefined gradient combinations for GradientText
export const PULSAI_GRADIENTS = {
	orange: ['#FA4616', '#FAC090', '#FA4616'],
	blueGreen: ['#2751E3', '#00B050', '#2751E3'],
	accent: ['#43635A', '#00B050', '#43635A'],
	full: ['#FA4616', '#FAC090', '#2751E3', '#43635A', '#00B050']
};

