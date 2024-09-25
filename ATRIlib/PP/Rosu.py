import rosu_pp_py as rosu
from pathlib import Path

from ATRIlib.TOOLS.Download import fetch_beatmap_file_async_one
from ATRIlib.TOOLS.Download import beatmaps_path,beatmaps_path_tmp

# beatmaps_path = Path('./data/beatmaps/')
# beatmaps_path_tmp = Path('./data/beatmaps_tmp/')

# 计算pp(ranked or unranked)
async def calculate_pp_if_all(beatmap_id, mods, acc, combo, Temp=True):

    mods_int = calculate_mod_int(mods)

    result = {}

    await fetch_beatmap_file_async_one(beatmap_id, Temp=Temp)

    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'

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
def calculate_mod_int(modlists):
    Mods_Value={
        'NF': 1,
        'EZ': 2,
        'TD': 4,
        'HD': 8,
        'HR': 16,
        'SD': 32,
        'DT': 64,
        'RX': 128,
        'HT': 256,
        'NC': 512,
        'FL': 1024,
        'AT': 2048,
        'SO': 4096,
        'AP': 8192,
        'PF': 16384,
        '4K': 32768,
        '5K': 65536,
        '6K': 131072,
        '7K': 262144,
        '8K': 524288,
        'FI': 1048576,
        'RD': 2097152,
        'CM': 4194304,
        'TG': 8388608,
        '9K': 16777216,
        'CO': 33554432,
        '1K': 67108864,
        '3K': 134217728,
        '2K': 268435456,
        'V2': 536870912,
        'MR': 1073741824
    }
    mods_int = 0
    for i in modlists:
        mods_int += Mods_Value[i]
    return mods_int
