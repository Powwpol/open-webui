<script lang="ts">
	/**
	 * MCPSettings - Main MCP configuration component
	 * Integrates server list, form, and tools browser
	 */
	
	import { GradientText, IridescenceBackground } from '$lib/reactbits';
	import MCPServerList from './MCPServerList.svelte';
	import MCPServerForm from './MCPServerForm.svelte';
	import MCPToolsBrowser from './MCPToolsBrowser.svelte';
	import { exportMCPConfig, reloadMCPConfig } from '$lib/apis/mcp';
	import { toast } from 'svelte-sonner';
	
	export let token = '';
	
	let activeTab: 'servers' | 'tools' = 'servers';
	let reloading = false;
	
	async function handleReloadConfig() {
		try {
			reloading = true;
			const result = await reloadMCPConfig(token);
			toast.success(result.message || 'Configuration rechargée');
		} catch (error) {
			console.error('Failed to reload config:', error);
			toast.error('Erreur lors du rechargement');
		} finally {
			reloading = false;
		}
	}
	
	async function handleExportConfig() {
		try {
			const yaml = await exportMCPConfig(token);
			
			// Download as file
			const blob = new Blob([yaml], { type: 'text/yaml' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'mcp-servers.yaml';
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
			
			toast.success('Configuration exportée');
		} catch (error) {
			console.error('Failed to export config:', error);
			toast.error('Erreur lors de l\'exportation');
		}
	}
</script>

<div class="mcp-settings relative min-h-screen">
	<!-- Iridescence background (dark mode only) -->
	<IridescenceBackground opacity={0.08} />
	
	<div class="relative z-10 space-y-6">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<GradientText>
					<h1 class="text-3xl font-bold mb-2">Model Context Protocols</h1>
				</GradientText>
				<p class="text-gray-600 dark:text-gray-400">
					Gérez vos serveurs MCP et explorez les outils disponibles
				</p>
			</div>
			
			<div class="flex gap-2">
				<button
					on:click={handleReloadConfig}
					disabled={reloading}
					class="px-4 py-2 rounded-lg bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-200 transition-all"
					title="Recharger la configuration depuis le fichier YAML"
				>
					{#if reloading}
						<span class="inline-block animate-spin">⟳</span>
					{:else}
						🔄 Recharger YAML
					{/if}
				</button>
				
				<button
					on:click={handleExportConfig}
					class="px-4 py-2 rounded-lg bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800 text-green-700 dark:text-green-200 transition-all"
					title="Exporter la configuration en YAML"
				>
					📥 Exporter
				</button>
			</div>
		</div>
		
		<!-- Tabs -->
		<div class="flex gap-2 border-b border-gray-200 dark:border-gray-700">
			<button
				on:click={() => activeTab = 'servers'}
				class="px-6 py-3 font-semibold transition-all relative"
				class:text-pulsai-primary={activeTab === 'servers'}
				class:text-gray-600={activeTab !== 'servers'}
				class:dark:text-pulsai-primary={activeTab === 'servers'}
				class:dark:text-gray-400={activeTab !== 'servers'}
			>
				🖥️ Serveurs MCP
				{#if activeTab === 'servers'}
					<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-pulsai-primary"></div>
				{/if}
			</button>
			
			<button
				on:click={() => activeTab = 'tools'}
				class="px-6 py-3 font-semibold transition-all relative"
				class:text-pulsai-primary={activeTab === 'tools'}
				class:text-gray-600={activeTab !== 'tools'}
				class:dark:text-pulsai-primary={activeTab === 'tools'}
				class:dark:text-gray-400={activeTab !== 'tools'}
			>
				🔧 Explorateur d'Outils
				{#if activeTab === 'tools'}
					<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-pulsai-primary"></div>
				{/if}
			</button>
		</div>
		
		<!-- Content -->
		<div class="py-6">
			{#if activeTab === 'servers'}
				<MCPServerList {token}>
					<svelte:fragment slot="form" let:server let:onSuccess let:onCancel>
						<MCPServerForm {server} {token} {onSuccess} {onCancel} />
					</svelte:fragment>
				</MCPServerList>
			{:else if activeTab === 'tools'}
				<MCPToolsBrowser {token} />
			{/if}
		</div>
		
		<!-- Help Section -->
		<div class="mt-12 p-6 bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20 rounded-lg border border-blue-200 dark:border-blue-800">
			<h3 class="font-semibold mb-3 flex items-center gap-2">
				<span class="text-2xl">💡</span>
				<GradientText colors={['#2751E3', '#00B050']}>
					<span class="text-lg">Aide MCP</span>
				</GradientText>
			</h3>
			
			<div class="space-y-3 text-sm text-gray-700 dark:text-gray-300">
				<div>
					<strong>🖥️ stdio:</strong> Exécute un processus local (Python, Node.js, etc.)
				</div>
				<div>
					<strong>🌐 HTTP:</strong> Se connecte à un serveur MCP via REST API
				</div>
				<div>
					<strong>🐳 Docker:</strong> Utilise un container Docker comme serveur MCP
				</div>
				<div>
					<strong>📡 SSE:</strong> Stream en temps réel via Server-Sent Events
				</div>
				<div>
					<strong>🔌 WebSocket:</strong> Communication bidirectionnelle via WebSocket
				</div>
			</div>
			
			<div class="mt-4 pt-4 border-t border-blue-200 dark:border-blue-700">
				<p class="text-xs text-gray-600 dark:text-gray-400">
					📖 Pour créer votre propre serveur MCP, consultez la documentation dans
					<code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">mcp-server/README.md</code>
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	.mcp-settings {
		animation: fade-in 0.5s ease-out;
	}
	
	@keyframes fade-in {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>

