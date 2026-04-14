/**
 * SAMURAI ULTIMATE SERVER v54 FINAL
 * ═══════════════════════════════════════════════════════════════
 * Auth · Redis · BullMQ · WebSocket · Molecule API proxy
 * Users с планами FREE/PRO/MAX и рефералами
 * Samurai Core: события/recovery/метрики
 * Market reader (Binance)
 * RCA диагностика
 * Viral Trend Engine
 * Webhook monitor
 * Admin API
 * ═══════════════════════════════════════════════════════════════
 */
'use strict';

const path = require('path');
const fs = require('fs');
const http = require('http');
const https = require('https');
const express = require('express');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const Redis = require('ioredis');
const { Queue, Worker } = require('bullmq');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const fetch = require('node-fetch');
const dotenv = require('dotenv');

dotenv.config({ path: path.join(__dirname, '..', '.env') });

const PORT = parseInt(process.env.API_PORT || '3000', 10);
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-CHANGE-ME-32chars!!!!';
const ADMIN_PASS = process.env.ADMIN_PASSWORD || 'admin1234';
const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY || '';
const CLAUDE_MODEL = process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514';
const MAX_TOKENS = parseInt(process.env.MAX_TOKENS || '2000', 10);
const RATE_LIMIT_MS = parseInt(process.env.RATE_LIMIT_MS || '2000', 10);

const DATA_DIR = path.join(__dirname, '..', 'data');
const USERS_FILE = path.join(DATA_DIR, 'users.json');
const LOGS_DIR = path.join(__dirname, '..', 'logs');
[DATA_DIR, LOGS_DIR].forEach(d => fs.mkdirSync(d, { recursive: true }));

// Redis
const redis = new Redis(REDIS_URL, {
  lazyConnect: true,
  maxRetriesPerRequest: null,
  enableOfflineQueue: false,
});
redis.on('error', e => { });
let redisReady = false;
redis.connect().then(() => { redisReady = true; }).catch(() => {});

const rcGet = async (k) => redisReady ? redis.get(k).catch(() => null) : null;
const rcSet = async (k, v, ex) => redisReady ? redis.set(k, v, 'EX', ex).catch(() => null) : null;

// BullMQ
const ALLOWED_HOSTS = new Set(['api.binance.com', 'api.coingecko.com', 'android-review.googlesource.com']);
const taskQueue = new Queue('tasks', {
  connection: { host: '127.0.0.1', port: 6379 },
  defaultJobOptions: { attempts: 3, backoff: { type: 'exponential', delay: 2000 } },
});
const taskWorker = new Worker('tasks', async (job) => {
  const { url, type } = job.data;
  if (!url) throw new Error('No URL');
  const host = new URL(url).hostname;
  if (!ALLOWED_HOSTS.has(host)) throw new Error(`Host not in allowlist: ${host}`);
  const r = await fetch(url, { timeout: 12000 });
  const result = await r.json();
  io.emit('task_result', { id: job.id, type, result });
  return result;
}, { connection: { host: '127.0.0.1', port: 6379 } });
taskWorker.on('failed', (j, e) => console.error(`[BullMQ] Job ${j?.id} failed: ${e.message}`));

// Express + Socket.io
const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' }, pingTimeout: 30000, pingInterval: 10000 });

app.use(cors());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json({ limit: '2mb' }));
app.use(rateLimit({ windowMs: 60000, max: 400, standardHeaders: true, legacyHeaders: false }));

// USERS
let usersDB = { users: [], nextId: 1 };

function loadUsers() {
  if (fs.existsSync(USERS_FILE)) {
    try { usersDB = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8')); } catch {}
  }
}
function saveUsers() {
  const tmp = USERS_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(usersDB, null, 2));
  fs.renameSync(tmp, USERS_FILE);
}
function findUser(username) { return usersDB.users.find(u => u.username === username); }
function findUserById(id) { return usersDB.users.find(u => u.id === id); }

async function createUser(username, password, role = 'user', refId = null) {
  const hash = await bcrypt.hash(password, 10);
  const user = {
    id: usersDB.nextId++,
    username, password: hash, role, refId,
    plan: 'free', expireAt: 0, earned: 0, actions: 0, createdAt: Date.now(),
  };
  usersDB.users.push(user);
  saveUsers();
  return user;
}

