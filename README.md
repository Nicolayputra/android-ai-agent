# NOIR AGENT v6 — README
# ========================

## Struktur Proyek
```
android-ai-agent/
├── noir-core/          ← Jalankan di Termux (Redmi Note 14)
│   └── agent.py        ← Main loop agent
├── noir-gateway/       ← Deploy ke Cloudflare Workers
│   ├── src/index.ts    ← Gateway logic (Hono)
│   ├── schema.sql      ← D1 database schema
│   ├── wrangler.toml   ← Cloudflare config
│   └── package.json
├── noir-ui/            ← Jalankan di PC
│   └── dashboard.py    ← Command center CLI
├── noir-vps/           ← Deploy ke VPS (AI/ML stack)
├── logs/               ← Log semua aktivitas
├── install.py          ← Installer otomatis untuk Termux
└── .env.example        ← Template konfigurasi
```

## Quick Start

### 1. Setup Cloudflare Gateway
```bash
cd noir-gateway
npm install
wrangler d1 create noir-db
# Salin database_id ke wrangler.toml
wrangler d1 execute noir-db --file=schema.sql
wrangler secret put NOIR_API_KEY
wrangler deploy
```

### 2. Setup Android (Termux)
```bash
git clone <repo> atau salin folder ke /sdcard
cd android-ai-agent
cp .env.example .env
nano .env  # Isi URL gateway dan API key
python install.py
python noir-core/agent.py
```

### 3. Jalankan PC Dashboard
```bash
pip install requests
python noir-ui/dashboard.py
```

## Kewenangan
USER memiliki kewenangan mutlak. Semua tindakan kritis memerlukan konfirmasi.
