# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .pair import PairMode
from .scanner import FastqFileScanner
from collections import defaultdict


class SampleFastqMap(defaultdict):
    "Map sample names to lists of corresponding FASTQ files."

    @classmethod
    def new(cls, sample_names, data_path, pair_mode=PairMode.Unspecified):
        files_by_sample = cls(list)
        scanner = FastqFileScanner.new(sample_names)
        for sample_name, fastq in scanner.scan(data_path):
            files_by_sample[sample_name].append(fastq)
            files_by_sample[sample_name].sort()
        cls.validate_sample_files(sample_names, files_by_sample, pair_mode=pair_mode)
        return files_by_sample

    @staticmethod
    def validate_sample_files(sample_names, files_by_sample, pair_mode=PairMode.Unspecified):
        for sample in sample_names:
            fastq_files = files_by_sample[sample]
            pair_mode.check(len(fastq_files), sample)
