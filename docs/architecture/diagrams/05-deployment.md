# Deployment Architecture

## Overview

Platform ini di-deploy menggunakan **Kubernetes** dengan multi-region setup untuk high availability dan low latency global.

---

## Deployment Diagram

```mermaid
graph TB
    subgraph "Global Edge"
        DNS[Global DNS<br/>Route 53]
        CDN[CDN<br/>CloudFlare/CloudFront]
        WAF[WAF<br/>DDoS Protection]
    end

    subgraph "Region: Singapore (Primary)"
        subgraph "K8s Cluster SG"
            APILBSG[API Load Balancer]
            WSLBSG[WebSocket LB]

            subgraph "Ingress"
                IngressSG[Nginx Ingress Controller]
            end

            subgraph "Application Pods"
                AuthPodsSG[Auth Service<br/>3 replicas]
                UserPodsSG[User Service<br/>3 replicas]
                LivePodsSG[Live Service<br/>5 replicas]
                GiftPodsSG[Gift Service<br/>3 replicas]
                WalletPodsSG[Wallet Service<br/>3 replicas]
            end

            subgraph "Realtime Pods"
                WSPodsSG[WebSocket Servers<br/>5 replicas]
                SignalPodsSG[Signaling Servers<br/>3 replicas]
            end

            subgraph "Streaming"
                IngestPodsSG[Ingest Nodes<br/>5 replicas]
                TransPodsSG[Transcoder Workers<br/>10 replicas]
            end
        end

        subgraph "Data Layer SG"
            PGSG[(PostgreSQL Primary<br/>RDS/CloudSQL)]
            RedisSG[(Redis Cluster<br/>ElastiCache)]
            KafkaSG[Kafka Cluster<br/>MSK/Confluent]
        end

        subgraph "Storage SG"
            S3SG[Object Storage<br/>S3/GCS]
        end
    end

    subgraph "Region: US-East (Replica)"
        subgraph "K8s Cluster US"
            IngressUS[Nginx Ingress]
            APIPods US[API Services<br/>Read Replicas]
            WSPodsUS[WebSocket Servers]
            IngestPodsUS[Ingest Nodes]
            TransPodsUS[Transcoder Workers]
        end

        subgraph "Data Layer US"
            PGUS[(PostgreSQL Replica)]
            RedisUS[(Redis Cluster)]
        end
    end

    subgraph "Region: EU (Replica)"
        K8sEU[K8s Cluster EU<br/>Similar Setup]
        DataEU[(Data Layer EU<br/>Read Replicas)]
    end

    subgraph "Monitoring & Logging"
        Prometheus[Prometheus]
        Grafana[Grafana Dashboards]
        ELK[ELK Stack]
        Jaeger[Jaeger Tracing]
    end

    DNS --> WAF
    WAF --> CDN
    CDN --> APILBSG
    CDN --> IngressUS
    CDN --> K8sEU

    APILBSG --> IngressSG
    WSLBSG --> WSPodsSG

    IngressSG --> AuthPodsSG
    IngressSG --> UserPodsSG
    IngressSG --> LivePodsSG
    IngressSG --> GiftPodsSG
    IngressSG --> WalletPodsSG

    AuthPodsSG --> PGSG
    AuthPodsSG --> RedisSG

    LivePodsSG --> PGSG
    LivePodsSG --> RedisSG
    LivePodsSG --> KafkaSG

    WalletPodsSG --> PGSG
    WalletPodsSG --> KafkaSG

    IngestPodsSG --> TransPodsSG
    TransPodsSG --> S3SG
    TransPodsSG --> CDN

    PGSG -.replication.-> PGUS
    PGSG -.replication.-> DataEU

    AuthPodsSG --> Prometheus
    LivePodsSG --> Prometheus
    TransPodsSG --> Prometheus
    Prometheus --> Grafana

    classDef global fill:#e3f2fd,stroke:#1565c0
    classDef primary fill:#e8f5e9,stroke:#2e7d32
    classDef replica fill:#fff3e0,stroke:#ef6c00
    classDef monitoring fill:#f3e5f5,stroke:#6a1b9a

    class DNS,CDN,WAF global
    class APILBSG,IngressSG,AuthPodsSG,LivePodsSG,PGSG,RedisSG primary
    class IngressUS,APIPods,PGUS,K8sEU,DataEU replica
    class Prometheus,Grafana,ELK,Jaeger monitoring
```

