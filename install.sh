#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║              ПОЛНАЯ УСТАНОВКА SAMURAI SUITE                         ║
# ║         PyLingo Pro + Samurai Ultimate + DevOps Tools              ║
# ╚══════════════════════════════════════════════════════════════════════╝
set -euo pipefail

R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' B='\033[1m' Z='\033[0m'
ok()  { echo -e "${G}✓${Z} $*"; }
inf() { echo -e "${C}→${Z} $*"; }
hdr() { echo; echo -e "  ${B}$*${Z}"; }

ROOT="$HOME/samurai"

hdr "1. Установка системных пакетов"
pkg update -y -q 2>/dev/null
pkg install -y nodejs python redis git openssh 2>/dev/null
ok "Системные пакеты установлены"

hdr "2. Установка глобальных npm"
npm install -g pm2 serve 2>/dev/null
ok "PM2, serve установлены"


hdr "3. Python зависимости"
pip install --break-system-packages --quiet flask python-telegram-bot aiohttp 2>/dev/null || \
pip install --quiet flask python-telegram-bot aiohttp 2>/dev/null
ok "Python пакеты установлены"

hdr "4. Создание структуры"
mkdir -p "$ROOT"/{server,web,app/templates,python,logs,data,config,samurai-devops}
ok "Структура создана"

hdr "5. Node.js зависимости"
cat > "$ROOT/server/package.json" << 'PKGEOF'
{"name":"samurai-ultimate","version":"54.0.0","main":"server.js","dependencies":{"express":"^4.18.2","express-rate-limit":"^7.1.5","helmet":"^7.1.0","cors":"^2.8.5","socket.io":"^4.7.2","jsonwebtoken":"^9.0.2","bcrypt":"^5.1.1","ioredis":"^5.3.2","bullmq":"^5.1.1","node-fetch":"^2.7.0","dotenv":"^16.3.1"}}
PKGEOF
cd "$ROOT/server" && npm install --silent 2>/dev/null
ok "Node.js зависимости установлены"

hdr "6. Конфигурация .env"
if [ ! -f "$ROOT/.env" ]; then
cat > "$ROOT/.env" << 'ENVEOF'
ANTHROPIC_API_KEY=sk-ant-ТВОЙ_КЛЮЧ
JWT_SECRET=samurai_secret_change_32chars
ADMIN_PASSWORD=admin123
API_PORT=3000
REDIS_URL=redis://127.0.0.1:6379
ENVEOF
  ok ".env создан"
fi

hdr "7. Запуск Redis"
redis-server --daemonize yes 2>/dev/null || true
ok "Redis запущен"

hdr "8. Запуск Samurai Ultimate"
cd "$ROOT/server"
pm start &
sleep 3

hdr "9. Установка в автозагрузку"
pm2 startup 2>/dev/null || true
pm2 save 2>/dev/null || true

echo ""
echo -e "${G}🎉 SAMURAI SUITE УСТАНОВЛЕН!${Z}"
echo ""
echo "  🌐 Web UI:  http://localhost:3000"
echo "  📁 Файлы:  $ROOT"
echo ""
echo "  Команды:"
echo "    pm2 status      — статус"
echo "    pm2 logs       — логи"
echo "    pm2 restart    — перезапуск"
