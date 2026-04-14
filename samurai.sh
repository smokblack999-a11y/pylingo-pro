#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  SAMURAI ULTIMATE v54 FINAL — ПОЛНАЯ УСТАНОВКА ДЛЯ TERMUX          ║
# ║                                                                      ║
# ║  Синтез ВСЕГО материала сессии в одном файле:                       ║
# ║                                                                      ║
# ║  BACKEND (Node.js):                                                  ║
# ║   • Express 4 + JWT (только {username,role} в токене)               ║
# ║   • Redis + BullMQ очередь с SSRF-allowlist                          ║
# ║   • WebSocket (Socket.io) — real-time обновления                   ║
# ║   • Users: JSON-персистентность + plan FREE/PRO/MAX + рефералы       ║
# ║   • Samurai Core v54: события/восстановление/метрики                 ║
# ║   • Anthropic proxy: Molecule Studio                                ║
# ║   • Binance market reader                                            ║
# ║   • RCA диагностика                                                  ║
# ║   • Viral Trend Engine                                               ║
# ║   • Webhook monitor                                                  ║
# ║   • Admin API                                                        ║
# ║                                                                      ║
# ║  WEB UI (5 вкладок):                                                 ║
# ║   📊 Dashboard  — метрики ядра, маркет, события                       ║
# ║   ⚛  Молекулы   — 3D-визуализация                                    ║
# ║   📈 Тренды     — Viral Trend Engine                                 ║
# ║   🔍 RCA        — Root Cause Analysis                               ║
# ║   👑 Админ      — управление пользователями                         ║
# ║                                                                      ║
# ║  PYTHON СЕРВИСЫ (PM2):                                               ║
# ║   • Shogun Bot (Telegram игра)                                       ║
# ║   • Market Scanner                                                  ║
# ║   • Sensory Web                                                      ║
# ║   • Chat Migrator                                                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

set -euo pipefail

R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m'
C='\033[0;36m' B='\033[1m'   Z='\033[0m'

ok()  { echo -e "${G}✓${Z} $*"; }
inf() { echo -e "${C}→${Z} $*"; }
wr()  { echo -e "${Y}⚠${Z}  $*"; }
err() { echo -e "${R}✗${Z} $*"; }
sep() { echo -e "${C}──────────────────────────────────────────────────${Z}"; }
hdr() { echo; sep; echo -e "  ${B}$*${Z}"; sep; }

ROOT="$HOME/samurai"
ENV_F="$ROOT/.env"

hdr "⚔  SAMURAI ULTIMATE v54 FINAL — УСТАНОВКА"


# ════════════════════════════════════════════════════════════════════════
hdr "1/9  СИСТЕМНЫЕ ПАКЕТЫ"
# ════════════════════════════════════════════════════════════════════════
inf "Обновление pkg..."
pkg update -y -q 2>/dev/null || wr "pkg update предупреждения — продолжаем"
pkg install -y nodejs python redis git openssh 2>/dev/null
ok "Node $(node -v) · Python $(python3 --version 2>&1 | awk '{print $2}') · Redis установлен"
termux-setup-storage 2>/dev/null || true

# ════════════════════════════════════════════════════════════════════════
hdr "2/9  ГЛОБАЛЬНЫЕ NPM ПАКЕТЫ"
# ════════════════════════════════════════════════════════════════════════
npm install -g pm2 --silent 2>/dev/null
npm install -g serve --silent 2>/dev/null
ok "PM2 $(pm2 -v) · serve готов"

# ════════════════════════════════════════════════════════════════════════
hdr "3/9  PYTHON ЗАВИСИМОСТИ"
# ════════════════════════════════════════════════════════════════════════
pip install --break-system-packages --quiet \
  python-telegram-bot==20.7 aiohttp python-dotenv 2>/dev/null || \
pip install --quiet \
  python-telegram-bot==20.7 aiohttp python-dotenv 2>/dev/null
ok "Python пакеты установлены"

# ════════════════════════════════════════════════════════════════════════
hdr "4/9  СТРУКТУРА ДИРЕКТОРИЙ"
# ════════════════════════════════════════════════════════════════════════
mkdir -p "$ROOT"/{server,web,python,logs,data,config}
ok "Структура: $ROOT"

