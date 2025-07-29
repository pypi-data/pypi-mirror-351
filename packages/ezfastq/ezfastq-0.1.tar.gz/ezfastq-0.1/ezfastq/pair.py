# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from enum import Enum


class PairMode(Enum):
    Unspecified = 0
    SingleEnd = 1
    PairedEnd = 2

    def check(self, num_files, sample):
        if num_files == 0:
            raise FileNotFoundError(f"sample {sample}: found 0 FASTQ files")
        if num_files not in self.expected_num_files:
            exp_file_str = " or ".join(map(str, self.expected_num_files))
            message = f"sample {sample}: found {num_files} FASTQ file(s), expected {exp_file_str} in {self.mode} mode"
            raise ValueError(message)

    @property
    def mode(self):
        if self == PairMode.Unspecified:
            return "unspecified"
        elif self == PairMode.SingleEnd:
            return "single-end"
        else:
            return "paired-end"

    @property
    def expected_num_files(self):
        if self == PairMode.Unspecified:
            return [1, 2]
        elif self == PairMode.SingleEnd:
            return [1]
        else:
            return [2]
