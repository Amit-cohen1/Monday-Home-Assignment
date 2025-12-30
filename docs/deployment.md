# Deployment Guide: QBR Auto-Drafter

This guide covers deploying the QBR Auto-Drafter to Streamlit Community Cloud with secure API key management.

---

## Prerequisites

1. **GitHub Account** - Your code must be pushed to a GitHub repository
2. **OpenAI API Key** - Get one at [platform.openai.com](https://platform.openai.com/api-keys)
3. **Streamlit Account** - Free at [share.streamlit.io](https://share.streamlit.io)

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────────┐     ┌─────────────┐
│   User Browser  │────▶│   Streamlit Cloud        │────▶│  OpenAI API │
│  (Password Auth)│     │  (Secrets Manager)       │     │   (GPT-4o)  │
└─────────────────┘     └──────────────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Encrypted    │
                        │ Secrets:     │
                        │ - API Key    │
                        │ - Password   │
                        └──────────────┘
```

**Security Features:**
- OpenAI API key is stored server-side in encrypted secrets
- Users never see or enter the API key
- Password protection for app access
- All traffic over HTTPS

---

## Step 1: Local Development Setup

1. Create a `.streamlit/secrets.toml` file for local testing:

```toml
# .streamlit/secrets.toml (DO NOT COMMIT!)
OPENAI_API_KEY = "sk-your-actual-key-here"
APP_PASSWORD = "your-password-here"
```

2. Test locally:
```bash
streamlit run app.py
```

3. Verify password protection works and QBR generation functions correctly.

---

## Step 2: Push to GitHub

Ensure your code is pushed to GitHub. The `.gitignore` already excludes `secrets.toml`.

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

---

## Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub

2. Click **"New app"**

3. Select your repository and branch:
   - Repository: `your-username/Monday-Home-Assignment`
   - Branch: `main`
   - Main file path: `app.py`

4. Click **"Advanced settings"** before deploying

5. In the **Secrets** section, add your secrets in TOML format:

```toml
OPENAI_API_KEY = "sk-proj-your-actual-openai-key"
APP_PASSWORD = "SecurePassword123!"
```

6. Click **"Deploy!"**

---

## Step 4: Share the App

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL along with the password with authorized users.

---

## Managing Secrets After Deployment

To update secrets (e.g., rotate API key or change password):

1. Go to your app's dashboard at [share.streamlit.io](https://share.streamlit.io)
2. Click the **⋮** menu next to your app
3. Select **"Settings"**
4. Go to the **"Secrets"** tab
5. Update the values and save
6. The app will automatically reboot with new secrets

---

## Disabling Password Protection

If you want to remove password protection (not recommended for public deployments):

Simply remove the `APP_PASSWORD` line from your secrets. The app will detect that no password is configured and skip authentication.

---

## Troubleshooting

### "API key not configured" Error
- Verify `OPENAI_API_KEY` is set in Streamlit Cloud secrets
- Check there are no extra spaces or quotes around the key
- Ensure the key starts with `sk-`

### "Incorrect password" Error
- Verify `APP_PASSWORD` matches exactly (case-sensitive)
- Check for trailing spaces in the secret value

### App Won't Start
- Check the logs in Streamlit Cloud dashboard
- Verify all dependencies are in `requirements.txt`
- Ensure Python version compatibility

---

## Cost Considerations

- **Streamlit Community Cloud**: Free for public repos
- **OpenAI API**: Pay-per-use pricing
  - GPT-4o: ~$5 per 1M input tokens, ~$15 per 1M output tokens
  - Typical QBR generation: ~$0.01-0.03 per report

---

## Security Best Practices

1. **Rotate API keys regularly** - Update in Streamlit Cloud secrets
2. **Use strong passwords** - Minimum 12 characters with mixed case and numbers
3. **Monitor usage** - Check OpenAI dashboard for unusual activity
4. **Limit access** - Only share the password with authorized users

---

*Deployment Guide - QBR Auto-Drafter*
*Last updated: December 2024*

