import rosu_pp_py as rosu

from pathlib import Path

from ATRIlib import Download


class Rosu:
    def __init__(self):
        self.beatmaps_path = Path('./data/beatmaps/')
        self.beatmaps_path_tmp = Path('./data/beatmaps_tmp/')
        self.download = Download.Downloader()

    # 获取单个谱面(ranked)
    async def get_beatmap_file_async_one(self, beatmap_id):
        filepath = self.beatmaps_path / f'{beatmap_id}.osu'
        if filepath.exists():
            return
        else:
            beatmap_ids = [beatmap_id]
        await self.download.download_files(beatmap_ids)

    # 批量获取谱面(ranked)
    async def get_beatmap_file_async_all(self, beatmap_id_list):
        beatmap_ids = []
        for beatmap_id in beatmap_id_list:
            file_path = self.beatmaps_path / f'{beatmap_id}.osu'
            if file_path.exists():
                pass
            else:
                beatmap_ids.append(beatmap_id)

        await self.download.download_files(beatmap_ids)

    # 获取单个谱面(unranked)
    async def get_beatmap_file_tmp_async_one(self, beatmap_id):
        filepath = self.beatmaps_path_tmp / f'{beatmap_id}.osu'
        if filepath.exists():
            return
        else:
            await self.download.get_beatmap_file_tmp(beatmap_id)

    # 计算pp(ranked)
    async def calculate_pp_if_all(self, beatmap_id, mods, acc, combo):

        mods_int = self.calculate_mod_int(mods)

        result = {}

        await self.get_beatmap_file_async_one(beatmap_id)

        file_path = self.beatmaps_path / f'{beatmap_id}.osu'

        map = rosu.Beatmap(path=str(file_path))

        perf = rosu.Performance(mods=mods_int)

        perf.set_combo(None)
        perf.set_accuracy(acc)
        attrs = perf.calculate(map)
        result['fcpp'] = attrs.pp

        perf.set_accuracy(95)
        attrs = perf.calculate(map)
        result['95fcpp'] = attrs.pp

        perf.set_accuracy(96)
        attrs = perf.calculate(map)
        result['96fcpp'] = attrs.pp

        perf.set_accuracy(97)
        attrs = perf.calculate(map)
        result['97fcpp'] = attrs.pp

        perf.set_accuracy(98)
        attrs = perf.calculate(map)
        result['98fcpp'] = attrs.pp

        perf.set_accuracy(99)
        attrs = perf.calculate(map)
        result['99fcpp'] = attrs.pp

        perf.set_accuracy(100)
        attrs = perf.calculate(map)
        result['100fcpp'] = attrs.pp

        result['fullaimpp'] = attrs.pp_aim
        result['fullspeedpp'] = attrs.pp_speed
        result['fullaccpp'] = attrs.pp_accuracy

        result['maxcombo'] = attrs.difficulty.max_combo

        perf.set_accuracy(acc)
        perf.set_combo(combo)
        attrs = perf.calculate(map)
        result['pp'] = attrs.pp

        result['aimpp'] = attrs.pp_aim
        result['speedpp'] = attrs.pp_speed
        result['accpp'] = attrs.pp_accuracy

        result['difficulty'] = attrs.difficulty.stars

        return result

    # 计算rosu数据(unranked)
    async def calculate_pp_if_all_tmp(self, beatmap_id, mods, acc, combo):

        mods_int = self.calculate_mod_int(mods)

        result = {}

        await self.get_beatmap_file_async_one(beatmap_id)

        file_path = self.beatmaps_path_tmp / f'{beatmap_id}.osu'

        map = rosu.Beatmap(path=str(file_path))

        perf = rosu.Performance(mods=mods_int)

        perf.set_combo(None)
        perf.set_accuracy(acc)
        attrs = perf.calculate(map)
        result['fcpp'] = attrs.pp

        perf.set_accuracy(95)
        attrs = perf.calculate(map)
        result['95fcpp'] = attrs.pp

        perf.set_accuracy(96)
        attrs = perf.calculate(map)
        result['96fcpp'] = attrs.pp

        perf.set_accuracy(97)
        attrs = perf.calculate(map)
        result['97fcpp'] = attrs.pp

        perf.set_accuracy(98)
        attrs = perf.calculate(map)
        result['98fcpp'] = attrs.pp

        perf.set_accuracy(99)
        attrs = perf.calculate(map)
        result['99fcpp'] = attrs.pp

        perf.set_accuracy(100)
        attrs = perf.calculate(map)
        result['100fcpp'] = attrs.pp

        result['fullaimpp'] = attrs.pp_aim
        result['fullspeedpp'] = attrs.pp_speed
        result['fullaccpp'] = attrs.pp_accuracy

        result['maxcombo'] = attrs.difficulty.max_combo

        perf.set_accuracy(acc)
        perf.set_combo(combo)
        attrs = perf.calculate(map)
        result['pp'] = attrs.pp

        result['aimpp'] = attrs.pp_aim
        result['speedpp'] = attrs.pp_speed
        result['accpp'] = attrs.pp_accuracy

        result['difficulty'] = attrs.difficulty.stars

        return result

    # 计算mod_int
    def calculate_mod_int(self, modlists):
        mods_int = 0
        for i in modlists:
            if i == "NF":
                mods_int += 1
            if i == "EZ":
                mods_int += 2
            if i == "TD":
                mods_int += 4
            if i == "HD":
                mods_int += 8
            if i == "HR":
                mods_int += 16
            if i == "SD":
                mods_int += 32
            if i == "DT":
                mods_int += 64
            if i == "RX":
                mods_int += 128
            if i == "HT":
                mods_int += 256
            if i == "NC":
                mods_int += 576
            if i == "FL":
                mods_int += 1024
            if i == "AT":
                mods_int += 2048
            if i == "SO":
                mods_int += 4096
            if i == "AP":
                mods_int += 8192
            if i == "PF":
                mods_int += 16416
            if i == "4K":
                mods_int += 32768
            if i == "5K":
                mods_int += 65536
            if i == "6K":
                mods_int += 131072
            if i == "7K":
                mods_int += 262144
            if i == "8K":
                mods_int += 524288
            if i == "FI":
                mods_int += 1048576
            if i == "RD":
                mods_int += 2097152
            if i == "CM":
                mods_int += 4194304
            if i == "TP":
                mods_int += 8388608
            if i == "9K":
                mods_int += 16777216
            if i == "CO":
                mods_int += 33554432
            if i == "1K":
                mods_int += 67108864
            if i == "3K":
                mods_int += 134217728
            if i == "2K":
                mods_int += 268435456
            if i == "V2":
                mods_int += 536870912
            if i == "MR":
                mods_int += 1073741824
        return mods_int
