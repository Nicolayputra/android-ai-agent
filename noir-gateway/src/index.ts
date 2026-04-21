import { Hono } from 'hono';
import { cors } from 'hono/cors';

type Bindings = {
  DB: D1Database;
  BUCKET: R2Bucket;
  API_KEY: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use('*', cors());

// Authentication Middleware
app.use('*', async (c, next) => {
  if (c.req.path === '/' || c.req.path === '/health') return await next();
  const auth = c.req.header('Authorization');
  if (auth !== `Bearer ${c.env.API_KEY}`) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  await next();
});

app.get('/', (c) => c.text('Noir Sovereign Gateway v14.0 ACTIVE'));
app.get('/health', (c) => c.json({ status: 'ok', version: '14.0' }));

// --- AGENT ENDPOINTS ---

app.post('/agent/register', async (c) => {
  const data = await c.req.json();
  const { device_id, agent, stats } = data;
  await c.env.DB.prepare(
    'INSERT OR REPLACE INTO agents (device_id, name, last_seen, stats) VALUES (?, ?, CURRENT_TIMESTAMP, ?)'
  ).bind(device_id, agent, JSON.stringify(stats)).run();
  return c.json({ status: 'ok' });
});

app.get('/agent/poll', async (c) => {
  const device_id = c.req.query('device_id') || 'UNKNOWN';
  
  // Update activity timestamp
  await c.env.DB.prepare(
    'UPDATE agents SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?'
  ).bind(device_id).run();

  const cmds = await c.env.DB.prepare(
    "SELECT id, action FROM commands WHERE status = 'pending' LIMIT 5"
  ).all();
  
  if (cmds.results.length > 0) {
    const ids = cmds.results.map(r => r.id);
    await c.env.DB.prepare(
      `UPDATE commands SET status = 'sent' WHERE id IN (${ids.map(() => '?').join(',')})`
    ).bind(...ids).run();
  }
  
  return c.json({ commands: cmds.results.map(r => ({ command_id: r.id, action: JSON.parse(r.action as string) })) });
});

app.post('/agent/result', async (c) => {
  const data = await c.req.json();
  const { command_id } = data;
  await c.env.DB.prepare(
    "UPDATE commands SET status = 'done', result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
  ).bind(JSON.stringify(data), command_id).run();
  return c.json({ status: 'ok' });
});

app.post('/agent/upload', async (c) => {
  const device_id = c.req.query('device_id') || 'UNKNOWN';
  const body = await c.req.parseBody();
  const file = body.file as File;
  const key = `ss_${Date.now()}.png`;
  
  await c.env.BUCKET.put(key, await file.arrayBuffer(), {
    httpMetadata: { contentType: 'image/png' }
  });
  
  await c.env.DB.prepare(
    'UPDATE agents SET last_screenshot = ? WHERE device_id = ?'
  ).bind(key, device_id).run();
  
  return c.json({ ok: true, key });
});

// --- DASHBOARD ENDPOINTS ---

app.get('/agent/summary', async (c) => {
  const agents = await c.env.DB.prepare('SELECT * FROM agents ORDER BY last_seen DESC').all();
  const commands = await c.env.DB.prepare('SELECT id, description, status, updated_at FROM commands ORDER BY updated_at DESC LIMIT 10').all();
  
  const agent = agents.results[0] || null;
  const is_online = agent ? (Date.now() - new Date(agent.last_seen as string).getTime() < 60000) : false;

  return c.json({
    online: is_online,
    agent: agent ? {
      name: agent.name,
      last_seen: agent.last_seen,
      stats: JSON.parse(agent.stats as string || '{}'),
      last_screenshot: agent.last_screenshot
    } : null,
    commands: commands.results
  });
});

app.get('/agent/assets', async (c) => {
  const objects = await c.env.BUCKET.list({ limit: 20 });
  return c.json(objects.objects.map(o => ({ key: o.key, uploaded: o.uploaded })));
});

app.get('/agent/asset/:key', async (c) => {
  const key = c.req.param('key');
  const object = await c.env.BUCKET.get(key);
  if (!object) return c.text('Not Found', 404);
  
  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('etag', object.httpEtag);
  
  return new Response(object.body, { headers });
});

app.post('/agent/command', async (c) => {
  const data = await c.req.json();
  const { action, description } = data;
  const id = crypto.randomUUID().split('-')[0].toUpperCase();
  await c.env.DB.prepare(
    "INSERT INTO commands (id, action, description, status, updated_at) VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)"
  ).bind(id, JSON.stringify(action), description).run();
  return c.json({ status: 'queued', command_id: id });
});

app.get('/admin/migrate', async (c) => {
  await c.env.DB.prepare(`
    ALTER TABLE agents ADD COLUMN stats TEXT;
    ALTER TABLE agents ADD COLUMN last_screenshot TEXT;
  `).run().catch(() => {});
  return c.text('Migration check complete');
});

export default app;
