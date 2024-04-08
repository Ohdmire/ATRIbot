from ppyapiv2 import PPYdata

import asyncio


class ATRICore:
    def __init__(self):
        self.ppy=PPYdata()
        self.ppy.get_token()


    def get_user_id(self, osuname):
        return self.ppy.get_user_id(osuname)


a=ATRICore()


id=a.get_user_id('ATRI1024')

print(id)