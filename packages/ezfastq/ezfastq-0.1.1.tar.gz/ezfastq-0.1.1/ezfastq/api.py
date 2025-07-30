# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .copier import FastqCopier
from .pair import PairMode
from pathlib import Path


def copy(sample_names, seq_path, pair_mode=PairMode.Unspecified, prefix="", workdir=Path(".")):
    copier = FastqCopier.from_dir(sample_names, seq_path, prefix=prefix, pair_mode=pair_mode)
    copier.copy_files(workdir / "seq")
    copier.print_copy_log()
    nlogs = len(list((workdir / "seq").glob("copy-log-*.toml")))
    with open(workdir / "seq" / f"copy-log-{nlogs + 1}.toml", "w") as fh:
        print(copier, file=fh)
    added_samples = set(fastq.sample for fastq in copier.copied_files)
    added_samples = sorted(added_samples)
    with open(workdir / "samples.txt", "a") as fh:
        print(*added_samples, sep="\n", file=fh)
    return copier
