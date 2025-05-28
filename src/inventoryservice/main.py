import os
import sys
import time
import random
from flask import Flask, jsonify
from logger import getJSONLogger

app = Flask(__name__)

# Configure logging using the JSON logger
logger = getJSONLogger('inventoryservice')

# Simulate inventory data
inventory_data = {}

def process_inventory():
    """Process inventory data with increasing complexity"""
    try:
        while True:
            # Simulate inventory processing with less frequent updates
            for i in range(100):  # Reduced from 1000
                product_id = f"PROD-{random.randint(1000, 9999)}"
                inventory_data[product_id] = {
                    'stock': random.randint(0, 100),
                    'reserved': random.randint(0, 50),
                    'history': [random.randint(0, 100) for _ in range(100)]  # Reduced from 1000
                }
            
            # Log normal operation
            logger.info(f"Processed {len(inventory_data)} products")
            time.sleep(5)  # Increased sleep time to reduce resource usage
            
    except MemoryError:
        logger.error("Inventory processing failed")
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