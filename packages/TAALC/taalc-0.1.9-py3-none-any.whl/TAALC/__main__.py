from .bots.taalc_bot import TaalcBot
from epure.files import IniFile
import asyncio
import argparse
from epure.dbs import GresDb
from .handlers.gift import *
from .handlers.administration import *

class Config:
    pass

if __name__ == '__main__':
    # config = IniFile('./pyconfig.ini')    
    parser = argparse.ArgumentParser(description='bot token')
    parser.add_argument('--token', type=str, help='bot token', required=False)
    parser.add_argument('--config', type=str, help='configuration file', required=False)
    args = parser.parse_args()
    # config = {'bot_token': args.token}

    config = Config()
    if hasattr(args, 'token') and args.token:
        config.bot_token = args.token
    if hasattr(args, 'config') and args.config:
        config = IniFile(args.config)

    db = GresDb(config.db_conn_str,
        log_level=3, 
        default_namespace='marat')
    db.connect()
    
    bot = TaalcBot(config.bot_token, db, config)
    bot.start()
    # asyncio.run(bot.start())