# Vercel Deployment Configuration

## Project Settings in Vercel Dashboard

When setting up your project in Vercel, use these settings:

### Build & Development Settings

- **Framework Preset**: Other
- **Root Directory**: `frontend/landing`
- **Build Command**: Leave empty (or use `echo "Static site"`)
- **Output Directory**: Leave empty (defaults to root)
- **Install Command**: Leave empty

### Alternative: Use vercel.json

The `vercel.json` file in the root will automatically configure these settings.

## Deploy

```bash
# Install Vercel CLI (optional)
npm i -g vercel

# Deploy from root directory
vercel

# Or just push to GitHub - Vercel will auto-deploy
git push origin main
```

## Custom Domain

After deployment, you can add a custom domain in Vercel dashboard:
- Go to your project settings
- Click "Domains"
- Add your domain (e.g., concilium.ai)

## Environment Variables

If you need to point to your API:
- Add environment variable in Vercel: `VITE_API_URL=https://api.concilium.com`
- Update script.js to use this URL for API calls

## Troubleshooting

### 404 Error
- Make sure Root Directory is set to `frontend/landing` in Vercel dashboard
- Or use the vercel.json configuration file

### Files Not Found
- Ensure index.html, styles.css, and script.js are in `frontend/landing/`
- Check that paths in HTML are relative (not absolute)

### Deployment Not Updating
- Clear Vercel cache: Settings > General > Clear Cache
- Redeploy: Deployments > Click "..." > Redeploy
