# ZELZAL v5.0 — Cybersecurity Platform

Full-stack cybersecurity platform with Flask backend, React frontend, and Kali Linux toolkit.

## Architecture

```
ZELZAL/
├── backend/          # Flask API server (Python)
│   ├── app.py        # Main entry point
│   ├── models.py     # 7 SQLAlchemy models
│   ├── routes/       # 7 API blueprints
│   ├── auth.py       # JWT + bcrypt authentication
│   └── seed.py       # Database seeder
├── frontend/         # React SPA (Vite + Tailwind)
│   ├── src/
│   │   ├── api/      # Axios client with JWT refresh
│   │   ├── context/  # Auth + Language providers
│   │   ├── i18n/     # Arabic/English translations
│   │   └── components/
│   │       ├── Common/   # 9 shared components
│   │       ├── Layout/   # Navbar, Sidebar
│   │       └── Sections/ # 7 pages
│   └── ...
├── kali_tools/       # Standalone Kali Linux toolkit
│   ├── zelzal.py     # Rich TUI launcher
│   ├── core.py       # Core engine
│   └── modules/      # 7 security modules
├── render.yaml       # Render deployment config
└── Dockerfile        # Container deployment
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py    # Seed database
python app.py     # Start on :5000
```

### Frontend (development)
```bash
cd frontend
npm install
npm run dev       # Start on :3000
```

### Kali Toolkit
```bash
cd kali_tools
pip install -r requirements.txt
python zelzal.py
```

## Deployment

### Render
1. Push to GitHub
2. Connect repo to Render
3. Use `render.yaml` for automatic config
4. Set `SECRET_KEY` and `JWT_SECRET_KEY` env vars

### Docker
```bash
docker build -t zelzal .
docker run -p 5000:5000 -e SECRET_KEY=... -e JWT_SECRET_KEY=... zelzal
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | dev fallback | Flask secret key |
| `JWT_SECRET_KEY` | No | dev fallback | JWT signing key |
| `DATABASE_URL` | No | SQLite | PostgreSQL for production |
| `FLASK_DEBUG` | No | 0 | Debug mode |

## Features

- **Dark cyberpunk theme** with neon green (#00ff41) aesthetics
- **Arabic/English RTL support** with Cairo font
- **JWT authentication** with access/refresh tokens + blocklist
- **Rate limiting** on all API endpoints
- **Security headers** (CSP, HSTS, X-Frame-Options, etc.)
- **7 API blueprints**: auth, dashboard, security, AI, projects, analytics, users
- **7 Kali modules**: network, web, firewall, system, performance, identity, container
- **Real tool integration**: nmap, iptables, clamav, lynis, docker, kubectl, trivy

## Credentials (Dev)

```
Admin: admin / admin123
Users: cyber_agent/agent123, netwatch/watch123, ...
```

## License

MIT
