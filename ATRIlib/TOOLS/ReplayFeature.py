import json
import math
from pathlib import Path

import numpy as np
from slider import Beatmap, Replay
from slider.beatmap import Slider
from slider.mod import circle_radius


PLAYFIELD_WIDTH = 512.0
PLAYFIELD_HEIGHT = 384.0
EPS = 1e-6
FRAME_INTERVAL_MS = 1000.0 / 60.0
WINDOW_MS = 2000.0
STRIDE_MS = 500.0
OBJECT_CONTEXT_MS = 300.0
DOUBLE_TIME_RATE = 1.5

FRAME_FEATURE_NAMES = [
    "x_norm",
    "y_norm",
    "dx_norm",
    "dy_norm",
    "speed",
    "speed_norm",
    "acceleration",
    "acceleration_norm",
    "angle_sin",
    "angle_cos",
    "angle_change",
    "time_to_next_object_norm",
    "distance_to_next_object_norm",
    "dx_to_next_object_norm",
    "dy_to_next_object_norm",
    "required_speed_to_next",
    "is_during_slider",
    "slider_ball_error_norm",
    "slider_ball_dx_norm",
    "slider_ball_dy_norm",
    "slider_progress",
]

WINDOW_STAT_NAMES = [
    "speed_mean",
    "speed_std",
    "speed_max",
    "acceleration_std",
    "angle_change_std",
    "hard_turn_count",
    "hard_stop_count",
    "path_efficiency",
    "cursor_to_next_error_mean_norm",
    "cursor_to_next_error_std_norm",
    "slider_ball_error_mean_norm",
    "slider_ball_error_std_norm",
    "slider_follow_ratio",
    "object_count",
    "slider_count",
]


def _ms(value):
    return value.total_seconds() * 1000.0


def _safe_div(numerator, denominator, default=0.0):
    if abs(float(denominator)) < EPS:
        return default
    return numerator / denominator


def _wrapped_angle_diff(a, b):
    return (a - b + np.pi) % (2.0 * np.pi) - np.pi


def _replay_clock_rate(replay):
    if getattr(replay, "double_time", False) or getattr(replay, "nightcore", False):
        return DOUBLE_TIME_RATE
    return 1.0


def _build_replay_track(replay):
    actions = replay.actions
    if not actions:
        raise ValueError("replay contains no actions")
    times = np.array([_ms(action.offset) for action in actions], dtype=np.float64)
    xs = np.array([float(action.position.x) for action in actions], dtype=np.float64)
    ys = np.array([float(action.position.y) for action in actions], dtype=np.float64)
    keep = np.concatenate(([True], np.diff(times) > 0))
    return times[keep], xs[keep], ys[keep]


def _prepare_objects(beatmap, replay):
    hard_rock = bool(getattr(replay, "hard_rock", False))
    return sorted(beatmap.hit_objects(stacking=False, hard_rock=hard_rock), key=lambda obj: _ms(obj.time))


def _build_object_index(objects):
    start_ms = np.array([_ms(obj.time) for obj in objects], dtype=np.float64)
    end_ms = np.array([_ms(getattr(obj, "end_time", obj.time)) for obj in objects], dtype=np.float64)
    xs = np.array([float(obj.position.x) for obj in objects], dtype=np.float64)
    ys = np.array([float(obj.position.y) for obj in objects], dtype=np.float64)
    is_slider = np.array([isinstance(obj, Slider) for obj in objects], dtype=bool)
    slider_indices = np.nonzero(is_slider)[0]
    return {
        "objects": objects,
        "start_ms": start_ms,
        "end_ms": end_ms,
        "xs": xs,
        "ys": ys,
        "is_slider": is_slider,
        "slider_indices": slider_indices,
        "slider_start_ms": start_ms[slider_indices],
        "slider_end_ms": end_ms[slider_indices],
    }


def _interpolate_track(source_times, source_xs, source_ys, target_times):
    return np.interp(target_times, source_times, source_xs), np.interp(target_times, source_times, source_ys)


def _next_previous_indices(times, target_times):
    next_indices = np.searchsorted(times, target_times, side="left")
    prev_indices = next_indices - 1
    next_indices = np.clip(next_indices, 0, len(times) - 1)
    prev_indices = np.clip(prev_indices, 0, len(times) - 1)
    return next_indices, prev_indices