---

## Kubernetes Cluster Architecture

### Cluster Specifications

**Primary Region (Singapore)**:
```yaml
cluster:
  name: liveplatform-sg-prod
  version: 1.28
  nodes:
    - node_pool: general
      machine_type: n2-standard-8 (8 vCPU, 32 GB RAM)
      min_nodes: 5
      max_nodes: 20
      auto_scaling: true

    - node_pool: compute-intensive
      machine_type: n2-highcpu-16 (16 vCPU, 16 GB RAM)
      min_nodes: 3
      max_nodes: 50
      auto_scaling: true
      taints:
        - key: workload
          value: transcoding
          effect: NoSchedule

    - node_pool: memory-intensive
      machine_type: n2-highmem-8 (8 vCPU, 64 GB RAM)
      min_nodes: 2
      max_nodes: 10
      auto_scaling: true
      taints:
        - key: workload
          value: cache
          effect: NoSchedule

  networking:
    network_policy: calico
    service_mesh: istio (optional)
```

---

## Service Deployments

### 1. API Gateway (Kong)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kong-gateway
  namespace: gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kong-gateway
  template:
    metadata:
      labels:
        app: kong-gateway
    spec:
      containers:
      - name: kong
        image: kong:3.5
        env:
        - name: KONG_DATABASE
          value: "postgres"
        - name: KONG_PG_HOST
          value: "postgres.database.svc.cluster.local"
        - name: KONG_PROXY_ACCESS_LOG
          value: "/dev/stdout"
        - name: KONG_ADMIN_ACCESS_LOG
          value: "/dev/stdout"
        ports:
        - containerPort: 8000
          name: proxy
        - containerPort: 8443
          name: proxy-ssl
        - containerPort: 8001
          name: admin
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /status
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /status
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: kong-gateway
  namespace: gateway
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    name: proxy
  - port: 443
    targetPort: 8443
    name: proxy-ssl
  selector:
    app: kong-gateway
```

---

### 2. Microservices (Example: Live Service)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: live-service
  namespace: services
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: live-service
  template:
    metadata:
      labels:
        app: live-service
        version: v1
    spec:
      containers:
      - name: live-service
        image: gcr.io/liveplatform/live-service:v1.2.3
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: KAFKA_BROKERS
          value: "kafka-0.kafka.kafka.svc.cluster.local:9092"
        - name: PORT
          value: "8003"
        ports:
        - containerPort: 8003
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: live-service
  namespace: services
spec:
  type: ClusterIP
  ports:
  - port: 8003
    targetPort: 8003
  selector:
    app: live-service
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: live-service-hpa
  namespace: services
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: live-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

### 3. WebSocket Server

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: websocket-server
  namespace: realtime
spec:
  replicas: 5
  selector:
    matchLabels:
      app: websocket-server
  template:
    metadata:
      labels:
        app: websocket-server
    spec:
      containers:
      - name: websocket
        image: gcr.io/liveplatform/websocket-server:v1.0.5
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: PORT
          value: "8080"
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 4000m
            memory: 8Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: websocket-server
  namespace: realtime
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP  # Sticky sessions
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: websocket-server
```

---

### 4. Transcoding Workers

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transcoding-worker
  namespace: streaming
