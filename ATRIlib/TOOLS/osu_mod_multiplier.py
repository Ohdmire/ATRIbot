#!/usr/bin/env python3
"""osu!standard lazer mod score multiplier calculator.

The default multipliers and combination rules mirror the local osu! source:
osu.Game.Rulesets.Osu/Scoring/OsuScoreMultiplierCalculatorV2.cs
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable


DEFAULT_MULTIPLIERS: dict[str, float] = {
    # Difficulty reduction
    "EZ": 0.8,
    "NF": 0.5,
    "HT": 0.55,
    "DC": 0.55,
    # Difficulty increase
    "HR": 1.09,
    "SD": 1.0,
    "PF": 1.0,
    "DT": 1.23,
    "NC": 1.23,
    "HD": 1.04,
    "TC": 1.02,
    "FL": 1.2,
    "BL": 1.24,
    "ST": 1.0,
    "AC": 1.0,
    # Conversion
    "TP": 0.01,
    "DA": 1.0,
    "CL": 0.985,
    "RD": 0.7,
    "MR": 1.0,
    "AL": 1.0,
    "SG": 1.0,
    # Automation
    "AT": 1.0,
    "CN": 1.0,
    "RX": 0.1,
    "AP": 0.1,
    "SO": 0.95,
    # Fun
    "TR": 1.0,
    "WG": 1.0,
    "SI": 1.0,
    "GR": 1.0,
    "DF": 1.0,
    "WU": 1.046,
    "WD": 0.64,
    "BR": 1.0,
    "AD": 0.7,
    "MU": 1.0,
    "NS": 1.0,
    "MG": 0.4,
    "RP": 1.0,
    "AS": 0.1,
    "FR": 1.0,
    "BU": 1.0,
    "SY": 0.99,
    "DP": 1.0,
    "BM": 1.0,
    # System
    "TD": 1.0,
    "SV2": 1.0,
}

ACRONYMS = tuple(sorted(DEFAULT_MULTIPLIERS, key=len, reverse=True))

ALIASES: dict[str, tuple[str, ...]] = {
    "NOMOD": (),
    "NM": (),
    "NONE": (),
}

CONFLICT_GROUPS: tuple[set[str], ...] = (
    {"EZ", "HR"},
    {"HT", "DC", "DT", "NC", "WU", "WD"},
    {"SD", "PF"},
    {"HD", "TC"},
    {"FL", "BL"},
    {"AL", "SG"},
    {"AT", "CN"},
    {"GR", "DF"},
    {"MG", "RP"},
)


def parse_mods(raw: str) -> list[str]:
    cleaned = raw.upper().replace("+", " ").replace(",", " ")
    parts = re.findall(r"[A-Z0-9]+", cleaned)

    mods: list[str] = []
    for part in parts:
        if part in ALIASES:
            mods.extend(ALIASES[part])
            continue

        if part in DEFAULT_MULTIPLIERS:
            mods.append(part)
            continue

        index = 0
        while index < len(part):
            matched = next(
                (acronym for acronym in ACRONYMS if part.startswith(acronym, index)),
                None,
            )
            if matched is None:
                raise ValueError(f"未知模组: {part[index:]}")
            mods.append(matched)
            index += len(matched)

    result: list[str] = []
    for mod in mods:
        if mod not in result:
            result.append(mod)
    return result


def validate_mods(mods: list[str]) -> None:
    for group in CONFLICT_GROUPS:
        selected = group.intersection(mods)
        if len(selected) > 1:
            names = ", ".join(sorted(selected))
            raise ValueError(f"冲突模组不能同时使用: {names}")


def calculate_multiplier(mods: list[str]) -> float:
    multiplier = 1.0
    remaining = set(mods)

    for combo, combo_multiplier in (
        ({"HD", "BL"}, 1.24),
        ({"HD", "WG"}, 1.02),
        ({"HD", "GR"}, 1.02),
        ({"HD", "DF"}, 1.02 * DEFAULT_MULTIPLIERS["DF"]),
        ({"HD", "RP"}, 1.02),
        ({"HD", "DP"}, 1.02),
        ({"TC", "BL"}, 1.24),
        ({"FL", "FR"}, 1.1),
    ):
        if combo <= remaining:
            multiplier *= combo_multiplier
            remaining -= combo

    for mod in mods:
        if mod in remaining:
            multiplier *= DEFAULT_MULTIPLIERS[mod]
    return multiplier


def mod_multiplier(mods: str | Iterable[str]) -> float:
    """Return the osu!standard lazer score multiplier for default mod settings."""
    parsed = parse_mods(mods if isinstance(mods, str) else " ".join(mods))
    validate_mods(parsed)
    return calculate_multiplier(parsed)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按 osu!lazer 源码计算 osu!standard 默认模组分数倍率，例如: HD DT / HDDT / +HDDT"
    )
    parser.add_argument("mods", nargs="*", help="模组缩写，例如 HD DT 或 HDDT")
    args = parser.parse_args()

    raw = " ".join(args.mods) if args.mods else input("请输入模组: ")

    try:
        multiplier = mod_multiplier(raw)
    except ValueError as exc:
        print(f"错误: {exc}")
        return 1

    print(multiplier)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
