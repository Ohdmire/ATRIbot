import operator
import base64
from pathlib import Path

def calc_diff_color(star):
    bottom, top = None, None
    r0, r1, g0, g1, b0, b1 = None, None, None, None, None, None
    if star < 0.1:
        return "AAAAAA"
    elif star < 1.25:
        r0, g0, b0 = 66, 144, 251
        r1, g1, b1 = 79, 192, 255
        bottom, top = 0.1, 1.25
    elif star < 2:
        r0, g0, b0 = 79, 192, 255
        r1, g1, b1 = 79, 255, 213
        bottom, top = 1.25, 2
    elif star < 2.5:
        r0, g0, b0 = 79, 255, 213
        r1, g1, b1 = 124, 255, 79
        bottom, top = 2, 2.5
    elif star < 3.3:
        r0, g0, b0 = 124, 255, 79
        r1, g1, b1 = 246, 240, 92
        bottom, top = 2.5, 3.3
    elif star < 4.2:
        r0, g0, b0 = 246, 240, 92
        r1, g1, b1 = 255, 128, 104
        bottom, top = 3.3, 4.2
    elif star < 4.9:
        r0, g0, b0 = 255, 128, 104
        r1, g1, b1 = 255, 78, 111
        bottom, top = 4.2, 4.9
    elif star < 5.8:
        r0, g0, b0 = 255, 78, 111
        r1, g1, b1 = 198, 69, 184
        bottom, top = 4.9, 5.8
    elif star < 6.7:
        r0, g0, b0 = 198, 69, 184
        r1, g1, b1 = 101, 99, 222
        bottom, top = 5.8, 6.7
    elif star < 7.7:
        r0, g0, b0 = 101, 99, 222
        r1, g1, b1 = 24, 21, 142
        bottom, top = 6.7, 7.7
    elif star < 9:
        r0, g0, b0 = 24, 21, 142
        r1, g1, b1 = 0, 0, 0
        bottom, top = 7.7, 9
    else:
        return "000000"
    s = (star - bottom) / (top - bottom)
    r_hex = color_to_hex(r0, r1, s, 0.9)
    g_hex = color_to_hex(g0, g1, s, 0.9)
    b_hex = color_to_hex(b0, b1, s, 0.9)
    return r_hex + g_hex + b_hex


# 功能模块-排序
def sort_by_firstvalue(list_of_dicts):
    sorted_list = sorted(list_of_dicts, key=lambda x: list(x.values())[0])
    return sorted_list


def sorted_by_firstvalue_reverse(list_of_dicts):
    sorted_list = sorted(list_of_dicts, key=lambda x: list(
        x.values())[0], reverse=True)
    return sorted_list


def sort_by_firstkey(list_of_dicts):
    sorted_list = sorted(list_of_dicts, key=lambda x: list(x.keys())[0])
    return sorted_list


def sort_dict_by_value_reverse(mydict):
    sorted_dict = dict(sorted(mydict.items(), reverse=True,key=operator.itemgetter(1)))
    return sorted_dict

def sort_dict_by_value(mydict):
    sorted_dict = dict(sorted(mydict.items(), key=operator.itemgetter(1)))
    return sorted_dict


def sort_by_givenkey_reverse(list_of_dicts, key):
    sorted_list = sorted(list_of_dicts, key=lambda x: x[key], reverse=True)
    return sorted_list


def color_to_hex(color0, color1, s, gamma):
    result = hex(int(min(max(round(pow((1 - s) * pow(color0, gamma) +
                 s * pow(color1, gamma), 1 / gamma)), 0), 255)))[2:]
    if len(result) == 1:
        return "0" + result
    else:
        return result

def get_base64_encoded_data(content, mime_type):
    """
    将内容转换为base64编码的字符串
    """
    encoded_string = base64.b64encode(content).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"


def get_relative_path(target_path: str, parent_level: int) -> Path:
    """
    根据目录和父级层级生成相对路径

    Args:
        target_path (str): 目标Path
        parent_level (int): 需要返回几层父目录

    Returns:
        Path: 生成的路径，如 "../../../assets/grade"

    """
    parent_prefix = "../" * parent_level
    return Path(f"{parent_prefix}{target_path}")

def mods_to_str(mods_list):

    mods_str = ", ".join(mod["acronym"] for mod in mods_list)
    reversed_mods = ", ".join(reversed(mods_str.split(", ")))
    return reversed_mods

def mod_list_to_newlist(mods_list):
    new_mod_list = []
    for mod in mods_list:
        new_mod_list.append({"acronym" : mod})
    return new_mod_list


def calculate_rank_for_stable(count_300, count_100, count_50, count_miss):
    """
    根据游戏成绩计算Rank

    参数:
    count_300 (int): 300分的数量
    count_100 (int): 100分的数量
    count_50 (int): 50分的数量
    count_miss (int): Miss的数量

    返回:
    str: 对应的Rank (SS, S, A, B, C, D)
    """
    total_hits = count_300 + count_100 + count_50 + count_miss

    if total_hits == 0:
        return "D"

    accuracy = count_300 / total_hits
    percent_300 = count_300 / total_hits * 100
    percent_50 = count_50 / total_hits * 100 if total_hits > 0 else 0

    # SS: 100% accuracy
    if count_300 == total_hits:
        return "SS"

    # S: Over 90% 300s, at most 1% 50s, and no misses
    if (percent_300 > 90 and
            percent_50 <= 1 and
            count_miss == 0):
        return "S"

    # A: Over 80% 300s and no misses OR over 90% 300s
    if ((percent_300 > 80 and count_miss == 0) or
            percent_300 > 90):
        return "A"

    # B: Over 70% 300s and no misses OR over 80% 300s
    if ((percent_300 > 70 and count_miss == 0) or
            percent_300 > 80):
        return "B"

    # C: Over 60% 300s
    if percent_300 > 60:
        return "C"

    # D: Anything else
    return "D"