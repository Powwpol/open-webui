/**
 * Pulsai Inference API Client
 * Unified API for Ollama, vLLM, and multi-backend inference
 */

export interface InferenceRequest {
	model: string;
	prompt?: string;
	messages?: Array<{ role: string; content: string }>;
	temperature?: number;
	max_tokens?: number;
	top_p?: number;
	top_k?: number;
	stop?: string[];
	stream?: boolean;
	backend?: string;
}

export interface InferenceResponse {
	model: string;
	content: string;
	finish_reason?: string;
	usage?: {
		prompt_tokens?: number;
		completion_tokens?: number;
		total_tokens?: number;
	};
	backend: string;
	latency_ms?: number;
	error?: string;
}

export interface ModelInfo {
	id: string;
	name: string;
	backend: string;
	context_window?: number;
	capabilities?: string[];
	parameters?: Record<string, any>;
	available: boolean;
}

export interface BackendStatus {
	backend: string;
	healthy: boolean;
	latency_ms?: number;
	models_count: number;
	request_count: number;
	status: string;
	error?: string;
}

export interface BackendHealth {
	current_status: string;
	uptime_24h: number;
	avg_latency_ms?: number;
	checks_count: number;
}

export interface BackendConfig {
	backend_type: string;
	base_url: string;
	api_key?: string;
	timeout?: number;
}

/**
 * Generate completion (non-streaming)
 */
export const generateCompletion = async (
	token: string,
	request: InferenceRequest
): Promise<InferenceResponse> => {
	const res = await fetch(`/api/v1/inference/generate`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Generation failed');
	}

	return await res.json();
};

/**
 * Generate completion (streaming)
 */
export const generateCompletionStream = async (
	token: string,
	request: InferenceRequest
): Promise<ReadableStream> => {
	const res = await fetch(`/api/v1/inference/generate/stream`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Stream generation failed');
	}

	return res.body!;
};

/**
 * List all available models from all backends
 */
export const listAllModels = async (token: string): Promise<Record<string, ModelInfo[]>> => {
	const res = await fetch(`/api/v1/inference/models`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		throw new Error('Failed to fetch models');
	}

	return await res.json();
};

/**
 * Get backend status
 */
export const getBackendsStatus = async (token: string): Promise<Record<string, BackendStatus>> => {
	const res = await fetch(`/api/v1/inference/backends/status`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		throw new Error('Failed to fetch backend status');
	}

	return await res.json();
};

/**
 * Get backend health metrics
 */
export const getBackendsHealth = async (
	token: string
): Promise<Record<string, BackendHealth>> => {
	const res = await fetch(`/api/v1/inference/backends/health`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		throw new Error('Failed to fetch backend health');
	}

	return await res.json();
};

/**
 * Add new backend dynamically
 */
export const addBackend = async (token: string, config: BackendConfig): Promise<void> => {
	const res = await fetch(`/api/v1/inference/backends/add`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(config)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to add backend');
	}
};

/**
 * Remove backend
 */
export const removeBackend = async (token: string, backendName: string): Promise<void> => {
	const res = await fetch(`/api/v1/inference/backends/${backendName}`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to remove backend');
	}
};

/**
 * Test backend connection
 */
export const testBackendConnection = async (
	token: string,
	config: BackendConfig
): Promise<{ success: boolean; latency_ms?: number; error?: string }> => {
	try {
		// Temporarily add backend
		await addBackend(token, config);

		// Check status
		const status = await getBackendsStatus(token);
		const backendStatus = status[config.backend_type];

		// Remove temporary backend
		await removeBackend(token, config.backend_type);

		return {
			success: backendStatus?.healthy ?? false,
			latency_ms: backendStatus?.latency_ms,
			error: backendStatus?.error
		};
	} catch (error) {
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Connection test failed'
		};
	}
};

