# SvelteKit Template

A template for deploying [SvelteKit](https://svelte.dev/) applications using Node.js, perfect for modern web applications.

## What is SvelteKit?

SvelteKit is a framework for building web applications using Svelte. It provides server-side rendering, routing, and other features needed for production-ready web apps. This template uses the Node.js adapter to deploy your SvelteKit application.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your SvelteKit application:

1. **Prepare your SvelteKit app** - Configure Node.js adapter (see below)
2. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `svelte` or `sveltekit`
3. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure environment variables as needed
4. **[Upload your code](../../../guides/common-steps.md#upload-files)** - Via GIT or SSH
5. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Your app will build and start
6. **Access your application** - Via your configured domain or port

## Prepare Your SvelteKit Application

### Required Configuration

Your SvelteKit project must use the **Node.js adapter**. Install it if not already configured:

```bash
npm install -D @sveltejs/adapter-node
```

Configure it in `svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter()
  }
};

export default config;
```

### Required Files

- **`package.json`** - Node.js dependencies and scripts
- **`svelte.config.js`** - SvelteKit configuration with Node adapter
- **`src/`** - Your SvelteKit application source code

### Example `package.json`

```json
{
  "name": "my-sveltekit-app",
  "version": "0.0.1",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "@sveltejs/adapter-node": "^5.0.0",
    "@sveltejs/kit": "^2.0.0",
    "svelte": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

## Configuration

### Default Settings

- **Runtime:** Node.js with SvelteKit
- **Working Directory:** `/app` (your SvelteKit project root)
- **Build Process:** Automatically runs `npm install` and `npm run build`
- **Port:** Container port 3000 (default Node.js adapter port) is exposed
- **Volume:** `/app` directory stores your application code
- **Start Command:** Runs the built application using Node.js

### Environment Variables

[Configure your application](../../../guides/common-steps.md#configure-environment-variables) using environment variables:

```bash
--env PUBLIC_API_URL=https://api.example.com \
--env DATABASE_URL=postgresql://user:pass@db:5432/mydb \
--env NODE_ENV=production
```

Access environment variables in SvelteKit:

**Public variables** (available in browser):
```javascript
// Use PUBLIC_ prefix
import { PUBLIC_API_URL } from '$env/static/public';
```

**Private variables** (server-side only):
```javascript
// No PUBLIC_ prefix
import { DATABASE_URL } from '$env/static/private';
```

### Customizing Port

To use a different port, configure the Node adapter in `svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-node';

const config = {
  kit: {
    adapter: adapter({
      out: 'build',
      env: {
        port: 'PORT'
      }
    })
  }
};

export default config;
```

Then set the `PORT` environment variable when creating the service.

## Connecting to Databases

### PostgreSQL Example

Install the PostgreSQL client:
```bash
npm install pg
```

Create a database connection:
```javascript
// src/lib/db.js
import pg from 'pg';
import { DATABASE_URL } from '$env/static/private';

const pool = new pg.Pool({
  connectionString: DATABASE_URL
});

export default pool;
```

Use in your routes:
```javascript
// src/routes/+page.server.js
import pool from '$lib/db';

export async function load() {
  const result = await pool.query('SELECT * FROM items');
  return {
    items: result.rows
  };
}
```

Configure with:
```bash
--env DATABASE_URL=postgresql://user:password@my-postgres:5432/mydb
```

For more details, see [Access Services via DNS](../../../guides/common-steps.md#access-services-via-dns).

## Build Process

The template automatically:

1. **Copies your code** to `/app` directory
2. **Installs dependencies** with `npm install`
3. **Builds your application** with `npm run build`
4. **Starts the production server** using the built output

All build output is logged. [Check logs](../../../guides/common-steps.md#view-service-logs) if builds fail.

## Troubleshooting

### Build Failures

1. **[Check logs](../../../guides/common-steps.md#view-service-logs):** View detailed error messages
2. **Verify package.json:** Ensure all dependencies are listed
3. **Check Node version:** Ensure your app is compatible with the Node.js version in the template
4. **Verify adapter:** Ensure `@sveltejs/adapter-node` is installed and configured

### Application Won't Start

1. **Check build output:** Ensure build completed successfully
2. **Verify adapter configuration:** Check `svelte.config.js`
3. **Check port:** Ensure the app listens on `0.0.0.0` (not `localhost`)

### Module Not Found Errors

1. **Missing dependency:** Add package to `package.json`
2. **Rebuild:** After updating `package.json`, [restart the service](../../../guides/common-steps.md#restart-a-service) to trigger rebuild

### Static Assets Not Loading

1. **Check build output:** Verify static files are in the build directory
2. **Adapter configuration:** Ensure adapter is configured correctly
3. **Check routes:** Verify asset paths in your code

## API Routes

SvelteKit supports API routes. Create them in `src/routes/api/`:

```javascript
// src/routes/api/hello/+server.js
import { json } from '@sveltejs/kit';

export function GET() {
  return json({
    message: 'Hello from API!'
  });
}
```

Access at `https://myapp.example.com/api/hello`.

## Server-Side Rendering (SSR)

SvelteKit supports SSR by default. To disable for specific pages:

```javascript
// src/routes/+page.js
export const ssr = false;
```

## Best Practices

- **Use Node adapter:** This template requires `@sveltejs/adapter-node`
- **Environment variables:** Use `PUBLIC_` prefix for browser-accessible variables
- **Production mode:** Set `NODE_ENV=production` for production deployments
- **Error handling:** Implement proper error pages in `src/routes/+error.svelte`
- **Build optimization:** Use SvelteKit's built-in optimizations

## Common Use Cases

- **Web Applications:** Full-featured web apps with SSR
- **API Backends:** RESTful APIs using SvelteKit's API routes
- **Static Sites:** Pre-render pages for static hosting
- **Single Page Apps:** Disable SSR for SPA behavior
- **Progressive Web Apps:** Add service workers for PWA features

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/svelte.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/svelte.Dockerfile"
    ```

## Additional Resources

- [SvelteKit Official Documentation](https://svelte.dev/docs/kit)
- [Node Adapter Documentation](https://svelte.dev/docs/kit/adapter-node)
- [Svelte Official Documentation](https://svelte.dev/docs)
- [Common Deployment Steps](../../../guides/common-steps.md)
