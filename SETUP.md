# ⚔️ SAMURAI SUITE - ИНСТРУКЦИЯ ПО НАСТРОЙКЕ

## 📋 СОДЕРЖАНИЕ

1. [Быстрый старт](#быстрый-старт)
2. [Настройка .env](#настройка-env)
3. [Получение API ключей](#получение-api-ключей)
4. [Настройка Telegram Bot](#настройка-telegram-bot)
5. [Запуск и управление](#запуск-и-управление)
6. [Возможные проблемы](#возможные-проблемы)

---

## 🚀 БЫСТРЫЙ СТАРТ

### Шаг 1: Установка

```bash
# Клонируем репозиторий
git clone https://github.com/smokblack999-a11y/pylingo-pro.git ~/samurai
cd ~/samurai

# Запускаем установщик
bash install_full.sh
```

### Шаг 2: Запуск

```bash
# После установки открой в браузере:
http://localhost:3000

# Или с другого устройства:
http://ТВОЙ_IP:3000
```

---

## ⚙️ НАСТРОЙКА .ENV

### Создай/открой файл:

```bash
cd ~/samurai
nano .env
```

### Пример заполненного .env:

```env
# ═══════════════════════════════════════════════════════════════
# SAMURAI SUITE - КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# ── ОБЯЗАТЕЛЬНО ЗАПОЛНИ ─────────────────────────────────

# Anthropic API для 3D молекул
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Секретный ключ (любая строка 32+ символа)
JWT_SECRET=samurai_super_secret_key_change_this_32_chars

# Пароль админа
ADMIN_PASSWORD=МойПароль123

# ── ОПЦИОНАЛЬНО ────────────────────────────────────────────

# Telegram Bot Token
BOT_TOKEN=123456789:ABCDefGHIjklMNOpqrsTUVwxyz

# Твой Telegram ID
ADMIN_TG_ID=123456789

# Порт (по умолчанию 3000)
API_PORT=3000

# Claude модель
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=2000
```

---

## 🔑 ПОЛУЧЕНИЕ API КЛЮЧЕЙ

### 1. ANTHROPIC_API_KEY (для 3D молекул)

1. Зайди на https://console.anthropic.com/
2. Зарегистрируйся или войди
3. API Keys → Create Key
4. Скопируй ключ (начинается с `sk-ant-`)
5. Вставь в `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 2. TELEGRAM BOT TOKEN

1. Открой @BotFather в Telegram
2. Отправь `/newbot`
3. Следуй инструкциям
4. Получи токен (формат: `123456789:ABCDefGHI...`)
5. Добавь в `.env`:

```env
BOT_TOKEN=123456789:ABCDefGHIjklMNOpqrsTUVwxyz
```

### 3. ADMIN_TG_ID (твой Telegram ID)

1. Открой @userinfobot в Telegram
2. Получи свой ID (число)
3. Добавь в `.env`:

```env
ADMIN_TG_ID=123456789
```

---

## 📱 НАСТРОЙКА TELEGRAM BOT

### Команды бота:

| Команда | Описание |
|---------|----------|
| `/start` | Регистрация в системе |
| `/hunt <запрос>` | Поиск цели |
| `/start_hunt <цель>` | Начать охоту |

### Пример использования:

```
/hunt crypto arbitrage
/start_hunt BTC/USDT arbitrage
```

### Структура бота:

```
⚔️ SAMURAI HUNTER BOT
├── Регистрация охотников
├── Поиск целей
├── Статистика клана
├── Реферальная система
└── Система выплат
```

---

## 🔧 ЗАПУСК И УПРАВЛЕНИЕ

### Основные команды:

```bash
# Статус всех процессов
pm2 status

# Логи сервера
pm2 logs samurai-server

# Логи конкретного процесса
pm2 logs samurai-telegram

# Перезапуск всех процессов
pm2 restart all

# Остановка всех процессов
pm2 stop all

# Просмотр в реальном времени
pm2 monit
```

### Ручной запуск:

```bash
# Запуск сервера
cd ~/samurai/server
node server.js

# Запуск в фоне
nohup node server.js > logs/server.log 2>&1 &

# Проверка
curl http://localhost:3000/health
```

### Автозапуск при перезагрузке:

```bash
# Сохраняем процессы
pm2 save

# Генерируем startup скрипт
pm2 startup
# (скопируй и выполни команду из вывода)
```

---

## 🌐 ДОСТУП ИЗВНЕ

### Узнай свой IP:

```bash
# В Termux:
ip route get 1.1.1.1 | grep -oP 'src \K\S+'

# Или:
ifconfig | grep 'inet ' | grep -v 127
```

### Доступ:

```
Локально:  http://localhost:3000
Внешний:    http://ТВОЙ_IP:3000

Пример:
http://192.168.1.100:3000
```

### Проброс портов (роутер):

Если нужен доступ из интернета:
1. Зайди в настройки роутера
2. Пробрось порт 3000 на устройство
3. Узнай внешний IP: https://2ip.ru

---

## 🛠 ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема: "Node not found"

```bash
# Установи Node.js
pkg install nodejs
```

### Проблема: "Redis connection refused"

```bash
# Запусти Redis
redis-server --daemonize yes

# Или установи
pkg install redis
```

### Проблема: Server не запускается

```bash
# Проверь логи
cat ~/samurai/logs/server.out.log

# Или запусти вручную для отладки
cd ~/samurai/server
node server.js
```

### Проблема: "Module not found"

```bash
# Переустанови зависимости
cd ~/samurai/server
rm -rf node_modules package-lock.json
npm install
```

### Проблема: Telegram Bot не работает

```bash
# Проверь токен в .env
cat ~/samurai/.env | grep BOT_TOKEN

# Проверь логи
pm2 logs samurai-telegram
```

### Проблема: Не заходит на Web UI

```bash
# Проверь что порт открыт
netstat -tlnp | grep 3000

# Проверь firewall
# Android: Settings → Apps → Termux → Network
```

---

## 📊 МОНИТОРИНГ

### Чек-лист перед запуском:

- [ ] .env заполнен (минимум JWT_SECRET, ADMIN_PASSWORD)
- [ ] Redis запущен
- [ ] Node_modules установлены
- [ ] Server работает
- [ ] PM2 настроен

### Проверка статуса:

```bash
# 1. Проверь health endpoint
curl http://localhost:3000/health

# Ожидаемый ответ:
{"status":"ok","version":"54.0.0","uptime":123,"redis":true,"users":1}

# 2. Проверь PM2
pm2 status

# Должны быть запущены:
# - samurai-server
# - samurai-telegram (если BOT_TOKEN задан)
# - samurai-market
# - samurai-sensory
```

---

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации:

1. **Не делись .env файлом**
2. **Используй сложные пароли**
3. **Не запускай от root** (в Termux это нормально)
4. **Обновляй зависимости** периодически

```bash
# Обновление Node.js пакетов
cd ~/samurai/server
npm update

# Обновление Python пакетов
pip install --upgrade python-telegram-bot aiohttp
```

---

## 📞 КОНТАКТЫ

- GitHub: https://github.com/smokblack999-a11y/pylingo-pro
- Issues: https://github.com/smokblack999-a11y/pylingo-pro/issues

---

⚔️ * Samurai Suite - Система автономной охоты за возможностями *
