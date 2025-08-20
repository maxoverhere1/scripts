# Contentful Webhooks

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install ngrok:**
   ```bash
   brew install --cask ngrok
   ```

3. **Start the webhook server:**
   ```bash
   python3 webhook_server.py
   ```
   Server runs on `http://localhost:5000/webhook`

4. **Expose server to the internet (in a new terminal):**
   ```bash
   ngrok http 5000
   ```
   Copy the `https://` URL from ngrok output (e.g., `https://abc123.ngrok.io`)

5. **Test with curl (optional but recommended):**
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/webhook \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook", "message": "hello from curl"}'
   ```

6. **Create webhook in Contentful:**
   - Open `contentful_webhooks.http` in your HTTP client
   - **Change the URL** in the request to your ngrok URL + `/webhook`
   - Run the "Create webhook for local development server" request

7. **Test with real Contentful changes:**
   - Make changes in Contentful
   - Watch terminal for webhook messages
   - Check `webhook_log.json` for logs

Done! 🎉
