<script lang="ts">
	import InferenceBackendList from './InferenceBackendList.svelte';
	import VLLMSettings from './VLLMSettings.svelte';
	
	export let sessionUser;

	let activeTab = 'backends';

	const tabs = [
		{ id: 'backends', label: 'Backend Status', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
		{ id: 'vllm', label: 'vLLM Configuration', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }
	];
</script>

<div class="space-y-6">
	<!-- Header -->
	<div>
		<h2 class="text-2xl font-bold gradient-text mb-2">Inference Configuration</h2>
		<p class="text-gray-600 dark:text-gray-400">
			Manage inference backends (Ollama, vLLM) and monitor performance metrics
		</p>
	</div>

	<!-- Tabs -->
	<div class="border-b border-gray-200 dark:border-gray-700">
		<nav class="flex space-x-8" aria-label="Tabs">
			{#each tabs as tab}
				<button
					on:click={() => (activeTab = tab.id)}
					class={`
						flex items-center space-x-2 py-3 px-1 border-b-2 font-medium text-sm transition
						${activeTab === tab.id
							? 'border-pulsai-primary text-pulsai-primary'
							: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
						}
					`}
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={tab.icon} />
					</svg>
					<span>{tab.label}</span>
				</button>
			{/each}
		</nav>
	</div>

	<!-- Tab Content -->
	<div class="pt-4">
		{#if activeTab === 'backends'}
			<InferenceBackendList {sessionUser} />
		{:else if activeTab === 'vllm'}
			<VLLMSettings {sessionUser} />
		{/if}
	</div>

	<!-- Information Box -->
	<div class="mt-8 p-4 bg-gradient-to-r from-pulsai-primary/10 to-pulsai-info/10 border border-pulsai-primary/20 dark:border-pulsai-primary/30 rounded-lg">
		<div class="flex items-start space-x-3">
			<svg class="w-6 h-6 text-pulsai-primary mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
				<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
			</svg>
			<div class="flex-1">
				<h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-1">
					About Inference Backends
				</h4>
				<p class="text-sm text-gray-700 dark:text-gray-300">
					Pulsai supports multiple inference backends for flexibility and performance optimization:
				</p>
				<ul class="mt-2 text-sm text-gray-700 dark:text-gray-300 space-y-1 list-disc list-inside">
					<li><strong>Ollama</strong>: Easy-to-use local inference with model management</li>
					<li><strong>vLLM</strong>: High-performance inference optimized for production workloads</li>
					<li><strong>Load Balancing</strong>: Automatic distribution of requests across available backends</li>
					<li><strong>Failover</strong>: Seamless switching when a backend becomes unavailable</li>
				</ul>
			</div>
		</div>
	</div>
</div>

<style>
	.gradient-text {
		background: var(--pulsai-gradient-orange);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
</style>

