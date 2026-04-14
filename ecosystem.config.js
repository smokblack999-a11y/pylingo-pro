const env = (() => {
  const fs = require('fs'), path = require('path');
  const f = path.join(__dirname, '.env');
  if (!fs.existsSync(f)) return {};
  const r = {};
  fs.readFileSync(f, 'utf8').split('\n').forEach(l => {
    const [k, ...v] = l.split('=');
    if (k && !k.startsWith('#') && v.length) r[k.trim()] = v.join('=').trim();
  });
  return r;
})();

module.exports = {
  apps: [
    {
      name: 'samurai-server',
      script: './server/server.js',
      cwd: __dirname,
      autorestart: true,
      max_restarts: 15,
      restart_delay: 3000,
      env: { ...env, NODE_ENV: 'production' },
      error_file: './logs/server.err.log',
      out_file: './logs/server.out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
    },
    {
      name: 'samurai-shogun',
      script: 'python3',
      args: './python/shogun_bot.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      error_file: './logs/shogun.err.log',
      out_file: './logs/shogun.out.log',
    },
    {
      name: 'samurai-market',
      script: 'python3',
      args: './python/market.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      error_file: './logs/market.err.log',
      out_file: './logs/market.out.log',
    },
    {
      name: 'samurai-sensory',
      script: 'python3',
      args: './python/sensory.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      restart_delay: 10000,
      error_file: './logs/sensory.err.log',
      out_file: './logs/sensory.out.log',
    },
  ],
};
