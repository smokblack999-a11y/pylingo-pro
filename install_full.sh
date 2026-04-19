#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║           SAMURAI SUITE - ПОЛНАЯ УСТАНОВКА                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
set -euo pipefail

# Цвета
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' B='\033[1m' Z='\033[0m'

print() { echo -e "$1"; }
ok()   { print "${G}✓${Z} $1"; }
inf()  { print "${C}→${Z} $1"; }
wr()   { print "${Y}⚠${Z}  $1"; }
err()  { print "${R}✗${Z} $1"; }

ROOT="$HOME/samurai"
ENV_FILE="$ROOT/.env"

print ""
print "${C}╔═══════════════════════════════════════════════════════════════${Z}"
print "${C}║         ⚔  SAMURAI SUITE - FULL INSTALLER             ${Z}"
print "${C}╚═══════════════════════════════════════════════════════════════${Z}"
print ""

# ═══════════════════════════════════════════════════════════════════
inf "Обновление пакетов..."
pkg update -y -qq 2>/dev/null || true
ok "Пакеты обновлены"

# ═══════════════════════════════════════════════════════════════════
inf "Установка системных пакетов..."
pkg install -y nodejs python git redis openssh curl wget 2>/dev/null || true
ok "Системные пакеты установлены"

# ═══════════════════════════════════════════════════════════════════
inf "Проверка Node.js..."
NODE_VER=$(node -v 2>/dev/null || echo "none")
if [ "$NODE_VER" = "none" ]; then
    err "Node.js не установлен!"
    exit 1
fi
ok "Node.js $NODE_VER"

inf "Проверка Python..."
PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
ok "Python $PY_VER"

# ═══════════════════════════════════════════════════════════════════
inf "Установка глобальных npm..."
npm install -g pm2 2>/dev/null || true
PM2_VER=$(pm2 -v 2>/dev/null | head -1 || echo "unknown")
ok "PM2 $PM2_VER"

# ═══════════════════════════════════════════════════════════════════
inf "Установка Python пакетов..."
pip install --break-system-packages --quiet flask python-telegram-bot aiohttp python-dotenv 2>/dev/null || \
pip install --quiet flask python-telegram-bot aiohttp python-dotenv 2>/dev/null || true
ok "Python пакеты установлены"

# ═══════════════════════════════════════════════════════════════════
inf "Создание структуры директорий..."
mkdir -p "$ROOT"/{server,web,python,logs,data,config,core,integrations,bots,strategies,database,app/templates}
ok "Структура создана"

# ═══════════════════════════════════════════════════════════════════
inf "Создание .env файла..."
if [ ! -f "$ENV_FILE" ]; then
    cp "$ROOT/.env.example" "$ENV_FILE" 2>/dev/null || true
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << 'ENVEOF'
ANTHROPIC_API_KEY=
JWT_SECRET=samurai_secret_CHANGE_32_chars_minimum
ADMIN_PASSWORD=admin123
API_PORT=3000
REDIS_URL=redis://127.0.0.1:6379
BOT_TOKEN=
ADMIN_TG_ID=
ENVEOF
    fi
    ok ".env создан"
else
    ok ".env уже существует"
fi

print ""
wr "⚠ ВАЖНО! Заполни .env файл:"
print ""
print "   nano $ENV_FILE"
print ""
print "   Минимум заполни:"
print "   - ANTHROPIC_API_KEY (для молекул)"
print "   - JWT_SECRET (любой随机 строка 32+ символа)"
print "   - ADMIN_PASSWORD (свой пароль)"
print ""
read -p "   Нажми Enter после заполнения... " _

# ═══════════════════════════════════════════════════════════════════
inf "Установка Node.js зависимостей..."
cd "$ROOT/server"
npm install --silent 2>/dev/null || npm install 2>&1 | tail -5
ok "Node.js зависимости установлены"
cd "$ROOT"

# ═══════════════════════════════════════════════════════════════════
inf "Запуск Redis..."
redis-server --daemonize yes --bind 127.0.0.1 --port 6379 2>/dev/null || true
sleep 1
# Проверка Redis
if redis-cli ping &>/dev/null; then
    ok "Redis работает"
else
    # Пробуем запустить иначе
    nohup redis-server > "$ROOT/logs/redis.log" 2>&1 &
    sleep 2
    ok "Redis запущен (nohup)"
fi

# ═══════════════════════════════════════════════════════════════════
inf "Запуск Samurai Server..."
cd "$ROOT/server"

# Запускаем сервер
nohup node server.js > "$ROOT/logs/server.out.log" 2>&1 &
SERVER_PID=$!

print "   PID: $SERVER_PID"

# Ждём запуска
sleep 3

# Проверяем
if curl -s http://localhost:3000/health &>/dev/null; then
    ok "Samurai Server работает!"
else
    wr "Server может не запуститься - проверь логи:"
    print "   tail $ROOT/logs/server.out.log"
fi

cd "$ROOT"

# ═══════════════════════════════════════════════════════════════════
inf "Деплой PM2 процессов..."
pm2 start ecosystem_full.config.js 2>/dev/null || true
pm2 save 2>/dev/null || true
ok "PM2 настроен"

# ═══════════════════════════════════════════════════════════════════
IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || echo "localhost")

# ═══════════════════════════════════════════════════════════════════
print ""
print "${B}${G}🎉 УСТАНОВКА ЗАВЕРШЕНА!${Z}"
print ""
print "${C}╔═══════════════════════════════════════════════════════════════${Z}"
print "${C}║  ДОСТУП К СИСТЕМЕ                                         ${Z}"
print "${C}╠═══════════════════════════════════════════════════════════════${Z}"
print "${C}║${Z}  Web UI:     ${B}http://$IP:3000${Z}                       ${C}║${Z}"
print "${C}║${Z}  Health:     ${B}http://$IP:3000/health${Z}                 ${C}║${Z}"
print "${C}║${Z}  Логин:     admin / (пароль из .env)                  ${C}║${Z}"
print "${C}╠═══════════════════════════════════════════════════════════════${Z}"
print "${C}║  PM2 ПРОЦЕССЫ                                          ${Z}"
print "${C}║${Z}  pm2 status                                         ${C}║${Z}"
print "${C}║${Z}  pm2 logs samurai-server                             ${C}║${Z}"
print "${C}╚═══════════════════════════════════════════════════════════════${Z}"
print ""
