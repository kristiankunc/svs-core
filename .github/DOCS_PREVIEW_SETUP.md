# Documentation Preview Setup

This repository uses Cloudflare Pages to automatically deploy documentation previews for pull requests.

## How It Works

When you open or update a pull request that changes documentation files, a GitHub Actions workflow automatically:

1. Builds the documentation using Zensical (mkdocs)
2. Compiles CLI documentation from the Typer CLI
3. Compiles the fancy typst documentation to PDF
4. Deploys the built documentation to Cloudflare Pages
5. Posts a comment on the PR with the preview URL

## Preview URL Format

Preview deployments are accessible at:
```
https://pr-{PR_NUMBER}.svs-docs.pages.dev
```

For example, PR #42 would be available at: `https://pr-42.svs-docs.pages.dev`

## Required Secrets

To enable this workflow, the following GitHub repository secrets must be configured:

### `CLOUDFLARE_API_TOKEN`

A Cloudflare API token with the following permissions:
- Account > Cloudflare Pages > Edit

To create this token:
1. Go to your Cloudflare dashboard
2. Navigate to "My Profile" → "API Tokens"
3. Click "Create Token"
4. Use the "Edit Cloudflare Workers" template or create a custom token
5. Add the permissions: `Account.Cloudflare Pages:Edit`
6. Set the Account Resources to include your account
7. Create the token and copy it

### `CLOUDFLARE_ACCOUNT_ID`

Your Cloudflare account ID.

To find your account ID:
1. Log in to your Cloudflare dashboard
2. Select any website/domain
3. Scroll down on the right sidebar - you'll see "Account ID"
4. Or navigate to any domain's overview page, and it's in the URL: `https://dash.cloudflare.com/{ACCOUNT_ID}/...`

## Cloudflare Pages Project Setup

### Option 1: Automatic Setup (Recommended)

The workflow will automatically create the Cloudflare Pages project on the first deployment. No manual setup is required!

### Option 2: Manual Setup

If you prefer to set up the project manually:

1. Log in to your Cloudflare dashboard
2. Go to "Workers & Pages" → "Pages"
3. Click "Create a project"
4. Choose "Direct Upload"
5. Set project name to: `svs-docs`
6. You don't need to upload anything - the workflow will handle deployments

## Triggering Preview Deployments

The workflow automatically triggers when:
- A pull request is opened
- New commits are pushed to an open pull request
- A closed pull request is reopened

The workflow only runs when changes are made to:
- `docs/**` - Documentation content
- `mkdocs.yml` - Documentation configuration
- `fancy-docs/**` - Typst documentation source
- `docs-includes/**` - Documentation includes
- `svs_core/**` - Source code (for API documentation)
- `.github/workflows/docs-preview.yml` - The workflow itself

## Cleanup

Preview deployments remain available on Cloudflare Pages but can be managed:
- Cloudflare Pages keeps all deployments by default
- You can manually delete old preview deployments from the Cloudflare dashboard
- Consider setting up retention policies in your Cloudflare Pages project settings

## Production Documentation

Production documentation is deployed separately via the main `publish.yml` workflow when releases are created. It's deployed to GitHub Pages at: https://svs.kristn.co.uk

## Troubleshooting

### Workflow fails with "Unauthorized" error
- Check that `CLOUDFLARE_API_TOKEN` is set correctly
- Verify the token has the required permissions
- Ensure the token hasn't expired

### Workflow fails with "Account not found" error
- Verify `CLOUDFLARE_ACCOUNT_ID` is set correctly
- Check that the account ID matches your Cloudflare account

### Preview URL returns 404
- Wait a few minutes - deployments can take 1-2 minutes to become available
- Check the workflow logs for deployment errors
- Verify the Cloudflare Pages project exists

### Documentation not updating
- Ensure your changes are in the paths that trigger the workflow
- Check that the workflow completed successfully in the Actions tab
- Clear your browser cache and try the preview URL again

## Alternative: GitHub Pages Preview

If you prefer not to use Cloudflare Pages, you can alternatively use:
- **Netlify** - Similar setup using `netlify/actions/cli@master`
- **Vercel** - Using `amondnet/vercel-action@v25`
- **Surge.sh** - Using `afc163/surge-preview@v1`
- **GitHub Pages with subdirectories** - More complex but doesn't require external service

To switch to a different provider, modify the deployment step in `.github/workflows/docs-preview.yml`.
