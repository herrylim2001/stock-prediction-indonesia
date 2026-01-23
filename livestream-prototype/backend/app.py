"""
Backend API untuk Livestream Prototype
Fitur: Talent Management, Livestream Control, Real-time Updates
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enable CORS untuk semua routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO untuk real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ============================================
# REST API ENDPOINTS
# ============================================

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Livestream API is running",
        "version": "1.0.0"
    })

# ============================================
# TALENT ENDPOINTS
# ============================================

@app.route('/api/talents', methods=['GET'])
def get_talents():
    """Get semua talent"""
    talents = db.get_all_talents()
    return jsonify({
        "success": True,
        "data": talents
    })

@app.route('/api/talents/<talent_id>', methods=['GET'])
def get_talent(talent_id):
    """Get talent by ID"""
    talent = db.get_talent_by_id(talent_id)
    if talent:
        return jsonify({
            "success": True,
            "data": talent
        })
    return jsonify({
        "success": False,
        "message": "Talent not found"
    }), 404

@app.route('/api/talents/<talent_id>', methods=['PUT'])
def update_talent(talent_id):
    """Update talent data"""
    data = request.get_json()
    talent = db.update_talent(talent_id, data)

    if talent:
        # Broadcast update ke semua client
        socketio.emit('talent_updated', talent, broadcast=True)

        return jsonify({
            "success": True,
            "data": talent
        })
    return jsonify({
        "success": False,
        "message": "Talent not found"
    }), 404

@app.route('/api/talents/<talent_id>/status', methods=['PUT'])
def update_talent_status(talent_id):
    """Update talent status"""
    data = request.get_json()
    status = data.get('status')

    if status not in ['online', 'offline', 'live']:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        }), 400

    talent = db.update_talent_status(talent_id, status)

    if talent:
        # Broadcast status update
        socketio.emit('talent_status_changed', {
            "talent_id": talent_id,
            "status": status
        }, broadcast=True)

        return jsonify({
            "success": True,
            "data": talent
        })
    return jsonify({
        "success": False,
        "message": "Talent not found"
    }), 404

# ============================================
# LIVESTREAM ENDPOINTS
# ============================================

@app.route('/api/livestreams', methods=['GET'])
def get_livestreams():
    """Get semua active livestreams"""
    livestreams = db.get_all_livestreams()
    return jsonify({
        "success": True,
        "data": livestreams
    })

@app.route('/api/livestreams/<livestream_id>', methods=['GET'])
def get_livestream(livestream_id):
    """Get livestream by ID"""
    livestream = db.get_livestream_by_id(livestream_id)
    if livestream:
        return jsonify({
            "success": True,
            "data": livestream
        })
    return jsonify({
        "success": False,
        "message": "Livestream not found"
    }), 404

@app.route('/api/livestreams', methods=['POST'])
def create_livestream():
    """Create livestream baru"""
    data = request.get_json()
    talent_id = data.get('talent_id')
    title = data.get('title', 'Live Stream')

    if not talent_id:
        return jsonify({
            "success": False,
            "message": "talent_id is required"
        }), 400

    livestream = db.create_livestream(talent_id, title)

    if livestream:
        # Broadcast livestream baru ke semua client
        socketio.emit('livestream_started', livestream, broadcast=True)

        return jsonify({
            "success": True,
            "data": livestream
        }), 201

    return jsonify({
        "success": False,
        "message": "Failed to create livestream"
    }), 400

@app.route('/api/livestreams/<livestream_id>/end', methods=['POST'])
def end_livestream(livestream_id):
    """End livestream"""
    success = db.end_livestream(livestream_id)

    if success:
        # Broadcast livestream ended
        socketio.emit('livestream_ended', {
            "livestream_id": livestream_id
        }, broadcast=True)

        return jsonify({
            "success": True,
            "message": "Livestream ended"
        })

    return jsonify({
        "success": False,
        "message": "Livestream not found"
    }), 404

@app.route('/api/livestreams/<livestream_id>/like', methods=['POST'])
def add_like(livestream_id):
    """Tambah like ke livestream"""
    livestream = db.add_like(livestream_id)

    if livestream:
        # Broadcast like update
        socketio.emit('livestream_stats_update', {
            "livestream_id": livestream_id,
            "likes": livestream['likes']
        }, broadcast=True, room=livestream_id)

        return jsonify({
            "success": True,
            "data": livestream
        })

    return jsonify({
        "success": False,
        "message": "Livestream not found"
    }), 404

@app.route('/api/livestreams/<livestream_id>/gift', methods=['POST'])
def send_gift(livestream_id):
    """Send gift (diamonds) ke livestream"""
    data = request.get_json()
    amount = data.get('amount', 1)

    livestream = db.add_diamonds(livestream_id, amount)

    if livestream:
        # Broadcast gift
        socketio.emit('gift_received', {
            "livestream_id": livestream_id,
            "amount": amount,
            "total_diamonds": livestream['diamonds']
        }, broadcast=True, room=livestream_id)

        return jsonify({
            "success": True,
            "data": livestream
        })

    return jsonify({
        "success": False,
        "message": "Livestream not found"
    }), 404

# ============================================
# STATS ENDPOINTS
# ============================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    stats = db.get_platform_stats()
    return jsonify({
        "success": True,
        "data": stats
    })

# ============================================
# SOCKET.IO EVENTS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_livestream')
def handle_join_livestream(data):
    """Handle viewer join livestream"""
    livestream_id = data.get('livestream_id')

    if livestream_id:
        join_room(livestream_id)

        # Increment viewer count
        livestream = db.increment_viewer(livestream_id)

        if livestream:
            # Broadcast viewer update
            emit('viewer_joined', {
                "livestream_id": livestream_id,
                "viewers": livestream['viewers']
            }, room=livestream_id, broadcast=True)

            print(f'Client {request.sid} joined livestream {livestream_id}')

@socketio.on('leave_livestream')
def handle_leave_livestream(data):
    """Handle viewer leave livestream"""
    livestream_id = data.get('livestream_id')

    if livestream_id:
        leave_room(livestream_id)

        # Decrement viewer count
        livestream = db.decrement_viewer(livestream_id)

        if livestream:
            # Broadcast viewer update
            emit('viewer_left', {
                "livestream_id": livestream_id,
                "viewers": livestream['viewers']
            }, room=livestream_id, broadcast=True)

            print(f'Client {request.sid} left livestream {livestream_id}')

@socketio.on('send_comment')
def handle_comment(data):
    """Handle live comment"""
    livestream_id = data.get('livestream_id')
    username = data.get('username', 'Anonymous')
    message = data.get('message', '')

    if livestream_id and message:
        # Broadcast comment ke room
        emit('new_comment', {
            "username": username,
            "message": message,
            "timestamp": db.datetime.now().isoformat()
        }, room=livestream_id, broadcast=True)

@socketio.on('send_like')
def handle_like(data):
    """Handle like event"""
    livestream_id = data.get('livestream_id')

    if livestream_id:
        livestream = db.add_like(livestream_id)

        if livestream:
            # Broadcast like animation
            emit('like_animation', {
                "livestream_id": livestream_id,
                "likes": livestream['likes']
            }, room=livestream_id, broadcast=True)

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Server running on http://localhost:{port}")
    print("Endpoints:")
    print("  - GET  /api/talents")
    print("  - GET  /api/livestreams")
    print("  - GET  /api/stats")
    print("  - POST /api/livestreams")
    print("  - WebSocket: ws://localhost:{}/socket.io/")

    socketio.run(app, host='0.0.0.0', port=port, debug=True)
