import rosu_pp_py as rosu
from rosu_pp_py.rosu_pp_py import GameMode

from ATRIlib.TOOLS.Download import fetch_beatmap_file_async_one

from ATRIlib.Config import path_config

beatmaps_path = path_config.beatmaps_path
beatmaps_path_tmp = path_config.beatmaps_path_tmp

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

# 计算pp(ranked or unranked)
async def calculate_pp_if_all_stable(beatmap_id, mods, acc, combo, judge_statistic,Temp=True):

    result = {}

    await fetch_beatmap_file_async_one(beatmap_id, Temp=Temp)

    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'

    map = rosu.Beatmap(path=str(file_path))

    perf = rosu.Performance(mods=mods,lazer=False)

    perf.set_n300(judge_statistic['great'])
    perf.set_n100(judge_statistic['ok'])
    perf.set_n50(judge_statistic['meh'])
    perf.set_misses(judge_statistic['miss'])
    perf.set_combo(combo)
    perf.set_accuracy(acc)
    attrs = perf.calculate(map)
    result['pp'] = attrs.pp

    perf.set_combo(None)
    perf.set_misses(0)
    attrs = perf.calculate(map)
    result['fcpp'] = attrs.pp

    perf.set_accuracy(100)
    perf.set_n300(None)
    perf.set_n100(None)
    perf.set_n50(None)
    attrs = perf.calculate(map)
    result['100fcpp'] = attrs.pp

    return result

# 计算map在mod影响后bpm ar cs od hp等数值
async def calculate_map_attrs(beatmap_id, mods,Temp=True):

    await fetch_beatmap_file_async_one(beatmap_id, Temp=Temp)

    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'

    map = rosu.Beatmap(path=str(file_path))

    build_diff = rosu.BeatmapAttributesBuilder()

    build_diff.set_map(map)
    build_diff.set_mods(mods)

    result = build_diff.build()

    perf = rosu.Performance(mods=mods,lazer=False)

    attrs = perf.calculate(map)

    stars = attrs.difficulty.stars

    max_combo_map = attrs.difficulty.max_combo


    return {'ar':result.ar,
            'od':result.od,
            'hp':result.hp,
            'cs':result.cs,
            'stars':stars,
            'max_combo_map':max_combo_map,
            }