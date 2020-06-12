from api.routes import app
import uvicorn, configparser, os
import settings

if __name__ == '__main__':
    config = configparser.ConfigParser();
    config.read('config/config.dev.ini');
    uvicorn.run(app, host='0.0.0.0', port=7778, ssl_keyfile=config.get('BASIC', 'KEY', vars=os.environ), ssl_certfile=config.get('BASIC', 'CERT', vars=os.environ));
