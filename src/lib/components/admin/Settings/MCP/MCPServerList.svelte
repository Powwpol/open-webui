<script lang="ts">
	/**
	 * MCPServerList - Display and manage MCP servers
	 * With Pulsai branding and ReactBits enhancements
	 */
	
	import { onMount } from 'svelte';
	import { getMCPServers, deleteMCPServer, enableMCPServer, disableMCPServer, testMCPConnection } from '$lib/apis/mcp';
	import { GradientText } from '$lib/reactbits';
	import type { MCPServerConfig } from '$lib/apis/mcp';
	import { toast } from 'svelte-sonner';
	
	export let token = '';
	
	let servers: MCPServerConfig[] = [];
	let loading = true;
	let selectedServer: MCPServerConfig | null = null;
	let testingServer: string | null = null;
	
	// Protocol badges with Pulsai colors
	const protocolColors = {
		stdio: 'bg-pulsai-info text-white',
		http: 'bg-pulsai-success text-white',
		docker: 'bg-pulsai-accent text-white',
		sse: 'bg-pulsai-primary text-white',
		websocket: 'bg-pulsai-primary-light text-black'
	};
	
	const protocolIcons = {
		stdio: '🖥️',
		http: '🌐',
		docker: '🐳',
		sse: '📡',
		websocket: '🔌'
	};
	
	onMount(async () => {
		await loadServers();
	});
	
	async function loadServers() {
		try {
			loading = true;
			servers = await getMCPServers(token);
		} catch (error) {
			console.error('Failed to load MCP servers:', error);
			toast.error('Erreur de chargement des serveurs MCP');
		} finally {
			loading = false;
		}
	}
	
	async function handleDelete(serverId: string) {
		if (!confirm('Êtes-vous sûr de vouloir supprimer ce serveur MCP ?')) {
			return;
		}
		
		try {
			await deleteMCPServer(serverId, token);
			toast.success('Serveur MCP supprimé');
			await loadServers();
		} catch (error) {
			console.error('Failed to delete server:', error);
			toast.error('Erreur lors de la suppression');
		}
	}
	
	async function handleToggle(server: MCPServerConfig) {
		try {
			if (server.enabled) {
				await disableMCPServer(server.id, token);
				toast.success(`${server.name} désactivé`);
			} else {
				await enableMCPServer(server.id, token);
				toast.success(`${server.name} activé`);
			}
			await loadServers();
		} catch (error) {
			console.error('Failed to toggle server:', error);
			toast.error('Erreur lors du changement d\'état');
		}
	}
	
	async function handleTest(serverId: string) {
		try {
			testingServer = serverId;
			const result = await testMCPConnection(serverId, token);
			
			if (result.success) {
				toast.success(`Connexion réussie ${result.latency_ms ? `(${result.latency_ms}ms)` : ''}`);
			} else {
				toast.error(`Échec de connexion: ${result.message}`);
			}
		} catch (error) {
			console.error('Failed to test connection:', error);
			toast.error('Erreur lors du test de connexion');
		} finally {
			testingServer = null;
		}
	}
</script>

