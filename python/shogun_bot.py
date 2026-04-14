"""SHOGUN BOT v68 — Telegram игра. LIME = игровая валюта, НЕ финансовый инструмент."""
import os, json, random, logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

try:
    load_dotenv(Path(__file__).parent.parent / '.env')
except:
    pass

TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_TG_ID', '0') or '0')

if not TOKEN or 'ВСТАВЬ' in TOKEN:
    print('[Shogun] BOT_TOKEN не задан в .env — пропуск')
    import sys
    sys.exit(0)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.WARNING)
DB = Path(__file__).parent.parent / 'data' / 'shogun.json'
DB.parent.mkdir(exist_ok=True)


class DB_:
    def __init__(self):
        self.u = {}
        if DB.exists():
            try:
                self.u = json.loads(DB.read_text())
            except:
                pass

    def save(self):
        DB.write_text(json.dumps(self.u, ensure_ascii=False, indent=2))

    def get(self, uid, name):
        k = str(uid)
        if k not in self.u:
            self.u[k] = {
                'name': name,
                'bal': 1000.0,
                'power': 10,
                'wpn': 'Кулаки',
                'armor': 'Кимоно',
                'trades': 0,
                'ref': None,
                'plan': 'free'
            }
        return self.u[k]


db = DB_()
ITEMS = {
    '1': ('Катана', 500, 'power', 20, 'wpn'),
    '2': ('Броня Самурая', 1200, 'power', 50, 'armor'),
    '3': ('Шлем', 800, 'power', 30, 'wpn')
}
BACK = InlineKeyboardMarkup([[InlineKeyboardButton('⬅ Назад', callback_data='back')]])


async def start(u: Update, c):
    uid = u.effective_user.id
    name = u.effective_user.first_name
    usr = db.get(uid, name)
    if c.args and c.args[0].isdigit() and c.args[0] != str(uid) and not usr.get('ref'):
        ref = c.args[0]
        if ref in db.u:
            db.u[ref]['bal'] = round(db.u[ref]['bal'] + 250, 2)
            usr['ref'] = ref
    db.save()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('🛒 Магазин', callback_data='shop'),
         InlineKeyboardButton('🏆 ТОП', callback_data='top')],
        [InlineKeyboardButton('🤝 Реф', callback_data='ref'),
         InlineKeyboardButton('📊 Статус', callback_data='st')],
        [InlineKeyboardButton('💰 Вывод', callback_data='wd')]
    ])
    await u.message.reply_text(
        f'🏯 *BUSHIDO v68*\n👤 {name}\n💰 {round(usr["bal"], 2)} LIME _(игровая валюта)_\n'
        f'⚡ Мощь: {usr["power"]} | ⚔ {usr["wpn"]} | 🛡 {usr["armor"]}\n`id:{uid}`',
        reply_markup=kb, parse_mode='Markdown'
    )


async def btn(u: Update, c):
    q = u.callback_query
    uid = q.from_user.id
    usr = db.get(uid, q.from_user.first_name)
    await q.answer()

    if q.data == 'st':
        ch = round(random.uniform(-3, 9), 2)
        usr['bal'] = round(usr['bal'] + ch, 2)
        usr['trades'] += 1
        db.save()
        await q.message.edit_text(
            f'📊 *Статус*\n💰 {usr["bal"]} LIME\n🎮 Раундов: {usr["trades"]}\n'
            f'{"📈" if ch >= 0 else "📉"} Раунд: {ch:+}\n_LIME — игровая симуляция_',
            reply_markup=BACK, parse_mode='Markdown'
        )
    elif q.data == 'shop':
        await q.message.edit_text(
            '🛒 *Магазин*\n1. Катана — 500 LIME (+20 мощь)\n'
            '2. Броня — 1200 LIME (+50 защита)\n3. Шлем — 800 LIME (+30 мощь)\n'
            'Купить: `/buy 1`',
            reply_markup=BACK, parse_mode='Markdown'
        )
    elif q.data == 'top':
        top = sorted(db.u.values(), key=lambda x: x['bal'], reverse=True)[:5]
        lines = '\n'.join(f'{i + 1}. {u["name"]} — {round(u["bal"], 2)} LIME' for i, u in enumerate(top))
        await q.message.edit_text(f'🏆 *ТОП-5*\n{lines}', reply_markup=BACK, parse_mode='Markdown')
    elif q.data == 'ref':
        me = await c.bot.get_me()
        await q.message.edit_text(
            f'🤝 `https://t.me/{me.username}?start={uid}`\n+250 LIME за друга!',
            reply_markup=BACK, parse_mode='Markdown'
        )
    elif q.data == 'wd':
        await q.message.edit_text('Отправь `/withdraw <сумма>`', reply_markup=BACK, parse_mode='Markdown')
    elif q.data == 'back':
        await q.message.edit_text('Напиши /start')


async def buy(u: Update, c):
    uid = u.effective_user.id
    usr = db.get(uid, u.effective_user.first_name)
    arg = (c.args or [''])[0]
    if arg not in ITEMS:
        return await u.message.reply_text('Используй /buy 1, /buy 2 или /buy 3')
    name, cost, attr, bonus, slot = ITEMS[arg]
    if usr['bal'] < cost:
        return await u.message.reply_text(f'Мало LIME. Нужно {cost}, у тебя {round(usr["bal"], 2)}')
    usr['bal'] = round(usr['bal'] - cost, 2)
    usr[attr] += bonus
    usr[slot] = name
    db.save()
    await u.message.reply_text(f'✅ {name} куплен (+{bonus} {attr}). Баланс: {usr["bal"]} LIME')


async def withdraw(u: Update, c):
    uid = u.effective_user.id
    usr = db.get(uid, u.effective_user.first_name)
    try:
        amt = float((c.args or ['0'])[0])
        if amt <= 0 or amt > usr['bal']:
            raise ValueError
        usr['bal'] = round(usr['bal'] - amt, 2)
        db.save()
        if ADMIN_ID:
            await c.bot.send_message(ADMIN_ID, f'💰 Вывод: {usr["name"]} ({uid}) — {amt} LIME')
        await u.message.reply_text('✅ Заявка отправлена!')
    except:
        await u.message.reply_text('❌ Пример: `/withdraw 500`', parse_mode='Markdown')


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('buy', buy))
    app.add_handler(CommandHandler('withdraw', withdraw))
    app.add_handler(CallbackQueryHandler(btn))
    print('🏯 Shogun Bot запущен')
    app.run_polling(drop_pending_updates=True)
