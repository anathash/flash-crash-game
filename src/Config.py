class Config:
    APP_NAME = 'myapp'
    SECRET_KEY = 'secret-key-of-myapp'
    ADMIN_NAME = 'administrator'


class DevelopmentConfig(Config):
    DEBUG = True

    INITIAL_CAPITAL = 1000000
    CURRENCY_MIN_ORDER_UNIT = 1000
    ALPHA = 1.0536
    SELL_SHARE_PORTION_JUMP = 0.05
    BUY_SHARE_PORTION_JUMP = 0.0
    MAX_ASSETS_IN_ACTION = 5


class ProductionConfig(Config):
    DEBUG = False


