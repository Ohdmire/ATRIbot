import asyncio
import importlib.util
import json
import re
import time
from pathlib import Path

import aiohttp
import numpy as np

from ATRIlib.API import PPYapiv2
from ATRIlib.Config.config import osu_token
from ATRIlib.DB.Mongodb import db_user
from ATRIlib.DB.pipeline_getgroupusers import get_group_users_id_list
from ATRIlib.TOOLS.Download import download_replay_file, fetch_beatmap_file_async_one
from ATRIlib.TOOLS.ReplayFeature import extract_replay_feature


ROOT = Path(__file__).resolve().parents[1]
REPLAY_DIR = ROOT / "data" / "replay"
BEATMAP_DIR = ROOT / "data" / "beatmaps"
MODEL_DIR = ROOT / "assets" / "models"
MODEL_CACHE = {}


def _safe_path_part(value):
    cleaned = re.sub(r"[^\w.\-]+", "_", str(value).strip(), flags=re.UNICODE)
    cleaned = cleaned.strip("._")
    return cleaned or "unknown"


def _score_id(score):
    return score.get("id") or score.get("score_id") or score.get("legacy_score_id")


def _score_beatmap_id(score):
    beatmap = score.get("beatmap") or {}
    return beatmap.get("id") or beatmap.get("beatmap_id") or score.get("beatmap_id")


def _score_has_replay(score):
    return bool(score.get("replay") or score.get("has_replay"))


def _score_mods(score):
    mods = score.get("mods") or []
    acronyms = []
    for mod in mods:
        if isinstance(mod, str):
            acronyms.append(mod)
        elif isinstance(mod, dict) and mod.get("acronym"):
            acronyms.append(str(mod["acronym"]))
    return "".join(acronyms) or "NM"


def _player_replay_dir(user_id):
    return REPLAY_DIR / _safe_path_part(user_id)


def _existing_replay(user_id):
    replay_dir = _player_replay_dir(user_id)
    if not replay_dir.exists():
        return None
    for path in sorted(replay_dir.glob("*.osr")):
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def _replay_metadata_path(replay_path):
    return replay_path.with_suffix(".json")


def _feature_path_for_replay(replay_path):
    return replay_path.with_suffix(".npz")


def _beatmap_id_from_path(replay_path):
    stem_parts = replay_path.stem.split("_")
    for part in reversed(stem_parts):
        if part.isdigit():
            return part
    return None


def _load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _select_replay_score(scores):
    for score in scores:
        if _score_id(score) and _score_beatmap_id(score) and _score_has_replay(score):
            return score
    raise ValueError("bp 中没有找到 replay=true 的成绩")


def _api_v2_bearer_token():
    authorization = PPYapiv2.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return ""


async def _beatmap_id_from_replay(replay_path):
    from slider import Replay

    replay = await asyncio.to_thread(Replay.from_path, replay_path, retrieve_beatmap=False)
    beatmap_md5 = replay.beatmap_md5
    if not beatmap_md5:
        raise ValueError(f"无法从 replay 读取 beatmap md5: {replay_path}")
    url = f"https://api.ppy.sb/v1/get_map_info?md5={beatmap_md5}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status >= 400:
                text = await response.text()
                raise ValueError(f"replay 谱面查询失败: HTTP {response.status} {text[:120]}")
            data = await response.json()
    if isinstance(data, list):
        data = data[0] if data else {}
    elif isinstance(data, dict):
        if isinstance(data.get("data"), list):
            data = data["data"][0] if data["data"] else {}
        elif isinstance(data.get("data"), dict):
            data = data["data"]
        elif isinstance(data.get("map"), dict):
            data = data["map"]
    beatmap_id = data.get("beatmap_id") or data.get("id") or data.get("bid")
    if not beatmap_id:
        raise ValueError(f"replay 谱面查询结果没有 beatmap id: {beatmap_md5}")
    return str(beatmap_id)


async def _ensure_replay(user_id, username):
    existing = _existing_replay(user_id)
    if existing is not None:
        metadata = _load_json(_replay_metadata_path(existing))
        beatmap_id = str(metadata.get("beatmap_id") or await _beatmap_id_from_replay(existing))
        return {
            "user_id": str(user_id),
            "username": username,
            "replay_path": existing,
            "score_id": str(metadata.get("score_id", "unknown")),
            "beatmap_id": beatmap_id,
            "source": "cache",
            "metadata": metadata,
        }

    scores = await PPYapiv2.get_user_best_all_info(user_id)
    if not isinstance(scores, list) or not scores:
        raise ValueError(f"{username} 没有 bp 数据")
    score = _select_replay_score(scores)
    score_id = str(_score_id(score))
    beatmap_id = str(_score_beatmap_id(score))
    replay_path = (
        _player_replay_dir(user_id)
        / f"{_safe_path_part(user_id)}_{_safe_path_part(score_id)}_{_safe_path_part(_score_mods(score))}_{_safe_path_part(beatmap_id)}.osr"
    )
    download_source = await download_replay_file(score_id, replay_path, osu_token, _api_v2_bearer_token())
    metadata = {
        "user_id": str(user_id),
        "username": username,
        "score_id": score_id,
        "beatmap_id": beatmap_id,
        "mods": _score_mods(score),
        "download_source": download_source,
        "downloaded_at": int(time.time()),
    }
    _save_json(_replay_metadata_path(replay_path), metadata)
    return {
        "user_id": str(user_id),
        "username": username,
        "replay_path": replay_path,
        "score_id": score_id,
        "beatmap_id": beatmap_id,
        "source": download_source,
        "metadata": metadata,
    }


