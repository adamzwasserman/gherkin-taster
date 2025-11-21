# Linear OAuth Setup Guide

This guide explains how to configure Linear OAuth authentication for Gherkin Taster.

## Why Linear OAuth?

Gherkin Taster uses Linear OAuth to:
- Allow users to sign in with their Linear accounts (social login)
- Create Linear issues using the user's own credentials (not a service account)
- Ensure proper attribution (issues are created by the actual user)

## Setup Steps

### 1. Create a Linear OAuth Application

1. Go to [Linear OAuth Applications](https://linear.app/settings/api/applications/new)
2. Click **"Create new OAuth application"**
3. Fill in the details:
   - **Name**: `Gherkin Taster` (or your preferred name)
   - **Description**: `Business-friendly Gherkin feature review and approval`
   - **Callback URL**: `http://localhost:8030/auth/callback` (for local development)
   - **Scopes**: Select `read` and `write` (required to create issues)
4. Click **"Create application"**
5. Copy the **Client ID** and **Client Secret** (you'll need these next)

### 2. Update Environment Variables

Open `.env` file and add your OAuth credentials:

```bash
# Linear OAuth Configuration
LINEAR_OAUTH_CLIENT_ID=your_client_id_from_step_1
LINEAR_OAUTH_CLIENT_SECRET=your_client_secret_from_step_1
```

### 3. Restart Docker

After updating `.env`, restart the Docker containers:

```bash
docker-compose restart
```

### 4. Test the Flow

1. Navigate to `http://localhost:8030`
2. You should be redirected to the login page
3. Click **"Sign in with Linear"**
4. Authorize the application in Linear
5. You should be redirected back to `/features` with a valid session

## OAuth Flow

```
User → Login Page → Linear OAuth → Authorization → Callback → Session Created → Features Page
```

### Detailed Flow:

1. **User visits `/`** → Redirected to `/auth/login`
2. **User clicks "Sign in with Linear"** → Redirected to Linear OAuth authorize page
3. **User authorizes app** → Linear redirects to `/auth/callback?code=...`
4. **Backend exchanges code for token** → Calls Linear token endpoint
5. **Backend gets user info** → Calls Linear GraphQL API for user details
6. **Backend creates session** → Stores token in HTTP-only cookie
7. **User redirected to `/features`** → Can now create issues with their token

## Production Setup

For production deployment:

1. **Update callback URL** in Linear OAuth app settings:
   ```
   https://your-domain.com/auth/callback
   ```

2. **Update redirect_uri** in `backend/routes/auth.py`:
   ```python
   redirect_uri = "https://your-domain.com/auth/callback"
   ```

3. **Enable secure cookies** in `backend/routes/auth.py`:
   ```python
   response.set_cookie(
       key="linear_token",
       value=access_token,
       httponly=True,
       secure=True,  # Set to True for HTTPS
       samesite="lax",
       max_age=2592000,
   )
   ```

4. **Move session storage to Redis** (recommended):
   - Currently using cookies (temporary solution)
   - Should move to Redis for better security and session management

## Troubleshooting

### "Invalid client_id" error
- Check that `LINEAR_OAUTH_CLIENT_ID` in `.env` matches the Linear OAuth app
- Restart Docker after updating `.env`

### "Redirect URI mismatch" error
- Ensure callback URL in Linear app matches `http://localhost:8030/auth/callback`
- For production, use HTTPS URL

### Token not persisting
- Check browser allows cookies
- Verify `linear_token` cookie is set (Chrome DevTools → Application → Cookies)

### Can't create issues
- Verify OAuth scopes include `write` permission
- Check user has permission to create issues in the Linear workspace

## Next Steps

After OAuth is configured:

1. **Test screen recording** on `/features/new`
2. **Implement issue creation** using user's Linear token
3. **Add multimedia upload** (store videos/audio, attach to Linear issues)
4. **Integrate AI analysis** (transcribe media, generate Gherkin)

## Security Notes

- Tokens stored in HTTP-only cookies (can't be accessed by JavaScript)
- Cookies should use `secure` flag in production (HTTPS only)
- Session tokens should expire and refresh periodically
- Move to Redis-based session storage for production
- Never commit `.env` file to version control (already in `.gitignore`)
