#!/usr/bin/env python3

from pathlib import Path

import logging
from sample import part1
import tyro

logger = logging.getLogger()


def main(input_path: Path, output_path: Path, gpu: bool = False):
    logger.info("Starting sample computation.")
    x = part1.load(input_path)
    if gpu:
        logger.info('Using GPU')
        x = x.to("cuda")
    y = part1.do_something(x)
    if gpu:
        logger.info('Using GPU')
        y = y.to("cpu")
    part1.save(y, output_path)
    logger.info("Finished sample computation.")


if __name__ == "__main__":
    # logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    tyro.cli(main)
