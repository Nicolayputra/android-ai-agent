import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { prettyJSON } from 'hono/pretty-json';
import { secureHeaders } from 'hono/secure-headers';

/**
 * NOIR AGENT v6.0 — CLOUDFLARE GATEWAY
 * ======================================
 * Akun: si-umkm-ikm-pbd
 * URL:  https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev
 * D1:   noir-db (6ba7279d-e022-481e-8d1b-d05aa773d305)
 * R2:   noir-storage
 * Authority: USER (Absolute Sovereign)
 */

type Bindings = {
  DB: D1Database;
  STORAGE: R2Bucket;
  NOIR_API_KEY: string;
  ENVIRONMENT: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// ─── GLOBAL MIDDLEWARE ───
app.use('*', logger());
app.use('*', prettyJSON());
app.use('*', cors());
app.use('*', secureHeaders());

// ─── AUTH ───
const auth = (c: any): boolean => {
  const key =
    c.req.header('Authorization')?.replace('Bearer ', '') ||
    c.req.header('X-API-Key');
  const validKey = c.env.NOIR_API_KEY || "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
  return key === validKey;
};

const unauthorized = (c: any) =>
  c.json({ error: 'Unauthorized. Noir Agent: Sovereign Authority Required.' }, 401);

// ─── ADMIN: MIGRATION (Emergency Schema Fix) ───
app.get('/admin/migrate', async (c) => {
  if (!auth(c)) return unauthorized(c);
  try {
    // 1. Add stats column to agents
    await c.env.DB.prepare(`ALTER TABLE agents ADD COLUMN stats TEXT`).run();
  } catch (e) {}
  
  try {
    // 2. Add last_screenshot column if missing
    await c.env.DB.prepare(`ALTER TABLE agents ADD COLUMN last_screenshot TEXT`).run();
  } catch (e) {}

  return c.json({ status: 'migration_attempted', ts: new Date().toISOString() });
});

// ─── PUBLIC: HEALTH CHECK ───
app.get('/health', (c) =>
  c.json({
    agent: 'Noir Agent v6.0',
    status: 'online',
    environment: c.env.ENVIRONMENT || 'production',
    ts: new Date().toISOString(),
  })
);

// ─── AGENT REGISTER (v11.0 with Stats) ───
app.post('/agent/register', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const { device_id, agent, stats } = await c.req.json();
  const stats_str = stats ? JSON.stringify(stats) : null;
  
  await c.env.DB.prepare(
    `INSERT INTO agents (device_id, name, last_seen, stats)
     VALUES (?, ?, CURRENT_TIMESTAMP, ?)
     ON CONFLICT(device_id) DO UPDATE SET 
        last_seen = CURRENT_TIMESTAMP, 
        name = excluded.name,
        stats = ?`
  ).bind(device_id, agent, stats_str, stats_str).run();
  
  return c.json({ status: 'registered', device_id });
});

// ─── DASHBOARD SUMMARY (v11.0 Elite - FAILSAFE) ───
app.get('/agent/summary', async (c) => {
  if (!auth(c)) return unauthorized(c);
  
  let agentData: any = null;
  let commands: any[] = [];
  let assets: string[] = [];
  let isOnline = false;

  try {
    // 1. Fetch Agent Stats
    const agent = await c.env.DB.prepare(
      `SELECT name, last_seen, stats FROM agents ORDER BY last_seen DESC LIMIT 1`
    ).first();
    
    if (agent) {
      isOnline = (Date.now() - new Date(agent.last_seen as string).getTime() < 60000);
      agentData = {
        name: agent.name,
        last_seen: agent.last_seen,
        stats: agent.stats ? JSON.parse(agent.stats as string) : {}
      };
    }
  } catch (e) { console.error("DB Agent Error", e); }

  try {
    // 2. Fetch Recent Commands
    const { results } = await c.env.DB.prepare(
      `SELECT id, description, status, result, updated_at FROM commands 
       ORDER BY updated_at DESC LIMIT 10`
    ).all();
    commands = results;
  } catch (e) { console.error("DB Command Error", e); }

  try {
    // 3. Fetch Asset List
    const assetList = await c.env.STORAGE.list({ limit: 5 });
    assets = assetList.objects.map(o => o.key);
  } catch (e) { console.error("Storage Error", e); }
  
  return c.json({
    online: isOnline,
    agent: agentData,
    commands,
    assets
  });
});

