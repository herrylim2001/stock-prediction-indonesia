# Whitelabel Live Streaming Platform

A B2B SaaS platform for whitelabel live streaming with virtual gift monetization.

## Overview

This platform enables:
- **Providers** (Platform Owners) to onboard multiple clients (brands)
- **Clients** (Brands) to manage their hosts and payouts
- **Hosts** (Talent) to go live and earn through virtual gifts

## Tech Stack

### Backend
- **Language**: Go 1.21+
- **Framework**: Gin
- **Database**: PostgreSQL
- **ORM**: GORM
- **Auth**: JWT

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand + React Query
- **Forms**: React Hook Form + Zod

## Project Structure

```
.
├── backend/                 # Go API server
│   ├── cmd/api/            # Application entrypoint
│   ├── internal/
│   │   ├── config/         # Configuration
│   │   ├── database/       # Database connection
│   │   ├── handlers/       # HTTP handlers
│   │   ├── middleware/     # Auth, CORS middleware
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── Dockerfile
│   └── go.mod
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities, API client
│   │   └── types/         # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # Production compose
├── docker-compose.dev.yml  # Development compose
└── Makefile               # Development commands
```

## Quick Start

### Prerequisites
- Go 1.21+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/herrylim2001/whitelabel-streaming.git
   cd whitelabel-streaming
   ```

2. **Start database services**
   ```bash
   make dev-db
   ```

3. **Start backend** (in terminal 1)
   ```bash
   cd backend
   cp .env.example .env
   go run ./cmd/api
   ```

4. **Start frontend** (in terminal 2)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API Health: http://localhost:8080/health

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login for all roles
- `POST /api/v1/auth/register/provider` - Register provider
- `GET /api/v1/auth/me` - Get current user

### Provider Routes (`/api/v1/provider/*`)
- `GET /dashboard` - Provider dashboard stats
- `GET/POST /clients` - List/create clients
- `GET/PUT/DELETE /clients/:id` - Manage client
- `POST /clients/:id/activate` - Activate client
- `POST /clients/:id/suspend` - Suspend client
- `GET/POST /gifts` - Manage gift catalog

### Client Routes (`/api/v1/client/*`)
- `GET /dashboard` - Client dashboard stats
- `GET/POST /hosts` - List/create hosts
- `GET/PUT/DELETE /hosts/:id` - Manage host
- `GET /sessions` - List sessions
- `GET /payouts` - List payouts
- `POST /payouts/:id/approve` - Approve payout
- `POST /payouts/:id/reject` - Reject payout

### Host Routes (`/api/v1/host/*`)
- `GET /dashboard` - Host dashboard stats
- `GET/PUT /profile` - Manage profile
- `GET /earnings` - View earnings
- `POST /sessions/start` - Start live session
- `POST /sessions/:id/end` - End live session
- `POST /payouts` - Request payout

## User Roles

| Role | Description | Access |
|------|-------------|--------|
| Provider | Platform owner/super admin | Full platform control |
| Client | Brand/operator | Manage own hosts and payouts |
| Host | Content creator/talent | Go live, view earnings |

## Development

### Make Commands

```bash
make help        # Show all commands
make dev         # Start everything
make dev-db      # Start only database
make backend     # Run backend
make frontend    # Run frontend
make test        # Run tests
make fmt         # Format code
```

### Environment Variables

**Backend (.env)**
```env
SERVER_PORT=8080
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=whitelabel_streaming
JWT_SECRET=your-secret-key
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
```

## License

MIT
