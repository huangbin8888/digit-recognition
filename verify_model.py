# -*- coding: utf-8 -*-
"""模型权重自检：结构、形状、数值范围、元数据一致性与文件指纹。

用法：python verify_model.py
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "model" / "weights.json"
META = ROOT / "model" / "metadata.json"
MANIFEST = ROOT / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, label: str) -> None:
    print(("  OK   " if condition else "  FAIL ") + label)
    if not condition:
        raise SystemExit("校验未通过：" + label)


def main() -> None:
    w = json.loads(WEIGHTS.read_text(encoding="utf-8"))
    m = json.loads(META.read_text(encoding="utf-8"))
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))

    print("== 权重结构 ==")
    check(w.get("kind") == "sparse_softmax", "kind = sparse_softmax")
    n = w.get("n_features")
    check(n == 256, "n_features = 256")
    W, b = w.get("W"), w.get("b")
    check(isinstance(W, list) and len(W) == 10, "W 有 10 行（类别 0-9）")
    check(all(isinstance(row, list) and len(row) == n for row in W), "每行 W 均为 256 列")
    check(isinstance(b, list) and len(b) == 10, "b 有 10 项")
    flat = [v for row in W for v in row] + list(b)
    check(all(isinstance(v, (int, float)) and math.isfinite(v) for v in flat), "全部权重为有限数值")
    check(w.get("seed") == 20261109, "seed = 20261109")

    print("== 元数据一致性 ==")
    check(m.get("weights_file") == "model/weights.json", "weights_file 指向本仓库权重")
    check(m.get("preprocess_version") == "P6-v1", "预处理版本 P6-v1")
    check(m.get("id") == "mdl_20261110094140_0074", "模型版本 ID 一致")
    check(m["config_snapshot"]["values"]["seed"] == w["seed"], "配置快照 seed 与权重一致")
    check(m["metrics"]["train_acc"] == 1.0 and m["metrics"]["val_acc"] == 1.0,
          "记录的训练/验证准确率可读")

    print("== 源码清单 ==")
    check(isinstance(entries, list) and len(entries) == 27, "清单含 27 个源码/文档文件")
    check(all(set(e) == {"path", "bytes", "sha256"} and len(e["sha256"]) == 64
              for e in entries), "每条含路径、字节数与 64 位 SHA256")

    print("== 数值摘要 ==")
    print("  权重数量:", len(flat))
    print("  最小值:", round(min(flat), 6), " 最大值:", round(max(flat), 6))
    print("  weights.json SHA256:", sha256(WEIGHTS))
    print("  metadata.json SHA256:", sha256(META))
    print("校验全部通过。")


if __name__ == "__main__":
    main()
