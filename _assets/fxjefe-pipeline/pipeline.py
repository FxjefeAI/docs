"""
FXJEFE Pipeline — end-to-end orchestration script.

Runs every stage of the FXJEFE-Quantum-Spirit project in the correct order:

  1. Path resolution & environment setup
  2. Data loading and processing
  3. Feature engineering
  4. Label generation
  5. Model predictions (XGBoost / ensemble)
  6. Evaluation framework (metrics + gate checks)
  7. Risk sizing
  8. Trade processing

Usage
-----
    python pipeline.py                           # full pipeline
    python pipeline.py --steps 1,2,3             # selected steps only
    python pipeline.py --config config.json      # custom config
    python pipeline.py --dry-run                 # validate without executing
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("fxjefe.pipeline")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default project root — override via FXJEFE_PROJECT_ROOT env-var or --root
_DEFAULT_ROOT = Path(__file__).resolve().parent

ALL_STEPS = [
    "setup",
    "load_data",
    "generate_features",
    "generate_labels",
    "model_predictions",
    "evaluation",
    "risk_sizing",
    "process_trades",
]


class StepStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


@dataclass
class StepResult:
    name: str
    status: StepStatus = StepStatus.PENDING
    elapsed_seconds: float = 0.0
    error: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PipelineConfig:
    """Runtime configuration for the pipeline."""

    project_root: Path = _DEFAULT_ROOT
    data_dir: Path = field(default_factory=lambda: _DEFAULT_ROOT / "data")
    models_dir: Path = field(default_factory=lambda: _DEFAULT_ROOT / "models")
    output_dir: Path = field(default_factory=lambda: _DEFAULT_ROOT / "output")
    steps: List[str] = field(default_factory=lambda: list(ALL_STEPS))
    dry_run: bool = False

    # Data loading
    symbol: str = "EURUSD"
    timeframe: str = "H1"
    data_file: str = ""

    # Feature engineering
    feature_count: int = 43

    # Evaluation thresholds (from FXJEFE evaluation framework)
    sharpe_threshold: float = 0.8
    sortino_threshold: float = 1.25
    profit_factor_threshold: float = 1.7
    expectancy_threshold: float = 0.10
    calmar_threshold: float = 1.0

    # Risk management
    account_equity: float = 10_000.0
    max_risk_pct: float = 1.5

    @classmethod
    def from_file(cls, path: str | Path) -> "PipelineConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        cfg = cls()
        for key, value in raw.items():
            if hasattr(cfg, key):
                current = getattr(cfg, key)
                if isinstance(current, Path):
                    setattr(cfg, key, Path(value))
                else:
                    setattr(cfg, key, type(current)(value))
        return cfg


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def _resolve_module(project_root: Path, *candidates: str):
    """Try to import a module from *candidates*, returning the first success."""
    original_path = list(sys.path)
    # Add common source directories to sys.path so imports resolve
    for sub in ("", "src", "src/pipeline", "src/features", "src/models",
                "src/evaluation", "src/trading", "src/tracing", "src/utils"):
        p = str(project_root / sub)
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        for name in candidates:
            try:
                return importlib.import_module(name)
            except ImportError:
                continue
        return None
    finally:
        sys.path = original_path


# -- Step 1: Setup -----------------------------------------------------------

def step_setup(cfg: PipelineConfig) -> StepResult:
    """Resolve paths and verify the project environment."""
    result = StepResult(name="setup")
    logger.info("Step 1/8 — Setup & path resolution")

    root = Path(os.environ.get("FXJEFE_PROJECT_ROOT", str(cfg.project_root))).resolve()
    cfg.project_root = root

    # Ensure critical directories exist
    for d in (cfg.data_dir, cfg.models_dir, cfg.output_dir):
        d = root / d if not d.is_absolute() else d
        d.mkdir(parents=True, exist_ok=True)
        logger.info("  Directory OK: %s", d)

    # Try importing path_resolver if it exists
    mod = _resolve_module(root, "path_resolver")
    if mod and hasattr(mod, "resolve"):
        mod.resolve()
        logger.info("  path_resolver.resolve() executed")

    result.status = StepStatus.SUCCESS
    result.output = {"project_root": str(root)}
    return result


# -- Step 2: Load data -------------------------------------------------------

def step_load_data(cfg: PipelineConfig) -> StepResult:
    """Load and pre-process market data."""
    result = StepResult(name="load_data")
    logger.info("Step 2/8 — Load & process data")

    mod = _resolve_module(cfg.project_root, "Load_and_process", "load_and_process")
    if mod is None:
        logger.warning("  Load_and_process module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "load_and_process"):
        mod.load_and_process()
    elif hasattr(mod, "run"):
        mod.run()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 3: Feature engineering ----------------------------------------------

def step_generate_features(cfg: PipelineConfig) -> StepResult:
    """Run feature engineering / generation."""
    result = StepResult(name="generate_features")
    logger.info("Step 3/8 — Generate features")

    mod = _resolve_module(
        cfg.project_root,
        "feature_engineering",
        "generate_features",
        "GenerateFeatures",
    )
    if mod is None:
        logger.warning("  Feature engineering module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "generate"):
        mod.generate()
    elif hasattr(mod, "run"):
        mod.run()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 4: Label generation -------------------------------------------------

def step_generate_labels(cfg: PipelineConfig) -> StepResult:
    """Generate target labels for supervised learning."""
    result = StepResult(name="generate_labels")
    logger.info("Step 4/8 — Generate labels")

    mod = _resolve_module(cfg.project_root, "generate_labels")
    if mod is None:
        logger.warning("  generate_labels module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "generate"):
        mod.generate()
    elif hasattr(mod, "run"):
        mod.run()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 5: Model predictions ------------------------------------------------

def step_model_predictions(cfg: PipelineConfig) -> StepResult:
    """Run model inference (XGBoost, ensemble, etc.)."""
    result = StepResult(name="model_predictions")
    logger.info("Step 5/8 — Model predictions")

    mod = _resolve_module(
        cfg.project_root,
        "ensemble_predictions",
        "generate_signals_with_xgboost",
        "xgboost_predictions_api",
    )
    if mod is None:
        logger.warning("  Prediction module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "predict"):
        mod.predict()
    elif hasattr(mod, "run"):
        mod.run()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 6: Evaluation framework ---------------------------------------------

def step_evaluation(cfg: PipelineConfig) -> StepResult:
    """Evaluate model performance via the FXJEFE evaluation framework."""
    result = StepResult(name="evaluation")
    logger.info("Step 6/8 — Evaluation framework")

    mod = _resolve_module(cfg.project_root, "evaluation_framework")
    if mod is None:
        logger.warning("  evaluation_framework module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    # Use the quick evaluate_model helper if available
    if hasattr(mod, "evaluate_model"):
        report = mod.evaluate_model(
            sharpe_threshold=cfg.sharpe_threshold,
            sortino_threshold=cfg.sortino_threshold,
            profit_factor_threshold=cfg.profit_factor_threshold,
            expectancy_threshold=cfg.expectancy_threshold,
            calmar_threshold=cfg.calmar_threshold,
        )
        result.output["report"] = str(report)
    elif hasattr(mod, "main"):
        mod.main()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 7: Risk sizing ------------------------------------------------------

def step_risk_sizing(cfg: PipelineConfig) -> StepResult:
    """Calculate dynamic position sizing based on evaluation results."""
    result = StepResult(name="risk_sizing")
    logger.info("Step 7/8 — Risk sizing")

    mod = _resolve_module(cfg.project_root, "evaluation_framework", "risk_management", "risk_managementnew")
    if mod is None:
        logger.warning("  Risk module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "RiskSizer"):
        sizer = mod.RiskSizer()
        risk = sizer.calculate_risk(cfg.account_equity) if hasattr(sizer, "calculate_risk") else None
        if risk is not None:
            result.output["risk"] = str(risk)
    elif hasattr(mod, "main"):
        mod.main()

    result.status = StepStatus.SUCCESS
    return result


# -- Step 8: Trade processing ------------------------------------------------

def step_process_trades(cfg: PipelineConfig) -> StepResult:
    """Process and execute (or log) trades."""
    result = StepResult(name="process_trades")
    logger.info("Step 8/8 — Process trades")

    mod = _resolve_module(cfg.project_root, "process_trades", "trading_integration")
    if mod is None:
        logger.warning("  Trading module not found — skipping")
        result.status = StepStatus.SKIPPED
        return result

    if hasattr(mod, "main"):
        mod.main()
    elif hasattr(mod, "process"):
        mod.process()
    elif hasattr(mod, "run"):
        mod.run()

    result.status = StepStatus.SUCCESS
    return result


# ---------------------------------------------------------------------------
# Step registry (maps step name → callable)
# ---------------------------------------------------------------------------

STEP_REGISTRY = {
    "setup": step_setup,
    "load_data": step_load_data,
    "generate_features": step_generate_features,
    "generate_labels": step_generate_labels,
    "model_predictions": step_model_predictions,
    "evaluation": step_evaluation,
    "risk_sizing": step_risk_sizing,
    "process_trades": step_process_trades,
}


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(cfg: PipelineConfig) -> List[StepResult]:
    """Execute the pipeline steps in order and return results."""
    results: List[StepResult] = []
    logger.info("=" * 60)
    logger.info("FXJEFE Pipeline — starting (%d steps)", len(cfg.steps))
    logger.info("  Project root : %s", cfg.project_root)
    logger.info("  Dry run      : %s", cfg.dry_run)
    logger.info("=" * 60)

    for step_name in cfg.steps:
        fn = STEP_REGISTRY.get(step_name)
        if fn is None:
            logger.error("Unknown step: %s", step_name)
            results.append(StepResult(name=step_name, status=StepStatus.FAILED,
                                      error=f"Unknown step: {step_name}"))
            continue

        if cfg.dry_run:
            logger.info("[DRY-RUN] Would execute step: %s", step_name)
            results.append(StepResult(name=step_name, status=StepStatus.SKIPPED))
            continue

        t0 = time.time()
        try:
            result = fn(cfg)
            result.elapsed_seconds = time.time() - t0
            results.append(result)
            logger.info(
                "  ✓ %s completed in %.2fs (%s)",
                step_name,
                result.elapsed_seconds,
                result.status.value,
            )
        except Exception as exc:
            elapsed = time.time() - t0
            tb = traceback.format_exc()
            logger.error("  ✗ %s FAILED after %.2fs: %s", step_name, elapsed, exc)
            logger.debug(tb)
            results.append(StepResult(
                name=step_name,
                status=StepStatus.FAILED,
                elapsed_seconds=elapsed,
                error=str(exc),
            ))

    # Summary
    _print_summary(results)
    return results


def _print_summary(results: List[StepResult]) -> None:
    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 60)
    total = sum(r.elapsed_seconds for r in results)
    for r in results:
        icon = {"SUCCESS": "✅", "SKIPPED": "⏭️", "FAILED": "❌"}.get(
            r.status.value, "⬜"
        )
        extra = f"  ({r.error})" if r.error else ""
        logger.info(
            "  %s %-25s %7.2fs%s",
            icon,
            r.name,
            r.elapsed_seconds,
            extra,
        )
    failed = [r for r in results if r.status == StepStatus.FAILED]
    logger.info("-" * 60)
    logger.info(
        "Total: %.2fs | Passed: %d | Skipped: %d | Failed: %d",
        total,
        sum(1 for r in results if r.status == StepStatus.SUCCESS),
        sum(1 for r in results if r.status == StepStatus.SKIPPED),
        len(failed),
    )
    if failed:
        logger.error("Pipeline finished with errors.")
    else:
        logger.info("Pipeline finished successfully.")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FXJEFE Pipeline — run all project stages in order.",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Project root directory (default: script location or FXJEFE_PROJECT_ROOT)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a JSON configuration file",
    )
    parser.add_argument(
        "--steps",
        type=str,
        default=None,
        help="Comma-separated list of steps to run (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate the pipeline without executing steps",
    )
    parser.add_argument(
        "--list-steps",
        action="store_true",
        default=False,
        help="List available steps and exit",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if args.list_steps:
        print("Available pipeline steps (executed in this order):")
        for i, name in enumerate(ALL_STEPS, 1):
            print(f"  {i}. {name}")
        return 0

    # Build config
    if args.config:
        cfg = PipelineConfig.from_file(args.config)
    else:
        cfg = PipelineConfig()

    if args.root:
        cfg.project_root = Path(args.root).resolve()

    if args.steps:
        requested = [s.strip() for s in args.steps.split(",")]
        # Accept step numbers or names
        resolved: List[str] = []
        for s in requested:
            if s.isdigit():
                idx = int(s) - 1
                if 0 <= idx < len(ALL_STEPS):
                    resolved.append(ALL_STEPS[idx])
                else:
                    logger.error("Invalid step number: %s", s)
                    return 1
            elif s in ALL_STEPS:
                resolved.append(s)
            else:
                logger.error("Unknown step: %s", s)
                return 1
        cfg.steps = resolved

    cfg.dry_run = args.dry_run

    results = run_pipeline(cfg)
    failed = any(r.status == StepStatus.FAILED for r in results)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
