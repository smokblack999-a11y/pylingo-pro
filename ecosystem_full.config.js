const path = require('path');
const fs = require('fs');

// Загрузка .env
const envPath = path.join(__dirname, '.env');
const env = {};
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [key, ...values] = line.split('=');
    if (key && !key.startsWith('#') && values.length) {
      env[key.trim()] = values.join('=').trim();
    }
  });
}

module.exports = {
  apps: [
    {
      name: 'samurai-server',
      script: './server/server.js',
      cwd: __dirname,
      autorestart: true,
      max_restarts: 15,
      min_uptime: '5000',
      restart_delay: 3000,
      env: {
        NODE_ENV: 'production',
        API_PORT: env.API_PORT || '3000',
        JWT_SECRET: env.JWT_SECRET || 'samurai_secret_change_32chars',
        ADMIN_PASSWORD: env.ADMIN_PASSWORD || 'admin123',
        REDIS_URL: env.REDIS_URL || 'redis://127.0.0.1:6379',
        ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY || '',
        CLAUDE_MODEL: env.CLAUDE_MODEL || 'claude-sonnet-4-20250514',
        MAX_TOKENS: env.MAX_TOKENS || '2000',
        RATE_LIMIT_MS: env.RATE_LIMIT_MS || '2000'
      },
      error_file: './logs/server.err.log',
      out_file: './logs/server.out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true
    },
    {
      name: 'samurai-telegram',
      script: 'python3',
      args: './integrations/telegram_bot.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10000',
      restart_delay: 5000,
      env: {
        BOT_TOKEN: env.BOT_TOKEN || '',
        ADMIN_TG_ID: env.ADMIN_TG_ID || '0'
      },
      error_file: './logs/telegram.err.log',
      out_file: './logs/telegram.out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'samurai-market',
      script: 'python3',
      args: './python/market.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10000',
      restart_delay: 5000,
      error_file: './logs/market.err.log',
      out_file: './logs/market.out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'samurai-sensory',
      script: 'python3',
      args: './python/sensory.py',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10000',
      restart_delay: 10000,
      error_file: './logs/sensory.err.log',
      out_file: './logs/sensory.out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    }
  ]
};
