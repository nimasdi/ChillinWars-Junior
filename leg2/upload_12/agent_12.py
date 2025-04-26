# TEAM 12

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

try:
    import onnxruntime as ort
except ModuleNotFoundError:
    sys.stderr.write("[agent] onnxruntime not found; please install via `pip install onnxruntime`\n")
    sys.exit(1)

############################################################
# Constants duplicated from training code                  #
############################################################
ARENA_W, ARENA_H = 1000, 540
LIGHT_CD, HEAVY_CD = 25, 100
DASH_CD = 40
ATTACK_RANGE = 180 - 1e-3

# Action mapping (no idle)
ACTION_TABLE: List[Dict[str, object]] = [
    {"move": "left",  "attack": None, "jump": False, "dash": None},
    {"move": "right", "attack": None, "jump": False, "dash": None},
    {"move": None,    "attack": None, "jump": True,  "dash": None},
    {"move": None,    "attack": None, "jump": False, "dash": "left"},
    {"move": None,    "attack": None, "jump": False, "dash": "right"},
    {"move": None,    "attack": 1,    "jump": False, "dash": None},
    {"move": None,    "attack": 2,    "jump": False, "dash": None},
]

############################################################
# ONNX Runtime session (loaded once)                       #
############################################################
MODELS_DIR = Path(__file__).with_suffix("").parent / "models"
MODEL_PATH = os.getenv("FIGHTER_ONNX", MODELS_DIR / "latest_v2.onnx")

if not Path(MODEL_PATH).is_file():
    sys.stderr.write(f"[agent] ONNX model not found at {MODEL_PATH}\n")
    sys.exit(1)

session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name  # logits only

############################################################
# Helper                                                   #
############################################################

def _state_vector(f: dict, o: dict) -> np.ndarray:
    can_hit = 1.0 if abs(f["x"] - o["x"]) < ATTACK_RANGE else 0.0
    return np.array([
        f["x"] / ARENA_W,
        f["y"] / ARENA_H,
        f["health"] / 100,
        float(f["attacking"]),
        f["attack_cooldown"][0] / LIGHT_CD,
        f["attack_cooldown"][1] / HEAVY_CD,
        float(f["jump"]),
        f["dash_cooldown"] / DASH_CD,
        o["x"] / ARENA_W,
        o["y"] / ARENA_H,
        o["health"] / 100,
        float(o["attacking"]),
        can_hit,
    ], dtype=np.float32)


def _make_decision(state: np.ndarray) -> int:
    logits = session.run([output_name], {input_name: state[None, :]})[0]
    return int(np.argmax(logits, axis=1)[0])

############################################################
# External API                                             #
############################################################

def make_move(fighter_info, opponent_info, saved_data):  # called each frame
    state = _state_vector(fighter_info, opponent_info)
    action_idx = _make_decision(state)
    action_dict = ACTION_TABLE[action_idx].copy()
    action_dict.update({"debug": None, "saved_data": saved_data})
    return action_dict

############################################################
# Stdin → Stdout wrapper so the engine can spawn the file  #
############################################################
if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    fighter = payload["fighter"]
    opponent = payload["opponent"]
    saved = payload.get("saved_data", {})
    out = make_move(fighter, opponent, saved)
    sys.stdout.write(json.dumps(out))
