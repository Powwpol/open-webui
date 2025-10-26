<script lang="ts">
	/**
	 * MCPToolsBrowser - Browse and test tools from MCP servers
	 */
	
	import { onMount } from 'svelte';
	import { getAllMCPTools, getMCPServerTools, executeMCPTool } from '$lib/apis/mcp';
	import { GradientText } from '$lib/reactbits';
	import type { MCPTool } from '$lib/apis/mcp';
	import { toast } from 'svelte-sonner';
	
	export let token = '';
	
	let allTools: Record<string, MCPTool[]> = {};
	let loading = true;
	let searchQuery = '';
	let selectedTool: { serverId: string; tool: MCPTool } | null = null;
	let toolParameters: Record<string, any> = {};
	let executingTool = false;
	let toolResult: any = null;
	
	onMount(async () => {
		await loadTools();
	});
	
	async function loadTools() {
		try {
			loading = true;
			allTools = await getAllMCPTools(token);
		} catch (error) {
			console.error('Failed to load MCP tools:', error);
			toast.error('Erreur de chargement des outils');
		} finally {
			loading = false;
		}
	}
	
	$: filteredTools = Object.entries(allTools).reduce((acc, [serverId, tools]) => {
		const filtered = tools.filter(tool =>
			tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			tool.description.toLowerCase().includes(searchQuery.toLowerCase())
		);
		if (filtered.length > 0) {
			acc[serverId] = filtered;
		}
		return acc;
	}, {} as Record<string, MCPTool[]>);
	
	$: totalToolsCount = Object.values(allTools).reduce((sum, tools) => sum + tools.length, 0);
	$: filteredToolsCount = Object.values(filteredTools).reduce((sum, tools) => sum + tools.length, 0);
	
	function handleSelectTool(serverId: string, tool: MCPTool) {
		selectedTool = { serverId, tool };
		toolParameters = {};
		toolResult = null;
		
		// Initialize parameters with default values
		tool.parameters.forEach(param => {
			if (param.type === 'boolean') {
				toolParameters[param.name] = false;
			} else if (param.type === 'integer' || param.type === 'number') {
				toolParameters[param.name] = 0;
			} else {
				toolParameters[param.name] = '';
			}
		});
	}
	
	async function handleExecuteTool() {
		if (!selectedTool) return;
		
		try {
			executingTool = true;
			toolResult = null;
			
			const result = await executeMCPTool(
				selectedTool.serverId,
				selectedTool.tool.name,
				toolParameters,
				token
			);
			
			toolResult = result;
			toast.success('Outil exécuté avec succès');
		} catch (error) {
			console.error('Failed to execute tool:', error);
			toast.error(`Erreur: ${error.message}`);
			toolResult = { error: error.message };
		} finally {
			executingTool = false;
		}
	}
	
	function getTypeIcon(type: string): string {
		const icons = {
			string: '📝',
			integer: '🔢',
			number: '🔢',
			boolean: '✓',
			array: '📋',
			object: '📦'
		};
		return icons[type] || '❓';
	}
</script>

