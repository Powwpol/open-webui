<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getBackendsStatus, getBackendsHealth, type BackendStatus, type BackendHealth } from '$lib/apis/inference';
	
	export let sessionUser;

	let backends: Record<string, BackendStatus> = {};
	let health: Record<string, BackendHealth> = {};
	let loading = true;
	let refreshInterval: any;

	const statusColors = {
		healthy: 'bg-green-500',
		degraded: 'bg-yellow-500',
		unhealthy: 'bg-red-500',
		unknown: 'bg-gray-500'
	};

	const statusLabels = {
		healthy: 'Healthy',
		degraded: 'Degraded',
		unhealthy: 'Unhealthy',
		unknown: 'Unknown'
	};

	const loadData = async () => {
		try {
			const [statusData, healthData] = await Promise.all([
				getBackendsStatus(localStorage.token),
				getBackendsHealth(localStorage.token)
			]);
			backends = statusData;
			health = healthData;
			loading = false;
		} catch (error) {
			console.error('Failed to load backend data:', error);
			toast.error('Failed to load inference backends');
			loading = false;
		}
	};

	onMount(() => {
		loadData();
		// Refresh every 30 seconds
		refreshInterval = setInterval(loadData, 30000);
		
		return () => {
			if (refreshInterval) clearInterval(refreshInterval);
		};
	});

	const formatLatency = (ms?: number) => {
		if (!ms) return 'N/A';
		return `${ms.toFixed(1)}ms`;
	};

	const formatUptime = (percentage: number) => {
		return `${percentage.toFixed(1)}%`;
	};
</script>

<div class="space-y-4">
	<div class="flex justify-between items-center">
		<h3 class="text-lg font-semibold">Inference Backends</h3>
		<button
			on:click={loadData}
			class="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition"
		>
			<svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
			</svg>
			Refresh
		</button>
	</div>

	{#if loading}
		<div class="text-center py-8">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-pulsai-primary"></div>
			<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading backends...</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each Object.entries(backends) as [backendName, backend]}
				{@const backendHealth = health[backendName]}
				<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition">
					<!-- Header -->
					<div class="flex justify-between items-start mb-3">
						<div class="flex items-center space-x-2">
							<div class={`w-3 h-3 rounded-full ${statusColors[backend.status] || statusColors.unknown}`}></div>
							<h4 class="font-semibold capitalize">{backendName}</h4>
						</div>
						<span class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800">
							{statusLabels[backend.status] || statusLabels.unknown}
						</span>
					</div>

					<!-- Metrics -->
					<div class="space-y-2 text-sm">
						<div class="flex justify-between">
							<span class="text-gray-600 dark:text-gray-400">Latency:</span>
							<span class="font-mono">{formatLatency(backend.latency_ms)}</span>
						</div>
						
						<div class="flex justify-between">
							<span class="text-gray-600 dark:text-gray-400">Models:</span>
							<span class="font-semibold">{backend.models_count}</span>
						</div>
						
						<div class="flex justify-between">
							<span class="text-gray-600 dark:text-gray-400">Requests:</span>
							<span class="font-mono">{backend.request_count}</span>
						</div>

						{#if backendHealth}
							<div class="flex justify-between">
								<span class="text-gray-600 dark:text-gray-400">Uptime (24h):</span>
								<span class="font-semibold text-green-600 dark:text-green-400">
									{formatUptime(backendHealth.uptime_24h)}
								</span>
							</div>

							{#if backendHealth.avg_latency_ms}
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">Avg Latency:</span>
									<span class="font-mono">{formatLatency(backendHealth.avg_latency_ms)}</span>
								</div>
							{/if}
						{/if}

						{#if backend.error}
							<div class="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-xs">
								{backend.error}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>

		{#if Object.keys(backends).length === 0}
			<div class="text-center py-8 text-gray-500 dark:text-gray-400">
				<svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
				</svg>
				<p>No inference backends configured</p>
			</div>
		{/if}
	{/if}
</div>

<style>
	/* Pulsai gradient text for titles */
	h3 {
		background: var(--pulsai-gradient-orange);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
</style>