async def _ensure_beatmap(beatmap_id):
    beatmap_path = BEATMAP_DIR / f"{beatmap_id}.osu"
    if beatmap_path.exists():
        return beatmap_path
    await fetch_beatmap_file_async_one(beatmap_id, Temp=False)
    if not beatmap_path.exists():
        raise ValueError(f"谱面下载失败: {beatmap_id}")
    return beatmap_path


def _extract_feature_sync(user_id, replay_path, beatmap_path, feature_path):
    if feature_path.exists():
        return feature_path
    extract_replay_feature(beatmap_path, replay_path, feature_path, str(user_id))
    return feature_path


async def _ensure_feature(user_id, username):
    replay_data = await _ensure_replay(user_id, username)
    beatmap_path = await _ensure_beatmap(replay_data["beatmap_id"])
    feature_path = _feature_path_for_replay(replay_data["replay_path"])
    await asyncio.to_thread(
        _extract_feature_sync,
        user_id,
        replay_data["replay_path"],
        beatmap_path,
        feature_path,
    )
    replay_data["feature_path"] = feature_path
    return replay_data


async def _ensure_existing_feature(user_id, username):
    replay_path = _existing_replay(user_id)
    if replay_path is None:
        raise ValueError("没有本地 replay")

    feature_path = _feature_path_for_replay(replay_path)
    metadata = _load_json(_replay_metadata_path(replay_path))
    beatmap_id = str(metadata.get("beatmap_id") or _beatmap_id_from_path(replay_path) or "")
    if feature_path.exists():
        return {
            "user_id": str(user_id),
            "username": username,
            "replay_path": replay_path,
            "feature_path": feature_path,
            "score_id": str(metadata.get("score_id", "unknown")),
            "beatmap_id": beatmap_id or "unknown",
            "source": "cache",
            "metadata": metadata,
        }

    if not beatmap_id:
        raise ValueError("本地 replay 缺少 beatmap_id metadata")
    beatmap_path = BEATMAP_DIR / f"{beatmap_id}.osu"
    if not beatmap_path.exists():
        raise ValueError(f"本地缺少谱面文件: {beatmap_id}")

    await asyncio.to_thread(_extract_feature_sync, user_id, replay_path, beatmap_path, feature_path)
    return {
        "user_id": str(user_id),
        "username": username,
        "replay_path": replay_path,
        "feature_path": feature_path,
        "score_id": str(metadata.get("score_id", "unknown")),
        "beatmap_id": beatmap_id,
        "source": "cache",
        "metadata": metadata,
    }


def _sample_windows(frames, max_windows):
    if frames.shape[0] == max_windows:
        return frames
    if frames.shape[0] < max_windows:
        padded = np.zeros((max_windows, frames.shape[1], frames.shape[2]), dtype=frames.dtype)
        padded[: frames.shape[0]] = frames
        return padded
    indices = np.linspace(0, frames.shape[0] - 1, max_windows).round().astype(np.int64)
    return frames[indices]


def _load_model_metadata(model_path):
    metadata_path = model_path.with_suffix(".json")
    if not metadata_path.exists():
        raise ValueError(f"模型 metadata 不存在: {metadata_path}")
    return _load_json(metadata_path)


