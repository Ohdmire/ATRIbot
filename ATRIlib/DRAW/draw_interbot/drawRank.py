# coding: utf-8

import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from ATRIlib.Config import path_config
from ATRIlib.TOOLS import Download
from ATRIlib.TOOLS.CommonTools import calculate_rank_for_stable,mods_to_str

from io import BytesIO

interbot_path = Path('./assets/interbot')

default_skin = Path('New!+game!')  # 使用 os.path.join 处理路径
osu_ui = interbot_path.joinpath('osu!ui', 'Resources')
font_cn = interbot_path.joinpath('font', 'msyh.ttc')  # 微软雅黑（需确保文件存在）
font_alp = interbot_path.joinpath('font', 'Aller_Rg_MODFIED.ttf')  # Aller 字体（需确保文件存在）

cover_path = path_config.cover_path
avatar_path =path_config.avatar_path

class DrawRec():
    def __init__(self, **kw):
        self.width = kw.get('width', 1366)
        self.height = kw.get('height', 768)
        self.skin = kw.get('skin', default_skin)
        self.ui = kw.get('ui', osu_ui)
        self.RecImg = Image.new('RGBA', (self.width, self.height), 0)
        self.font_cn = kw.get('font', font_cn)
        self.font_alp = kw.get('font2', font_alp)

    def get_img(self, iname, path=None, factor=0):
        if path:
            fpath = Path(path)
        else:
            fpath = interbot_path.joinpath(self.skin,iname)
        # fpath = '%s/%s' % (self.skin, iname) if not path else path
        # 没头像的临时处理，通用方法都暂时指向default
        if not Path.exists(fpath):
            # fpath = 'image/userimg/default.jpg'
            fpath = interbot_path.joinpath('image','userimg','default.jpg')
        im = Image.open(fpath)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        if factor:
            im = self.addTransparency(im, factor)
        return im

    def draw_title_bg(self):
        im2 = Image.new('RGBA', (self.width, self.height))
        ImageDraw.Draw(im2).rectangle((0, 0, self.width, 200), fill=(0, 0, 0, 170))  # 左上右下
        self.RecImg.paste(im2, (0, 0), mask=im2)

    def draw_rectangle(self, x, y, width, height, fill=(0, 0, 0, 170)):
        im2 = Image.new('RGBA', (width, height))
        ImageDraw.Draw(im2).rectangle((0, 0, width, height), fill=fill)  # 左上右下
        self.RecImg.paste(im2, (x, y), mask=im2)

    def add_items(self, fname=None, x=0, y=0, **kwargs):
        # 默认皮肤
        itemImg = self.get_img(fname, path=kwargs.get('path', None), factor=kwargs.get('factor', 0))
        if kwargs.get('isresize', False):
            itemImg = itemImg.resize((kwargs.get('width', self.width), kwargs.get('height', self.height)))
        mask = itemImg if kwargs.get('ismask', 1) else None
        self.RecImg.paste(itemImg, (x, y), mask=mask)

    def add_items2(self, fname, x=0, y=0, **kwargs):
        # UI元素或者使用默认路径外的
        path_pref = self.ui if not kwargs.get('path', None) else kwargs['path']
        path = path_pref.joinpath(fname)
        self.add_items(x=x, y=y, path=path, **kwargs)

    def add_text(self, x, y, text, font_size=28, color='white', font_path=None, ttype='en'):
        if font_path:
            f = font_path
        else:
            f = self.font_alp if ttype == 'en' else self.font_cn
        font = ImageFont.truetype(f, font_size)
        ImageDraw.Draw(self.RecImg).text((x, y), text, font=font, fill=color)

    def addTransparency(self, img, factor=0.8):
        img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
        img = Image.blend(img_blender, img, factor)
        return img

    def save(self, name='rec.png'):
        self.RecImg.save(name)


