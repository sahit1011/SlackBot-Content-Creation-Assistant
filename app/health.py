# app/health.py
from flask import Flask, jsonify
import threading
from app.config import Config

app = Flask(__name__)

# Health status
health_status = {
    'status': 'healthy',
    'services': {
        'slack': 'unknown',
        'database': 'unknown',
        'redis': 'unknown'
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(health_status), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint"""
    if health_status['status'] == 'healthy':
        return jsonify({'status': 'ready'}), 200
    return jsonify({'status': 'not ready'}), 503

def update_health_status(service: str, status: str):
    """Update health status for a service"""
    health_status['services'][service] = status

    # Update overall status
    if all(s != 'unhealthy' for s in health_status['services'].values()):
        health_status['status'] = 'healthy'
    else:
        health_status['status'] = 'unhealthy'

def start_health_server():
    """Start health check server"""
    app.run(host='0.0.0.0', port=Config.HEALTH_CHECK_PORT, debug=False)

def run_health_server_background():
    """Run health server in background thread"""
    thread = threading.Thread(target=start_health_server)
    thread.daemon = True
    thread.start()