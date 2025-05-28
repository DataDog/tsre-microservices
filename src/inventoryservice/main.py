import os
import sys
import time
import random
import redis
from flask import Flask, jsonify, request
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
    
    logger.info(f"Attempting to connect to Redis at {redis_host}:{redis_port}")
    try:
        # Simulate Redis connection issues
        if random.random() < 0.7:  # 70% chance of connection failure
            raise redis.ConnectionError("Failed to connect to Redis")
            
        redis_client = redis.Redis(host=redis_host, port=redis_port)
        logger.info("Successfully connected to Redis")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}", extra={
            'redis_host': redis_host,
            'redis_port': redis_port,
            'error_type': type(e).__name__
        })
        raise

def process_inventory():
    """Process inventory data with Redis dependency"""
    backoff = 1
    max_backoff = 30
    consecutive_failures = 0
    
    while True:
        try:
            # Try to connect to Redis
            redis_client = connect_to_redis()
            
            # If we get here, connection was successful
            if consecutive_failures > 0:
                logger.info(f"Recovered from {consecutive_failures} consecutive failures")
                consecutive_failures = 0
            
            backoff = 1  # Reset backoff on success
            
            # Simulate normal inventory processing
            start_time = time.time()
            products_processed = 0
            
            for i in range(100):
                product_id = f"PROD-{random.randint(1000, 9999)}"
                stock = random.randint(0, 100)
                reserved = random.randint(0, 50)
                
                inventory_data[product_id] = {
                    'stock': stock,
                    'reserved': reserved
                }
                products_processed += 1
                
                # Log low stock warnings
                if stock < 10:
                    logger.warning(f"Low stock alert for product {product_id}", extra={
                        'product_id': product_id,
                        'current_stock': stock,
                        'reserved': reserved
                    })
            
            processing_time = time.time() - start_time
            logger.info(f"Inventory processing complete", extra={
                'products_processed': products_processed,
                'processing_time_seconds': round(processing_time, 2),
                'total_products': len(inventory_data)
            })
            
            time.sleep(5)
            
        except redis.ConnectionError as e:
            consecutive_failures += 1
            logger.error(f"Redis connection error (attempt {consecutive_failures})", extra={
                'error': str(e),
                'backoff_seconds': backoff,
                'consecutive_failures': consecutive_failures
            })
            # Exponential backoff
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            
        except Exception as e:
            logger.error(f"Unexpected error in inventory processing", extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'consecutive_failures': consecutive_failures
            })
            sys.exit(1)

@app.route('/health')
def health_check():
    logger.info("Health check requested")
    return jsonify({"status": "healthy"})

@app.route('/inventory/<product_id>')
def get_inventory(product_id):
    logger.info(f"Inventory lookup requested", extra={
        'product_id': product_id,
        'client_ip': request.remote_addr
    })
    
    if product_id in inventory_data:
        logger.info(f"Product found", extra={
            'product_id': product_id,
            'stock': inventory_data[product_id]['stock'],
            'reserved': inventory_data[product_id]['reserved']
        })
        return jsonify(inventory_data[product_id])
    
    logger.warning(f"Product not found", extra={
        'product_id': product_id,
        'client_ip': request.remote_addr
    })
    return jsonify({
        "product_id": product_id,
        "quantity": 0,
        "status": "not_found"
    })

if __name__ == '__main__':
    try:
        logger.info("Starting inventory service", extra={
            'redis_host': os.getenv("REDIS_HOST", "redis"),
            'redis_port': os.getenv("REDIS_PORT", "6379")
        })
        process_inventory()
    except Exception as e:
        logger.error(f"Service failed to start", extra={
            'error': str(e),
            'error_type': type(e).__name__
        })
        sys.exit(1) 