spec:
  replicas: 10
  selector:
    matchLabels:
      app: transcoding-worker
  template:
    metadata:
      labels:
        app: transcoding-worker
    spec:
      nodeSelector:
        workload: transcoding
      tolerations:
      - key: workload
        operator: Equal
        value: transcoding
        effect: NoSchedule
      containers:
      - name: worker
        image: gcr.io/liveplatform/transcoding-worker:v2.1.0
        env:
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: url
        - name: S3_BUCKET
          value: "liveplatform-recordings"
        - name: AWS_REGION
          value: "ap-southeast-1"
        resources:
          requests:
            cpu: 8000m
            memory: 16Gi
          limits:
            cpu: 16000m
            memory: 32Gi
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir:
          sizeLimit: 50Gi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: transcoding-worker-hpa
  namespace: streaming
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transcoding-worker
  minReplicas: 5
  maxReplicas: 100
  metrics:
  - type: External
    external:
      metric:
        name: rabbitmq_queue_messages_ready
        selector:
          matchLabels:
            queue: transcoding_jobs
      target:
        type: Value
        value: "10"  # Scale up if queue > 10
```

---

## Ingress Configuration

### Nginx Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: services
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: api-tls-secret
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /api/v1/auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /api/v1/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 8001
      - path: /api/v1/live
        pathType: Prefix
        backend:
          service:
            name: live-service
            port:
              number: 8003
      - path: /api/v1/gifts
        pathType: Prefix
        backend:
          service:
            name: gift-service
            port:
              number: 8004
      - path: /api/v1/wallet
        pathType: Prefix
        backend:
          service:
            name: wallet-service
            port:
              number: 8005
```

---

## ConfigMaps & Secrets

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: services
data:
  LOG_LEVEL: "info"
  ENVIRONMENT: "production"
  KAFKA_TOPIC_PREFIX: "prod"
  CDN_BASE_URL: "https://cdn.yourdomain.com"
  INGEST_BASE_URL: "rtmp://ingest.yourdomain.com/live"
```

### Secrets (managed via Sealed Secrets or External Secrets Operator)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: services
type: Opaque
data:
  url: <base64-encoded-database-url>
  username: <base64-encoded-username>
  password: <base64-encoded-password>
---
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: services
type: Opaque
data:
  access-token-secret: <base64-encoded-secret>
  refresh-token-secret: <base64-encoded-secret>
```

---

## Database Setup

### PostgreSQL (Managed Service)

**AWS RDS**:
```
Instance: db.r6g.2xlarge (8 vCPU, 64 GB RAM)
Storage: 500 GB SSD (gp3) with autoscaling
Multi-AZ: Yes
Backup: Daily automated backups, 7 days retention
Read Replicas: 2 (same region), 1 per remote region
```

**Connection Pooling (PgBouncer)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
  namespace: database
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pgbouncer
  template:
    metadata:
      labels:
        app: pgbouncer
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:1.21.0
        volumeMounts:
        - name: config
          mountPath: /etc/pgbouncer
        ports:
        - containerPort: 5432
      volumes:
      - name: config
        configMap:
          name: pgbouncer-config
```

---

### Redis (Managed Service)

**AWS ElastiCache**:
```
Node Type: cache.r6g.xlarge (4 vCPU, 26 GB RAM)
Number of Nodes: 3 (1 primary, 2 replicas)
Cluster Mode: Enabled
Shards: 3
Replicas per Shard: 2
Automatic Failover: Enabled
```

---

### Kafka (Managed Service)

**AWS MSK or Confluent Cloud**:
```
Broker Nodes: 3
Instance Type: kafka.m5.2xlarge
Storage: 1 TB per broker
Replication Factor: 3
Partitions: Auto-scaled based on topics
```

---

## CI/CD Pipeline

### GitLab CI / GitHub Actions

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_REGISTRY: gcr.io/liveplatform
  K8S_NAMESPACE: services

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_REGISTRY/live-service:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/live-service:$CI_COMMIT_SHA
  only:
    - main

test:
  stage: test
  image: node:18
  script:
    - npm install
    - npm test
    - npm run lint
  only:
    - main
    - merge_requests

deploy:staging:
  stage: deploy
  image: google/cloud-sdk
  script:
    - gcloud container clusters get-credentials staging-cluster --region asia-southeast1
    - kubectl set image deployment/live-service live-service=$DOCKER_REGISTRY/live-service:$CI_COMMIT_SHA -n $K8S_NAMESPACE
    - kubectl rollout status deployment/live-service -n $K8S_NAMESPACE
  environment:
    name: staging
  only:
    - main

deploy:production:
  stage: deploy
  image: google/cloud-sdk
  script:
    - gcloud container clusters get-credentials prod-cluster --region asia-southeast1
    - kubectl set image deployment/live-service live-service=$DOCKER_REGISTRY/live-service:$CI_COMMIT_SHA -n $K8S_NAMESPACE
    - kubectl rollout status deployment/live-service -n $K8S_NAMESPACE
  environment:
    name: production
  when: manual
  only:
    - main
```

