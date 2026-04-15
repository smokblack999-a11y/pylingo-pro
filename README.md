# ⚔️ SAMURAI SUITE v54

**Автономная Империя** — комплексная система для поиска и эксплуатации возможностей заработка с использованием ИИ.

## 🏗 Архитектура

```
SAMURAI SUITE
├── core/                    # Ядро системы
│   ├── agent_swarm.py      # Level 3: Architect Core
│   ├── sovereign_engine.py # Level 4: Sovereign Engine  
│   └── singularity_engine.py# Level 5: Singularity Engine
│
├── server/                  # Backend (Node.js)
│   ├── server.js           # Express + WebSocket + Redis
│   └── package.json
│
├── web/                    # Frontend (React + Three.js)
│   └── index.html          # 5 вкладок UI
│
├── python/                  # Python сервисы
│   ├── shogun_bot.py       # Telegram игра
│   ├── market.py           # Binance scanner
│   └── sensory.py          # DNS монитор
│
├── integrations/           # Интеграции
│   ├── telegram_bot.py      # Telegram Hunter
│   ├── discord_bot.py      # Discord Hunter
│   └── twitter_bot.py      # Twitter Hunter
│
├── database/               # Базы данных
│   └── opportunity_tracker.py
│
├── strategies/             # Стратегии заработка
│   └── money_strategies.py # Арбитраж, флиппинг, etc
│
├── bots/                   # Деплой ботов
│   └── deployer.py         # Hunter Deployer
│
└── app/                    # PyLingo Pro
    └── main.py
```

## 📊 Уровни Автономии

### Level 1: Basic AI Assistant
Базовый ИИ-ассистент

### Level 2: Exploit Finder
Поиск уязвимостей и возможностей

### Level 3: Architect Core (agent_swarm.py)
- **AGENT SWARM**: Рой специализированных агентов
- **ADAPTIVE FEEDBACK**: Петля обратной связи
- **SCARCITY & FOMO ENGINE**: Создание дефицита
- **SHADOW SEARCH**: Поиск скрытых ресурсов

### Level 4: Sovereign Engine (sovereign_engine.py)
- **SELF-CODING**: Самогенерация кода
- **MULTI-AGENT SWARM**: Управление роем
- **RESOURCE ALLOCATION**: Распределение ресурсов
- **RECURSIVE SELF-IMPROVEMENT**: Самооптимизация

### Level 5: Singularity Engine (singularity_engine.py)
- **MARKET MANIPULATION**: Управление рынком
- **INTER-AGENT ECONOMY**: Экономика ИИ-агентов
- **PREDICTIVE DOMINANCE**: Предиктивный анализ
- **RECURSIVE EVOLUTION**: Полная автономия

## 🚀 Быстрый старт

```bash
# Клонирование
git clone https://github.com/smokblack999-a11y/pylingo-pro.git ~/samurai
cd ~/samurai

# Установка
bash install.sh

# Запуск
bash launcher.sh
```

## ⚙️ Конфигурация

Создай `.env` файл:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=your_secret_32_chars
ADMIN_PASSWORD=admin123

# Optional
BOT_TOKEN=...
ADMIN_TG_ID=...
API_PORT=3000
REDIS_URL=redis://127.0.0.1:6379
```

## 🌐 Доступ

- Web UI: `http://localhost:3000`
- Логин: `admin` / пароль из `.env`

## 📱 Модули

| Модуль | Описание |
|--------|----------|
| Telegram Hunter | Охота в Telegram |
| Discord Hunter | Охота в Discord |
| Twitter Hunter | Охота в Twitter/X |
| Arbitrage Engine | Арбитраж между биржами |
| Whale Hunter | Охота на крупных клиентов |
| Opportunity Tracker | Трекер возможностей |
| Bot Deployer | Деплой охотников |

## 📦 PM2 Процессы

```
samurai-server   - Express API + WebSocket
samurai-shogun   - Telegram игра
samurai-market   - Binance scanner
samurai-sensory - DNS монитор
```

## 🔧 Управление

```bash
pm2 status           # Статус
pm2 logs samurai     # Логи
pm2 restart all     # Перезапуск
bash samurai.sh      # Меню
```

## 📄 License

MIT

---

⚔️ *Создано для достижения финансовой независимости*
