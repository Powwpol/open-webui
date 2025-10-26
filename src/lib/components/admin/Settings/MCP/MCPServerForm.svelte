<script lang="ts">
	/**
	 * MCPServerForm - Add/Edit MCP server configuration
	 * Protocol-specific forms with validation
	 */
	
	import { addMCPServer, updateMCPServer } from '$lib/apis/mcp';
	import type { MCPServerConfig } from '$lib/apis/mcp';
	import { toast } from 'svelte-sonner';
	
	export let server: MCPServerConfig;
	export let token = '';
	export let onSuccess: () => void;
	export let onCancel: () => void;
	
	let formData: MCPServerConfig = { ...server };
	let saving = false;
	let validationErrors: Record<string, string> = {};
	
	const protocols = [
		{ value: 'stdio', label: 'Standard I/O (stdio)', icon: '🖥️' },
		{ value: 'http', label: 'HTTP/HTTPS', icon: '🌐' },
		{ value: 'docker', label: 'Docker Container', icon: '🐳' },
		{ value: 'sse', label: 'Server-Sent Events (SSE)', icon: '📡' },
		{ value: 'websocket', label: 'WebSocket', icon: '🔌' }
	];
	
	// Initialize config based on protocol
	$: if (formData.protocol) {
		if (!formData.config || Object.keys(formData.config).length === 0) {
			formData.config = getDefaultConfig(formData.protocol);
		}
	}
	
	function getDefaultConfig(protocol: string): Record<string, any> {
		switch (protocol) {
			case 'stdio':
				return { command: ['python', '-m', 'mcp_server'] };
			case 'http':
			case 'sse':
				return { url: 'http://localhost:8100' };
			case 'docker':
				return { container_name: 'my-mcp-server', port: 8100 };
			case 'websocket':
				return { url: 'ws://localhost:8100' };
			default:
				return {};
		}
	}
	
	function validate(): boolean {
		validationErrors = {};
		
		if (!formData.id || formData.id.trim() === '') {
			validationErrors.id = 'L\'ID est requis';
		}
		
		if (!formData.name || formData.name.trim() === '') {
			validationErrors.name = 'Le nom est requis';
		}
		
		// Protocol-specific validation
		switch (formData.protocol) {
			case 'stdio':
				if (!formData.config.command || formData.config.command.length === 0) {
					validationErrors.command = 'La commande est requise';
				}
				break;
			case 'http':
			case 'sse':
				if (!formData.config.url) {
					validationErrors.url = 'L\'URL est requise';
				}
				break;
			case 'docker':
				if (!formData.config.container_name) {
					validationErrors.container_name = 'Le nom du container est requis';
				}
				break;
			case 'websocket':
				if (!formData.config.url) {
					validationErrors.url = 'L\'URL WebSocket est requise';
				}
				break;
		}
		
		return Object.keys(validationErrors).length === 0;
	}
	
	async function handleSubmit() {
		if (!validate()) {
			toast.error('Veuillez corriger les erreurs du formulaire');
			return;
		}
		
		try {
			saving = true;
			
			if (server.id) {
				await updateMCPServer(formData.id, formData, token);
				toast.success('Serveur MCP mis à jour');
			} else {
				await addMCPServer(formData, token);
				toast.success('Serveur MCP ajouté');
			}
			
			onSuccess();
		} catch (error) {
			console.error('Failed to save MCP server:', error);
			toast.error(`Erreur: ${error.message}`);
		} finally {
			saving = false;
		}
	}
	
	function addCommandArg() {
		if (!Array.isArray(formData.config.command)) {
			formData.config.command = [];
		}
		formData.config.command = [...formData.config.command, ''];
	}
	
	function removeCommandArg(index: number) {
		formData.config.command = formData.config.command.filter((_, i) => i !== index);
	}
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
	<!-- Basic Information -->
	<div class="space-y-4">
		<div>
			<label for="server-id" class="block text-sm font-medium mb-2">
				ID du serveur *
			</label>
			<input
				id="server-id"
				type="text"
				bind:value={formData.id}
				disabled={!!server.id}
				placeholder="pulsai-custom-mcp"
				class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 {validationErrors.id ? 'border-red-500' : ''}"
				required
			/>
			{#if validationErrors.id}
				<p class="text-red-500 text-sm mt-1">{validationErrors.id}</p>
			{/if}
			<p class="text-xs text-gray-500 mt-1">Identifiant unique (non modifiable après création)</p>
		</div>
		
		<div>
			<label for="server-name" class="block text-sm font-medium mb-2">
				Nom d'affichage *
			</label>
			<input
				id="server-name"
				type="text"
				bind:value={formData.name}
				placeholder="Mon serveur MCP personnalisé"
				class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 {validationErrors.name ? 'border-red-500' : ''}"
				required
			/>
			{#if validationErrors.name}
				<p class="text-red-500 text-sm mt-1">{validationErrors.name}</p>
			{/if}
		</div>
		
		<div>
			<label for="server-protocol" class="block text-sm font-medium mb-2">
				Protocole *
			</label>
			<select
				id="server-protocol"
				bind:value={formData.protocol}
				class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
				required
			>
				{#each protocols as proto}
					<option value={proto.value}>
						{proto.icon} {proto.label}
					</option>
				{/each}
			</select>
		</div>
		
		<div class="flex items-center gap-2">
			<input
				id="server-enabled"
				type="checkbox"
				bind:checked={formData.enabled}
				class="w-4 h-4"
			/>
			<label for="server-enabled" class="text-sm font-medium">
				Activer le serveur au démarrage
			</label>
		</div>
	</div>
	
	<!-- Protocol-specific configuration -->
	<div class="border-t pt-4 dark:border-gray-700">
		<h4 class="font-semibold mb-4">Configuration du protocole {formData.protocol.toUpperCase()}</h4>
		
		{#if formData.protocol === 'stdio'}
			<div class="space-y-4">
				<div>
					<label class="block text-sm font-medium mb-2">
						Commande et arguments *
					</label>
					{#each formData.config.command || [] as cmd, i}
						<div class="flex gap-2 mb-2">
							<input
								type="text"
								bind:value={formData.config.command[i]}
								placeholder={i === 0 ? 'python' : 'argument'}
								class="flex-1 px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
							/>
							<button
								type="button"
								on:click={() => removeCommandArg(i)}
								class="px-3 py-2 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 text-red-700 dark:text-red-200 rounded-lg"
							>
								✕
							</button>
						</div>
					{/each}
					<button
						type="button"
						on:click={addCommandArg}
						class="px-3 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-200 rounded-lg text-sm"
					>
						➕ Ajouter un argument
					</button>
					{#if validationErrors.command}
						<p class="text-red-500 text-sm mt-1">{validationErrors.command}</p>
					{/if}
				</div>
				
				<div>
					<label for="stdio-env" class="block text-sm font-medium mb-2">
						Variables d'environnement (JSON)
					</label>
					<textarea
						id="stdio-env"
						bind:value={formData.config.env}
						placeholder='{"PYTHONPATH": "/app/tools"}'
						rows="3"
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 font-mono text-sm"
					></textarea>
				</div>
			</div>
			
		{:else if formData.protocol === 'http' || formData.protocol === 'sse'}
			<div class="space-y-4">
				<div>
					<label for="http-url" class="block text-sm font-medium mb-2">
						URL du serveur *
					</label>
					<input
						id="http-url"
						type="url"
						bind:value={formData.config.url}
						placeholder="http://localhost:8100"
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 {validationErrors.url ? 'border-red-500' : ''}"
						required
					/>
					{#if validationErrors.url}
						<p class="text-red-500 text-sm mt-1">{validationErrors.url}</p>
					{/if}
				</div>
				
				<div>
					<label for="http-auth" class="block text-sm font-medium mb-2">
						Type d'authentification
					</label>
					<select
						id="http-auth"
						bind:value={formData.config.auth_type}
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
					>
						<option value="">Aucune</option>
						<option value="bearer">Bearer Token</option>
						<option value="basic">Basic Auth</option>
						<option value="api_key">API Key</option>
					</select>
				</div>
				
				{#if formData.config.auth_type === 'bearer'}
					<div>
						<label for="http-token" class="block text-sm font-medium mb-2">
							Token
						</label>
						<input
							id="http-token"
							type="password"
							bind:value={formData.config.token}
							placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
							class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 font-mono text-sm"
						/>
					</div>
				{:else if formData.config.auth_type === 'api_key'}
					<div>
						<label for="http-apikey" class="block text-sm font-medium mb-2">
							API Key
						</label>
						<input
							id="http-apikey"
							type="password"
							bind:value={formData.config.api_key}
							placeholder="sk-..."
							class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 font-mono text-sm"
						/>
					</div>
				{/if}
			</div>
			
		{:else if formData.protocol === 'docker'}
			<div class="space-y-4">
				<div>
					<label for="docker-container" class="block text-sm font-medium mb-2">
						Nom du container *
					</label>
					<input
						id="docker-container"
						type="text"
						bind:value={formData.config.container_name}
						placeholder="my-mcp-server"
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 {validationErrors.container_name ? 'border-red-500' : ''}"
						required
					/>
					{#if validationErrors.container_name}
						<p class="text-red-500 text-sm mt-1">{validationErrors.container_name}</p>
					{/if}
				</div>
				
				<div>
					<label for="docker-port" class="block text-sm font-medium mb-2">
						Port (optionnel)
					</label>
					<input
						id="docker-port"
						type="number"
						bind:value={formData.config.port}
						placeholder="8100"
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
					/>
					<p class="text-xs text-gray-500 mt-1">Si le container expose un port HTTP/WebSocket</p>
				</div>
			</div>
			
		{:else if formData.protocol === 'websocket'}
			<div class="space-y-4">
				<div>
					<label for="ws-url" class="block text-sm font-medium mb-2">
						URL WebSocket *
					</label>
					<input
						id="ws-url"
						type="url"
						bind:value={formData.config.url}
						placeholder="ws://localhost:8100"
						class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 {validationErrors.url ? 'border-red-500' : ''}"
						required
					/>
					{#if validationErrors.url}
						<p class="text-red-500 text-sm mt-1">{validationErrors.url}</p>
					{/if}
				</div>
			</div>
		{/if}
	</div>
	
	<!-- Actions -->
	<div class="flex justify-end gap-3 border-t pt-4 dark:border-gray-700">
		<button
			type="button"
			on:click={onCancel}
			class="px-4 py-2 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 dark:border-gray-600"
			disabled={saving}
		>
			Annuler
		</button>
		<button
			type="submit"
			class="px-4 py-2 bg-pulsai-primary hover:bg-opacity-90 text-white rounded-lg font-semibold transition-all"
			disabled={saving}
		>
			{#if saving}
				<span class="inline-block animate-spin">⟳</span> Enregistrement...
			{:else}
				{server.id ? '💾 Mettre à jour' : '➕ Ajouter'}
			{/if}
		</button>
	</div>
</form>

