# Live Room API Specification

## Base URL
```
https://api.yourdomain.com/api/v1
```

## Authentication
All endpoints require JWT Bearer token in header (except public endpoints).

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Start Live Stream

**Endpoint**: `POST /live/start`

**Description**: Create a new live room and get streaming credentials.

**Request**:
```json
{
  "title": "My First Live Stream",
  "description": "Welcome to my stream!",
  "category": "music",
  "tags": ["guitar", "cover", "live"],
  "language": "en",
  "thumbnail_url": "https://cdn.yourdomain.com/thumbnails/123.jpg"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "room_id": 12345,
    "stream_key": "live_a1b2c3d4e5f6",
    "ingest_url": "rtmp://ingest.yourdomain.com/live/live_a1b2c3d4e5f6",
    "playback_url": "https://cdn.yourdomain.com/hls/12345/master.m3u8",
    "webrtc_signaling_url": "wss://signal.yourdomain.com",
    "room": {
      "id": 12345,
      "host": {
        "id": 789,
        "username": "john_doe",
        "display_name": "John Doe",
        "avatar_url": "https://cdn.yourdomain.com/avatars/789.jpg",
        "level": 15
      },
      "title": "My First Live Stream",
      "description": "Welcome to my stream!",
      "category": "music",
      "tags": ["guitar", "cover", "live"],
      "status": "live",
      "current_viewers": 0,
      "started_at": "2026-01-23T10:30:00Z"
    }
  }
}
```

**Errors**:
- `400 Bad Request`: Missing required fields
- `409 Conflict`: Host already has an active live room
- `429 Too Many Requests`: Rate limit exceeded

---

### 2. End Live Stream

**Endpoint**: `POST /live/:room_id/end`

**Description**: End an active live stream.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "room_id": 12345,
    "status": "ended",
    "session_summary": {
      "duration_seconds": 3600,
      "peak_viewers": 1250,
      "total_viewers": 5430,
      "total_gifts_received": 125000,
      "total_messages": 8934,
      "average_watch_time": 450
    }
  }
}
```

**Errors**:
- `404 Not Found`: Room not found
- `403 Forbidden`: Not the host of this room
- `400 Bad Request`: Room is not live

---

### 3. Get Live Room Details

**Endpoint**: `GET /live/:room_id`

**Description**: Get details of a live room.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "room": {
      "id": 12345,
      "host": {
        "id": 789,
        "username": "john_doe",
        "display_name": "John Doe",
        "avatar_url": "https://cdn.yourdomain.com/avatars/789.jpg",
        "level": 15,
        "badges": [
          {
            "type": "verified",
            "icon_url": "https://cdn.yourdomain.com/badges/verified.png"
          }
        ],
        "is_following": false,
        "total_followers": 12450
      },
      "title": "My First Live Stream",
      "description": "Welcome to my stream!",
      "category": "music",
      "tags": ["guitar", "cover", "live"],
      "thumbnail_url": "https://cdn.yourdomain.com/thumbnails/123.jpg",
      "status": "live",
      "current_viewers": 856,
      "peak_viewers": 1250,
      "total_viewers": 5430,
      "total_gifts": 125000,
      "started_at": "2026-01-23T10:30:00Z",
      "playback_url": "https://cdn.yourdomain.com/hls/12345/master.m3u8"
    },
    "top_gifters": [
      {
        "user": {
          "id": 456,
          "username": "big_fan",
          "avatar_url": "https://cdn.yourdomain.com/avatars/456.jpg",
          "level": 25
        },
        "total_coins": 25000
      }
    ]
  }
}
```

---

### 4. Join Live Room

**Endpoint**: `POST /live/:room_id/join`

**Description**: Join a live room as a viewer.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "room": { /* same as Get Room Details */ },
    "viewer_count": 857,
    "ws_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "chat_server_url": "wss://chat.yourdomain.com",
    "playback_urls": {
      "hls": "https://cdn.yourdomain.com/hls/12345/master.m3u8?token=xxx&expires=1674567890",
      "webrtc": "wss://sfu.yourdomain.com/room/12345"
    }
  }
}
```

**Errors**:
- `404 Not Found`: Room not found or not live
- `403 Forbidden`: User is banned from this room

---

### 5. Leave Live Room

**Endpoint**: `POST /live/:room_id/leave`

**Description**: Leave a live room.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "watch_time_seconds": 450,
    "gifts_sent": 5,
    "messages_sent": 23
  }
}
```

---

### 6. Get Active Live Rooms

**Endpoint**: `GET /live/active`

**Description**: Get list of currently active live rooms.

**Query Parameters**:
- `category` (optional): Filter by category
- `language` (optional): Filter by language
- `limit` (default: 20, max: 100)
- `offset` (default: 0)
- `sort` (default: viewers): Sort by (viewers, started_at, gifts)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "rooms": [
      {
        "id": 12345,
        "host": {
          "id": 789,
          "username": "john_doe",
          "display_name": "John Doe",
          "avatar_url": "https://cdn.yourdomain.com/avatars/789.jpg",
          "level": 15
        },
        "title": "My First Live Stream",
        "category": "music",
        "tags": ["guitar", "cover", "live"],
        "thumbnail_url": "https://cdn.yourdomain.com/thumbnails/123.jpg",
        "current_viewers": 856,
        "started_at": "2026-01-23T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 1247,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
  }
}
```

---

### 7. Get Recommended Rooms

**Endpoint**: `GET /live/recommended`

**Description**: Get personalized room recommendations based on user preferences.

**Query Parameters**:
- `limit` (default: 20)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "rooms": [ /* same format as active rooms */ ]
  }
}
```

