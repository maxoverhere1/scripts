#!/usr/bin/env python3
"""
Simple Flask server to receive Contentful webhook messages locally.
Run with: python webhook_server.py
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming webhook from Contentful"""
    try:
        # Get the raw data
        data = request.get_json()
        headers = dict(request.headers)
        
        # Log the webhook received
        timestamp = datetime.now().isoformat()
        logger.info(f"Webhook received at {timestamp}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Payload: {json.dumps(data, indent=2)}")
        
        # Print to console for easy viewing
        print("\n" + "="*50)
        print(f"WEBHOOK RECEIVED - {timestamp}")
        print("="*50)
        print("Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        print("\nPayload:")
        print(json.dumps(data, indent=2))
        print("="*50 + "\n")
        
        # Save to file for persistence
        with open('webhook_log.json', 'a') as f:
            log_entry = {
                'timestamp': timestamp,
                'headers': headers,
                'payload': data
            }
            f.write(json.dumps(log_entry) + '\n')
        
        # Return success response
        return jsonify({'status': 'success', 'message': 'Webhook received'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/', methods=['GET'])
def index():
    """Simple index page"""
    return """
    <h1>Contentful Webhook Server</h1>
    <p>This server is running and ready to receive webhooks!</p>
    <ul>
        <li><strong>Webhook endpoint:</strong> <code>POST /webhook</code></li>
        <li><strong>Health check:</strong> <code>GET /health</code></li>
    </ul>
    <p>Check the console output and <code>webhook_log.json</code> for received webhooks.</p>
    """

if __name__ == '__main__':
    print("Starting Contentful Webhook Server...")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("Health check: http://localhost:5000/health")
    print("Press Ctrl+C to stop")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)