<div class="mcp-server-list space-y-4">
	<!-- Header with gradient text -->
	<div class="flex items-center justify-between mb-6">
		<GradientText>
			<h2 class="section-header">Serveurs MCP</h2>
		</GradientText>
		
		<div class="flex gap-2">
			<button
				on:click={loadServers}
				class="px-4 py-2 rounded-lg bg-pulsai-info hover:bg-opacity-90 text-white transition-all"
				disabled={loading}
			>
				{#if loading}
					<span class="inline-block animate-spin">⟳</span>
				{:else}
					🔄 Actualiser
				{/if}
			</button>
			
			<button
				on:click={() => selectedServer = { id: '', name: '', protocol: 'http', config: {}, enabled: true }}
				class="px-4 py-2 rounded-lg bg-pulsai-primary hover:bg-opacity-90 text-white font-semibold transition-all"
			>
				➕ Ajouter un serveur
			</button>
		</div>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-pulse space-y-4 w-full">
				<div class="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
				<div class="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
				<div class="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
			</div>
		</div>
	{:else if servers.length === 0}
		<div class="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
			<div class="text-6xl mb-4">🔌</div>
			<p class="text-gray-600 dark:text-gray-400">
				Aucun serveur MCP configuré. Ajoutez-en un pour commencer !
			</p>
		</div>
	{:else}
		<div class="grid gap-4">
			{#each servers as server (server.id)}
				<div class="server-card bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-200 dark:border-gray-700">
					<div class="flex items-start justify-between">
						<div class="flex-1">
							<div class="flex items-center gap-3 mb-2">
								<span class="text-2xl">{protocolIcons[server.protocol]}</span>
								<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
									{server.name}
								</h3>
								<span class="px-2 py-1 text-xs font-medium rounded {protocolColors[server.protocol]}">
									{server.protocol.toUpperCase()}
								</span>
								{#if server.enabled}
									<span class="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
										✓ Activé
									</span>
								{:else}
									<span class="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
										○ Désactivé
									</span>
								{/if}
							</div>
							
							<div class="text-sm text-gray-600 dark:text-gray-400 mb-3">
								<span class="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
									ID: {server.id}
								</span>
							</div>
							
							<!-- Configuration preview -->
							<div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
								{#each Object.entries(server.config).slice(0, 3) as [key, value]}
									<div>
										<span class="font-semibold">{key}:</span>
										<span class="font-mono">{typeof value === 'string' && value.length > 50 ? value.slice(0, 50) + '...' : JSON.stringify(value)}</span>
									</div>
								{/each}
								{#if Object.keys(server.config).length > 3}
									<div class="text-gray-400">
										+ {Object.keys(server.config).length - 3} paramètre(s) supplémentaire(s)
									</div>
								{/if}
							</div>
						</div>
						
						<!-- Actions -->
						<div class="flex flex-col gap-2 ml-4">
							<button
								on:click={() => handleTest(server.id)}
								disabled={testingServer === server.id}
								class="px-3 py-1.5 text-sm rounded bg-blue-50 hover:bg-blue-100 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-200 transition-colors"
							>
								{#if testingServer === server.id}
									<span class="inline-block animate-spin">⟳</span> Test...
								{:else}
									🔍 Tester
								{/if}
							</button>
							
							<button
								on:click={() => handleToggle(server)}
								class="px-3 py-1.5 text-sm rounded {server.enabled ? 'bg-yellow-50 hover:bg-yellow-100 dark:bg-yellow-900 dark:hover:bg-yellow-800 text-yellow-700 dark:text-yellow-200' : 'bg-green-50 hover:bg-green-100 dark:bg-green-900 dark:hover:bg-green-800 text-green-700 dark:text-green-200'} transition-colors"
							>
								{server.enabled ? '⏸ Désactiver' : '▶ Activer'}
							</button>
							
							<button
								on:click={() => selectedServer = server}
								class="px-3 py-1.5 text-sm rounded bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 transition-colors"
							>
								✏️ Modifier
							</button>
							
							<button
								on:click={() => handleDelete(server.id)}
								class="px-3 py-1.5 text-sm rounded bg-red-50 hover:bg-red-100 dark:bg-red-900 dark:hover:bg-red-800 text-red-700 dark:text-red-200 transition-colors"
							>
								🗑️ Supprimer
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if selectedServer}
	<!-- Modal for add/edit would go here - we'll create MCPServerForm component next -->
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
			<div class="flex items-center justify-between mb-4">
				<GradientText>
					<h3 class="text-xl font-bold">
						{selectedServer.id ? 'Modifier' : 'Ajouter'} un serveur MCP
					</h3>
				</GradientText>
				<button
					on:click={() => selectedServer = null}
					class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
				>
					✕
				</button>
			</div>
			
			<!-- Import the form component (we'll create it next) -->
			<slot name="form" server={selectedServer} {token} onSuccess={loadServers} onCancel={() => selectedServer = null} />
		</div>
	</div>
{/if}

<style>
	.server-card {
		transition: all 0.3s ease;
	}
	
	.server-card:hover {
		transform: translateY(-2px);
	}
</style>

