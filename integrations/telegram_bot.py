"""
⚔️ TELEGRAM HUNTER BOT
Бот-охотник для Telegram с интеграцией в Core
"""
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_TG_ID', '0') or '0')

if not TOKEN or 'ВСТАВЬ' in TOKEN:
    print('[Telegram Bot] BOT_TOKEN не задан - пропуск')
    exit(0)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes

# База данных охотников
HUNTERS_DB = Path(__file__).parent.parent / 'data' / 'hunters.json'
HUNTERS_DB.parent.mkdir(exist_ok=True)

def load_hunters():
    if HUNTERS_DB.exists():
        return json.loads(HUNTERS_DB.read_text())
    return {}

def save_hunters(data):
    HUNTERS_DB.write_text(json.dumps(data, indent=2))

class HunterBot:
    def __init__(self):
        self.hunters = load_hunters()
        self.core = None  # Подключаем ядро
    
    async def start(self, u: Update, c):
        """Регистрация охотника"""
        uid = u.effective_user.id
        name = u.effective_user.first_name
        
        if uid not in self.hunters:
            self.hunters[uid] = {
                'name': name,
                'registered': datetime.now().isoformat(),
                'kills': 0,
                'earnings': 0,
                'status': 'active',
                'specialization': None
            }
            save_hunters(self.hunters)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton('🎯 Моя охота', callback_data='my_hunt')],
            [InlineKeyboardButton('📊 Статистика', callback_data='stats')],
            [InlineKeyboardButton('💰 Баланс', callback_data='balance')],
            [InlineKeyboardButton('⚔️ Список охотников', callback_data='hunters_list')]
        ])
        
        await u.message.reply_text(
            f'⚔️ <b>SAMURAI HUNTER BOT</b>\n\n'
            f'Привет, {name}!\n'
            f'Твой ID: <code>{uid}</code>\n\n'
            f'Статус: {self.hunters[uid]["status"]}\n'
            f'Убийств: {self.hunters[uid]["kills"]}\n'
            f'Заработано: ${self.hunters[uid]["earnings"]}',
            reply_markup=kb, parse_mode='HTML'
        )
    
    async def handle_callback(self, u: Update, c):
        q = u.callback_query
        uid = q.from_user.id
        await q.answer()
        
        if q.data == 'my_hunt':
            hunter = self.hunters.get(uid, {})
            await q.message.edit_text(
                f'🎯 <b>Моя охота</b>\n\n'
                f'Статус: {hunter.get("status", "unknown")}\n'
                f'Специализация: {hunter.get("specialization", "Не выбрана")}\n\n'
                f'Используй /hunt <запрос> для поиска цели',
                parse_mode='HTML'
            )
        elif q.data == 'stats':
            total_kills = sum(h.get('kills', 0) for h in self.hunters.values())
            total_earnings = sum(h.get('earnings', 0) for h in self.hunters.values())
            await q.message.edit_text(
                f'📊 <b>Статистика клана</b>\n\n'
                f'Всего охотников: {len(self.hunters)}\n'
                f'Всего убийств: {total_kills}\n'
                f'Всего заработано: ${total_earnings}',
                parse_mode='HTML'
            )
        elif q.data == 'balance':
            hunter = self.hunters.get(uid, {})
            await q.message.edit_text(
                f'💰 <b>Баланс</b>\n\n'
                f'Заработано: ${hunter.get("earnings", 0)}\n'
                f'Убийств: {hunter.get("kills", 0)}\n\n'
                f'<i>Приглашай друзей - получай 10% от их заработка!</i>',
                parse_mode='HTML'
            )
        elif q.data == 'hunters_list':
            top = sorted(self.hunters.values(), key=lambda x: x.get('earnings', 0), reverse=True)[:10]
            text = '⚔️ <b>Топ охотников</b>\n\n'
            for i, h in enumerate(top, 1):
                text += f'{i}. {h["name"]} - ${h.get("earnings", 0)}\n'
            await q.message.edit_text(text, parse_mode='HTML')
    
    async def hunt(self, u: Update, c, query: str):
        """Поиск цели через Core"""
        uid = u.effective_user.id
        
        # Здесь интеграция с Core Level 3-5
        # Результат поиска
        result = f"🎯 Найдена цель по запросу: {query}\n\n"
        result += f"Тип: High-ticket opportunity\n"
        result += f"Потенциал: $500-2000\n"
        result += f"Сложность: Средняя\n\n"
        result += f"Детали: [скрыто]\n\n"
        result += f"Для старта охоты - /start_hunt {query}"
        
        await u.message.reply_text(result, parse_mode='HTML')
    
    async def start_hunt(self, u: Update, c, target: str):
        """Начало охоты"""
        uid = u.effective_user.id
        
        if uid in self.hunters:
            self.hunters[uid]['status'] = 'hunting'
            self.hunters[uid]['current_target'] = target
            save_hunters(self.hunters)
        
        await u.message.reply_text(
            f'⚔️ <b>Охота начата!</b>\n\n'
            f'Цель: {target}\n\n'
            f'Система анализирует цепочку...',
            parse_mode='HTML'
        )
        
        # Симуляция процесса
        await asyncio.sleep(2)
        
        # Результат
        earnings = round(100 + (hash(target) % 500), 2)
        
        if uid in self.hunters:
            self.hunters[uid]['kills'] += 1
            self.hunters[uid]['earnings'] += earnings
            self.hunters[uid]['status'] = 'active'
            save_hunters(self.hunters)
        
        await u.message.reply_text(
            f'✅ <b>Охота успешна!</b>\n\n'
            f'Добыча: ${earnings}\n'
            f'Общий заработок: ${self.hunters[uid]["earnings"]}',
            parse_mode='HTML'
        )


async def main():
    app = Application.builder().token(TOKEN).build()
    bot = HunterBot()
    
    app.add_handler(CommandHandler('start', bot.start))
    app.add_handler(CommandHandler('hunt', lambda u, c: bot.hunt(u, c, ' '.join(c.args))))
    app.add_handler(CommandHandler('start_hunt', lambda u, c: bot.start_hunt(u, c, ' '.join(c.args))))
    app.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    print('⚔️ Telegram Hunter Bot запущен')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
