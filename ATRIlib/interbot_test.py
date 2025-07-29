import aiohttp
import math
from ATRIlib.Manager.UserManager import get_bp_score_struct

# async def get_interbot_test1(osuname):
#     data = {"osuname": osuname}
#     async with aiohttp.ClientSession() as session:
#         async with session.post('https://interbot.cn/osubot/test', data=data) as response:
#             result_text = await response.text()
#             if 'HTML' in result_text:
#                 raise ValueError("interbot请求错误")
#             else:
#                 return result_text


# async def get_interbot_test2(osuname):
#     data = {"osuname": osuname}
#     async with aiohttp.ClientSession() as session:
#         async with session.post('https://interbot.cn/osubot/pptest', data=data) as response:
#             result_text = await response.text()
#             if 'HTML' in result_text:
#                 raise ValueError("interbot请求错误")
#             else:
#                 return result_text
            
# async def get_interbot_skill(osuname):
#     data = {"osuname": osuname}
#     async with aiohttp.ClientSession() as session:
#         async with session.post('https://interbot.cn/osubot/skill', data=data) as response:
#             result_text = await response.text()
#             if 'HTML' in result_text:
#                 raise ValueError("interbot请求错误")
#             else:
#                 return result_text

def health_check(user, bp):
    pp = float(user['statistics']['pp'])
    pc = int(user['statistics']['play_count'])
    tth = int(user['statistics']['count_300']) + int(user['statistics']['count_100']) + int(user['statistics']['count_50'])
    bp1 = float(bp["bps_pp"][0])
    bp5 = float(bp["bps_pp"][4])
    acc_list = []
    for i in range(5):
        score_struct = get_bp_score_struct(user['id'],i)
        c50 = float(score_struct["statistics"]['meh'])
        c100 = float(score_struct["statistics"]['ok'])
        c300 = float(score_struct["statistics"]['great'])
        cmiss = float(score_struct["statistics"]['miss'])
        acc = round((c50 * 50 + c100 * 100 + c300 * 300) / (c50 + c100 + c300 + cmiss) / 300, 2)
        acc_list.append(acc)
    acc_list = sorted(acc_list, reverse=True)
    acc1 = acc_list[0]
    acc2 = acc_list[1]
    acc3 = acc_list[2]
    # print(pp,pc,tth,bp1,bp5,acc1,acc2,acc3)
    v = pp * pc * tth * bp1 * bp5 * acc1 * acc2 * acc3
    if v == 0:
        return "%s 数据不正常" % user['username']
    else:
        A1 = pp / (4 * bp1 - 3 * bp5)
        A2 = math.log(tth / pc) / math.log(15.5)
        if pp < 1000:
            A31 = 1000 * pc / (1.2 * pp) - 400
        elif pp < 7000:
            A31 = 1000 * pc / (0.0008 * pp * pp + 0.4 * pp) - 400
        else:
            A31 = 1000 * pc / (6 * pp) - 400
        if A31 > 1:
            A3 = math.log(A31) / math.log(24.5)
        else:
            A3 = 0
        A4 = math.pow((acc1 + acc2 + acc3) / 3, 5)
        total = A1 * A2 * A3 * A4

        if pp < 300:
            level = "该号pp较低，不作出评价"
        elif total >= 55:
            level = "该号成绩卓越，同分段中的老登!"
        elif total >= 44:
            level = "该号成绩优秀，标准的正常玩家!"
        elif A3 < 1 or A1 < 3:
            level = "基本断定是小号或者离线党!"
        elif A3 < 1.7:
            if A1 < 9:
                level = "要么天赋超群，要么小号或者离线党,总之这个pp严重虚低!"
            else:
                if A4 < 0.75:
                    level = "虽然天赋超群,但是求你别糊图了!"
                elif A4 < 0.88:
                    level = "虽然天赋超群，但是建议花些pc好好练习一下acc吧!"
                elif A2 < 1.7:
                    level = "是一个有天赋的超级pp刷子,求求你不要re了!"
                elif A2 < 1.9:
                    level = "是一个有天赋的高级pp刷子,建议降低re图次数!"
                else:
                    level = "是一个有天赋又认真的pp刷子,建议多打点综合图!"


        elif A3 < 1.9:
            if A1 < 9 and A4 > 0.75:
                level = "有一定天赋，将来一定时间内还是可以飞升一波的!"
            if A1 < 11 and A4 > 0.75:
                level = "有一定天赋，将来一定时间内还是可以小幅涨一点的!"
            else:
                if A4 < 0.75:
                    level = "虽然有一些天赋,但是求你别糊图了!"
                elif A4 < 0.88:
                    level = "虽然有一些天赋，但是建议花些pc好好练习一下acc吧!"
                elif A2 < 1.7:
                    level = "是一个标准pp刷子,求求你不要re了!"
                elif A2 < 1.9:
                    level = "是一个标准pp刷子,建议降低re图次数!"
                elif A2 < 2.1:
                    level = "是一个标准pp刷子,建议多打点综合图!"
                else:
                    level = "这种情况比较罕见，你应该和各种类型的人都不一样!"


        elif A3 < 2.1:
            if A1 < 9 and A4 > 0.75:
                level = "看样子正渡过瓶颈期了，将来一定时间内还是可以飞升一波的!"
            if A1 < 11 and A4 > 0.75:
                level = "要么即将渡过瓶颈期，要么之前飞太快即将进入瓶颈期!"
            else:
                if A4 < 0.75:
                    level = "你啥都不错,但是求你别糊图了!"
                elif A4 < 0.88:
                    level = "比较正常，但是建议好好练习一下acc吧!"
                elif A2 < 1.7:
                    level = "是一个没天赋的pp刷子,求求你不要re了!"
                elif A2 < 1.9:
                    level = "是一个没天赋的pp刷子,建议降低re图次数!"
                else:
                    level = "比较正常，但是可能某些方面有所欠缺，请参考指标!"


        elif A3 < 2.4:
            if A1 < 9 and A4 > 0.75:
                level = "相信自己，你正在飞升!"
            if A1 < 11 and A4 > 0.75:
                level = "也许在瓶颈期附近，但是相信你能克服它!"
            else:
                if A4 < 0.75:
                    level = "你真的很强,但是求你别糊图了!"
                elif A4 < 0.88:
                    level = "你真的很强，但是建议好好练习一下acc吧!"
                elif A2 < 1.7:
                    level = "是一个没救了的pp刷子,求求你不要re了!"
                elif A2 < 1.9:
                    level = "是一个没救了的pp刷子,建议降低re图次数!"
                else:
                    level = "这孩子瓶颈了!"

        else:
            if A1 < 10 and A4 > 0.75:
                level = "打图经验充足，不飞升没理由!"
            else:
                if A2 < 1.8:
                    level = "你这么个re图毫无用处，好好考虑下吧!"
                else:
                    level = "你不适合屙屎，删游戏吧!"

        msg = '%s\nBP指标:%.2f 参考值12.00\nTTH指标:%.2f 参考值2.00\nPC指标:%.2f 参考值2.00\nACC指标:%.4f 参考值0.9000\n综合指标:%.2f\n结论:%s' % (
        user['username'], A1, A2, A3, round(A4, 4), round(total, 2), level)
        return msg