// ─── POLL (Agent minta perintah) ───
app.get('/agent/poll', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const { results } = await c.env.DB.prepare(
    `SELECT id as command_id, action FROM commands
     WHERE status = 'pending' ORDER BY created_at ASC LIMIT 5`
  ).all();

  if (results.length > 0) {
    const ids = results.map((r) => r.command_id);
    await c.env.DB.prepare(
      `UPDATE commands SET status = 'sent' WHERE id IN (${ids.map(() => '?').join(',')})`
    ).bind(...ids).run();
  }

  return c.json({
    commands: results.map((r) => ({
      command_id: r.command_id,
      action: JSON.parse(r.action as string),
    })),
  });
});

// ─── PUSH COMMAND (Dashboard/Telegram kirim perintah) ───
app.post('/agent/command', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const body = await c.req.json();
  const id = crypto.randomUUID().split('-')[0].toUpperCase();
  await c.env.DB.prepare(
    `INSERT INTO commands (id, action, description, status, created_at)
     VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)`
  ).bind(id, JSON.stringify(body.action), body.description || 'Manual').run();
  return c.json({ status: 'queued', command_id: id });
});

// ─── RESULT (Agent kirim hasil eksekusi) ───
app.post('/agent/result', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const { command_id, success, output, error, device_id } = await c.req.json();
  await c.env.DB.prepare(
    `UPDATE commands SET status = 'done', result = ?, updated_at = CURRENT_TIMESTAMP
     WHERE id = ?`
  ).bind(JSON.stringify({ success, output, error, device_id }), command_id).run();
  return c.json({ ok: true });
});

// ─── ASSET STORAGE (R2) ───

// Agent upload screenshot ke R2
app.post('/agent/upload', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const body = await c.req.parseBody();
  const file = body['file'] as File;
  const device_id = body['device_id'] as string;

  if (!file) return c.json({ error: 'No file uploaded' }, 400);

  const key = `ss_${device_id}_${Date.now()}.png`;
  await c.env.STORAGE.put(key, await file.arrayBuffer(), {
    httpMetadata: { contentType: 'image/png' },
  });

  // --- AUTO-PURGE OLD ASSETS (Maintenance-Free) ---
  try {
    const list = await c.env.STORAGE.list({ prefix: `ss_${device_id}` });
    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    for (const obj of list.objects) {
        // Asumsi nama file ss_id_timestamp.png
        const ts = parseInt(obj.key.split('_')[2]);
        if (ts < sevenDaysAgo) {
            await c.env.STORAGE.delete(obj.key);
            console.log(`[Auto-Purge] Deleted old asset: ${obj.key}`);
        }
    }
  } catch(e) { console.error("Purge Error", e); }

  return c.json({ ok: true, key });
});

// Ambil asset dari R2
app.get('/agent/asset/:key', async (c) => {
  const key = c.req.param('key');
  const object = await c.env.STORAGE.get(key);
  if (!object) return c.json({ error: 'Asset not found' }, 404);

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('etag', object.httpEtag);

  return new Response(object.body, { headers });
});

// ─── RESULTS HISTORY (Dashboard ambil histori) ───
app.get('/agent/results', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const { results } = await c.env.DB.prepare(
    `SELECT id, description, action, result, updated_at FROM commands
     WHERE status = 'done' ORDER BY updated_at DESC LIMIT 20`
  ).all();
  return c.json({ results });
});

// ─── ASSET LIST (Dashboard ambil gallery) ───
app.get('/agent/assets', async (c) => {
  if (!auth(c)) return unauthorized(c);
  const list = await c.env.STORAGE.list();
  return c.json({
    assets: list.objects.map(obj => ({
      key: obj.key,
      size: obj.size,
      uploaded: obj.uploaded
    })).sort((a, b) => b.uploaded.getTime() - a.uploaded.getTime())
  });
});

// ─── 404 HANDLER ───
app.notFound((c) =>
  c.json({ error: 'Route tidak ditemukan', path: c.req.path }, 404)
);

// ─── ERROR HANDLER ───
app.onError((err, c) => {
  console.error('[Noir Gateway Error]', err);
  return c.json({ error: 'Internal Server Error', message: err.message }, 500);
});

export default app;
