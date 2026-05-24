"""Weights & Biases logging for CLaMP3 evaluation results.

W&B is optional: if the ``wandb`` package is not installed or the user is not
logged in, all functions in this module are no-ops and a warning is printed.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import wandb as _wandb

    _WANDB_AVAILABLE = True
except ImportError:
    _wandb = None
    _WANDB_AVAILABLE = False


def _parse_clamp3_score(output: str) -> Optional[float]:
    """Extract the numeric CLaMP3 score from raw script output.

    The script prints a line like ``CLaMP3 Score: 0.7423``.

    Args:
        output: Raw stdout string from the CLaMP3 script.

    Returns:
        Parsed float score, or ``None`` if not found.
    """
    match = re.search(r"CLaMP3\s+Score[:\s]+([0-9.]+)", output, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def log_clamp3_results(
    results: dict,
    run_name: str,
    project: str,
    entity: Optional[str] = None,
    extra_config: Optional[dict] = None,
) -> None:
    """Log CLaMP3 evaluation results to Weights & Biases.

    Each key in *results* is logged as a separate metric.  The function
    parses the numeric score from the raw CLaMP3 output string.

    Args:
        results: Dict mapping label (e.g. ``"classical/angry"``) to raw
            CLaMP3 stdout.  May be nested (``{"genre_vibe": {...}, ...}``).
        run_name: Name of the W&B run.
        project: W&B project name.
        entity: W&B entity (username or team).  Uses the default if ``None``.
        extra_config: Additional key-value pairs to store in the run config.
    """
    if not _WANDB_AVAILABLE:
        logger.warning("Pakiet wandb nie jest zainstalowany; pomijam logowanie.")
        return

    flat: dict[str, float] = {}

    def _flatten(d: dict, prefix: str = "") -> None:
        for k, v in d.items():
            full_key = f"{prefix}/{k}" if prefix else k
            if isinstance(v, dict):
                _flatten(v, prefix=full_key)
            elif isinstance(v, str):
                score = _parse_clamp3_score(v)
                if score is not None:
                    flat[full_key] = score

    _flatten(results)

    if not flat:
        logger.warning("Nie znaleziono zadnych wynikow CLaMP3 do zalogowania.")
        return

    run = _wandb.init(
        project=project,
        entity=entity,
        name=run_name,
        config=extra_config or {},
    )
    run.log(flat)
    run.finish()
    logger.info("Wyniki CLaMP3 zalogowane do W&B jako '%s'.", run_name)