function activatePlan(userId, plan, days) {
  const user = findUserById(userId);
  if (!user) return null;
  user.plan = plan;
  user.expireAt = Date.now() + days * 86400000;
  if (user.refId) {
    const ref = findUserById(user.refId);
    if (ref) { ref.earned += 300; }
  }
  saveUsers();
  return user;
}

function canUse(user) {
  if (user.plan === 'free') return user.actions < 10;
  return user.expireAt > Date.now();
}

loadUsers();

// SAMURAI CORE
const core = {
  logs: [],
  state: { deals: 0, income: 0, totalRecovered: 0, lossPrevented: 0 },
  startTime: Date.now(),
};

function ingestEvent(status) {
  core.logs.push({ status, ts: Date.now() });
  if (core.logs.length > 500) core.logs.shift();
}

function aiAnalyze() {
  const fails = core.logs.filter(l => l.status === 'fail').length;
  const ok = core.logs.filter(l => l.status === 'ok').length;
  const rec = core.logs.filter(l => l.status === 'recovered').length;
  let recommendation = 'nominal';
  if (fails > 5) recommendation = 'critical_recovery_needed';
  else if (fails > 0) recommendation = 'recovery_recommended';
  return { fails, ok, recovered: rec, recommendation };
}

function calcLoss() {
  return core.logs.filter(l => l.status === 'fail').length * 5;
}

function recover() {
  let count = 0;
  core.logs.forEach(l => { if (l.status === 'fail') { l.status = 'recovered'; count++; } });
  return count;
}

function getMetrics() {
  const now = Date.now();
  return {
    events: core.logs.length,
    ok: core.logs.filter(l => l.status === 'ok').length,
    fails: core.logs.filter(l => l.status === 'fail').length,
    recovered: core.logs.filter(l => l.status === 'recovered').length,
    deals: core.state.deals,
    income: core.state.income,
    lossPrevented: core.state.lossPrevented,
    uptime: Math.floor((now - core.startTime) / 1000),
  };
}

setInterval(() => {
  const s = Math.random() > 0.25 ? 'ok' : 'fail';
  ingestEvent(s);
  if (s === 'fail') {
    const loss = calcLoss();
    const rec = recover();
    if (rec > 0) {
      core.state.totalRecovered += rec;
      core.state.lossPrevented += loss;
    }
  }
  io.emit('core_update', getMetrics());
}, 8000);

// RCA
function rcaDiagnose(windowMs = 600000) {
  const now = Date.now();
  const window = core.logs.filter(l => now - l.ts < windowMs);
  const failRate = window.filter(l => l.status === 'fail').length / Math.max(window.length, 1);
  const anomaly = failRate > 0.2;
  const recent1m = core.logs.filter(l => now - l.ts < 60000);
  const trend = recent1m.filter(l => l.status === 'fail').length > 2 ? 'worsening' : 'stable';
  let rootCause = null, reason = 'nominal';
  if (failRate > 0.5) { rootCause = 'samurai-core-events'; reason = 'high_failure_rate_>50%'; }
  else if (failRate > 0.2) { rootCause = 'event_ingestion_pipeline'; reason = 'elevated_failure_rate'; }
  else if (trend === 'worsening') { rootCause = 'recent_ingestion_spike'; reason = 'sudden_increase_in_fails'; }
  return { timestamp: new Date().toISOString(), window_events: window.length, fail_rate: Math.round(failRate * 100) + '%', anomaly, trend, root_cause: rootCause, reason, recommendation: rootCause ? `Run recover() and monitor ${rootCause}` : 'System nominal' };
}

// Viral Trends
const trendCache = { data: null, ts: 0 };

