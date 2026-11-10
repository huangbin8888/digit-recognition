# -*- coding: utf-8 -*-
"""DigitLab sparse_softmax 模型推理（仅 Python 标准库）。

与训练软件 digit_lab/core/classifier.py 的 logits / predict_proba / predict
保持同一口径：类别索引 0-9 对应数字 0-9，特征为归一化后的 16x16 灰度（256 维）。

用法：
    python predict.py                    # 零特征向量自检
    python predict.py features.json      # 从 JSON 文件读特征
    python predict.py "[0, 0.1, ...]"    # 直接传 JSON 字符串

特征支持两种写法：
    1) 稠密：[0.0, 0.12, ...]（长度必须 256）
    2) 稀疏：[[3, 0.12], [17, 0.8], ...]（与训练时 nz_features 一致）
也可用 {"features": ...} 包装。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "model" / "weights.json"
N_CLASSES = 10


def load_model(path: Path = WEIGHTS) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if d.get("kind") != "sparse_softmax":
        raise ValueError("权重 kind 不是 sparse_softmax")
    if len(d["W"]) != N_CLASSES or len(d["b"]) != N_CLASSES:
        raise ValueError("W / b 的类别数不是 10")
    if any(len(row) != d["n_features"] for row in d["W"]):
        raise ValueError("W 的列数与 n_features 不一致")
    return d


def to_sparse(features, n_features: int) -> list[tuple[int, float]]:
    """把稠密向量或稀疏对统一成 [(索引, 值)]，跳过零值。"""
    if isinstance(features, dict):
        features = features.get("features")
    if not isinstance(features, list):
        raise ValueError("特征必须是数组")
    if features and isinstance(features[0], (list, tuple)):
        pairs = []
        for item in features:
            if len(item) != 2:
                raise ValueError("稀疏特征每项必须是 [索引, 值]")
            idx, val = int(item[0]), float(item[1])
            if not 0 <= idx < n_features:
                raise ValueError("特征索引越界：%d" % idx)
            if val != 0.0 and math.isfinite(val):
                pairs.append((idx, val))
        return pairs
    if len(features) != n_features:
        raise ValueError("稠密特征长度应为 %d，实际 %d" % (n_features, len(features)))
    out = []
    for idx, raw in enumerate(features):
        val = float(raw)
        if not math.isfinite(val):
            raise ValueError("第 %d 个特征不是有限数值" % idx)
        if val != 0.0:
            out.append((idx, val))
    return out


def logits(model: dict, nz: list[tuple[int, float]]) -> list[float]:
    out = list(model["b"])
    W = model["W"]
    for idx, val in nz:
        for c in range(N_CLASSES):
            out[c] += W[c][idx] * val
    return out


def softmax(z: list[float]) -> list[float]:
    m = max(z)
    exps = [math.exp(v - m) for v in z]
    s = sum(exps)
    return [e / s for e in exps]


def predict(model: dict, features) -> dict:
    nz = to_sparse(features, model["n_features"])
    z = logits(model, nz)
    p = softmax(z)
    best = max(range(N_CLASSES), key=lambda c: p[c])
    return {
        "digit": best,
        "confidence": round(p[best], 8),
        "probabilities": [round(v, 8) for v in p],
        "scores": [round(v, 8) for v in z],
        "nonzero_features": len(nz),
    }


def main() -> None:
    model = load_model()
    if len(sys.argv) > 2:
        raise SystemExit("用法：python predict.py [特征JSON文件 | 特征JSON字符串]")
    if len(sys.argv) == 1:
        features = [0.0] * model["n_features"]
    else:
        arg = sys.argv[1]
        p = Path(arg)
        text = p.read_text(encoding="utf-8") if p.is_file() else arg
        features = json.loads(text)
    print(json.dumps(predict(model, features), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
