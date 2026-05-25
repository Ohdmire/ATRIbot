from io import BytesIO

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"]
mpl.rcParams["axes.unicode_minus"] = False


def _boxes_overlap(left, right):
    return not (
        left[2] < right[0]
        or left[0] > right[2]
        or left[3] < right[1]
        or left[1] > right[3]
    )


def _label_box(x, y, text, x_span, y_span):
    max_line_len = max(len(line) for line in text.splitlines())
    width = max(0.08 * x_span, max_line_len * 0.012 * x_span)
    height = max(0.055 * y_span, 0.05 * y_span * len(text.splitlines()))
    return (x, y, x + width, y + height)


def _label_position(x, y, text, placed_boxes, x_span, y_span):
    offsets = [
        (0.014, 0.014),
        (0.014, -0.075),
        (-0.19, 0.014),
        (-0.19, -0.075),
        (0.055, 0.07),
        (-0.24, 0.07),
        (0.055, -0.13),
        (-0.24, -0.13),
    ]
    for ring in range(6):
        for dx_ratio, dy_ratio in offsets:
            label_x = x + (dx_ratio + ring * 0.035 * np.sign(dx_ratio)) * x_span
            label_y = y + (dy_ratio + ring * 0.026 * np.sign(dy_ratio)) * y_span
            box = _label_box(label_x, label_y, text, x_span, y_span)
            if not any(_boxes_overlap(box, placed) for placed in placed_boxes):
                placed_boxes.append(box)
                return label_x, label_y
    placed_boxes.append(_label_box(x, y, text, x_span, y_span))
    return x, y


def draw_replay_similarity_distance(data):
    comparisons = data["comparisons"]
    if not comparisons:
        raise ValueError("没有可绘制的 replay 相似度数据")

    top = comparisons[:30]
    similarities = np.array([item["similarity"] for item in top], dtype=float)
    xs = np.array([item["x"] for item in top], dtype=float)
    ys = np.array([item["y"] for item in top], dtype=float)
    max_extent = max(
        float(np.max(np.abs(xs))) if len(xs) else 0.0,
        float(np.max(np.abs(ys))) if len(ys) else 0.0,
        0.05,
    )
    x_span = max_extent * 2.9
    y_span = max_extent * 2.9

    fig, ax = plt.subplots(figsize=(12, 12), dpi=160)
    fig.patch.set_facecolor("#f7f8fb")
    ax.set_facecolor("#ffffff")

    colors = np.where(similarities >= data["threshold"] * 100.0, "#d64f6f", "#2d7dd2")
    ax.axhline(0, color="#d0d7de", linewidth=1.0, zorder=0)
    ax.axvline(0, color="#d0d7de", linewidth=1.0, zorder=0)
    ax.scatter(
        [0],
        [0],
        s=180,
        c="#111827",
        marker="*",
        zorder=4,
        label=data["base"]["username"],
    )
    ax.scatter(
        xs,
        ys,
        s=88,
        c=colors,
        edgecolors="#1f2933",
        linewidths=0.7,
        alpha=0.92,
        zorder=3,
    )

    placed_boxes = []
    for item, x, y, similarity in zip(top, xs, ys, similarities):
        label = f"{item['player']['username']}\n{similarity:.1f}%"
        label_x, label_y = _label_position(x, y, label, placed_boxes, x_span, y_span)
        if abs(label_x - x) > x_span * 0.02 or abs(label_y - y) > y_span * 0.02:
            ax.plot(
                [x, label_x],
                [y, label_y],
                color="#9aa6b2",
                linewidth=0.6,
                alpha=0.75,
                zorder=2,
            )
        ax.text(
            label_x,
            label_y,
            label,
            va="bottom",
            ha="left",
            fontsize=9,
            color="#26313d",
            bbox={
                "boxstyle": "round,pad=0.18",
                "facecolor": "#ffffff",
                "edgecolor": "#d0d7de",
                "alpha": 0.86,
            },
            zorder=5,
        )
    ax.text(
        0,
        0,
        f" {data['base']['username']}",
        va="top",
        ha="left",
        fontsize=12,
        color="#111827",
    )

    ax.set_xlabel("Embedding PCA X relative to player", fontsize=12)
    ax.set_ylabel("Embedding PCA Y relative to player", fontsize=12)
    ax.set_title(
        f"{data['base']['username']} 的本群 replay 二维距离图 (越近越相似)",
        fontsize=18,
        pad=16,
        color="#1f2933",
    )
    # ax.text(
    #     0,
    #     1.015,
    #     f"展示最近的 {len(top)}/{len(comparisons)} 人，跳过 {len(data['skipped'])} 人；X/Y 为模型 embedding 相对坐标的二维投影",
    #     transform=ax.transAxes,
    #     fontsize=11,
    #     color="#667085",
    # )

    ax.grid(color="#e5e9f0", linestyle="-", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d0d7de")
    ax.spines["bottom"].set_color("#d0d7de")
    ax.set_xlim(-max_extent * 1.45, max_extent * 1.45)
    ax.set_ylim(-max_extent * 1.45, max_extent * 1.45)
    ax.set_aspect("equal", adjustable="box")

    img_bytes = BytesIO()
    plt.savefig(
        img_bytes, bbox_inches="tight", format="jpeg", facecolor=fig.get_facecolor()
    )
    plt.close(fig)
    img_bytes.seek(0)
    return img_bytes
