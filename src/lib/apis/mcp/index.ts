/**
 * Pulsai MCP API Client
 * 
 * Provides TypeScript client functions for interacting with the MCP backend API.
 */

import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface MCPServerConfig {
	id: string;
	name: string;
	protocol: 'stdio' | 'http' | 'docker' | 'sse' | 'websocket';
	config: Record<string, any>;
	enabled: boolean;
}

export interface MCPServerStatus {
	id: string;
	name: string;
	protocol: string;
	enabled: boolean;
	connected: boolean;
	health: 'healthy' | 'unhealthy' | 'unknown';
	last_check: string;
	error?: string;
}

export interface MCPTool {
	name: string;
	description: string;
	parameters: MCPToolParameter[];
}

export interface MCPToolParameter {
	name: string;
	type: string;
	description: string;
	required: boolean;
}

export interface MCPModelInfo {
	id: string;
	name: string;
	description?: string;
	context_window?: number;
	capabilities: string[];
}

export interface MCPMessage {
	type: string;
	payload: Record<string, any>;
}

/**
 * Get list of all MCP servers
 */
export const getMCPServers = async (token: string = ''): Promise<MCPServerConfig[]> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch MCP servers: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Get details for a specific MCP server
 */
export const getMCPServer = async (serverId: string, token: string = ''): Promise<MCPServerStatus> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch MCP server: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Add a new MCP server
 */
export const addMCPServer = async (
	server: MCPServerConfig,
	token: string = ''
): Promise<MCPServerConfig> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || `Failed to add MCP server: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Update an existing MCP server
 */
export const updateMCPServer = async (
	serverId: string,
	server: Partial<MCPServerConfig>,
	token: string = ''
): Promise<MCPServerConfig> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || `Failed to update MCP server: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Delete an MCP server
 */
export const deleteMCPServer = async (serverId: string, token: string = ''): Promise<void> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to delete MCP server: ${response.statusText}`);
	}
};

/**
 * Test MCP server connection
 */
export const testMCPConnection = async (
	serverId: string,
	token: string = ''
): Promise<{ success: boolean; message: string; latency_ms?: number }> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/test`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		const error = await response.json();
		return {
			success: false,
			message: error.detail || response.statusText
		};
	}

	return await response.json();
};

/**
 * Enable an MCP server
 */
export const enableMCPServer = async (serverId: string, token: string = ''): Promise<void> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/enable`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to enable MCP server: ${response.statusText}`);
	}
};

/**
 * Disable an MCP server
 */
export const disableMCPServer = async (serverId: string, token: string = ''): Promise<void> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/disable`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to disable MCP server: ${response.statusText}`);
	}
};

/**
 * Get tools from a specific MCP server
 */
export const getMCPServerTools = async (
	serverId: string,
	token: string = ''
): Promise<MCPTool[]> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/tools`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch MCP tools: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Get all tools from all enabled MCP servers
 */
export const getAllMCPTools = async (
	token: string = ''
): Promise<Record<string, MCPTool[]>> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/tools`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch all MCP tools: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Execute a tool via MCP
 */
export const executeMCPTool = async (
	serverId: string,
	toolName: string,
	parameters: Record<string, any>,
	token: string = ''
): Promise<any> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/tools/execute`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			server_id: serverId,
			tool_name: toolName,
			parameters
		})
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || `Failed to execute tool: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Get models from a specific MCP server
 */
export const getMCPServerModels = async (
	serverId: string,
	token: string = ''
): Promise<MCPModelInfo[]> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/servers/${serverId}/models`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch MCP models: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Reload MCP configuration from file
 */
export const reloadMCPConfig = async (token: string = ''): Promise<{ message: string }> => {
	const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/reload`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		throw new Error(`Failed to reload MCP config: ${response.statusText}`);
	}

	return await response.json();
};

/**
 * Export MCP configuration as YAML
 */
export const exportMCPConfig = async (token: string = ''): Promise<string> => {
	const servers = await getMCPServers(token);
	
	// Convert to YAML-like format (simple implementation)
	let yaml = 'servers:\n';
	servers.forEach((server) => {
		yaml += `  - id: "${server.id}"\n`;
		yaml += `    name: "${server.name}"\n`;
		yaml += `    protocol: "${server.protocol}"\n`;
		yaml += `    enabled: ${server.enabled}\n`;
		yaml += `    config:\n`;
		Object.entries(server.config).forEach(([key, value]) => {
			if (typeof value === 'string') {
				yaml += `      ${key}: "${value}"\n`;
			} else if (Array.isArray(value)) {
				yaml += `      ${key}: [${value.map(v => `"${v}"`).join(', ')}]\n`;
			} else {
				yaml += `      ${key}: ${JSON.stringify(value)}\n`;
			}
		});
		yaml += '\n';
	});
	
	return yaml;
};

