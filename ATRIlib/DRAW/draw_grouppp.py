from io import BytesIO

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"]
mpl.rcParams["axes.unicode_minus"] = False  # 设置正常显示符号


def _median_gap_text(user_pp, median_pp):
    gap = user_pp - median_pp
    if round(gap) == 0:
        return "与中位数持平"
    if gap > 0:
        return f"比中位数高 {gap:.0f}pp"
    return f"比中位数低 {abs(gap):.0f}pp"


def draw_grouppp(players, user_id, median_pp):

    # 与文字版保持一致的排序：PP降序，PP相同时按user_id升序
    players = sorted(players, key=lambda player: (-player["pp"], player["user_id"]))
    total = len(players)

    ranks = list(range(1, total + 1))
    pps = [player["pp"] for player in players]

    user_rank = next(
        index + 1
        for index, player in enumerate(players)
        if player["user_id"] == user_id
    )
    user_pp = players[user_rank - 1]["pp"]

    fig, ax = plt.subplots(figsize=(14, 8), dpi=120)
    fig.patch.set_facecolor("white")

    # 所有群友
    ax.scatter(
        ranks,
        pps,
        s=42,
        color="#4C72B0",
        alpha=0.75,
        edgecolors="white",
        linewidths=0.7,
        zorder=3,
        label=f"群友（{total}人）",
    )

    # 中位数
    ax.axhline(
        median_pp,
        color="#2CA02C",
        linestyle="--",
        linewidth=2.2,
        zorder=2,
        label=f"中位数 {median_pp:.0f}pp",
    )

    # 查询者位置
    ax.scatter(
        [user_rank],
        [user_pp],
        s=320,
        color="#D62728",
        marker="*",
        edgecolors="white",
        linewidths=1.2,
        zorder=5,
        label="你在这里",
    )

    # 标注框放在曲线外侧的空区域，避免遮住其他群友
    if user_rank <= total / 2:
        if user_rank <= 2:
            xytext = (18, -46)  # 右下
            ha, va = "left", "top"
        else:
            xytext = (-18, -46)  # 左下
            ha, va = "right", "top"
    else:
        if user_rank >= total - 1:
            xytext = (-18, 42)  # 左上
            ha, va = "right", "bottom"
        else:
            xytext = (18, 42)  # 右上
            ha, va = "left", "bottom"

    ax.annotate(
        f"你在这里\n#{user_rank} / {total}  {user_pp:.0f}pp\n"
        f"{_median_gap_text(user_pp, median_pp)}",
        xy=(user_rank, user_pp),
        xytext=xytext,
        textcoords="offset points",
        ha=ha,
        va=va,
        fontsize=13,
        color="#D62728",
        fontweight="bold",
        multialignment="center",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#D62728", alpha=0.92),
        arrowprops=dict(
            arrowstyle="->", color="#D62728", lw=1.6, shrinkA=0, shrinkB=6
        ),
        zorder=6,
    )

    ax.set_title(
        f"本群PP排行（共{total}人）", fontsize=22, fontweight="bold", pad=16
    )

    ax.set_xlabel("排名", fontsize=14)
    ax.set_ylabel("PP", fontsize=14)
    tick_step = max((total + 7) // 8, 1)
    ax.set_xticks(sorted({1, total, *range(tick_step, total + 1, tick_step)}))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    ax.set_xlim(0.4, total + 0.6)

    min_pp, max_pp = min(pps), max(pps)
    padding = max((max_pp - min_pp) * 0.12, max_pp * 0.04, 10)
    ax.set_ylim(max(min_pp - padding, 0), max_pp + padding)

    ax.grid(alpha=0.15, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=11)

    ax.legend(loc="upper right", fontsize=12, framealpha=0.9)

    fig.tight_layout()

    img_bytes = BytesIO()
    fig.savefig(
        img_bytes, bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor()
    )
    plt.close(fig)

    img_bytes.seek(0)
    return img_bytes
