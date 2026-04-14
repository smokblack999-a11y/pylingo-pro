"""SAMURAI SENSORY v36 — глобальный монитор задержек DNS."""
import asyncio, aiohttp, time, json
from pathlib import Path

NODES = [('Google', '8.8.8.8'), ('Cloudflare', '1.1.1.1'), ('OpenDNS', '208.67.222.222')]
LOG = Path(__file__).parent.parent / 'logs' / 'sensory.jsonl'
LOG.parent.mkdir(exist_ok=True)


async def ping(s, ip):
    t = time.monotonic()
    try:
        async with s.get(f'http://{ip}', timeout=aiohttp.ClientTimeout(total=2)):
            pass
    except:
        pass
    return time.monotonic() - t


async def main():
    baseline = None
    print('🌐 SAMURAI SENSORY v36 — мониторинг глобального пульса')
    async with aiohttp.ClientSession() as s:
        while True:
            lats = await asyncio.gather(*[ping(s, ip) for _, ip in NODES])
            avg = sum(lats) / len(lats)
            if baseline is None:
                baseline = avg
            alert = avg > baseline * 1.5
            rec = {
                'ts': time.strftime('%H:%M:%S'),
                'avg_ms': round(avg * 1000, 1),
                'nodes': {n: round(l * 1000, 1) for (n, _), l in zip(NODES, lats)},
                'anomaly': alert
            }
            LOG.open('a').write(json.dumps(rec) + '\n')
            print(f'{"🚨" if alert else "📡"} [{rec["ts"]}] avg={rec["avg_ms"]}ms' + (' АНОМАЛИЯ' if alert else ''))
            await asyncio.sleep(60)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n[Sensory] Остановлен.')