def _active_slider_index_at(index, time_ms):
    if len(index["slider_indices"]) == 0:
        return None
    pos = np.searchsorted(index["slider_start_ms"], time_ms, side="right") - 1
    if pos < 0:
        return None
    slider_index = int(index["slider_indices"][pos])
    if time_ms <= index["end_ms"][slider_index]:
        return slider_index
    return None


def _slider_ball_position(slider, time_ms, start_ms, end_ms):
    progress = np.clip(_safe_div(time_ms - start_ms, end_ms - start_ms), 0.0, 1.0)
    repeat_progress = progress * max(float(slider.repeat), 1.0)
    repeat_index = min(int(math.floor(repeat_progress)), max(int(slider.repeat) - 1, 0))
    local = repeat_progress - repeat_index
    if repeat_index % 2 == 1:
        local = 1.0 - local
    pos = slider.curve(float(np.clip(local, 0.0, 1.0)))
    return float(pos.x), float(pos.y), float(progress)


def _window_object_indices(index, start_ms, end_ms):
    left = start_ms - OBJECT_CONTEXT_MS
    right = end_ms + OBJECT_CONTEXT_MS
    mask = (index["start_ms"] <= right) & (index["end_ms"] >= left)
    return np.nonzero(mask)[0]


def _make_frame_features(index, times, xs, ys, radius):
    next_indices, prev_indices = _next_previous_indices(index["start_ms"], times)
    dx = np.zeros_like(xs)
    dy = np.zeros_like(ys)
    dx[1:] = np.diff(xs)
    dy[1:] = np.diff(ys)

    speed = np.hypot(dx, dy) / FRAME_INTERVAL_MS
    acceleration = np.zeros_like(speed)
    acceleration[1:] = np.diff(speed) / FRAME_INTERVAL_MS
    angles = np.arctan2(dy, dx)
    angle_change = np.zeros_like(angles)
    angle_change[1:] = _wrapped_angle_diff(angles[1:], angles[:-1])

    out = np.zeros((len(times), len(FRAME_FEATURE_NAMES)), dtype=np.float32)
    for i, time_ms in enumerate(times):
        next_idx = int(next_indices[i])
        prev_idx = int(prev_indices[i])
        nx = index["xs"][next_idx]
        ny = index["ys"][next_idx]
        px = index["xs"][prev_idx]
        py = index["ys"][prev_idx]
        required_speed = _safe_div(
            math.hypot(nx - px, ny - py),
            index["start_ms"][next_idx] - index["start_ms"][prev_idx],
        )

        slider_values = [0.0, 0.0, 0.0, 0.0, 0.0]
        active_slider_idx = _active_slider_index_at(index, time_ms)
        if active_slider_idx is not None:
            slider = index["objects"][active_slider_idx]
            bx, by, progress = _slider_ball_position(
                slider,
                time_ms,
                index["start_ms"][active_slider_idx],
                index["end_ms"][active_slider_idx],
            )
            slider_values = [
                1.0,
                math.hypot(xs[i] - bx, ys[i] - by) / radius,
                (xs[i] - bx) / radius,
                (ys[i] - by) / radius,
                progress,
            ]

        out[i] = np.array(
            [
                xs[i] / PLAYFIELD_WIDTH,
                ys[i] / PLAYFIELD_HEIGHT,
                dx[i] / PLAYFIELD_WIDTH,
                dy[i] / PLAYFIELD_HEIGHT,
                speed[i],
                _safe_div(speed[i], required_speed),
                acceleration[i],
                _safe_div(acceleration[i], required_speed),
                math.sin(angles[i]),
                math.cos(angles[i]),
                angle_change[i],
                (index["start_ms"][next_idx] - time_ms) / WINDOW_MS,
                math.hypot(xs[i] - nx, ys[i] - ny) / radius,
                (xs[i] - nx) / radius,
                (ys[i] - ny) / radius,
                required_speed,
                *slider_values,
            ],
            dtype=np.float32,
        )
    return out


