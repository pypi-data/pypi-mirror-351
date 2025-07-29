from pathlib import Path
from torch import Tensor

import logging

import torch

logger = logging.getLogger("sample")


def do_something(a: Tensor):
    logger.info("Did something")
    return a + 1


def load(path: Path):
    logger.info(f"Loaded from {path}")
    return torch.load(path)


def save(a: Tensor, path: Path):
    logger.info(f"Saved to {path}")
    torch.save(a, path)
