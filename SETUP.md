# ⚔️ SAMURAI SUITE - ПОДРОБНАЯ ИНСТРУКЦИЯ ПО НАСТРОЙКЕ

## 📋 СОДЕРЖАНИЕ
1. [Требования](#требования)
2. [Установка](#установка)
3. [Настройка .env](#настройка-env)
4. [Первый запуск](#первый-запуск)
5. [Настройка Telegram](#настройка-telegram)
6. [Настройка интеграций](#настройка-интеграций)
7. [Управление процессами](#управление-процессами)
8. [Устранение проблем](#устранение-проблем)

---

## 1. ТРЕБОВАНИЯ

### Минимальные:
- **Termux** (Android) или Linux сервер
- **Node.js** v16+
- **Python** 3.8+
- **Redis** (для очередей)
- **100MB** свободного места

### Рекомендуемые:
- **2GB RAM**
- **SSH доступ** (для удалённого управления)
- **Статический IP** или DDNS

---

## 2. УСТАНОВКА

### Вариант А: Автоматическая (рекомендуется)
```bash
# Клонирование репозитория
git clone https://github.com/smokblack999-a11y/pylingo-pro.git ~/samurai

# Запуск установщика
cd ~/samurai
bash install_full.sh
```

### Вариант Б: Ручная установка
```bash
# 1. Установка зависимостей
pkg update
pkg install nodejs python git redis openssh curl wget

# 2. Клонирование
git clone https://github.com/smokblack999-a11y/pylingo-pro.git ~/samurai

# 3. Установка npm пакетов
cd ~/samurai/server
npm install

# 4. Установка Python пакетов
pip install flask python-telegram-bot aiohttp python-dotenv

# 5. Запуск Redis
redis-server --daemonize yes

# 6. Запуск сервера
cd ~/samurai/server
node server.js
```

---

## 3. НАСТРОЙКА .ENV

### Создание файла:
```bash
cd ~/samurai
cp .env.example .env
nano .env
```

### Параметры:

#### ОБЯЗАТЕЛЬНЫЕ:
| Параметр | Описание | Пример |
|----------|---------|--------|
| `ANTHROPIC_API_KEY` | API ключ Anthropic (для молекул) | `sk-ant-api03-...` |
| `JWT_SECRET` | Секрет для JWT токенов (32+ символа) | `samurai_secret_CHANGE_32chars` |
| `ADMIN_PASSWORD` | Пароль админа | `твой_пароль` |

#### ОПЦИОНАЛЬНЫЕ:
| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| `API_PORT` | Порт сервера | `3000` |
| `REDIS_URL` | URL Redis | `redis://127.0.0.1:6379` |
| `BOT_TOKEN` | Telegram бот токен | - |
| `ADMIN_TG_ID` | Telegram ID админа | - |
| `CLAUDE_MODEL` | Модель Claude | `claude-sonnet-4-20250514` |

### Получение API ключей:

#### Anthropic API Key:
1. Зарегистрируйся на [console.anthropic.com](https://console.anthropic.com)
2. Создай API ключ
3. Скопируй в `.env`

#### Telegram Bot:
1. Напиши @BotFather в Telegram
2. Команда `/newbot`
3. Следуй инструкциям
4. Скопируй токен в `.env`

#### Telegram ID:
1. Напиши @userinfobot
2. Скопируй свой ID в `ADMIN_TG_ID`

---

## 4. ПЕРВЫЙ ЗАПУСК

### После настройки .env:
```bash
cd ~/samurai

# Запуск Redis
redis-server --daemonize yes

# Запуск сервера (в фоне)
cd server
nohup node server.js > ../logs/server.log 2>&1 &

# Проверка
curl http://localhost:3000/health
```

### Ожидаемый ответ:
```json
{
  "status": "ok",
  "version": "54.0.0",
  "uptime": 10,
  "redis": true,
  "users": 1
}
```

---

## 5. НАСТРОЙКА TELEGRAM

### Запуск Telegram Hunter Bot:
```bash
cd ~/samurai

# Убедись что BOT_TOKEN заполнен в .env
nano .env
# Добавь: BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Запуск бота
python3 integrations/telegram_bot.py
```

### Команды бота:
| Команда | Описание |
|--------|----------|
| `/start` | Регистрация в системе |
| `/hunt <запрос>` | Поиск цели |
| `/start_hunt <цель>` | Начать охоту |

### Проверка работы:
1. Открой своего бота в Telegram
2. Напиши `/start`
3. Бот должен ответить приветствием

---

## 6. НАСТРОЙКА ИНТЕГРАЦИЙ

### Discord Hunter:
```bash
# Токен получаешь на discord.com/developers
# Добавь в .env:
DISCORD_TOKEN=твой_токен

# Запуск
python3 integrations/discord_bot.py
```

### Twitter/X Hunter:
```bash
# Добавь в .env:
TWITTER_API_KEY=твой_ключ
TWITTER_API_SECRET=твой_секрет

# Запуск
python3 integrations/twitter_bot.py
```

### Binance Scanner:
```bash
# Автоматически запускается с market.py
python3 python/market.py
```

---

## 7. УПРАВЛЕНИЕ ПРОЦЕССАМИ

### Основные команды PM2:
```bash
# Статус всех процессов
pm2 status

# Логи конкретного процесса
pm2 logs samurai-server

# Перезапуск
pm2 restart samurai-server

# Остановка
pm2 stop all

# Удаление всех
pm2 delete all
```

### Ручное управление:
```bash
# Проверка что процесс работает
ps aux | grep node

# Принудительная остановка
pkill -f "node server.js"
# Запуск заново
cd ~/samurai/server && node server.js
```

### Автозапуск:
```bash
# Создание автозапуска
pm2 startup
# Сохранение конфигурации
pm2 save
```

---

## 8. УСТРАНЕНИЕ ПРОБЛЕМ

### Сервер не запускается:
```bash
# Проверь логи
tail -50 ~/samurai/logs/server.log

# Проверь порт
lsof -i :3000

# Убить процесс на порту
fuser -k 3000/tcp
```

### Redis не работает:
```bash
# Проверка статуса
redis-cli ping
# Должен ответить PONG

# Запуск вручную
redis-server --daemonize yes
```

### Ошибка API ключа:
```bash
# Проверь что ключ не пустой
cat ~/samurai/.env | grep API

# Проверь формат (должен начинаться с sk-ant-)
```

### Бот Telegram не отвечает:
```bash
# Проверь токен
curl -s "https://api.telegram.org/bot<TOKEN>/getMe"

# Проверь логи
tail -50 ~/samurai/logs/telegram.log
```

---

## 📊 МОНИТОРИНГ

### Проверка здоровья системы:
```bash
curl http://localhost:3000/health
```

### Проверка метрик:
```bash
# Только для админа
curl -H "Authorization: Bearer <TOKEN>" http://localhost:3000/api/analytics
```

### Логи в реальном времени:
```bash
# Все процессы
pm2 logs

# Конкретный
pm2 logs samurai-server --lines 50
```

---

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации:
1. **Никогда не публикуй** `.env` файл
2. Используй **сложные пароли** (16+ символов)
3. Ограничь **доступ к порту 3000** файрволом
4. Регулярно **обновляй зависимости**
5. **Не запускай от root** без необходимости

### Защита SSH:
```bash
# Отключи парольную авторизацию в /etc/ssh/sshd_config
PasswordAuthentication no
PermitRootLogin without-password
```

---

## 📞 ПОДДЕРЖКА

При проблемах проверь:
1. Логи: `pm2 logs`
2. Статус процессов: `pm2 status`
3. Health endpoint: `curl http://localhost:3000/health`

---

## ✅ ЧЕК-ЛИСТ ЗАПУСКА

- [ ] Node.js установлен
- [ ] Python установлен
- [ ] Redis запущен
- [ ] `.env` заполнен
- [ ] Сервер запущен
- [ ] Web UI доступен
- [ ] Telegram бот работает (опционально)


---

⚔️ *Настройка завершена. Система готова к работе!*
