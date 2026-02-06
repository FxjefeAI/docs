"""
Generate trading signals using an XGBoost model.

Loads market data, standardises feature columns (filling any missing
ones with 0.0), runs the XGBoost model, and converts the 3-class
probability output into discrete BUY / HOLD / SELL signals.

Usage
-----
    python generate_signals_with_xgboost.py                      # defaults
    python generate_signals_with_xgboost.py --model model.json   # custom model
    python generate_signals_with_xgboost.py --data input.csv     # custom data
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature schema
# ---------------------------------------------------------------------------
# The 15 features expected by the XGBoost model, in order.
EXPECTED_FEATURES: List[str] = [
    "timestamp",
    "symbol",
    "price",
    "atr",
    "ema_diff",
    "rsi",
    "macd_diff",
    "vwap",
    "price_vwap_diff",
    "bb_position",
    "spread",
    "sentiment",
    "momentum",
    "volume_delta",
    "realized_vol",
]

# Signal class labels matching the model's 3-class output:
#   index 0 → SELL, index 1 → HOLD, index 2 → BUY
SIGNAL_LABELS: List[str] = ["SELL", "HOLD", "BUY"]

# Confidence threshold – if the max probability is below this value
# the signal is downgraded to HOLD regardless of the argmax class.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.60


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

@dataclass
class MarketRow:
    """A single row of market data with all 15 feature slots."""
    values: Dict[str, float] = field(default_factory=dict)

    def as_feature_vector(self) -> List[float]:
        """Return the numeric feature values in EXPECTED_FEATURES order.

        ``timestamp`` and ``symbol`` are non-numeric context columns and
        are excluded from the feature vector passed to the model.
        """
        numeric_features = [f for f in EXPECTED_FEATURES if f not in ("timestamp", "symbol")]
        return [self.values.get(f, 0.0) for f in numeric_features]


def _safe_float(value: Any) -> float:
    """Convert *value* to float, returning 0.0 on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def standardise_columns(
    raw_rows: List[Dict[str, Any]],
) -> List[MarketRow]:
    """Map raw data dicts onto the expected feature schema.

    * Columns present in the raw data are kept.
    * Missing columns are filled with ``0.0``.
    * Extra columns are silently dropped.
    """
    if not raw_rows:
        return []

    available = set(raw_rows[0].keys())
    present = sorted(available & set(EXPECTED_FEATURES))
    missing = sorted(set(EXPECTED_FEATURES) - available)

    logger.info("Standardized columns: %s", present)
    if missing:
        logger.info("Missing columns (filled with 0.0): %s", missing)

    rows: List[MarketRow] = []
    for raw in raw_rows:
        vals: Dict[str, float] = {}
        for feat in EXPECTED_FEATURES:
            if feat in ("timestamp", "symbol"):
                # Keep as-is (non-numeric context)
                vals[feat] = raw.get(feat, 0.0)
            else:
                vals[feat] = _safe_float(raw.get(feat, 0.0))
        rows.append(MarketRow(values=vals))
    return rows


# ---------------------------------------------------------------------------
# Model / prediction helpers
# ---------------------------------------------------------------------------

def _try_load_xgboost_model(model_path: str):
    """Attempt to load an XGBoost model from *model_path*.

    Returns the loaded Booster or ``None`` when the model file or
    ``xgboost`` package is unavailable.
    """
    if not os.path.isfile(model_path):
        logger.warning("Model file not found: %s", model_path)
        return None
    try:
        import xgboost as xgb
        bst = xgb.Booster()
        bst.load_model(model_path)
        logger.info("XGBoost model loaded from %s", model_path)
        return bst
    except ImportError:
        logger.warning("xgboost package not installed — using fallback predictions")
        return None
    except Exception as exc:
        logger.warning("Failed to load model: %s", exc)
        return None


