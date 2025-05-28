import os
import sys
import time
import random
import redis
from flask import Flask, jsonify
from logger import getJSONLogger

app = Flask(__name__)

# Configure logging using the JSON logger
logger = getJSONLogger('inventoryservice')

# Simulate inventory data
inventory_data = {}

def connect_to_redis():
    """Attempt to connect to Redis with increasing backoff"""
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    
    try:
        # Simulate Redis connection issues
        if random.random() < 0.7:  # 70% chance of connection failure
            raise redis.ConnectionError("Failed to connect to Redis")
            
        return redis.Redis(host=redis_host, port=redis_port)
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        raise

def process_inventory():
    """Process inventory data with Redis dependency"""
    backoff = 1
    max_backoff = 30
    
    while True:
        try:
            # Try to connect to Redis
            redis_client = connect_to_redis()
            
            # If we get here, connection was successful
            logger.info("Successfully connected to Redis")
            backoff = 1  # Reset backoff on success
            
            # Simulate normal inventory processing
            for i in range(100):
                product_id = f"PROD-{random.randint(1000, 9999)}"
                inventory_data[product_id] = {
                    'stock': random.randint(0, 100),
                    'reserved': random.randint(0, 50)
                }
            
            logger.info(f"Processed {len(inventory_data)} products")
            time.sleep(5)
            
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            # Exponential backoff
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            sys.exit(1)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/inventory/<product_id>')
def get_inventory(product_id):
    if product_id in inventory_data:
        return jsonify(inventory_data[product_id])
    return jsonify({
        "product_id": product_id,
        "quantity": 0,
        "status": "not_found"
    })

if __name__ == '__main__':
    try:
        logger.info("Starting inventory service")
        process_inventory()
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
        sys.exit(1) 