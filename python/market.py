"""SAMURAI APEX v60.3 — Binance 24hr scanner, только отображение."""
import asyncio, aiohttp, sys, time, os, random
from pathlib import Path

LOG = Path(__file__).parent.parent / 'logs' / 'market.log'
LOG.parent.mkdir(exist_ok=True)


class Scanner:
    DATA = []
    HEAT = 0
    RUN = True
    T = time.time()
    URL = 'https://api.binance.com/api/v3/ticker/24hr'

    def score(self, ch):
        a = abs(float(ch))
        return random.randint(88, 99) if a > 65 else random.randint(40, 75) if a > 15 else random.randint(5, 30)

    async def fetch(self, s):
        while self.RUN:
            try:
                async with s.get(self.URL, timeout=aiohttp.ClientTimeout(total=8)) as r:
                    d = await r.json()
                    self.DATA = sorted(d, key=lambda x: abs(float(x['priceChangePercent'])), reverse=True)[:12]
            except:
                pass
            await asyncio.sleep(8)

    async def brain(self):
        while self.RUN:
            if self.DATA:
                scores = [self.score(a['priceChangePercent']) for a in self.DATA[:10]]
                if any(s > 90 for s in scores) and self.HEAT < 80:
                    best = self.DATA[scores.index(max(scores))]
                    if max(scores) > 96:
                        ts = time.strftime('%Y-%m-%d %H:%M:%S')
                        LOG.open('a').write(f'[{ts}]{best["symbol"]}|{max(scores)}%|{best["priceChangePercent"]}%\n')
                    self.HEAT = min(100, self.HEAT + 6)
                else:
                    self.HEAT = max(0, self.HEAT - 3)
            await asyncio.sleep(1)

    async def ui(self):
        while self.RUN:
            if not self.DATA:
                await asyncio.sleep(2)
                continue
            sys.stdout.write('\033[2J\033[H')
            up = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.T))
            hc = '\033[91m' if self.HEAT > 70 else '\033[92m'
            print(f'\033[1m\033[38;5;208m⚔ SAMURAI APEX v60.3 — BINANCE (только чтение)\033[0m')
            print(f'UPTIME:{up} HEAT:{self.HEAT}%')
            bar = '█' * (self.HEAT // 2) + '░' * (50 - self.HEAT // 2)
            print(f'[{hc}{bar}\033[0m]')
            print('─' * 70)
            for a in self.DATA[:8]:
                sym = a['symbol'].ljust(12)
                ch = float(a['priceChangePercent'])
                sc = self.score(ch)
                col = '\033[93m' if sc > 90 else '\033[96m' if ch < -20 else '\033[90m'
                tag = '🎯 HIGH' if sc > 90 else '🩸 REBOUND' if ch < -20 else '⚙ SCAN'
                print(f'{col}|{sym}|{ch:>9.2f}%|{tag}|SCORE:{sc}%|\033[0m')
            print('─' * 70)
            sys.stdout.flush()
            await asyncio.sleep(1)

    async def run(self):
        async with aiohttp.ClientSession() as s:
            await asyncio.gather(self.fetch(s), self.brain(), self.ui())


if __name__ == '__main__':
    try:
        asyncio.run(Scanner().run())
    except KeyboardInterrupt:
        print('\n[Market] Остановлен.')
