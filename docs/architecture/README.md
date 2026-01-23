# Live Streaming Platform Architecture
## Platform Streaming Mirip Bigo Live

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Core Components](#core-components)
4. [Technology Stack](#technology-stack)
5. [Scalability & Performance](#scalability--performance)
6. [Security](#security)
7. [Documentation Structure](#documentation-structure)

---

## Overview

Platform live streaming yang komprehensif dengan fitur-fitur:
- 📹 Live streaming (host to viewers)
- 💬 Real-time chat
- 🎁 Virtual gifts & monetization
- 👥 Multi-host (PK battles)
- 🏆 Leaderboards & gamification
- 💰 Wallet & payment system
- 🛡️ Content moderation

**Target Scale**:
- Concurrent viewers: 100K - 1M+
- Concurrent rooms: 10K+
- Latency: 1-3 seconds (WebRTC) atau 3-10 seconds (HLS)

---

## High-Level Architecture

Platform dibagi menjadi 4 layer utama:

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
│  (Mobile Apps: iOS/Android, Web App)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EDGE & REALTIME LAYER                      │
│  • CDN (HLS/DASH Distribution)                              │
│  • WebRTC SFU Nodes (Low Latency)                           │
│  • WebSocket Servers (Chat, Signaling)                      │
│  • RTMP/WebRTC Ingest Nodes                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE BACKEND LAYER                        │
│         (API Gateway + Microservices)                        │
│  • Live Room Service    • Gift Service                      │
│  • User Service         • Wallet Service                    │
│  • Auth Service         • Ranking Service                   │
│  • Moderation Service   • Notification Service              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│  • PostgreSQL (Main DB)  • Redis (Cache)                    │
│  • Kafka (Event Bus)     • S3 (Object Storage)              │
│  • Elasticsearch (Logs)  • InfluxDB (Metrics)               │
└─────────────────────────────────────────────────────────────┘
```

**Lihat diagram detail**: [High-Level Architecture Diagram](./diagrams/01-high-level-architecture.md)

---

## Core Components

### 1. Streaming Engine
Pipeline untuk ingest, transcode, dan distribusi video stream.

- **Ingest**: RTMP/WebRTC dari host
- **Transcoding**: Multi-bitrate adaptive streaming
- **Distribution**: HLS/DASH via CDN, WebRTC via SFU
- **Recording**: Optional session recording ke S3

**Detail**: [Streaming Pipeline](./components/streaming-pipeline.md)

### 2. Realtime Communication
Sistem untuk komunikasi real-time antara host dan viewers.

- **Signaling Server**: WebSocket untuk room events
- **Chat Server**: Real-time messaging
- **Gift Event System**: Broadcast gift animations
- **Presence System**: Online/offline status

**Detail**: [Realtime Communication](./components/realtime-communication.md)

### 3. Backend Services (Microservices)
Kumpulan microservices untuk business logic.

- **User Service**: Authentication, profiles, followers
- **Live Room Service**: Room management, viewer tracking
- **Wallet Service**: Virtual currency, top-up, payouts
- **Gift Service**: Virtual gifts catalog & transactions
- **Ranking Service**: Leaderboards & achievements
- **Moderation Service**: Content moderation, bans

**Detail**: [Backend Services](./components/backend-services.md)

### 4. Data & Storage
Lapisan data untuk persistence dan caching.

- **PostgreSQL**: Transactional data
- **Redis**: Caching, session, real-time counters
- **Kafka**: Event streaming & message queue
- **S3-compatible**: Video recordings, thumbnails, assets
- **Elasticsearch**: Search & logs
- **InfluxDB**: Time-series metrics

**Detail**: [Data Architecture](./components/data-architecture.md)

---

## Technology Stack

### Backend
- **Language**: Go / Node.js / Java (pilih sesuai expertise)
- **API Framework**:
  - Go: Gin, Fiber, or Echo
  - Node.js: Express, NestJS, or Fastify
  - Java: Spring Boot
- **API Gateway**: Kong, Traefik, or AWS API Gateway
- **Service Mesh** (optional): Istio, Linkerd

### Streaming
- **Media Server**:
  - SRS (Simple Realtime Server)
  - Ant Media Server
  - Janus Gateway (WebRTC)
  - Mediasoup (WebRTC SFU)
- **Transcoder**: FFmpeg
- **CDN**: Cloudflare, AWS CloudFront, or Akamai

### Real-time
- **WebSocket**: Socket.io, WS, or native WebSocket
- **Message Broker**:
  - Kafka (high throughput)
  - RabbitMQ (easier setup)
  - NATS (low latency)

### Database & Storage
- **RDBMS**: PostgreSQL 14+
- **Cache**: Redis 6+
- **Object Storage**: MinIO, AWS S3, or DigitalOcean Spaces
- **Search**: Elasticsearch 8+
- **Metrics**: InfluxDB + Grafana

### DevOps & Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions, GitLab CI, or Jenkins
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger or Zipkin

### Mobile SDK
- **Streaming**:
  - Agora SDK (commercial)
  - Zego SDK (commercial)
  - Custom WebRTC SDK
- **Chat**: Socket.io client or native WebSocket

---

## Scalability & Performance

### Horizontal Scaling Strategy

```
Component                 | Scaling Method
--------------------------|----------------------------------
API Gateway              | Load Balancer + Auto-scaling
WebSocket Servers        | Sticky sessions + Redis PubSub
Ingest Nodes             | GeoDNS + Multi-region
Transcoding Workers      | Queue-based + Auto-scaling
SFU Nodes                | Dynamic routing based on load
Microservices            | Kubernetes HPA
Database                 | Read replicas + Sharding
Redis                    | Cluster mode
```

### Performance Targets

- **API Response Time**: < 100ms (p95)
- **Streaming Latency**:
  - HLS: 3-10 seconds
  - WebRTC: < 1 second
- **Chat Message Delivery**: < 200ms
- **Concurrent Viewers per Room**: 100K+
- **Database Query Time**: < 50ms (p95)

**Detail**: [Scalability Guide](./components/scalability.md)

---

## Security

### Authentication & Authorization
- JWT-based authentication
- OAuth 2.0 for social login
- Role-based access control (RBAC)
- API key for service-to-service communication

### Data Protection
- TLS/SSL for all communications
- Encrypted storage for sensitive data (PII, payment info)
- Tokenized stream URLs (HMAC-signed with expiry)
- Rate limiting per IP and per user

### Content Security
- Content moderation (AI + manual review)
- DMCA compliance for recordings
- Real-time abuse detection
- Geo-blocking capability

### Infrastructure Security
- WAF (Web Application Firewall)
- DDoS protection
- Network isolation (VPC, security groups)
- Secrets management (HashiCorp Vault, AWS Secrets Manager)

**Detail**: [Security Architecture](./components/security.md)

---

## Documentation Structure

```
docs/architecture/
├── README.md (this file)
├── diagrams/
│   ├── 01-high-level-architecture.md
│   ├── 02-streaming-pipeline.md
│   ├── 03-realtime-flow.md
│   ├── 04-microservices.md
│   └── 05-deployment.md
├── components/
│   ├── streaming-pipeline.md
│   ├── realtime-communication.md
│   ├── backend-services.md
│   ├── data-architecture.md
│   ├── scalability.md
│   └── security.md
├── api/
│   ├── authentication.md
│   ├── live-room-api.md
│   ├── chat-api.md
│   ├── gift-api.md
│   ├── wallet-api.md
│   └── user-api.md
└── database/
    ├── schema-overview.md
    ├── user-schema.md
    ├── live-schema.md
    ├── wallet-schema.md
    └── migrations/
```

---

## Quick Start

1. **Review Architecture Diagrams**: Start with [High-Level Architecture](./diagrams/01-high-level-architecture.md)
2. **Understand Data Flows**: Read [Streaming Pipeline](./components/streaming-pipeline.md)
3. **Check API Specs**: Review [API Documentation](./api/)
4. **Database Design**: See [Database Schema](./database/schema-overview.md)
5. **Deployment**: Follow [Deployment Guide](./diagrams/05-deployment.md)

---

## Key Design Decisions

### Why Microservices?
- Independent scaling per service
- Team autonomy
- Technology flexibility
- Fault isolation

### Why Event-Driven Architecture?
- Loose coupling between services
- Better scalability
- Asynchronous processing for heavy tasks
- Audit trail for financial transactions

### Why Multi-Region?
- Lower latency for global users
- High availability
- Disaster recovery
- Regulatory compliance (data residency)

### Why CDN for Streaming?
- Handle massive concurrent viewers
- Lower bandwidth cost
- Better user experience
- Reduced load on origin servers

---

## Cost Optimization

### Streaming Costs
- **CDN**: Biggest cost (per GB transferred)
  - Use regional CDN providers
  - Implement adaptive bitrate
  - Optimize segment size
- **Transcoding**: CPU-intensive
  - Use GPU instances for encoding
  - Only transcode when viewers > threshold
  - Cache transcoded segments

### Infrastructure Costs
- Use spot instances for transcoding workers
- Auto-scale down during low traffic
- Implement data retention policies
- Use cold storage for old recordings

---

## Future Enhancements

- AI-powered content moderation
- Real-time translation for chat
- AR filters & effects
- Live commerce integration
- Advanced analytics dashboard
- Machine learning recommendations
- Multi-camera streaming
- 4K streaming support

---

## References

- [WebRTC Specification](https://webrtc.org/)
- [HLS Protocol](https://developer.apple.com/streaming/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [Microservices Patterns](https://microservices.io/patterns/)

---

**Last Updated**: 2026-01-23
**Version**: 1.0
**Author**: Architecture Team
