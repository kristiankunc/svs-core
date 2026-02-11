# SvelteKit Template

A template for deploying [SvelteKit](https://svelte.dev/) applications using Node.js.

## Usage

1. Prepare your SvelteKit app (see below)
2. [Create a service](../../../guides/index.md#create-a-service)
3. [Upload your code](../../../guides/index.md#uploading-files) via GIT or SSH
4. [Start the service](../../../guides/index.md#control)

## Preparation

Your project **must use the Node.js adapter**. Install it:
```bash
npm install -D @sveltejs/adapter-node
```

Configure in `svelte.config.js`:
```javascript
import adapter from '@sveltejs/adapter-node';

const config = {
  kit: {
    adapter: adapter()
  }
};

export default config;
```

## Configuration

- **Runtime:** Node.js with SvelteKit
- **Working Directory:** `/app`
- **Build:** Automatically runs `npm install` and `npm run build`
- **Port:** Container port 3000 (default)
- **Volume:** `/app` - Application code

## Environment Variables

**Public variables** (browser-accessible):
```javascript
import { PUBLIC_API_URL } from '$env/static/public';
```

**Private variables** (server-only):
```javascript
import { DATABASE_URL } from '$env/static/private';
```

Example:
```bash
--env PUBLIC_API_URL=https://api.example.com \
--env DATABASE_URL=postgresql://my-db:5432/mydb
```

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/svelte.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/svelte.Dockerfile"
    ```
