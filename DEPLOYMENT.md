# Deployment Guide - Render

Quick reference guide for deploying DaNomNoms API to Render.

## Quick Start

1. **Push code to GitHub** (if not already done)
2. **Go to [Render Dashboard](https://dashboard.render.com)**
3. **Click "New +" → "Blueprint"**
4. **Connect your GitHub repo**
5. **Set environment variables** (see below)
6. **Deploy!**

## Required Environment Variables

Set these in Render Dashboard → Your Service → Environment:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DOORDASH_DEVELOPER_ID` | DoorDash Developer ID | `your_dev_id` |
| `DOORDASH_KEY_ID` | DoorDash Key ID | `your_key_id` |
| `DOORDASH_SIGNING_SECRET` | DoorDash signing secret (base64url) | `your_secret` |

## MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account (M0 cluster)
3. Create a database user
4. Whitelist IP addresses (or use `0.0.0.0/0` for Render)
5. Get connection string: `mongodb+srv://<username>:<password>@cluster.mongodb.net/`
6. Add database name: `mongodb+srv://<username>:<password>@cluster.mongodb.net/DaNomNoms`

## After Deployment

1. **Get your API URL**: `https://danomnoms-api.onrender.com`
2. **Test health endpoint**: `https://danomnoms-api.onrender.com/health`
3. **View API docs**: `https://danomnoms-api.onrender.com/docs`
4. **Update CORS** in `app.py` if you have a frontend

## Troubleshooting

### Service won't start
- Check build logs in Render dashboard
- Verify all environment variables are set
- Check that MongoDB URI is correct and accessible

### Database connection errors
- Verify MongoDB Atlas IP whitelist includes Render IPs
- Check MongoDB connection string format
- Ensure database user has correct permissions

### Slow first request (Free Tier)
- This is normal on Render's free tier (15 min spin-down)
- First request after inactivity takes 30-60 seconds
- Upgrade to paid plan to avoid spin-down

### CORS errors
- Update `allow_origins` in `app.py` from `["*"]` to your frontend domain
- Example: `allow_origins=["https://your-frontend.vercel.app"]`

## Upgrading from Free Tier

For production, consider upgrading to:
- **Starter Plan** ($7/month): No spin-down, better performance
- **Standard Plan** ($25/month): More resources, better for production

## Monitoring

- **Logs**: View in Render dashboard → Your Service → Logs
- **Metrics**: Available in paid plans
- **Health Checks**: Render automatically monitors `/health` endpoint

## Continuous Deployment

Render automatically deploys when you push to:
- `main` branch (production)
- Other branches (preview deployments)

To disable auto-deploy or change branch:
- Go to Service Settings → Build & Deploy