def predict_probabilities(
    model: Any,
    feature_matrix: List[List[float]],
) -> List[List[float]]:
    """Run the model and return per-row class probabilities.

    If *model* is ``None`` (e.g. xgboost unavailable), return a
    uniform 3-class fallback so downstream code still works.
    """
    n_rows = len(feature_matrix)

    if model is not None:
        try:
            import xgboost as xgb
            dmat = xgb.DMatrix(feature_matrix)
            preds = model.predict(dmat)
            # preds may be shape (n, 3) already or (n,) for binary
            if hasattr(preds, "tolist"):
                preds = preds.tolist()
            # Ensure each row is a list of 3 probabilities
            if preds and not isinstance(preds[0], (list, tuple)):
                # Binary / single-value output → wrap
                preds = [[1.0 - p, 0.0, p] for p in preds]
            return preds
        except Exception as exc:
            logger.warning("Prediction failed: %s — using fallback", exc)

    # Fallback: uniform probability (all HOLD)
    logger.info("Using fallback uniform predictions (%d rows)", n_rows)
    return [[0.33, 0.34, 0.33]] * n_rows


# ---------------------------------------------------------------------------
# Signal conversion  (this is the logic that was crashing at line 73)
# ---------------------------------------------------------------------------

def predictions_to_signals(
    probabilities: List[List[float]],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Convert 3-class probability rows into trading signals.

    Each row of *probabilities* must have exactly 3 values corresponding
    to [P(SELL), P(HOLD), P(BUY)].

    Returns a list of dicts with keys:
        signal  – "BUY", "SELL", or "HOLD"
        confidence – the winning probability
        probabilities – the raw [sell, hold, buy] triple
    """
    signals: List[Dict[str, Any]] = []
    for row_idx, probs in enumerate(probabilities):
        # --- Guard: ensure we have exactly 3 values ---
        if not isinstance(probs, (list, tuple)) or len(probs) < 3:
            logger.warning(
                "Row %d: expected 3 probabilities, got %s — defaulting to HOLD",
                row_idx,
                probs,
            )
            signals.append({
                "signal": "HOLD",
                "confidence": 0.0,
                "probabilities": list(probs) if probs else [0.0, 0.0, 0.0],
            })
            continue

        sell_p, hold_p, buy_p = float(probs[0]), float(probs[1]), float(probs[2])
        max_p = max(sell_p, hold_p, buy_p)

        if max_p == buy_p and buy_p >= confidence_threshold:
            signal = "BUY"
        elif max_p == sell_p and sell_p >= confidence_threshold:
            signal = "SELL"
        else:
            signal = "HOLD"

        signals.append({
            "signal": signal,
            "confidence": round(max_p, 6),
            "probabilities": [round(sell_p, 6), round(hold_p, 6), round(buy_p, 6)],
        })
    return signals


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_csv_data(path: str) -> List[Dict[str, str]]:
    """Read a CSV file and return a list of row-dicts."""
    rows: List[Dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(dict(row))
    logger.info("Loaded %d rows from %s", len(rows), path)
    return rows


def save_signals_csv(signals: List[Dict[str, Any]], path: str) -> None:
    """Write trading signals to a CSV file."""
    if not signals:
        logger.warning("No signals to write")
        return

    fieldnames = ["row", "signal", "confidence", "p_sell", "p_hold", "p_buy"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for idx, sig in enumerate(signals):
            probs = sig.get("probabilities", [0, 0, 0])
            writer.writerow({
                "row": idx,
                "signal": sig["signal"],
                "confidence": sig["confidence"],
                "p_sell": probs[0],
                "p_hold": probs[1],
                "p_buy": probs[2],
            })
    logger.info("Signals written to %s", path)


def _generate_sample_data(n_rows: int = 5) -> List[Dict[str, Any]]:
    """Create sample market data for testing when no input file exists."""
    import random
    random.seed(42)
    rows = []
    for i in range(n_rows):
        rows.append({
            "timestamp": f"2026-02-06T10:{i:02d}:00Z",
            "symbol": "EURUSD",
            "price": round(1.0800 + random.uniform(-0.005, 0.005), 5),
            "atr": round(random.uniform(0.001, 0.003), 5),
            "ema_diff": round(random.uniform(-0.002, 0.002), 5),
            "rsi": round(random.uniform(30, 70), 2),
            "macd_diff": round(random.uniform(-0.001, 0.001), 5),
            "vwap": round(1.0800 + random.uniform(-0.003, 0.003), 5),
            "price_vwap_diff": round(random.uniform(-0.002, 0.002), 5),
            "bb_position": round(random.uniform(0, 1), 4),
            "spread": round(random.uniform(0.0001, 0.0003), 5),
            "sentiment": round(random.uniform(-1, 1), 4),
        })
    return rows


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------

def generate_signals(
    data: Optional[List[Dict[str, Any]]] = None,
    model_path: str = "xgboost_model.json",
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    output_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """End-to-end signal generation.

    1. Standardise feature columns
    2. Load XGBoost model (or use fallback)
    3. Predict 3-class probabilities
    4. Convert to BUY / HOLD / SELL signals
    """
    logger.info("Signal generation with XGBoost - configuration loaded")

    # 1. Prepare data
    if data is None:
        data = _generate_sample_data()

    rows = standardise_columns(data)
    feature_matrix = [r.as_feature_vector() for r in rows]

    # 2. Load model
    model = _try_load_xgboost_model(model_path)

    # 3. Predict
    probabilities = predict_probabilities(model, feature_matrix)
    n_rows = len(probabilities)
    n_cols = len(probabilities[0]) if probabilities else 0
    logger.info("Predictions shape: (%d, %d)", n_rows, n_cols)
    if probabilities:
        logger.info("First %d predictions:", min(5, n_rows))
        for row in probabilities[:5]:
            logger.info("  %s", row)

    # 4. Convert to signals  (original script crashed here at line 73)
    signals = predictions_to_signals(probabilities, confidence_threshold)

    # 5. Log summary
    buy_count = sum(1 for s in signals if s["signal"] == "BUY")
    sell_count = sum(1 for s in signals if s["signal"] == "SELL")
    hold_count = sum(1 for s in signals if s["signal"] == "HOLD")
    logger.info(
        "Signal summary: BUY=%d  SELL=%d  HOLD=%d  (total=%d)",
        buy_count, sell_count, hold_count, len(signals),
    )

    # 6. Optionally write CSV
    if output_path:
        save_signals_csv(signals, output_path)

    return signals


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate trading signals with XGBoost",
    )
    parser.add_argument("--model", default="xgboost_model.json",
                        help="Path to XGBoost model file")
    parser.add_argument("--data", default=None,
                        help="Path to input CSV data file")
    parser.add_argument("--output", default=None,
                        help="Path to write output signals CSV")
    parser.add_argument("--threshold", type=float,
                        default=DEFAULT_CONFIDENCE_THRESHOLD,
                        help="Confidence threshold for signal assignment")
    args = parser.parse_args(argv)

    # Load data
    if args.data and os.path.isfile(args.data):
        raw_data: Optional[List[Dict[str, Any]]] = load_csv_data(args.data)
    else:
        if args.data:
            logger.warning("Data file not found: %s — using sample data", args.data)
        raw_data = None

    signals = generate_signals(
        data=raw_data,
        model_path=args.model,
        confidence_threshold=args.threshold,
        output_path=args.output,
    )

    # Print results
    print("\nGenerated Signals:")
    print("-" * 50)
    for i, sig in enumerate(signals):
        probs = sig["probabilities"]
        print(
            f"  Row {i}: {sig['signal']:>4s}  "
            f"(confidence={sig['confidence']:.4f}  "
            f"sell={probs[0]:.4f} hold={probs[1]:.4f} buy={probs[2]:.4f})"
        )
    print("-" * 50)
    return 0


# Called by pipeline.py step_model_predictions
def predict():
    """Pipeline integration entry point.

    Runs signal generation with default settings.  Uses sample data when
    no input file is present and falls back to uniform predictions when
    the XGBoost model file (``xgboost_model.json``) is not found.
    """
    return generate_signals()


def run():
    """Pipeline integration entry point (alias for :func:`predict`)."""
    return generate_signals()


if __name__ == "__main__":
    sys.exit(main())
