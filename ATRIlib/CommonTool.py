

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


def color_to_hex(color0, color1, s, gamma):
    result = hex(int(min(max(round(pow((1 - s) * pow(color0, gamma) +
                 s * pow(color1, gamma), 1 / gamma)), 0), 255)))[2:]
    if len(result) == 1:
        return "0" + result
    else:
        return result