---

### 8. Get Room Viewers

**Endpoint**: `GET /live/:room_id/viewers`

**Description**: Get current viewers in a room (host only).

**Query Parameters**:
- `limit` (default: 50)
- `offset` (default: 0)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "viewers": [
      {
        "user": {
          "id": 456,
          "username": "viewer1",
          "avatar_url": "https://cdn.yourdomain.com/avatars/456.jpg",
          "level": 10
        },
        "joined_at": "2026-01-23T10:35:00Z",
        "watch_time_seconds": 300,
        "gifts_sent": 2,
        "messages_sent": 15
      }
    ],
    "total_viewers": 856
  }
}
```

---

### 9. Update Room Settings

**Endpoint**: `PATCH /live/:room_id`

**Description**: Update live room settings while streaming (host only).

**Request**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["new", "tags"]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "room": { /* updated room object */ }
  }
}
```

---

### 10. Get Room Statistics

**Endpoint**: `GET /live/:room_id/stats`

**Description**: Get detailed statistics for a room (host only).

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "room_id": 12345,
    "current_viewers": 856,
    "peak_viewers": 1250,
    "total_viewers": 5430,
    "viewer_timeline": [
      { "timestamp": "2026-01-23T10:30:00Z", "count": 10 },
      { "timestamp": "2026-01-23T10:35:00Z", "count": 45 },
      { "timestamp": "2026-01-23T10:40:00Z", "count": 123 }
    ],
    "gifts": {
      "total_received": 125000,
      "count": 450,
      "top_gift": {
        "gift_id": 5,
        "name": "Super Rocket",
        "count": 25
      }
    },
    "engagement": {
      "total_messages": 8934,
      "average_watch_time": 450,
      "bounce_rate": 0.23
    },
    "quality": {
      "average_bitrate": 2450,
      "average_fps": 29,
      "dropped_frames": 45
    }
  }
}
```

---

## WebSocket Events

### Connection

```javascript
const ws = new WebSocket('wss://chat.yourdomain.com');

ws.on('connect', () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token'
  }));

  // Join room
  ws.send(JSON.stringify({
    type: 'join_room',
    room_id: 12345
  }));
});
```

### Events from Server

#### viewer.joined
```json
{
  "type": "viewer.joined",
  "data": {
    "user": {
      "id": 456,
      "username": "new_viewer",
      "avatar_url": "https://cdn.yourdomain.com/avatars/456.jpg"
    },
    "viewer_count": 857
  }
}
```

#### viewer.left
```json
{
  "type": "viewer.left",
  "data": {
    "user_id": 456,
    "viewer_count": 856
  }
}
```

#### gift.sent
```json
{
  "type": "gift.sent",
  "data": {
    "sender": {
      "id": 456,
      "username": "big_fan",
      "avatar_url": "https://cdn.yourdomain.com/avatars/456.jpg"
    },
    "gift": {
      "id": 5,
      "name": "Super Rocket",
      "animation_url": "https://cdn.yourdomain.com/animations/rocket.json",
      "quantity": 1,
      "combo_count": 5
    },
    "total_coins": 1000
  }
}
```

#### message.sent
```json
{
  "type": "message.sent",
  "data": {
    "id": 12345,
    "user": {
      "id": 456,
      "username": "viewer1",
      "avatar_url": "https://cdn.yourdomain.com/avatars/456.jpg",
      "level": 10
    },
    "message": "Hello everyone!",
    "timestamp": "2026-01-23T10:35:00Z"
  }
}
```

#### room.ended
```json
{
  "type": "room.ended",
  "data": {
    "room_id": 12345,
    "reason": "host_ended",
    "session_summary": {
      "duration_seconds": 3600,
      "peak_viewers": 1250
    }
  }
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "error": {
    "code": "ROOM_NOT_FOUND",
    "message": "The requested room does not exist or is not live",
    "details": {}
  }
}
```

### Common Error Codes

- `UNAUTHORIZED`: Missing or invalid authentication token
- `FORBIDDEN`: User doesn't have permission
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `VALIDATION_ERROR`: Invalid input data
- `ROOM_NOT_LIVE`: Room is not currently live
- `ALREADY_IN_ROOM`: User already in another room
- `HOST_ALREADY_LIVE`: Host already has an active stream
- `INSUFFICIENT_BALANCE`: Not enough coins for operation
- `USER_BANNED`: User is banned from this room/platform

---

## Rate Limits

```
Anonymous users:    20 requests/minute
Authenticated:     100 requests/minute
Premium users:     500 requests/minute
```

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1674567890
```

---

## Next Steps

- [Gift API](./gift-api.md)
- [Wallet API](./wallet-api.md)
- [User API](./user-api.md)
- [Chat API](./chat-api.md)
