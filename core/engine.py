"""
⚔️ SAMURAI CORE - MAIN ENGINE
Универсальный движок для всех уровней
"""
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List

# Уровни ядра
LEVELS = {
    1: "BASIC",
    2: "EXPLOIT",
    3: "ARCHITECT",
    4: "SOVEREIGN",
    5: "SINGULARITY"
}

class SamuraiCore:
    """
    Главное ядро системы
    """
    
    def __init__(self, ai_callback, level: int = 3):
        self.ai = ai_callback
        self.level = level
        self.status = "initializing"
        self.started_at = datetime.now()
        self.stats = {
            "opportunities_found": 0,
            "opportunities_exploited": 0,
            "earnings": 0,
            "errors": 0
        }
        
    async def initialize(self):
        """Инициализация ядра"""
        print(f"⚔️ Samurai Core Level {self.level} ({LEVELS[self.level]}) initializing...")
        
        # Инициализация компонентов
        if self.level >= 3:
            from core.agent_swarm import AgentSwarm
            self.agent_swarm = AgentSwarm(self.ai)
            print("   ✓ Agent Swarm initialized")
        
        if self.level >= 4:
            from core.sovereign_engine import SovereignEngine
            self.sovereign = SovereignEngine(self.ai)
            print("   ✓ Sovereign Engine initialized")
        
        if self.level >= 5:
            from core.singularity_engine import SingularityEngine
            self.singularity = SingularityEngine(self.ai)
            print("   ✓ Singularity Engine initialized")
        
        self.status = "running"
        print(f"   ✓ Core ready at Level {self.level}")
    
    async def process_task(self, task: str) -> Dict:
        """Обработка задачи"""
        result = {
            "task": task,
            "level": self.level,
            "timestamp": datetime.now().isoformat(),
            "result": None
        }
        
        try:
            if self.level == 1:
                result["result"] = await self.ai(task)
            elif self.level == 2:
                result["result"] = await self._level2_process(task)
            elif self.level == 3:
                result["result"] = await self._level3_process(task)
            elif self.level == 4:
                result["result"] = await self._level4_process(task)
            else:
                result["result"] = await self._level5_process(task)
            
            self.stats["opportunities_found"] += 1
            
        except Exception as e:
            result["error"] = str(e)
            self.stats["errors"] += 1
        
        return result
    
    async def _level2_process(self, task: str) -> str:
        """Level 2: Exploit Finder"""
        return await self.ai(f"Найди уязвимости и возможности в: {task}")
    
    async def _level3_process(self, task: str) -> str:
        """Level 3: Architect Core"""
        # Используем агентов
        evaluation = await self.agent_swarm.evaluate_opportunity(task)
        if evaluation["approved"]:
            refined = await self.agent_swarm.level_3_refinement(task)
            return refined
        return evaluation["evaluation"]
    
    async def _level4_process(self, task: str) -> str:
        """Level 4: Sovereign Engine"""
        # Генерируем код
        code_path = await self.sovereign.self_coding(task)
        # Создаём мини-агента
        agent = await self.sovereign.create_mini_core(task)
        return f"Code: {code_path}, Agent: {agent['name']}"
    
    async def _level5_process(self, task: str) -> str:
        """Level 5: Singularity Engine"""
        # Полная автономия
        shadow = await self.singularity.shadow_liquidity.find()
        bot = await self.singularity.hunter_deployer.create_specialized_bot(task)
        campaign = await self.singularity.hunter_deployer.launch_stealth_campaign(
            task, "high-ticket"
        )
        return f"Shadow: {shadow[:100]}, Bot: {bot['mission']}, Campaign: {campaign[:100]}"
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        uptime = (datetime.now() - self.started_at).total_seconds()
        return {
            **self.stats,
            "level": self.level,
            "status": self.status,
            "uptime_seconds": uptime
        }


# Экспорт
__all__ = ['SamuraiCore', 'LEVELS']