async def drawR(mapjson, rankjson, userjson):
    # skin
    # bg_e = draw_data.check_bg(mapjson['beatmap_id'], mapjson['beatmapset_id'])
    bg_e = True
    bg = '%s.jpg' % mapjson['beatmap_id'] if bg_e else 'newgame_background.png'
    back_icon = 'menu-back-0.png'
    mod_icon = 'selection-mode.png'
    mods_icon = 'selection-mods.png'
    random_icon = 'selection-random.png'
    options_icon = 'selection-options.png'
    rank_x = 'ranking-%s-small.png'

    # ous ui
    songselecttop = 'songselect-top.png'
    uptips = 'selection-update.png'
    osu_icon = 'menu-osu.png'
    songselect_bottom = 'songselect-bottom.png'
    level_bar = 'levelbar.png'
    level_bar_bg = 'levelbar-bg.png'
    selection_approved = 'selection-approved.png'

    # 用户信息
    uname = userjson.get('username', '')
    pp = f"{float(userjson.get('pp_raw', 0)):,.0f}"
    acc = round(float(userjson.get('accuracy', 0)), 2)
    lv = float(userjson.get('level', 0))
    level = int(lv)
    lv_left = lv - level  # 小数位，经验条
    rank = userjson.get('pp_rank', 0)
    umod = 'mode-osu-small.png'

    # 曲子信息
    title = mapjson.get('title_unicode', '')
    source = mapjson.get('source', '')
    artist = mapjson.get('artist_unicode', '')
    version = mapjson.get('version', '')
    creator = mapjson.get('creator', '')
    bpm = mapjson.get('bpm', '')
    max_combo = mapjson.get('max_combo', '')
    difficultyrating = round(float(mapjson.get('difficultyrating', '')), 2)  # stars
    diff_size = mapjson.get('diff_size', '')  # CS
    diff_approach = mapjson.get('diff_approach', '')  # AR
    diff_overall = mapjson.get('diff_overall', '')  # OD
    diff_drain = mapjson.get('diff_drain', '')  # HP
    count_normal = int(mapjson.get('count_normal', 0))
    count_slider = int(mapjson.get('count_slider', 0))
    count_spinner = int(mapjson.get('count_spinner', 0))

    m, s = divmod(int(mapjson.get('total_length')), 60)
    h, m = divmod(m, 60)
    if h != 0:
        hit_length = "%02d:%02d:%02d" % (h, m, s)  # sec
    else:
        hit_length = "%02d:%02d" % (m, s)  # sec

    # 头像download
    me = userjson.get('user_id', '')

    # 下载头像批量

    me_idx = -1

    avatar_url_list = []
    user_id_list = []

    # 遍历rankjson并记录索引
    for index, r in enumerate(rankjson):
        user_id = r['user_info']['id']
        avatar_img = avatar_path / str(user_id)
        if avatar_img.exists() is False:
            avatar_url_list.append(r['user_info']['avatar_url'])
            user_id_list.append(user_id)
        # 检查是否是当前用户

        if str(user_id) == str(me):
            me_idx = index  # 记录找到的索引位置

    await Download.download_avatar_async(avatar_url_list,user_id_list)

    d = DrawRec()

    # 第一层bg

    cover_img = cover_path / f'{mapjson["beatmapset_id"]}.jpg'
    if cover_img.exists() is True:
        pass
    else:
        await Download.download_cover(
            f'https://assets.ppy.sh/beatmaps/{mapjson["beatmapset_id"]}/covers/raw.jpg',
            mapjson["beatmapset_id"])

    # d.add_items(isresize=True, path='image/bg/default.jpg')
    d.add_items(isresize=True, path=cover_img)
    # title黑层
    d.add_items2(songselecttop)
    # 更新提示
    # d.add_items2(uptips, 20, 200)
    # 低下大黑条
    d.add_items2(songselect_bottom, 0, 648, isresize=True, width=1366, height=120)
    # 大粉饼
    d.add_items2(osu_icon, 1130, 550, isresize=True, width=300, height=300)
    # 返回
    d.add_items(back_icon, 10, 615)

    # mode
    d.add_items(mod_icon, 250, 678)
    # mods选择
    d.add_items(mods_icon, 340, 678)
    # random
    d.add_items(random_icon, 430, 678)
    # options
    d.add_items(options_icon, 520, 678)

    # 我的头像
    avatar_img = avatar_path / f'{userjson['user_id']}.jpeg'
    if avatar_img.exists() is True:
        pass
    else:
        await Download.download_avatar_async([userjson['avatar_url']],
                                             [userjson['user_id']])

    # 头像
    d.add_items(x=690, y=675, path=avatar_img, isresize=True, width=90, height=90)
    # 用户信息
    d.add_items2(umod, 998, 670, factor=0.5)
    d.add_text(968, 710, '# %s' % rank, font_size=16, ttype='en')
    d.add_text(788, 670, uname, font_size=24, ttype='en')
    d.add_text(788, 700, 'Performance:%spp' % pp, font_size=16, ttype='en')
    d.add_text(788, 720, 'Accuracy:%s%%' % acc, font_size=16, ttype='en')
    d.add_text(788, 740, 'Lv:%s' % level, font_size=16, ttype='en')
    if lv_left > 0.1:
        d.add_items2(level_bar, 840, 745, isresize=True, width=int(lv_left * 200), height=14)
    d.add_items2(level_bar_bg, 840, 745)

    # 曲子信息
    bid = mapjson['beatmap_id']
    d.add_text(35, 0, '%s (%s) - %s [%s]' % (source, artist, title, version), font_size=25, ttype='cn')
    d.add_items2(selection_approved, 7, 3)
    d.add_text(40, 30, '作者: %s   [bid: %s]' % (creator, bid), font_size=16, ttype='cn')
    d.add_text(5, 50, '长度: %s  BPM: %s  物件数: %s' % (hit_length, bpm, count_normal + count_slider + count_spinner),
               font_size=18, ttype='cn')
    d.add_text(5, 75, '圈数: %s 滑条数: %s 转盘数: %s' % (count_normal, count_slider, count_spinner), font_size=16,
               ttype='cn')
    d.add_text(5, 100, 'CS:%s AR:%s OD:%s HP:%s Star:%s★' % (diff_size, diff_approach, diff_overall, diff_drain,
                                                             difficultyrating), font_size=16, ttype='en')

    bid = mapjson['beatmap_id']
    d.add_text(1180, 30, f"bid: {bid}", font_size=25, ttype='en')

    # 榜区域
    nums = len(rankjson)
    # o = botHandler.botHandler()
    # res = o.get_usernames_by_uid(uids)
    # udict = {r['osuid']: r['osuname'] for r in res}
    # 遍历第一列要显示的用户
    # 判断用户数量是否超过6个
    if nums > 6:
        r1 = 6  # 第一列显示6个用户
        r2 = nums - 6  # 剩余用户在第二列显示
    else:
        r1 = nums  # 不超过6个就全部显示在第一列
        r2 = 0  # 第二列不显示

    offset1 = 65  # 每个用户条目在垂直方向的间距

    # 遍历第一列要显示的用户
    for i in range(r1):
        # 获取当前用户的数据字典
        r = rankjson[i]
        # 从字典中提取用户ID（每个字典只有一个键值对）
        # u = uids[i]
        mds_l = [mod['acronym'] for mod in r['top_score']['mods']]
        m = mods_to_str(r['top_score']['mods'])
        # 处理评级显示，F级显示为D

        stb_rank = calculate_rank_for_stable(r['top_score']["statistics"]["great"], r['top_score']["statistics"]["ok"],
                                             r['top_score']["statistics"]["meh"], r['top_score']["statistics"]["miss"])

        has_hd_or_fl = any(m["acronym"] in {"HD", "FL"} for m in r['top_score']['mods'])

        if has_hd_or_fl:
            if stb_rank == "S":
                stb_rank = "SH"
            elif stb_rank == "SS":
                stb_rank = "XH"

        r['top_score']["rank"] = stb_rank


        rank = 'D' if stb_rank == 'F' else stb_rank
        d.draw_rectangle(x=20, y=160 + i * offset1, width=460, height=60, fill=(0, 0, 0, 50))
        avatar_img = avatar_path / f'{r['user_info']['id']}.jpeg'
        if avatar_img.exists() is True:
            pass
        else:
            await Download.download_avatar_async([r['user_info']['avatar_url']],
                                                 [r['user_info']['id']])
        d.add_items(x=20, y=160 + i * offset1, path=avatar_img, isresize=True, width=60, height=60)
        d.add_items(rank_x % rank, 80, 170 + i * offset1)
        d.add_text(120, 160 + i * offset1, '%s' % (r['user_info']['username']), font_size=25, ttype='en')
        d.add_text(120, 190 + i * offset1, '得分: %s' % (format(int(r['top_score']['legacy_total_score']), ',')), font_size=20, ttype='cn')
        d.add_text(300, 190 + i * offset1, '(%sx)' % (format(int(r['top_score']['max_combo']), ',')), font_size=20, ttype='en')
        d.add_text(450 - 20 * len(mds_l), 165 + i * offset1, '%s' % (m), font_size=20, ttype='en')
        d.add_text(400, 190 + i * offset1, '%.2f%%' % (r['top_score']['accuracy']*100), font_size=18, ttype='en')

    d.add_text(150, 550, '个人最佳成绩', font_size=24, ttype='cn')
    d.draw_rectangle(x=20, y=590, width=460, height=60, fill=(0, 0, 0, 50))
    if me_idx != -1:
        r = rankjson[me_idx]
        mds_l = [mod['acronym'] for mod in r['top_score']['mods']]
        m = mods_to_str(r['top_score']['mods'])
        stb_rank = calculate_rank_for_stable(r['top_score']["statistics"]["great"], r['top_score']["statistics"]["ok"],
                                             r['top_score']["statistics"]["meh"], r['top_score']["statistics"]["miss"])

        has_hd_or_fl = any(m["acronym"] in {"HD", "FL"} for m in r['top_score']['mods'])

        if has_hd_or_fl:
            if stb_rank == "S":
                stb_rank = "SH"
            elif stb_rank == "SS":
                stb_rank = "XH"

        r['top_score']["rank"] = stb_rank

        rank = 'D' if stb_rank == 'F' else stb_rank

        # 我的头像
        avatar_img = avatar_path / f'{r['user_info']['id']}.jpeg'
        if avatar_img.exists() is True:
            pass
        else:
            await Download.download_avatar_async([r['user_info']['avatar_url']],
                                                 [r['user_info']['id']])

        d.add_items(x=20, y=590, path=avatar_img, isresize=True, width=60, height=60)
        d.add_items(rank_x % rank, 80, 595)
        d.add_text(120, 590, '%s  #%s' % (r['user_info']['username'], me_idx + 1), font_size=25, ttype='en')
        d.add_text(120, 620, '得分: %s' % (format(int(r['top_score']['legacy_total_score']), ',')), font_size=20, ttype='cn')
        d.add_text(300, 620, '(%sx)' % (format(int(r['top_score']['max_combo']), ',')), font_size=20, ttype='en')
        d.add_text(450 - 20 * len(mds_l), 600, '%s' % (m), font_size=20, ttype='en')
        d.add_text(410, 620, '%.2f%%' % (r['top_score']['accuracy']*100), font_size=18, ttype='en')
    # elif len(bestinfo) > 0:
    #     # mds = int(bestinfo['enabled_mods'])
    #     mds_l = bestinfo['enabled_mods']
    #     if 'NONE' in mds_l:
    #         mds_l.remove('NONE')
    #     m_str = ','.join(mds_l) if len(mds_l) > 0 else ''
    #     rank = 'D' if bestinfo['rank'] == 'F' else bestinfo['rank']
    #     d.add_items(x=20, y=590, path='image/userimg/%s.jpg' % me, isresize=True, width=60, height=60)
    #     d.add_items(rank_x % rank, 80, 595)
    #     d.add_text(120, 590, f"{uname}  #50+", font_size=25, ttype='en')
    #     d.add_text(120, 620, f"得分: {int(bestinfo['score']):,}    ({int(bestinfo['maxcombo']):,}x)", font_size=20,
    #                ttype='cn')
    #     d.add_text(450 - 20 * len(mds_l), 597, '%s' % (m_str), font_size=20, ttype='en')
    #     # acc = mods.get_acc(bestinfo['count300'], bestinfo['count100'], bestinfo['count50'], bestinfo['countmiss'])
    #     acc = bestinfo['accuracy']
    #     d.add_text(410, 620, f"{acc:.2f}%", font_size=18, ttype='en')
    else:
        d.add_text(130, 600, '你倒是快刚榜啊', font_size=25, ttype='cn')

    # copy
    for i in range(r2):
        if i == 6:
            break
        oi = i + 6
        r = rankjson[oi]

        mds_l = [mod['acronym'] for mod in r['top_score']['mods']]
        m = mods_to_str(r['top_score']['mods'])
        # 处理评级显示，F级显示为D

        stb_rank = calculate_rank_for_stable(r['top_score']["statistics"]["great"], r['top_score']["statistics"]["ok"],
                                             r['top_score']["statistics"]["meh"], r['top_score']["statistics"]["miss"])

        has_hd_or_fl = any(m["acronym"] in {"HD", "FL"} for m in r['top_score']['mods'])

        if has_hd_or_fl:
            if stb_rank == "S":
                stb_rank = "SH"
            elif stb_rank == "SS":
                stb_rank = "XH"

        r['top_score']["rank"] = stb_rank

        rank = 'D' if stb_rank == 'F' else stb_rank

        avatar_img = avatar_path / f'{r['user_info']['id']}.jpeg'
        if avatar_img.exists() is True:
            pass
        else:
            await Download.download_avatar_async([r['user_info']['avatar_url']],
                                                 [r['user_info']['id']])

        d.draw_rectangle(x=620, y=160 + i * offset1, width=460, height=60, fill=(0, 0, 0, 50))
        d.add_items(x=620, y=160 + i * offset1, path=avatar_img, isresize=True, width=60, height=60)
        d.add_items(rank_x % rank, 680, 170 + i * offset1)
        d.add_text(720, 160 + i * offset1, '%s' % (r['user_info']['username']), font_size=25, ttype='en')
        d.add_text(720, 190 + i * offset1, '得分: %s' % (format(int(r['top_score']['legacy_total_score']), ',')), font_size=20, ttype='cn')
        d.add_text(900, 190 + i * offset1, '(%sx)' % (format(int(r['top_score']['max_combo']), ',')), font_size=20, ttype='en')
        d.add_text(1050 - 20 * len(mds_l), 165 + i * offset1, '%s' % (m), font_size=20, ttype='en')
        d.add_text(1010, 190 + i * offset1, '%.2f%%' % (r['top_score']['accuracy']*100), font_size=18, ttype='en')

    img_bytes = BytesIO()
    img_rgb = d.RecImg.convert('RGB')  # 强制丢弃 Alpha 通道
    img_rgb.save(img_bytes, format='JPEG')
    # d.RecImg.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes

    # d.save(f)
    # # 压缩
    # os.system('pngquant -f %s' % f)
    # logging.info('[%s]榜单生成成功!' % pfs)
    # return pfs


# def start(bid='847314', groupid='614892339', hid=1, mods=-1, uid='8505303', bestinfo={}):
#     mapjson, rankjson = draw_data.map_ranks_info(str(bid), groupid, hid, mods)
#     ppyIns = ppyHandler.ppyHandler()
#     # 历史问题导致遗漏的情况
#     if not mapjson:
#         mapsinfo = [ppyIns.getOsuBeatMapInfo(bid)]
#         map_args = score.args_format('map', mapsinfo)
#         score.map2db(map_args)
#         mapjson, rankjson = draw_data.map_ranks_info(str(bid), groupid, hid, mods)
#     userjson = ppyIns.getOsuUserInfo(uid)[0]
#     mapjson = ppyIns.getOsuBeatMapInfo(bid)[0]
#     return drawR(mapjson, rankjson, userjson, bestinfo)
