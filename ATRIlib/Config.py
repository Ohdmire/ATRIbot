import configparser


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.osuclientid = self.config['OSUAPI']['client_id']
        self.osuclientsecret = self.config['OSUAPI']['client_secret']
