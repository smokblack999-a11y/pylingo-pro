"""
⚔️ HUNTER DEPLOYER
Деплоер ботов-охотников
"""
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

class BotDeployer:
    """Создание и деплой охотников"""
    
    BOT_TYPES = {
        'scanner': {
            'name': 'Scanner',
            'description': 'Сканирует рынки и площадки',
            'tasks': ['scan_markets', 'find_opportunities', 'track_prices']
        },
        'hunter': {
            'name': 'Hunter',
            'description': 'Охотится на клиентов и сделки',
            'tasks': ['find_leads', 'contact_prospects', 'close_deals']
        },
        'analyzer': {
            'name': 'Analyzer',
            'description': 'Анализирует данные и тренды',
            'tasks': ['analyze_trends', 'predict_movements', 'generate_insights']
        },
        'messenger': {
            'name': 'Messenger',
            'description': 'Рассылает сообщения и офферы',
            'tasks': ['send_dm', 'post_content', 'manage_campaigns']
        },
        'trader': {
            'name': 'Trader',
            'description': 'Торгует на биржах',
            'tasks': ['execute_trades', 'manage_portfolio', 'arbitrage']
        }
    }
    
    def __init__(self, ai_callback):
        self.ai = ai_callback
        self.deployed_bots = {}
        self.templates = Path('bots/templates')
        self.templates.mkdir(parents=True, exist_ok=True)
    
    async def create_bot(self, bot_type: str, mission: str, config: dict = None) -> dict:
        """Создание бота под задачу"""
        if bot_type not in self.BOT_TYPES:
            return {'error': f'Unknown type: {bot_type}'}
        
        template = self.BOT_TYPES[bot_type]
        
        # Генерируем код бота
        prompt = f"""Создай Python-скрипт бота-охотника:

Тип: {template['name']}
Описание: {template['description']}
Задачи: {template['tasks']}
Миссия: {mission}
Конфиг: {json.dumps(config or {})}

Требования:
1. Асинхронная работа (asyncio)
2. Логирование
3. Обработка ошибок
4. JSON-конфиг

Верни полный код."""
        
        code = await self.ai(prompt)
        
        bot_id = str(uuid.uuid4())
        bot = {
            'id': bot_id,
            'type': bot_type,
            'mission': mission,
            'config': config or {},
            'created': datetime.now().isoformat(),
            'status': 'created',
            'code': code
        }
        
        # Сохраняем код
        filepath = self.templates / f'{bot_id}.py'
        filepath.write_text(code, encoding='utf-8')
        bot['filepath'] = str(filepath)
        
        self.deployed_bots[bot_id] = bot
        
        return bot
    
    async def deploy_bot(self, bot_id: str) -> bool:
        """Деплой бота"""
        if bot_id not in self.deployed_bots:
            return False
        
        bot = self.deployed_bots[bot_id]
        bot['status'] = 'deployed'
        bot['deployed_at'] = datetime.now().isoformat()
        
        print(f"🚀 Bot {bot_id} deployed: {bot['mission']}")
        return True
    
    async def kill_bot(self, bot_id: str) -> bool:
        """Удаление бота"""
        if bot_id in self.deployed_bots:
            self.deployed_bots[bot_id]['status'] = 'killed'
            self.deployed_bots[bot_id]['killed_at'] = datetime.now().isoformat()
            return True
        return False
    
    def list_bots(self, status: str = None) -> list:
        bots = self.deployed_bots.values()
        if status:
            bots = [b for b in bots if b['status'] == status]
        return list(bots)
    
    async def swarm_deploy(self, mission: str, count: int = 5) -> list:
        """Деплой роя ботов"""
        bots = []
        for i in range(count):
            bot_type = list(self.BOT_TYPES.keys())[i % len(self.BOT_TYPES)]
            bot = await self.create_bot(bot_type, f"{mission} #{i+1}")
            await self.deploy_bot(bot['id'])
            bots.append(bot)
        return bots


__all__ = ['BotDeployer']