def _make_window_stats(frame_features, index, selected_indices, radius):
    speed = frame_features[:, FRAME_FEATURE_NAMES.index("speed")]
    acceleration = frame_features[:, FRAME_FEATURE_NAMES.index("acceleration")]
    angle_change = np.abs(frame_features[:, FRAME_FEATURE_NAMES.index("angle_change")])
    next_error = frame_features[:, FRAME_FEATURE_NAMES.index("distance_to_next_object_norm")]
    slider_mask = frame_features[:, FRAME_FEATURE_NAMES.index("is_during_slider")] > 0.5
    slider_error = frame_features[:, FRAME_FEATURE_NAMES.index("slider_ball_error_norm")]

    path_length = float(np.sum(speed) * FRAME_INTERVAL_MS)
    if len(selected_indices) >= 2:
        direct_distance = float(
            math.hypot(
                index["xs"][int(selected_indices[-1])] - index["xs"][int(selected_indices[0])],
                index["ys"][int(selected_indices[-1])] - index["ys"][int(selected_indices[0])],
            )
        )
    else:
        direct_distance = 0.0

    speed_max = float(np.max(speed)) if len(speed) else 0.0
    hard_stop_count = 0.0
    if speed_max > EPS and len(speed) > 1:
        hard_stop_count = float(np.count_nonzero((speed[:-1] > speed_max * 0.35) & (speed[1:] < speed[:-1] * 0.35)))

    slider_error_values = slider_error[slider_mask]
    slider_follow_ratio = float(np.mean(slider_error_values <= 1.0)) if len(slider_error_values) else 0.0
    slider_count = float(np.count_nonzero(index["is_slider"][selected_indices])) if len(selected_indices) else 0.0

    return np.array(
        [
            float(np.mean(speed)),
            float(np.std(speed)),
            speed_max,
            float(np.std(acceleration)),
            float(np.std(angle_change)),
            float(np.count_nonzero(angle_change > math.radians(90.0))),
            hard_stop_count,
            _safe_div(path_length, direct_distance),
            float(np.mean(next_error)),
            float(np.std(next_error)),
            float(np.mean(slider_error_values)) if len(slider_error_values) else 0.0,
            float(np.std(slider_error_values)) if len(slider_error_values) else 0.0,
            slider_follow_ratio,
            float(len(selected_indices)),
            slider_count,
        ],
        dtype=np.float32,
    )


def extract_replay_feature(beatmap_path: Path, replay_path: Path, output_path: Path, player_id: str):
    beatmap = Beatmap.from_path(beatmap_path)
    replay = Replay.from_path(replay_path, retrieve_beatmap=False)
    objects = _prepare_objects(beatmap, replay)
    if not objects:
        raise ValueError("beatmap contains no hit objects")

    index = _build_object_index(objects)
    replay_times, replay_xs, replay_ys = _build_replay_track(replay)
    start_ms = max(float(replay_times[0]), float(index["start_ms"][0]) - OBJECT_CONTEXT_MS)
    end_ms = min(float(replay_times[-1]), float(index["end_ms"][-1]) + OBJECT_CONTEXT_MS)
    if end_ms - start_ms < WINDOW_MS:
        raise ValueError("replay is shorter than one feature window")

    hard_rock = bool(getattr(replay, "hard_rock", False))
    radius = float(circle_radius(float(beatmap.cs(hard_rock=hard_rock))))
    frames_per_window = max(1, int(round(WINDOW_MS / FRAME_INTERVAL_MS)))
    frame_features = []
    window_stats = []
    window_starts = []

    current_start = start_ms
    while current_start + WINDOW_MS <= end_ms + EPS:
        current_end = current_start + WINDOW_MS
        frame_times = current_start + np.arange(frames_per_window, dtype=np.float64) * FRAME_INTERVAL_MS
        xs, ys = _interpolate_track(replay_times, replay_xs, replay_ys, frame_times)
        selected_indices = _window_object_indices(index, current_start, current_end)
        frame = _make_frame_features(index, frame_times, xs, ys, radius)
        frame_features.append(frame)
        window_stats.append(_make_window_stats(frame, index, selected_indices, radius))
        window_starts.append(current_start)
        current_start += STRIDE_MS

    metadata = {
        "beatmap_path": str(beatmap_path),
        "replay_path": str(replay_path),
        "player_id": str(player_id),
        "player_name": replay.player_name,
        "beatmap_md5": replay.beatmap_md5,
        "replay_md5": replay.replay_md5,
        "clock_rate": _replay_clock_rate(replay),
        "window_ms": WINDOW_MS,
        "stride_ms": STRIDE_MS,
        "frame_interval_ms": FRAME_INTERVAL_MS,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        frame_features=np.stack(frame_features).astype(np.float32),
        window_stats=np.stack(window_stats).astype(np.float32),
        window_starts_ms=np.array(window_starts, dtype=np.float32),
        frame_feature_names=np.array(FRAME_FEATURE_NAMES),
        window_stat_names=np.array(WINDOW_STAT_NAMES),
        player_id=np.array(str(player_id)),
        metadata=np.array(json.dumps(metadata, ensure_ascii=False)),
    )