---

## Monitoring & Observability

### Prometheus Setup

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)

      - job_name: 'kubernetes-services'
        kubernetes_sd_configs:
          - role: service
```

### Grafana Dashboards

**Key Metrics**:
- API request rate & latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Concurrent viewers per room
- Streaming bitrate & quality
- Database connection pool usage
- Redis cache hit rate
- Kafka consumer lag
- CPU & memory usage per service

---

## Disaster Recovery

### Backup Strategy

```yaml
# Velero for Kubernetes backups
velero backup create daily-backup \
  --include-namespaces services,database,realtime \
  --snapshot-volumes \
  --ttl 168h  # 7 days

# Database backups
# Automated daily snapshots via RDS
# Point-in-time recovery enabled
# 30-day retention
```

### Failover Procedure

1. **Primary Region Failure**:
   - DNS failover to secondary region (automatic via Route 53)
   - Promote read replica to primary
   - Scale up secondary region capacity

2. **Service Failure**:
   - Kubernetes auto-restarts failed pods
   - HPA scales up if needed
   - Circuit breaker prevents cascade failures

3. **Database Failure**:
   - Automatic failover to standby (Multi-AZ)
   - Promote read replica if needed
   - Point-in-time recovery from snapshots

---

## Cost Optimization

### Strategies

1. **Spot Instances** for transcoding workers (70% cost savings)
2. **Auto-scaling** to match traffic patterns
3. **CDN optimization** (caching, compression)
4. **Database right-sizing** based on metrics
5. **Reserved instances** for baseline capacity
6. **Storage lifecycle** policies (move old data to cold storage)

### Estimated Monthly Costs (10K concurrent streams)

```
Kubernetes Clusters:     $5,000
Database (RDS):          $3,000
Cache (Redis):           $1,500
Kafka:                   $1,000
Object Storage:          $2,000
CDN Bandwidth:          $10,000
Transcoding Workers:     $8,000
Load Balancers:          $500
Monitoring Tools:        $500
------------------------
Total:                  $31,500/month
```

---

## Security Measures

### Network Security

```yaml
# NetworkPolicy example
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress
  namespace: services
spec:
  podSelector:
    matchLabels:
      app: live-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: gateway
    ports:
    - protocol: TCP
      port: 8003
```

### Security Best Practices

- All secrets managed via External Secrets Operator
- TLS everywhere (in-cluster + external)
- Pod Security Standards enforced
- RBAC for all service accounts
- Regular security scanning (Trivy, Snyk)
- WAF rules for common attacks
- DDoS protection via CloudFlare

---

## Summary

Deployment architecture ini dirancang untuk:
- **High Availability**: Multi-region, auto-failover
- **Scalability**: Auto-scaling di semua layer
- **Performance**: CDN, caching, optimized infrastructure
- **Security**: Defense in depth, encryption everywhere
- **Cost Efficiency**: Spot instances, auto-scaling, right-sizing
- **Observability**: Comprehensive monitoring & logging

**Next Steps**:
- Review [Database Schema](../database/schema-overview.md)
- Check [API Documentation](../api/)
- Explore [Streaming Pipeline](../components/streaming-pipeline.md)
