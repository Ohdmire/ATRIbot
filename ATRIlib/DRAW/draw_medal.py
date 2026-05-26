from datetime import datetime
from io import BytesIO

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def draw_special_medal(specialmedalstruct_pass, specialmedalstruct_fc, username):
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.set_title(f"{username}'s Special Medal Timeline", fontsize=24)

    dates_pass = [
        datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        for date in specialmedalstruct_pass.values()
    ]
    dates_fc = [
        datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        for date in specialmedalstruct_fc.values()
    ]

    y_values_pass = [int(name.split()[0]) for name in specialmedalstruct_pass.keys()]
    y_values_fc = [int(name.split()[0]) for name in specialmedalstruct_fc.keys()]

    ax.plot(
        dates_pass,
        y_values_pass,
        color="blue",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        label="Pass",
    )
    ax.plot(
        dates_fc,
        y_values_fc,
        color="red",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        label="FC",
    )

    ax.set_ylim(0, 11)
    ax.set_yticks(range(1, 11))
    ax.set_ylabel("Star", fontsize=12)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    for date, y, name in zip(
        dates_pass + dates_fc,
        y_values_pass + y_values_fc,
        list(specialmedalstruct_pass.keys()) + list(specialmedalstruct_fc.keys()),
    ):
        ax.annotate(
            name + "*",
            (date, y),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            alpha=0.7,
            rotation=45,
        )

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    img_bytes = BytesIO()
    plt.savefig(img_bytes, format="PNG", dpi=300, bbox_inches="tight")
    img_bytes.seek(0)
    plt.close(fig)

    return img_bytes
