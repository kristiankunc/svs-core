# SVS Web Interface

Django-based web interface for SVS Core with Vite frontend.

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 20+ (recommended: 25+)
- npm 10+ (recommended: 11+)

### Install Dependencies

```bash
# Install Node.js dependencies
cd frontend
npm install
```

### Development Workflow

#### Running the Dev Server

For development with Hot Module Replacement (HMR):

```bash
# Terminal 1: Start Vite dev server
cd frontend
npm run dev

# Terminal 2: Start Django dev server
cd ..
python manage.py runserver
```

The Vite dev server runs on `http://127.0.0.1:5173` and provides:

- **Hot Module Replacement (HMR)**: Changes to JS/CSS are reflected instantly without page reload
- **Fast rebuilds**: Only changed files are rebuilt
- **Source maps**: Easy debugging in browser DevTools

When `DEBUG=True` in Django settings, templates automatically load assets from the Vite dev server.

#### Building for Production

```bash
cd frontend
npm run build
```

This creates optimized, minified assets in `static/vite/`:

- JavaScript is bundled and minified with esbuild
- CSS is extracted and minified
- A manifest file is generated for Django to reference

When `DEBUG=False`, Django serves the built assets from `static/vite/`.

## How It Works

### Development Mode (`DEBUG=True`)

1. Vite dev server runs on port 5173
1. Django templates load:
   - `@vite/client` script for HMR
   - Main entry point from dev server (`http://127.0.0.1:5173/src/main.js`)
1. CSS is injected by Vite automatically (no separate `<link>` tag needed)
1. Changes to `frontend/src/` trigger HMR updates

### Production Mode (`DEBUG=False`)

1. Run `npm run build` to generate assets
1. Django templates load:
   - CSS from `static/vite/assets/main-*.css`
   - JS from `static/vite/assets/main-*.js`
1. Asset paths are resolved using `manifest.json`

## Architecture

### Frontend Stack

- **Vite 7**: Build tool and dev server
- **Bootstrap 5**: UI framework with custom primary color (#ffa724)
- **Alpine.js 3**: Lightweight JavaScript framework
- **Highlight.js**: Code syntax highlighting
- **Sass**: CSS preprocessor

### Template Tag

The `{% vite %}` template tag in `app/templatetags/vite.py` handles:

- Switching between dev and production asset URLs
- Loading the HMR client in development
- Resolving asset paths from the manifest in production

### Configuration Files

- `frontend/vite.config.js`: Vite configuration
  - Dev server settings (HMR, watch options)
  - Build optimization
  - Output directory configuration
- `frontend/package.json`: Node.js dependencies and scripts
- `project/settings.py`: Django settings (DEBUG mode, static files)

## Troubleshooting

### HMR Not Working

- Ensure Vite dev server is running (`npm run dev` in `frontend/`)
- Check that `DEBUG=True` in Django settings
- Verify browser console for connection errors

### Build Errors

- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Clear the build output: `rm -rf static/vite`

### Assets Not Loading in Production

- Run `npm run build` to generate assets
- Ensure `DEBUG=False` in Django settings
- Check that `static/vite/.vite/manifest.json` exists
