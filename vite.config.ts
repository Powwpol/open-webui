import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: false,
		rollupOptions: {
			output: {
				manualChunks: {
					'vendor-ui': ['svelte', 'bits-ui', 'paneforge', 'svelte-sonner'],
					'vendor-editor': ['codemirror', '@codemirror/lang-javascript', '@codemirror/lang-python', '@tiptap/core', '@tiptap/starter-kit'],
					'vendor-charts': ['chart.js', 'mermaid'],
					'vendor-pdf': ['pdfjs-dist'],
					'vendor-ml': ['@huggingface/transformers', 'onnxruntime-web'],
				}
			}
		}
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	}
});
