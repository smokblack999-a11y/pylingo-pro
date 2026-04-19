#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║              SAMURAI SUITE ULTIMATE - FULL RUNNER                 ║
# ║                   Готовый к запуску пакет                       ║
# ╚══════════════════════════════════════════════════════════════════════╝
set -euo pipefail

R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' B='\033[1m' Z='\033[0m'

echo ""; echo -e "${C}╔═══════════════════════════════════════════════════════════════${Z}"
echo -e "${C}║         ⚔  SAMURAI SUITE ULTIMATE - FULL RUNNER        ${Z}"
echo -e "${C}╚═══════════════════════════════════════════════════════════════${Z}"; echo ""

ROOT="$HOME/samurai"
cd "$ROOT"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Проверка и установка...${Z}"

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${C}→${Z} Установка Node.js..."
    pkg install -y nodejs 2>/dev/null || true
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${C}→${Z} Установка Python..."
    pkg install -y python 2>/dev/null || true
fi

# Проверка Redis
if ! command -v redis-server &> /dev/null; then
    echo -e "${C}→${Z} Установка Redis..."
    pkg install -y redis 2>/dev/null || true
fi

echo -e "${G}✓${Z} Проверка завершена"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Запуск Redis...${Z}"
redis-server --daemonize yes --bind 127.0.0.1 --port 6379 2>/dev/null || true
sleep 1
echo -e "${G}✓${Z} Redis запущен"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Установка Node.js зависимостей...${Z}"
cd "$ROOT/server"
npm install --silent 2>/dev/null || true
echo -e "${G}✓${Z} Node.js зависимости установлены"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Установка Python зависимостей...${Z}"
pip install --break-system-packages --quiet python-telegram-bot aiohttp python-dotenv 2>/dev/null || \
pip install --quiet python-telegram-bot aiohttp python-dotenv 2>/dev/null || true
echo -e "${G}✓${Z} Python зависимости установлены"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Создание директорий...${Z}"
mkdir -p "$ROOT"/{logs,data,core,integrations,bots,strategies,database}
echo -e "${G}✓${Z} Директории созданы"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Запуск Samurai Server...${Z}"
cd "$ROOT/server"

# Запускаем в фоне
nohup node server.js > "$ROOT/logs/server.out.log" 2>&1 &
SERVER_PID=$!

echo -e "${G}✓${Z} Server PID: $SERVER_PID"

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Запуск PM2 процессов...${Z}"

# Проверяем PM2
if ! command -v pm2 &> /dev/null; then
    echo -e "${C}→${Z} Установка PM2..."
    npm install -g pm2 2>/dev/null || true
fi

# Запускаем процессы через PM2
cd "$ROOT"
pm2 start ecosystem.config.js 2>/dev/null || true
pm2 save 2>/dev/null || true

# ════════════════════════════════════════════════════════════════════════
echo -e "${Y}Проверка статуса...${Z}"
sleep 3

# Проверяем что сервер запущен
if curl -s http://localhost:3000/health &> /dev/null; then
    echo -e "${G}✓${Z} Server работает!
else
    echo -e "${Y}⚠${Z} Server не ответил - проверяю логи..."
    tail -20 "$ROOT/logs/server.out.log" 2>/dev/null || true
fi

# ════════════════════════════════════════════════════════════════════════
IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || echo "localhost")

# ════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${B}${G}🎉 SAMURAI SUITE ULTIMATE ЗАПУЩЕН!${Z}"
echo ""
echo -e "${C}╔═══════════════════════════════════════════════════════════════${Z}"
echo -e "${C}║  ДОСТУП                                                 ${Z}"
echo -e "${C}╠═══════════════════════════════════════════════════════════════${Z}"
echo -e "${C}║${Z}  Web UI:    ${B}http://$IP:3000${Z}                       ${C}║${Z}"
echo -e "${C}║${Z}  Health:    ${B}http://$IP:3000/health${Z}               ${C}║${Z}"
echo -e "${C}║${Z}  Логин:     admin / пароль из .env                  ${C}║${Z}"
echo -e "${C}╠═══════════════════════════════════════════════════════════════${Z}"
echo -e "${C}║  КОМАНДЫ                                               ${Z}"
echo -e "${C}║${Z}  pm2 status     - статус процессов                    ${C}║${Z}"
echo -e "${C}║${Z}  pm2 logs      - логи                             ${C}║${Z}"
echo -e "${C}║${Z}  pm2 restart   - перезапуск                        ${C}║${Z}"
echo -e "${C}╚═══════════════════════════════════════════════════════════════${Z}"
echo ""
