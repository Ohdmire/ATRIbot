import cProfile
import rosu_pp_py as rosu
from pathlib import Path

beatmaps_path = Path('./data/beatmaps/')


def calculate_pp_if_fc(beatmap_id, mods, acc):

    file_path = beatmaps_path / f'{beatmap_id}.osu'

    # either `path`, `bytes`, or `content` must be specified when parsing a map
    map = rosu.Beatmap(path=str(file_path))

    perf = rosu.Performance(mods=mods)

    perf.set_accuracy(acc)
    perf.set_combo(None)

    attrs = perf.calculate(map)

    print(attrs)

    return attrs.pp

# b=calculate_pp_if_fc(490154,8+64,98.)
# print(b)


cProfile.run('calculate_pp_if_fc(490154,8+64,98)')