def _model_embedding(feature_path, model_path):
    if importlib.util.find_spec("onnxruntime") is None:
        raise ValueError("缺少 onnxruntime，无法使用 assets/models 中的模型")
    import onnxruntime as ort

    cache_key = str(model_path.resolve())
    if cache_key not in MODEL_CACHE:
        session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        MODEL_CACHE[cache_key] = {
            "metadata": _load_model_metadata(model_path),
            "session": session,
            "input_name": session.get_inputs()[0].name,
            "output_name": session.get_outputs()[0].name,
        }
    model = MODEL_CACHE[cache_key]
    metadata = model["metadata"]
    data = np.load(feature_path, allow_pickle=False)
    frames = np.nan_to_num(data["frame_features"].astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    frames = _sample_windows(frames, int(metadata["max_windows"]))
    mean = np.asarray(metadata["mean"], dtype=np.float32).reshape(1, 1, -1)
    std = np.asarray(metadata["std"], dtype=np.float32).reshape(1, 1, -1)
    frames = ((frames - mean) / std).astype(np.float32)

    embedding = model["session"].run([model["output_name"]], {model["input_name"]: frames[None, ...]})[0]
    return np.asarray(embedding, dtype=np.float32).squeeze(0)


def _available_model_path():
    model_path = MODEL_DIR / "model.onnx"
    if model_path.exists():
        return model_path
    models = sorted(MODEL_DIR.glob("*.onnx")) if MODEL_DIR.exists() else []
    if models:
        return models[-1]
    return None


def _cosine(left, right):
    return float(left @ right / (np.linalg.norm(left) * np.linalg.norm(right) + 1e-8))


def _normalize_embedding(embedding):
    return embedding / (np.linalg.norm(embedding) + 1e-8)


def _relative_2d_coordinates(base_embedding, embeddings):
    base = _normalize_embedding(base_embedding)
    normalized = np.asarray([_normalize_embedding(embedding) for embedding in embeddings], dtype=np.float32)
    deltas = normalized - base[None, :]
    if deltas.shape[0] == 1:
        return np.array([[float(np.linalg.norm(deltas[0])), 0.0]], dtype=np.float32)

    _, _, vh = np.linalg.svd(deltas, full_matrices=False)
    axes = vh[:2]
    if axes.shape[0] == 1:
        axes = np.vstack([axes, np.zeros_like(axes[0])])
    return (deltas @ axes.T).astype(np.float32)


def _asset_result(data):
    return {
        "user_id": data["user_id"],
        "username": data["username"],
        "replay_path": str(data["replay_path"]),
        "feature_path": str(data["feature_path"]),
        "beatmap_id": data["beatmap_id"],
        "score_id": data["score_id"],
        "source": data["source"],
    }


def _user_name_from_db(user_id):
    user = db_user.find_one({"id": int(user_id)}) or db_user.find_one({"id": str(user_id)}) or {}
    return user.get("username") or str(user_id)


async def calculate_replay_similarity(user1, user2):
    REPLAY_DIR.mkdir(parents=True, exist_ok=True)
    left, right = await asyncio.gather(
        _ensure_feature(str(user1["id"]), user1["username"]),
        _ensure_feature(str(user2["id"]), user2["username"]),
    )
    model_path = _available_model_path()
    if model_path is None:
        raise ValueError("assets/models 中没有找到 replay 相似度模型")
    left_embedding, right_embedding = await asyncio.gather(
        asyncio.to_thread(_model_embedding, left["feature_path"], model_path),
        asyncio.to_thread(_model_embedding, right["feature_path"], model_path),
    )
    score = _cosine(left_embedding, right_embedding)
    threshold = float(_load_model_metadata(model_path).get("threshold", 0.0))
    return {
        "left": _asset_result(left),
        "right": _asset_result(right),
        "similarity": score * 100.0,
        "threshold": threshold,
        "is_same_player": bool(score >= threshold),
        "delta_percent": (score - threshold) * 100.0,
        "raw_score": score,
        "method": "model",
    }


async def calculate_group_replay_similarity(user, group_id):
    REPLAY_DIR.mkdir(parents=True, exist_ok=True)
    model_path = _available_model_path()
    if model_path is None:
        raise ValueError("assets/models 中没有找到 replay 相似度模型")

    base = await _ensure_feature(str(user["id"]), user["username"])
    base_embedding = await asyncio.to_thread(_model_embedding, base["feature_path"], model_path)
    threshold = float(_load_model_metadata(model_path).get("threshold", 0.0))

    group_user_ids = [str(user_id) for user_id in get_group_users_id_list(group_id)]
    skipped = []
    candidates = []
    for group_user_id in group_user_ids:
        if group_user_id == str(user["id"]):
            continue
        username = _user_name_from_db(group_user_id)
        try:
            candidates.append(await _ensure_existing_feature(group_user_id, username))
        except Exception as e:
            skipped.append({"user_id": group_user_id, "username": username, "reason": str(e)})

    if not candidates:
        return {
            "base": _asset_result(base),
            "comparisons": [],
            "skipped": skipped,
            "threshold": threshold,
            "method": "model",
        }

    embeddings = await asyncio.gather(
        *[asyncio.to_thread(_model_embedding, candidate["feature_path"], model_path) for candidate in candidates]
    )
    comparisons = []
    coordinates = _relative_2d_coordinates(base_embedding, embeddings)
    for candidate, embedding, coordinate in zip(candidates, embeddings, coordinates):
        score = _cosine(base_embedding, embedding)
        comparisons.append(
            {
                "player": _asset_result(candidate),
                "similarity": score * 100.0,
                "distance": 1.0 - score,
                "plot_distance": float(np.linalg.norm(coordinate)),
                "x": float(coordinate[0]),
                "y": float(coordinate[1]),
                "raw_score": score,
                "is_same_player": bool(score >= threshold),
            }
        )
    comparisons.sort(key=lambda item: item["distance"])
    return {
        "base": _asset_result(base),
        "comparisons": comparisons,
        "skipped": skipped,
        "threshold": threshold,
        "method": "model",
    }
