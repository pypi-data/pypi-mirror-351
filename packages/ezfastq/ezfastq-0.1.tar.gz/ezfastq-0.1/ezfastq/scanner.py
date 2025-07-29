# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import List


@dataclass
class FastqFileScanner:
    "Supports recursively scanning a directory for FASTQ files containing the given sample names."

    sample_names: List

    @classmethod
    def new(cls, sample_names):
        sample_names = cls.check_sample_names(sample_names)
        scanner = cls(sample_names)
        return scanner

    @staticmethod
    def check_sample_names(sample_names):
        sample_names = sorted(sample_names)
        for sample1, sample2 in combinations(sample_names, 2):
            if sample1 in sample2 or sample2 in sample1:
                message = f"one sample name cannot be a substring of another sample name: {sample1} vs {sample2}"
                raise ValueError(message)
        return sample_names

    def scan(self, path):
        self.check_scan_path(path)
        valid_suffixes = (".fastq", ".fastq.gz", ".fq", ".fq.gz")
        for file_path in self.traverse(path):
            if not file_path.name.endswith(valid_suffixes):
                continue
            for sample in self.sample_names:
                if sample in file_path.name:
                    yield sample, file_path

    @staticmethod
    def check_scan_path(path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_dir():
            raise NotADirectoryError(path)

    @staticmethod
    def traverse(path):
        path = Path(path)
        if not path.is_dir():  # pragma: no cover
            return
        for file_path in path.rglob("*"):
            if file_path.is_file():
                yield file_path