<div class="mcp-tools-browser space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<GradientText>
			<h2 class="section-header">Explorateur d'Outils MCP</h2>
		</GradientText>
		<button
			on:click={loadTools}
			class="px-4 py-2 rounded-lg bg-pulsai-info hover:bg-opacity-90 text-white transition-all"
			disabled={loading}
		>
			{#if loading}
				<span class="inline-block animate-spin">⟳</span>
			{:else}
				🔄 Actualiser
			{/if}
		</button>
	</div>
	
	<!-- Search and Stats -->
	<div class="flex items-center gap-4">
		<div class="flex-1 relative">
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Rechercher des outils..."
				class="w-full px-4 py-2 pl-10 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
			/>
			<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
		</div>
		
		<div class="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium">
			{filteredToolsCount} / {totalToolsCount} outils
		</div>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-pulse space-y-4 w-full">
				<div class="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
				<div class="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
			</div>
		</div>
	{:else if Object.keys(filteredTools).length === 0}
		<div class="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
			<div class="text-6xl mb-4">🔧</div>
			<p class="text-gray-600 dark:text-gray-400">
				{searchQuery ? 'Aucun outil trouvé' : 'Aucun outil disponible. Ajoutez des serveurs MCP !'}
			</p>
		</div>
	{:else}
		<div class="space-y-6">
			{#each Object.entries(filteredTools) as [serverId, tools]}
				<div class="server-tools-section">
					<h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
						<span class="text-pulsai-primary">🖥️</span>
						{serverId}
						<span class="text-sm font-normal text-gray-500">({tools.length} outil{tools.length > 1 ? 's' : ''})</span>
					</h3>
					
					<div class="grid gap-3">
						{#each tools as tool}
							<button
								on:click={() => handleSelectTool(serverId, tool)}
								class="tool-card text-left p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-pulsai-primary dark:hover:border-pulsai-primary transition-all"
								class:border-pulsai-primary={selectedTool?.tool.name === tool.name && selectedTool?.serverId === serverId}
							>
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<h4 class="font-semibold text-gray-900 dark:text-white mb-1">
											🔧 {tool.name}
										</h4>
										<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
											{tool.description}
										</p>
										
										{#if tool.parameters.length > 0}
											<div class="flex flex-wrap gap-2">
												{#each tool.parameters as param}
													<span class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded font-mono">
														{getTypeIcon(param.type)} {param.name}{param.required ? '*' : ''}
													</span>
												{/each}
											</div>
										{:else}
											<span class="text-xs text-gray-500">Aucun paramètre</span>
										{/if}
									</div>
									
									<div class="ml-4">
										<span class="text-2xl">▶</span>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Tool Execution Panel -->
{#if selectedTool}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
			<div class="flex items-center justify-between mb-6">
				<GradientText>
					<h3 class="text-xl font-bold">
						🔧 {selectedTool.tool.name}
					</h3>
				</GradientText>
				<button
					on:click={() => selectedTool = null}
					class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
				>
					✕
				</button>
			</div>
			
			<div class="mb-6">
				<p class="text-gray-600 dark:text-gray-400 mb-2">
					{selectedTool.tool.description}
				</p>
				<p class="text-sm text-gray-500">
					Serveur: <span class="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{selectedTool.serverId}</span>
				</p>
			</div>
			
			{#if selectedTool.tool.parameters.length > 0}
				<div class="space-y-4 mb-6">
					<h4 class="font-semibold">Paramètres</h4>
					
					{#each selectedTool.tool.parameters as param}
						<div>
							<label for="param-{param.name}" class="block text-sm font-medium mb-2">
								{getTypeIcon(param.type)} {param.name}
								{#if param.required}
									<span class="text-red-500">*</span>
								{/if}
							</label>
							<p class="text-xs text-gray-500 mb-2">{param.description}</p>
							
							{#if param.type === 'boolean'}
								<input
									id="param-{param.name}"
									type="checkbox"
									bind:checked={toolParameters[param.name]}
									class="w-4 h-4"
								/>
							{:else if param.type === 'integer' || param.type === 'number'}
								<input
									id="param-{param.name}"
									type="number"
									bind:value={toolParameters[param.name]}
									step={param.type === 'integer' ? '1' : '0.01'}
									class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
									required={param.required}
								/>
							{:else if param.type === 'array' || param.type === 'object'}
								<textarea
									id="param-{param.name}"
									bind:value={toolParameters[param.name]}
									placeholder="JSON format"
									rows="3"
									class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 font-mono text-sm"
									required={param.required}
								></textarea>
							{:else}
								<input
									id="param-{param.name}"
									type="text"
									bind:value={toolParameters[param.name]}
									class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
									required={param.required}
								/>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
			
			<!-- Execute Button -->
			<div class="mb-6">
				<button
					on:click={handleExecuteTool}
					disabled={executingTool}
					class="w-full px-4 py-3 bg-pulsai-primary hover:bg-opacity-90 text-white font-semibold rounded-lg transition-all disabled:opacity-50"
				>
					{#if executingTool}
						<span class="inline-block animate-spin">⟳</span> Exécution en cours...
					{:else}
						▶ Exécuter l'outil
					{/if}
				</button>
			</div>
			
			<!-- Results -->
			{#if toolResult !== null}
				<div class="border-t pt-6 dark:border-gray-700">
					<h4 class="font-semibold mb-3">Résultat</h4>
					
					<div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 overflow-x-auto">
						<pre class="text-sm font-mono whitespace-pre-wrap">{JSON.stringify(toolResult, null, 2)}</pre>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.tool-card {
		transition: all 0.2s ease;
	}
	
	.tool-card:hover {
		transform: translateX(4px);
	}
</style>

