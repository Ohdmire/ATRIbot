import operator
import base64

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