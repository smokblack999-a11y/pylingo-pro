#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    SAMURAI LAUNCHER v1.0                             ║
# ║              Универсальный лаунчер для всех модулей                ║
# ╚══════════════════════════════════════════════════════════════════════╝
set -euo pipefail

# Цвета
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' B='\033[1m' Z='\033[0m'

echo ""; echo -e "${C}╔═══════════════════════════════════════════════════════════${Z}"
echo -e "${C}║           ⚔  SAMURAI LAUNCHER v1.0  ⚔                  ${Z}"
echo -e "${C}╚═══════════════════════════════════════════════════════════${Z}"; echo ""

ROOT="$HOME/samurai"
cd "$ROOT"

# Меню
PS3='Выбери модуль (1-4): '
options=(
  "🚀 Samurai Ultimate v54 (Full Stack)"
  "🐍 PyLingo Pro (Python IDE + Remote)"
  "🛠️  DevOps Tools (Express + Pipeline)"
  "📦 Установить/Обновить всё"
  "❌ Выход"
)

select opt in "${options[@]}"; do
  case "$opt" in
    "🚀 Samurai Ultimate v54 (Full Stack)")
      echo -e "${G}Запуск Samurai Ultimate...${Z}"
      cd "$ROOT/server"
      pm2 start server.js --name samurai || pm2 restart samurai
      echo -e "${G}✓ Samurai Ultimate запущен${Z}"
      echo "  🌐 http://localhost:3000"
      break
      ;;
    "🐍 PyLingo Pro (Python IDE + Remote)")
      echo -e "${G}Запуск PyLingo Pro...${Z}"
      cd "$ROOT/app"
      pm2 start main.py --name pylingo || pm2 restart pylingo
      echo -e "${G}✓ PyLingo Pro запущен${Z}"
      echo "  🌐 http://localhost:8000"
      break
      ;;
    "🛠️  DevOps Tools (Express + Pipeline)")
      echo -e "${G}Запуск DevOps Tools...${Z}"
      cd "$ROOT/samurai-devops"
      pm2 start core/server.js --name devops || pm2 restart devops
      echo -e "${G}✓ DevOps Tools запущены${Z}"
      echo "  🌐 http://localhost:3000"
      break
      ;;
    "📦 Установить/Обновить всё")
      echo -e "${Y}Установка всех компонентов...${Z}"
      bash "$ROOT/samurai.sh"
      break
      ;;
    "❌ Выход")
      echo "Пока!"
      exit 0
      ;;
    *) echo -e "${R}Неверный выбор${Z}";;
  esac
done
