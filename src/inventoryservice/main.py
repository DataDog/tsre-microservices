import os
import sys
import time
from flask import Flask, jsonify
from logger import getJSONLogger

app = Flask(__name__)

# Configure logging using the JSON logger
logger = getJSONLogger('inventoryservice')

# This will cause the service to crash on startup
def check_required_services():
    required_services = {
        "REDIS_HOST": os.getenv("REDIS_HOST", "redis"),
        "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/inventory")
    }
    
    # Intentionally fail to check Redis
    if not required_services["REDIS_HOST"]:
        raise Exception("Redis host not configured")
    
    # This will always fail
    raise Exception("Intentionally failing to demonstrate crashloop")

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/inventory/<product_id>')
def get_inventory(product_id):
    return jsonify({
        "product_id": product_id,
        "quantity": 0,
        "status": "out_of_stock"
    })

if __name__ == '__main__':
    try:
        # This will crash the service
        check_required_services()
        
        # This code will never be reached
        port = int(os.getenv("PORT", "8080"))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Service failed to start: {str(e)}")
        sys.exit(1) 