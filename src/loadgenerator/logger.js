const { createLogger, format, transports } = require('winston');

const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  exitOnError: false,
  format: format.combine(
    format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    format.errors({ stack: true }),
    format.json()
  ),
  defaultMeta: { 
    service: process.env.DD_SERVICE || 'loadgenerator',
    env: process.env.DD_ENV || 'unknown'
  },
  transports: [
    new transports.Console({
      format: format.json()
    })
  ],
});

module.exports = logger;

