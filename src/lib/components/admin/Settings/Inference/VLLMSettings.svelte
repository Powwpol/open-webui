<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { addBackend, testBackendConnection, listAllModels, type ModelInfo } from '$lib/apis/inference';
	
	export let sessionUser;

	let baseUrl = 'http://localhost:8000';
	let apiKey = '';
	let timeout = 300;
	let testing = false;
	let saving = false;
	let loadingModels = false;
	let models: ModelInfo[] = [];
	let testResult: { success: boolean; latency_ms?: number; error?: string } | null = null;

	const testConnection = async () => {
		testing = true;
		testResult = null;

		try {
			const result = await testBackendConnection(localStorage.token, {
				backend_type: 'vllm',
				base_url: baseUrl,
				api_key: apiKey || undefined,
				timeout
			});

			testResult = result;

			if (result.success) {
				toast.success(`Connection successful! Latency: ${result.latency_ms?.toFixed(1)}ms`);
			} else {
				toast.error(`Connection failed: ${result.error}`);
			}
		} catch (error) {
			toast.error('Connection test failed');
			testResult = { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
		} finally {
			testing = false;
		}
	};

	const saveConfiguration = async () => {
		if (!baseUrl) {
			toast.error('Base URL is required');
			return;
		}

		saving = true;

		try {
			await addBackend(localStorage.token, {
				backend_type: 'vllm',
				base_url: baseUrl,
				api_key: apiKey || undefined,
				timeout
			});

			toast.success('vLLM backend added successfully');
			await loadModels();
		} catch (error) {
			toast.error('Failed to add vLLM backend');
			console.error(error);
		} finally {
			saving = false;
		}
	};

	const loadModels = async () => {
		loadingModels = true;

		try {
			const allModels = await listAllModels(localStorage.token);
			models = allModels.vllm || [];
		} catch (error) {
			console.error('Failed to load models:', error);
		} finally {
			loadingModels = false;
		}
	};

	onMount(() => {
		loadModels();
	});
</script>

<div class="space-y-6">
	<div>
		<h3 class="text-lg font-semibold mb-4">vLLM Configuration</h3>
		<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
			Configure vLLM as a high-performance inference backend. vLLM uses an OpenAI-compatible API.
		</p>
	</div>

	<!-- Configuration Form -->
	<div class="space-y-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
		<div>
			<label for="vllm-url" class="block text-sm font-medium mb-2">
				Base URL <span class="text-red-500">*</span>
			</label>
			<input
				id="vllm-url"
				type="text"
				bind:value={baseUrl}
				placeholder="http://localhost:8000"
				class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-pulsai-primary focus:border-transparent"
			/>
			<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
				The URL where your vLLM server is running (e.g., http://vllm:8000)
			</p>
		</div>

		<div>
			<label for="vllm-api-key" class="block text-sm font-medium mb-2">
				API Key (Optional)
			</label>
			<input
				id="vllm-api-key"
				type="password"
				bind:value={apiKey}
				placeholder="sk-..."
				class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-pulsai-primary focus:border-transparent"
			/>
			<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
				API key if your vLLM server requires authentication
			</p>
		</div>

		<div>
			<label for="vllm-timeout" class="block text-sm font-medium mb-2">
				Timeout (seconds)
			</label>
			<input
				id="vllm-timeout"
				type="number"
				bind:value={timeout}
				min="30"
				max="600"
				class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-pulsai-primary focus:border-transparent"
			/>
			<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
				Request timeout for inference requests (recommended: 300)
			</p>
		</div>

		<!-- Test Result -->
		{#if testResult}
			<div class={`p-3 rounded-lg border ${testResult.success ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'}`}>
				<div class="flex items-center space-x-2">
					{#if testResult.success}
						<svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
						<span class="text-sm font-medium text-green-800 dark:text-green-300">
							Connected successfully! Latency: {testResult.latency_ms?.toFixed(1)}ms
						</span>
					{:else}
						<svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
						</svg>
						<span class="text-sm text-red-800 dark:text-red-300">
							{testResult.error}
						</span>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Action Buttons -->
		<div class="flex space-x-3">
			<button
				on:click={testConnection}
				disabled={testing || !baseUrl}
				class="px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition"
			>
				{#if testing}
					<svg class="inline-block w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Testing...
				{:else}
					Test Connection
				{/if}
			</button>

			<button
				on:click={saveConfiguration}
				disabled={saving || !baseUrl}
				class="px-4 py-2 bg-pulsai-primary hover:bg-pulsai-primary/90 text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition"
			>
				{#if saving}
					<svg class="inline-block w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Saving...
				{:else}
					Save Configuration
				{/if}
			</button>
		</div>
	</div>

	<!-- Available Models -->
	<div>
		<h4 class="text-md font-semibold mb-3">Available Models</h4>
		
		{#if loadingModels}
			<div class="text-center py-4">
				<div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-pulsai-primary"></div>
			</div>
		{:else if models.length > 0}
			<div class="space-y-2">
				{#each models as model}
					<div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
						<div>
							<p class="font-mono text-sm">{model.id}</p>
							{#if model.capabilities && model.capabilities.length > 0}
								<div class="flex space-x-2 mt-1">
									{#each model.capabilities as capability}
										<span class="text-xs px-2 py-0.5 bg-pulsai-primary/10 text-pulsai-primary rounded">
											{capability}
										</span>
									{/each}
								</div>
							{/if}
						</div>
						<span class="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
							Available
						</span>
					</div>
				{/each}
			</div>
		{:else}
			<p class="text-sm text-gray-500 dark:text-gray-400 italic">
				No models detected. Make sure vLLM is running and connected.
			</p>
		{/if}
	</div>

	<!-- Documentation Link -->
	<div class="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
		<div class="flex items-start space-x-3">
			<svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
				<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
			</svg>
			<div>
				<p class="text-sm font-medium text-blue-900 dark:text-blue-300">
					Need help setting up vLLM?
				</p>
				<p class="text-sm text-blue-700 dark:text-blue-400 mt-1">
					Check out the <a href="/docs/vllm-integration" class="underline hover:text-blue-600 dark:hover:text-blue-300">vLLM Integration Guide</a> for installation and configuration instructions.
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	h3, h4 {
		background: var(--pulsai-gradient-orange);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
</style>

