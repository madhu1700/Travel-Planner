# Google OAuth Setup Instructions

To enable Google OAuth login for your Travel Planner app, follow these steps:

## 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** or **Google Identity** for your project
4. Navigate to **APIs & Services** > **Credentials**
5. Click **Create Credentials** > **OAuth 2.0 Client ID**
6. Configure the OAuth consent screen if you haven't already
7. Select **Web application** as the application type

## 2. Add Authorized JavaScript Origins

Add ALL of the following URLs to **Authorized JavaScript origins**:

```
https://itinera-2.preview.emergentagent.com
https://itinera-2.emergent.cloud
```

**If you have a custom domain, also add:**
```
https://your-custom-domain.com
```

## 3. Add Authorized Redirect URIs

Add ALL of the following URLs to **Authorized redirect URIs**:

```
https://itinera-2.preview.emergentagent.com/auth/google
https://itinera-2.emergent.cloud/auth/google
```

**If you have a custom domain, also add:**
```
https://your-custom-domain.com/auth/google
```

## 4. Get Your Client ID

After creating the OAuth client:
1. Copy the **Client ID** (it will look like: `123456789-abcdefg.apps.googleusercontent.com`)
2. You DON'T need the Client Secret for frontend-only OAuth

## 5. Update the Frontend

Open `/app/frontend/src/App.js` and replace the placeholder:

```javascript
const GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID";
```

With your actual Client ID:

```javascript
const GOOGLE_CLIENT_ID = "123456789-abcdefg.apps.googleusercontent.com";
```

## 6. Restart the Frontend

```bash
sudo supervisorctl restart frontend
```

## Important Notes

⚠️ **CRITICAL**: You MUST add ALL URLs (preview, deployed, and custom domain if applicable) to Google Console, or OAuth will fail on those domains.

⚠️ The redirect URLs in the code use `window.location.origin` dynamically, so they work across all domains automatically - DO NOT HARDCODE them.

✅ Once configured, users can log in with any Gmail account (no whitelist restriction).

## Testing

1. Open your app in the browser
2. Click "Login with Google" or "Continue with Google"
3. Select your Google account
4. You should be redirected to the dashboard

If you encounter errors, double-check that all URLs are added to Google Console.
