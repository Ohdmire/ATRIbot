import rosu_pp_py as rosu

from pathlib import Path


from ATRIlib import Download


class Rosu:
    def __init__(self):
        self.beatmaps_path = Path('./data/beatmaps/')
        self.download = Download.Downloader()

    async def get_beatmap_file_async_one(self, beatmap_id):
        filepath = self.beatmaps_path / f'{beatmap_id}.osu'
        if filepath.exists():
            return
        else:
            beatmap_ids = [beatmap_id]
        await self.download.download_files(beatmap_ids)

    async def get_beatmap_file_async_all(self, beatmap_id_list):
        beatmap_ids = []
        for beatmap_id in beatmap_id_list:
            file_path = self.beatmaps_path / f'{beatmap_id}.osu'
            if file_path.exists():
                pass
            else:
                beatmap_ids.append(beatmap_id)

        await self.download.download_files(beatmap_ids)

    async def calculate_pp_if_fc(self, beatmap_id, mods, acc):

        await self.get_beatmap_file_async_one(beatmap_id)

        file_path = self.beatmaps_path / f'{beatmap_id}.osu'

        map = rosu.Beatmap(path=str(file_path))

        perf = rosu.Performance(mods=mods)

        perf.set_accuracy(acc)
        perf.set_combo(None)

        attrs = perf.calculate(map)

        return attrs.pp

    async def calculate_maxcombo(self, beatmap_id):

        await self.get_beatmap_file_async_one(beatmap_id)

        file_path = self.beatmaps_path / f'{beatmap_id}.osu'

        map = rosu.Beatmap(path=str(file_path))

        perf = rosu.Performance()

        attrs = perf.calculate(map)

        maxcombo = attrs.difficulty.max_combo

        return maxcombo

    # 功能模块-计算mod_int
    def calculate_mod_int(self, modlists):
        mod_int = 0
        for i in modlists:
            if i == "NF":
                mod_int += 1
            if i == "EZ":
                mod_int += 2
            if i == "TD":
                mod_int += 4
            if i == "HD":
                mod_int += 8
            if i == "HR":
                mod_int += 16
            if i == "SD":
                mod_int += 32
            if i == "DT":
                mod_int += 64
            if i == "RX":
                mod_int += 128
            if i == "HT":
                mod_int += 256
            if i == "NC":
                mod_int += 576
            if i == "FL":
                mod_int += 1024
            if i == "AT":
                mod_int += 2048
            if i == "SO":
                mod_int += 4096
            if i == "AP":
                mod_int += 8192
            if i == "PF":
                mod_int += 16416
            if i == "4K":
                mod_int += 32768
            if i == "5K":
                mod_int += 65536
            if i == "6K":
                mod_int += 131072
            if i == "7K":
                mod_int += 262144
            if i == "8K":
                mod_int += 524288
            if i == "FI":
                mod_int += 1048576
            if i == "RD":
                mod_int += 2097152
            if i == "CM":
                mod_int += 4194304
            if i == "TP":
                mod_int += 8388608
            if i == "9K":
                mod_int += 16777216
            if i == "CO":
                mod_int += 33554432
            if i == "1K":
                mod_int += 67108864
            if i == "3K":
                mod_int += 134217728
            if i == "2K":
                mod_int += 268435456
            if i == "V2":
                mod_int += 536870912
            if i == "MR":
                mod_int += 1073741824
        return mod_int
