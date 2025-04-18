# Deploying Smart Soil to Vercel

This guide explains how to deploy the Smart Soil AI application to Vercel's platform.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Git](https://git-scm.com/downloads) installed on your computer
3. [Vercel CLI](https://vercel.com/download) (optional)

## Step 1: Prepare Your Repository

Ensure your project has been committed to a Git repository (GitHub, GitLab, or Bitbucket).

If you're starting from scratch:

```bash
git init
git add .
git commit -m "Initial commit"
```

Then create a new repository on GitHub, GitLab, or Bitbucket and push your code:

```bash
git remote add origin <your-repository-url>
git push -u origin main
```

## Step 2: Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard (Recommended for Beginners)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your repository from GitHub, GitLab, or Bitbucket
4. Configure your project:
   - Leave the framework preset as "Other"
   - No need to modify build settings as they're defined in `vercel.json`
5. Click "Deploy"

### Option 2: Deploy via Vercel CLI

If you prefer using the command line:

1. Install Vercel CLI if you haven't already:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Deploy your project:
   ```bash
   vercel
   ```

4. Follow the prompts to configure your deployment

## Important Notes

### Model Size Considerations

The TensorFlow model (`soil_classifier_model.h5`) is quite large (55MB). This is within Vercel's free tier limits (100MB), but it may cause longer cold starts when the serverless function hasn't been used recently.

### Serverless Limitations

- The application uses `/tmp` directory for file uploads in the serverless environment, which is cleared periodically.
- The model is loaded on-demand to reduce cold start times, but the first prediction after a period of inactivity may still be slow.

### Troubleshooting

If you encounter deployment issues:

1. Check Vercel's deployment logs for errors
2. Ensure your dependencies in `requirements.txt` are compatible with Vercel's Python runtime
3. Verify that the model file is being uploaded correctly

## Custom Domain (Optional)

To use a custom domain for your deployed application:

1. Go to your project in the Vercel dashboard
2. Navigate to "Settings" > "Domains"
3. Add your domain and follow the verification steps

## Monitoring

Vercel provides basic analytics and log information for your deployments. Visit the "Analytics" tab in your project dashboard to monitor performance and usage. 