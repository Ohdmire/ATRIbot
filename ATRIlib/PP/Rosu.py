import rosu_pp_py as rosu
from pathlib import Path

from ATRIlib.TOOLS.Download import fetch_beatmap_file_async_one
from ATRIlib.TOOLS.Download import beatmaps_path,beatmaps_path_tmp

# beatmaps_path = Path('./data/beatmaps/')
# beatmaps_path_tmp = Path('./data/beatmaps_tmp/')

# 计算pp(ranked or unranked)
async def calculate_pp_if_all(beatmap_id, mods, acc, combo, Temp=True):

    result = {}

    await fetch_beatmap_file_async_one(beatmap_id, Temp=Temp)

    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'

    map = rosu.Beatmap(path=str(file_path))

    perf = rosu.Performance(mods=mods)

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
