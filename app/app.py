from flask import Flask, jsonify, request
import redis
import json
import os

app = Flask(__name__)

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
MILVUS_HOST = os.getenv('MILVUS_HOST', 'milvus')
MILVUS_PORT = int(os.getenv('MILVUS_PORT', 19530))

redis_client = None
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
except:
    redis_client = None

@app.route('/')
def hello():
    return jsonify({
        "message": "AI Web App with Redis and Milvus", 
        "status": "success",
        "services": ["redis", "milvus"]
    })

@app.route('/health')
def health():
    status = {
        "status": "healthy",
        "service": "ai-web-app",
        "redis": "disconnected"
    }
    
    if redis_client:
        try:
            redis_client.ping()
            status["redis"] = "connected"
        except Exception as e:
            status["status"] = "unhealthy"
            status["redis"] = f"error: {str(e)}"
    else:
        status["status"] = "unhealthy"
        status["redis"] = "not initialized"
    
    return jsonify(status)

@app.route('/cache', methods=['POST', 'GET'])
def cache():
    if not redis_client:
        return jsonify({"error": "Redis not available"}), 503
        
    if request.method == 'POST':
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        if key and value:
            redis_client.set(key, json.dumps(value))
            return jsonify({"message": "Data cached", "key": key}), 201
        return jsonify({"error": "Key and value required"}), 400
    
    # GET method
    key = request.args.get('key')
    if key:
        value = redis_client.get(key)
        if value:
            return jsonify({"key": key, "value": json.loads(value)}), 200
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"error": "Key parameter required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
