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


### Full Production Setup

**See the [Web setup guide](http://svs.kristn.co.uk/setup/web/) for detailed instructions on deploying the web interface in production.**
