import rosu_pp_py as rosu
import requests

from pathlib import Path


class Rosu:
    def __init__(self):
        self.beatmaps_path = Path('./data/beatmaps/')

    def get_beatmap_file(self,beatmap_id):
        url = f'https://osu.ppy.sh/osu/{beatmap_id}'
        response = requests.get(url)
        with open(self.beatmaps_path / f'{beatmap_id}.osu', 'wb') as file:
            file.write(response.content)

    def calculate_pp_if_fc(self,beatmap_id,mods,acc):

        file_path=self.beatmaps_path / f'{beatmap_id}.osu'

        # either `path`, `bytes`, or `content` must be specified when parsing a map
        map = rosu.Beatmap(path = str(file_path))

        perf=rosu.Performance(mods=mods)

        perf.set_accuracy(acc)
        perf.set_combo(None)

        attrs = perf.calculate(map)

        return attrs.pp


    

       

r=Rosu()
r.get_beatmap_file(86324)
r.calculate_pp_if_fc(86324,0,100)