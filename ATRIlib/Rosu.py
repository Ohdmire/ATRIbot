import rosu_pp_py as rosu

from pathlib import Path


from ATRIlib import Download

class Rosu:
    def __init__(self):
        self.beatmaps_path = Path('./data/beatmaps/')
        self.download=Download.Downloader()


    async def get_beatmap_file_async_one(self,beatmap_id):
        filepath=self.beatmaps_path / f'{beatmap_id}.osu'
        if filepath.exists():
            return
        else:
            beatmap_ids=[beatmap_id]
        await self.download.download_files(beatmap_ids)

    async def get_beatmap_file_async_all(self,beatmap_id_list):
        beatmap_ids=[]
        for beatmap_id in beatmap_id_list:
            file_path=self.beatmaps_path / f'{beatmap_id}.osu'
            if file_path.exists():
                pass
            else:
                beatmap_ids.append(beatmap_id)

        await self.download.download_files(beatmap_ids)
        

    async def calculate_pp_if_fc(self,beatmap_id,mods,acc):

        await self.get_beatmap_file_async_one(beatmap_id)

        file_path=self.beatmaps_path / f'{beatmap_id}.osu'

        # either `path`, `bytes`, or `content` must be specified when parsing a map
        map = rosu.Beatmap(path = str(file_path))

        perf=rosu.Performance(mods=mods)

        perf.set_accuracy(acc)
        perf.set_combo(None)

        attrs = perf.calculate(map)

        return attrs.pp
    
    async def calculate_maxcombo(self,beatmap_id):

        await self.get_beatmap_file_async_one(beatmap_id)


        file_path=self.beatmaps_path / f'{beatmap_id}.osu'

        # either `path`, `bytes`, or `content` must be specified when parsing a map
        map = rosu.Beatmap(path = str(file_path))

        perf=rosu.Performance()

        attrs = perf.calculate(map)

        maxcombo=attrs.difficulty.max_combo


        return maxcombo
