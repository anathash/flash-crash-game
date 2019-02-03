class Config:
    MIN_ORDER_VALUE = "MIN_ORDER_VALUE"
    __conf = {"MIN_ORDER_VALUE": 1000}

    @staticmethod
    def get(name):
        return Config.__conf[name]

    @staticmethod
    def set(name, value):
        if name in Config.__conf.keys():
            Config.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")