async function getTrends() {
  const now = Date.now();
  if (trendCache.data && now - trendCache.ts < 120000) return trendCache.data;
  let binance = [];
  try { const raw = await rcGet('market:binance:top12'); if (raw) binance = JSON.parse(raw); } catch {}
  const trends = binance.length > 0
    ? binance.slice(0, 10).map((a, i) => {\ const score = Math.min(99, Math.abs(a.change) * 2 + 40 + Math.random() * 20); return { id: i + 1, title: a.symbol, subtitle: `${a.change > 0 ? '+' : ''}${a.change.toFixed(2)}% 24h`, score: Math.round(score), action: score > 80 ? 'SCALE' : score > 50 ? 'USE' : 'DROP', volume: a.volume }; })
    : Array.from({ length: 10 }, (_, i) => { const score = 95 - i * 5 + (Math.random() * 10 - 5); return { id: i + 1, title: `Тренд ${i + 1}`, subtitle: 'Симуляция', score: Math.round(Math.max(10, Math.min(99, score))), action: score > 80 ? 'SCALE' : score > 50 ? 'USE' : 'DROP' }; });
  trends.sort((a, b) => b.score - a.score);
  trendCache.data = trends;
  trendCache.ts = now;
  return trends;
}

// Webhook Monitor
const webhookLog = [];
function classifyWebhookError(statusCode, body) {
  if (statusCode === 429) return { type: 'rate_limit', action: 'exponential_backoff', priority: 'high' };
  if (statusCode === 408 || body?.includes?.('timeout')) return { type: 'timeout', action: 'retry_with_timeout', priority: 'medium' };
  if (statusCode === 401 || statusCode === 403) return { type: 'auth_error', action: 'refresh_credentials', priority: 'critical' };
  if (statusCode >= 500) return { type: 'server_error', action: 'retry_with_backoff', priority: 'high' };
  return { type: 'unknown', action: 'manual_review', priority: 'low' };
}
function webhookIncidentReport() {
  const total = webhookLog.length, failed = webhookLog.filter(w => w.status === 'failed').length, recovered = webhookLog.filter(w => w.status === 'recovered').length;
  const byType = {};
  webhookLog.forEach(w => { if (w.errorType) byType[w.errorType] = (byType[w.errorType] || 0) + 1; });
  return { generated: new Date().toISOString(), total_events: total, failed, recovered, success_rate: total ? `${Math.round((1 - failed / total) * 100)}%` : 'N/A', top_errors: byType, recommendation: failed > 5 ? 'Review authentication and retry logic' : 'System healthy' };
}

// Auth
function auth(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token required' });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    const user = findUser(req.user.username);
    if (user) { user.actions++; saveUsers(); }
    next();
  } catch { res.status(403).json({ error: 'Invalid or expired token' }); }
}
function requireRole(role) {
  return (req, res, next) => { if (req.user?.role !== role) return res.status(403).json({ error: 'Forbidden' }); next(); };
}

const molLastReq = new Map();
function molRateLimited(ip) {
  const now = Date.now(), last = molLastReq.get(ip) || 0;
  if (now - last < RATE_LIMIT_MS) return true;
  molLastReq.set(ip, now);
  return false;
}
setInterval(() => { const c = Date.now() - 120000; for (const [k, v] of molLastReq) if (v < c) molLastReq.delete(k); }, 60000);

// Anthropic
function callAnthropic(mol) {
  return new Promise((resolve, reject) => {
    const prompt = `You are a molecular data provider. Respond ONLY with valid JSON. Format: {"formula": "...", "elements": { "SYM": { "radius": 0.1-1.0, "color": "#hex" } }, "atoms": [ { "id": "EL-N", "element": "SYM", "position": [x,y,z] } ], "bonds": [ { "atom1": "id", "atom2": "id", "type": "single"|"double"|"triple" } ] }. Use realistic Angstrom coords. CPK colours. Output ONLY valid JSON. Molecule: ${mol}`;
    const body = JSON.stringify({ model: CLAUDE_MODEL, max_tokens: MAX_TOKENS, messages: [{ role: 'user', content: prompt }] });
    const req = https.request({
      hostname: 'api.anthropic.com', path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body), 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' },
    }, (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { const p = JSON.parse(d); if (p.error) return reject(new Error(p.error.message)); resolve(p.content?.[0]?.text || '{}'); } catch (e) { reject(e); } }); });
    req.on('error', reject);
    req.setTimeout(30000, () => req.destroy(new Error('Anthropic timeout')));
    req.write(body); req.end();
  });
}

// Routes
app.get('/health', (req, res) => res.json({ status: 'ok', version: '54.0.0', uptime: Math.floor(process.uptime()), redis: redisReady, users: usersDB.users.length }));

