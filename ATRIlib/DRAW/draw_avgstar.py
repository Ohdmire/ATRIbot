import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns
from io import BytesIO
mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"]
mpl.rcParams["axes.unicode_minus"] = False  # 设置正常显示符号


def plot_star_pp_density(data,user_pp,pp_range):
    stars = [d['star'] for d in data]
    pps = [d['pp'] for d in data]

    # 计算PP的最小和最大值
    min_pp = min(pps)
    max_pp = max(pps)
    min_star = min(stars)
    max_star = max(stars)

    total = len(pps)  # 总数据点数量

    # 创建双轴图形
    fig, ax1 = plt.subplots(figsize=(14, 8), dpi=120)
    ax2 = ax1.twinx()  # 共享x轴的第二个y轴

    # 1. 主图：KDE密度图
    sns.kdeplot(
        x=pps,
        ax=ax1,
        color='royalblue',
        fill=True,
        alpha=0.3,
        linewidth=2,
        label=f'PP分布密度 (N={total})',
    )

    #2. 标题
    if min_star == max_star:
        plt.suptitle(f'{max_star}* 难度PP分布图')
    else:
        plt.suptitle(f'{min_star}* - {max_star}* 难度PP分布图')

    plt.title(f"玩家总PP范围: {user_pp:.0f}±{pp_range}PP")

    # 3. 标注关键统计量
    median_pp = np.median(pps)
    ax1.axvline(median_pp, color='green', linestyle='-.', label=f'中位数: {median_pp:.0f}pp')

    # 4. 添加分位数区域
    q25, q75 = np.percentile(pps, [25, 75])
    ax1.axvspan(q25, q75, color='gray', alpha=0.1, label='25%~75%的数据')

    # 添加分位数标注
    ax1.text(q25, ax1.get_ylim()[1] * 0.95, f'{q25:.0f}',
             ha='center', va='top', color='gray', fontsize=10)
    ax1.text(q75, ax1.get_ylim()[1] * 0.95, f'{q75:.0f}',
             ha='center', va='top', color='gray', fontsize=10)

    # 设置x轴范围为PP的最小和最大值
    ax1.set_xlim(min_pp, max_pp)

    # 添加5%的边距使图形更美观
    pp_range = max_pp - min_pp
    ax1.set_xlim(min_pp - 0.05 * pp_range, max_pp + 0.05 * pp_range)

    # 美化图形
    ax1.set_xlabel('PP', fontsize=14)
    ax1.set_ylabel('分布密度', fontsize=14)
    ax2.set_ylabel('数据点分布', fontsize=14)

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.grid(alpha=0.1)

    # 返回图像
    img_bytes = BytesIO()
    plt.savefig(img_bytes, bbox_inches='tight', dpi=300)
    plt.close()

    img_bytes.seek(0)
    return img_bytes