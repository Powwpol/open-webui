/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'selector',
	theme: {
		extend: {
			// Pulsai Color Palette
            colors: {
				pulsai: {
					'primary': '#FA4616',
					'primary-light': '#FAC090',
					'success': '#00B050',
					'error': '#FF0000',
					'info': '#2751E3',
					'dark': '#000000',
					'dark-2': '#EAEAEA',
					'light': '#FFFFFF',
					'light-2': '#F5F5F5',
					'accent': '#43635A'
                },
                gray: {
                    850: '#1f2937'
                }
			},
			// Pulsai Font Sizes
			fontSize: {
				'nav': '18px',
				'nav-sub': '15px',
				'section': '20px'
			},
			// ReactBits Animations
			keyframes: {
				gradient: {
					'0%': { backgroundPosition: '0% 50%' },
					'50%': { backgroundPosition: '100% 50%' },
					'100%': { backgroundPosition: '0% 50%' },
				},
				'fade-in': {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' },
				},
				'slide-in': {
					'0%': { transform: 'translateX(-100%)' },
					'100%': { transform: 'translateX(0)' },
				},
			},
			animation: {
				'gradient': 'gradient 8s linear infinite',
				'gradient-slow': 'gradient 12s linear infinite',
				'gradient-fast': 'gradient 4s linear infinite',
				'fade-in': 'fade-in 0.5s ease-out',
				'slide-in': 'slide-in 0.3s ease-out',
			},
			// Custom Gradients
			backgroundImage: {
				'pulsai-gradient-orange': 'linear-gradient(135deg, #FA4616, #FAC090)',
				'pulsai-gradient-blue-green': 'linear-gradient(135deg, #2751E3, #00B050)',
				'pulsai-gradient-accent': 'linear-gradient(135deg, #43635A, #00B050)',
			}
		}
	},
	plugins: [
		require('@tailwindcss/typography'),
		require('@tailwindcss/container-queries')
	]
};