app.post('/register', async (req, res) => {
  const { username, password, refCode } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username и password обязательны' });
  if (username.length < 3 || password.length < 4) return res.status(400).json({ error: 'Слишком короткие данные' });
  if (findUser(username)) return res.status(409).json({ error: 'Пользователь уже существует' });
  let refId = null;
  if (refCode) { const refUser = findUser(refCode); if (refUser) { refId = refUser.id; refUser.earned += 150; saveUsers(); } }
  const user = await createUser(username, password, 'user', refId);
  const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '12h' });
  res.json({ success: true, token, role: user.role });
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body || {};
  const user = findUser(username);
  if (!user) return res.status(404).json({ error: 'Пользователь не найден' });
  if (!await bcrypt.compare(password, user.password)) return res.status(403).json({ error: 'Неверный пароль' });
  const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '12h' });
  res.json({ token, role: user.role, plan: user.plan });
});

app.post('/molecule', async (req, res) => {
  if (!ANTHROPIC_KEY || ANTHROPIC_KEY.includes('ВСТАВЬ')) return res.status(503).json({ error: 'ANTHROPIC_API_KEY не настроен' });
  const ip = req.ip || 'unknown';
  if (molRateLimited(ip)) return res.status(429).json({ error: 'Слишком часто' });
  const name = (req.body?.molecule || '').trim();
  if (!name || name.length > 100) return res.status(400).json({ error: 'Неверное имя' });
  if (['ignore', 'system', 'assistant', '<script', '{{', 'injection'].some(b => name.toLowerCase().includes(b))) return res.status(400).json({ error: 'Недопустимый ввод' });
  const cacheKey = `mol:${name.toLowerCase().replace(/\s+/g, '-')}`;
  const cached = await rcGet(cacheKey);
  if (cached) return res.json(JSON.parse(cached));
  try {
    const raw = await callAnthropic(name);
    const data = JSON.parse(raw);
    if (!data.formula || !data.atoms) throw new Error('Неверная структура');
    await rcSet(cacheKey, JSON.stringify(data), 3600);
    res.json(data);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.get('/api/market', auth, async (req, res) => {
  const key = 'market:binance:top12';
  const cached = await rcGet(key);
  if (cached) return res.json(JSON.parse(cached));
  try {
    const r = await fetch('https://api.binance.com/api/v3/ticker/24hr', { timeout: 8000 });
    const all = await r.json();
    const top = all.sort((a, b) => Math.abs(parseFloat(b.priceChangePercent)) - Math.abs(parseFloat(a.priceChangePercent))).slice(0, 12).map(a => ({ symbol: a.symbol, price: parseFloat(a.lastPrice), change: parseFloat(a.priceChangePercent), volume: parseFloat(a.quoteVolume), high: parseFloat(a.highPrice), low: parseFloat(a.lowPrice) }));
    await rcSet(key, JSON.stringify(top), 60);
    res.json(top);
  } catch (e) { res.status(502).json({ error: 'Binance недоступен: ' + e.message }); }
});

app.get('/api/core', auth, (req, res) => res.json({ ...getMetrics(), analysis: aiAnalyze() }));
app.post('/api/core/event', auth, (req, res) => {
  const status = req.body?.status || 'ok';
  if (!['ok', 'fail'].includes(status)) return res.status(400).json({ error: 'status: ok|fail' });
  const loss = status === 'fail' ? calcLoss() : 0;
  ingestEvent(status);
  if (status === 'fail') recover();
  core.state.lossPrevented += loss;
  io.emit('core_update', getMetrics());
  res.json({ ok: true, metrics: getMetrics() });
});

app.get('/api/rca', auth, (req, res) => { const windowMs = parseInt(req.query.window || '600000', 10); res.json(rcaDiagnose(windowMs)); });
app.post('/api/rca/run', auth, async (req, res) => { await new Promise(r => setTimeout(r, 1500)); const result = rcaDiagnose(); io.emit('rca_result', result); res.json(result); });

app.get('/api/trends', auth, async (req, res) => { try { res.json(await getTrends()); } catch (e) { res.status(500).json({ error: e.message }); } });

app.post('/api/webhook/simulate', auth, (req, res) => {
  const codes = [200, 200, 200, 429, 500, 408, 200, 403];
  const code = codes[Math.floor(Math.random() * codes.length)];
  const err = classifyWebhookError(code, '');
  const entry = { id: Date.now(), status: code === 200 ? 'ok' : 'failed', statusCode: code, ...err, ts: Date.now() };
  if (entry.status === 'failed') { setTimeout(() => { entry.status = 'recovered'; webhookLog.push(entry); }, Math.random() * 3000 + 500); } else { webhookLog.push(entry); }
  if (webhookLog.length > 100) webhookLog.shift();
  io.emit('webhook_event', entry);
  res.json(entry);
});
app.get('/api/webhook/report', auth, (req, res) => res.json(webhookIncidentReport()));

app.post('/api/task', auth, async (req, res) => {
  const { url, type } = req.body || {};
  if (!url) return res.status(400).json({ error: 'url обязателен' });
  try { const job = await taskQueue.add('fetch', { url, type }); res.json({ jobId: job.id, status: 'queued' }); } catch (e) { res.status(500).json({ error: e.message }); }
});

app.get('/api/analytics', auth, async (req, res) => {
  let cacheKeys = 0;
  if (redisReady) { let cursor = '0'; do { const [next, keys] = await redis.scan(cursor, 'COUNT', '100').catch(() => ['0', []]); cursor = next; cacheKeys += keys.length; } while (cursor !== '0'); }
  const plans = { free: 0, pro: 0, max: 0 };
  usersDB.users.forEach(u => { plans[u.plan] = (plans[u.plan] || 0) + 1; });
  const [completed, failed, active] = await Promise.all([taskQueue.getJobCounts('completed').catch(() => ({})), taskQueue.getJobCounts('failed').catch(() => ({}))]);
  res.json({ users: usersDB.users.length, plans, cache_keys: cacheKeys, core: getMetrics(), jobs: { completed, failed, active }, uptime: Math.floor(process.uptime()), webhooks: webhookIncidentReport() });
});

app.get('/admin/stats', auth, requireRole('admin'), async (req, res) => {
  const jobs = await taskQueue.getJobs(['completed', 'failed', 'active', 'waiting']).catch(() => []);
  res.json({ users: usersDB.users.map(u => ({ id: u.id, username: u.username, role: u.role, plan: u.plan, actions: u.actions, earned: u.earned, expireAt: u.expireAt ? new Date(u.expireAt).toISOString() : null })), total_jobs: jobs.length, core: getMetrics(), rca: rcaDiagnose(), redis_ready: redisReady });
});

app.post('/admin/users/:id/plan', auth, requireRole('admin'), (req, res) => {
  const { plan, days } = req.body || {};
  if (!['free', 'pro', 'max'].includes(plan)) return res.status(400).json({ error: 'plan: free|pro|max' });
  const user = activatePlan(parseInt(req.params.id), plan, days || 30);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json({ ok: true, user: { id: user.id, username: user.username, plan: user.plan } });
});

const webDir = path.join(__dirname, '..', 'web');
app.use(express.static(webDir));
app.get('*', (req, res) => { const idx = path.join(webDir, 'index.html'); fs.existsSync(idx) ? res.sendFile(idx) : res.status(404).send('Web UI не найден'); });

io.on('connection', (socket) => { socket.emit('core_state', getMetrics()); socket.emit('welcome', { version: '54.0.0', uptime: Math.floor(process.uptime()) }); });
setInterval(() => io.emit('core_update', getMetrics()), 15000);
setInterval(async () => { try { io.emit('trends_update', await getTrends()); } catch {} }, 120000);

async function start() {
  if (!findUser('admin')) { await createUser('admin', ADMIN_PASS, 'admin'); console.log('[Auth] Admin user created'); }
  server.listen(PORT, '0.0.0.0', () => {
    console.log('');
    console.log('⚔  SAMURAI ULTIMATE v54 FINAL');
    console.log(`   http://0.0.0.0:${PORT}`);
    console.log(`   Redis: ${redisReady ? 'connected' : 'offline'}`);
    console.log(`   Users: ${usersDB.users.length}`);
    console.log('');
  });
}

process.on('SIGTERM', () => { server.close(); redis.quit(); process.exit(0); });
process.on('SIGINT', () => { server.close(); redis.quit(); process.exit(0); });
start().catch(e => { console.error('[FATAL]', e); process.exit(1); });