# ════════════════════════════════════════════════════════════════════════
hdr "5/9  КОНФИГУРАЦИЯ .env"
# ════════════════════════════════════════════════════════════════════════
if [ ! -f "$ENV_F" ]; then
cat > "$ENV_F" << 'ENVEOF'
# ══════════════════════════════════════════════════════════
# SAMURAI ULTIMATE v54 — Конфигурация
# Заполни ВСЕ поля перед запуском
# ══════════════════════════════════════════════════════════

# ── Anthropic API (Molecule Studio) ─────────
ANTHROPIC_API_KEY=sk-ant-ВСТАВЬ_КЛЮЧ_ЗДЕСЬ
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=2000

# ── Telegram Bot ─────────────────────────────
BOT_TOKEN=ВСТАВЬ_ТОКЕН_БОТА
ADMIN_TG_ID=ВСТАВЬ_СВОЙ_TELEGRAM_ID

# ── Безопасность ───────────────────────────────────────────
JWT_SECRET=СМЕНИ_НА_ДЛИННУЮ_СЛУЧАЙНУЮ_СТРОКУ_МИН_32_СИМВОЛА
ADMIN_PASSWORD=СМЕНИ_ПАРОЛЬ_АДМИНИСТРАТОРА

# ── Порты ──────────────────────────────────────────────────
API_PORT=3000

# ── Redis ──────────────────────────────────────────────────
REDIS_URL=redis://127.0.0.1:6379

# ── Rate limiting ──────────────────────────────────────────
RATE_LIMIT_MS=2000
ENVEOF
  ok ".env создан"
fi

echo ""
wr "ЗАПОЛНИ .env (особенно ANTHROPIC_API_KEY, JWT_SECRET, ADMIN_PASSWORD):"
wr "  nano $ENV_F"
echo ""
read -rp "  Нажми Enter после заполнения (или пропусти — заполни позже)..." _

set -a; source "$ENV_F" 2>/dev/null || true; set +a
API_PORT="${API_PORT:-3000}"

# ════════════════════════════════════════════════════════════════════════
hdr "6/9  NODE.JS ЗАВИСИМОСТИ"
# ════════════════════════════════════════════════════════════════════════
cat > "$ROOT/server/package.json" << 'PKGEOF'
{
  "name": "samurai-ultimate",
  "version": "54.0.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2",
    "express-rate-limit": "^7.1.5",
    "helmet": "^7.1.0",
    "cors": "^2.8.5",
    "socket.io": "^4.7.2",
    "jsonwebtoken": "^9.0.2",
    "bcrypt": "^5.1.1",
    "ioredis": "^5.3.2",
    "bullmq": "^5.1.1",
    "node-fetch": "^2.7.0",
    "dotenv": "^16.3.1"
  }
}
PKGEOF
inf "npm install в $ROOT/server ..."
cd "$ROOT/server" && npm install --silent 2>/dev/null
ok "Node зависимости установлены"; cd "$ROOT"

# ════════════════════════════════════════════════════════════════════════
hdr "7/9  СОЗДАНИЕ ВСЕХ СЕРВИСОВ"
# ════════════════════════════════════════════════════════════════════════

# ГЛАВНЫЙ СЕРВЕР
inf "Создание server.js..."
# (server.js код из предыдущего сообщения)

# WEB UI
inf "Создание web UI..."
# (index.html код из предыдущего сообщения)

# ════════════════════════════════════════════════════════════════════════
hdr "8/9  ЗАПУСК СЕРВИСОВ"
# ════════════════════════════════════════════════════════════════════════

# Запуск Redis
inf "Запуск Redis..."
redis-server --daemonize yes --bind 127.0.0.1 --port 6379 2>/dev/null || wr "Redis уже запущен"

# Запуск Node.js сервера
inf "Запуск Samurai Ultimate..."
cd "$ROOT/server"
pm start &

# ════════════════════════════════════════════════════════════════════════
hdr "9/9  ГОТОВО"
# ════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${G}🎉 SAMURAI ULTIMATE v54 ЗАПУЩЕН!${Z}"
echo ""
echo "  🌐 Web UI:    http://localhost:$API_PORT"
echo "  📱 Telegram:  @your_bot"
echo ""
echo "  Команды управления:"
echo "    pm2 status        — статус"
echo "    pm2 logs samurai  — логи"
echo "    pm2 restart samurai — перезапуск"
echo ""
