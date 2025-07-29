# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .api import copy
from .pair import PairMode
from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path


def main(arglist=None):
    args = parse_args(arglist)
    copy(
        args.samples,
        args.seq_path,
        pair_mode=args.pair_mode,
        prefix=args.prefix,
        workdir=args.workdir,
    )


def parse_args(arglist=None):
    if arglist:
        arglist = map(str, arglist)
    args = get_parser().parse_args(arglist)
    samples_file = Path(args.samples[0])
    samples_file_exists = samples_file.is_file() or samples_file.is_fifo()
    if len(args.samples) == 1 and samples_file_exists:
        args.samples = samples_file.read_text().strip().split("\n")
    args.pair_mode = PairMode(args.pair_mode)
    return args


def get_parser():
    parser = ArgumentParser(description="Copy FASTQ files and update sample names")
    parser.add_argument(
        "seq_path",
        help="path to directory containing sequences in FASTQ format; subdirectories will be searched recursively",
    )
    parser.add_argument(
        "samples",
        nargs="+",
        help="name of one or more samples to process; can be provided as command-line arguments or as a file with one sample name per line",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"ezfastq v{version('ezfastq')}",
    )
    parser.add_argument(
        "-w",
        "--workdir",
        metavar="WD",
        type=Path,
        default=Path("."),
        help="directory to which input files will be copied and renamed",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        metavar="P",
        default="",
        help="prefix to prepend to sample names; resulting file path will be '{workdir}/seq/{prefix}_{sample}_R{1,2}.fastq.gz'",
    )
    parser.add_argument(
        "-m",
        "--pair-mode",
        metavar="M",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="specify 1 to indicate that all samples are single-end, or 2 to indicate that all samples are paired-end; by default, read layout is inferred automatically on a per-sample basis",
    )
    return parser