def get_acc(c300, c100, c50, cmiss):
    c300 = int(c300)
    c100 = int(c100)
    c50 = int(c50)
    cmiss = int(cmiss)

    tph = c50 * 50 + c100 * 100 + c300 * 300
    tnh = cmiss + c50 + c100 + c300
    acc = tph / tnh / 3
    return round(acc, 2)

def func_pp2(acc, bpacc, bppp, pc, tth):
    w = [0.22483119, -0.1217108, 0.82082623, 0.0294727, 0.06772371]
    b = [4.95929298e-09]
    pp_m = 2218.589021413463
    pp_s = 1567.8553119973133
    acc_m = 95.69755708902649
    acc_s = 3.014845506352131
    bpacc_m = 961.4064515140441
    bpacc_s = 38.812586876313496
    bppp_m = 1177.9167271984384
    bppp_s = 808.798796955419
    pc_m = 15030.912107867616
    pc_s = 17940.253798480247
    tth_m = 2756676.6760339583
    tth_s = 3498224.778143693
    acc_c = (acc - acc_m) / acc_s * (w[0])
    bpacc_c = (bpacc - bpacc_m) / (bpacc_s) * (w[1])
    bppp_c = (bppp - bppp_m) / bppp_s * (w[2])
    pc_c = (pc - pc_m) / pc_s * (w[3])
    tth_c = (tth - tth_m) / tth_s * (w[4]) + (b[0])
    pp = acc_c + bpacc_c + bppp_c + pc_c + tth_c
    res = [pp, acc_c, bpacc_c, bppp_c, pc_c, tth_c]
    res2 = [round(r * pp_s + pp_m, 1) for r in res]
    return res + res2

def check2(user):

    acc = float(user["statistics"]['hit_accuracy'])
    pc = float(user["statistics"]['play_count'])
    tth = float(int(user["statistics"]['count_300']) + int(user["statistics"]['count_100']) + int(user["statistics"]['count_50']))
    bpacc = bppp = 0
    for i in range(10):
        score_struct = get_bp_score_struct(user['id'], i)
        bppp += float(score_struct['pp'])
        bpacc += float(get_acc(score_struct["statistics"]['great'], score_struct["statistics"]['ok'], score_struct["statistics"]['meh'], score_struct["statistics"]['miss']))
    newpp_w, acc_w, bpacc_w, bppp_w, pc_w, tth_w, newpp, acc_c, bpacc_c, bppp_c, pc_c, tth_c = func_pp2(acc, bpacc, bppp, pc, tth)
    print(acc, bpacc, bppp, pc, tth)
    print(acc_w, bpacc_w, bppp_w, pc_w, tth_w)
    print(acc_c, bpacc_c, bppp_c, pc_c, tth_c)
    ret = "%s\n实际pp:%spp\n预测水平:%spp\n" % (user["username"], round(float(user["statistics"]['pp']),0), newpp)
    ret += f"acc:{acc:.1f}   指标值:{acc_c:.0f} (权重:{acc_w:.3f})\n"
    ret += f"pc:{pc:,.0f}   指标值:{pc_c:.0f} (权重:{pc_w:.3f})\n"
    ret += f"tth:{tth:,.0f}   指标值:{tth_c:.0f} (权重:{tth_w:.3f})\n"
    ret += f"bp10(acc):{bpacc/10:.1f}   指标值:{bpacc_c:.0f} (权重:{bpacc_w:.3f})\n"
    ret += f"bp10(pp):{bppp/10:.1f}   指标值:{bppp_c:.0f} (权重:{bppp_w:.3f})"
    return ret