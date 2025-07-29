# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from shutil import copy
from subprocess import run
from typing import Literal


@dataclass
class FastqFile:
    "Facilitate copying FASTQ files and standardizing FASTQ names internally."

    source_path: Path
    sample: str
    read: Literal[0, 1, 2]  # undefined, R1, R2
    prefix: str = ""

    def __str__(self):
        return f'"{self.source_path.name}" = "{self.name}"'

    def check_and_copy(self, destination):
        destination = Path(destination)
        compressed_copy = destination / self.name
        if compressed_copy.is_file():
            return False
        else:
            self.copy(destination)
            return True

    def copy(self, destination):
        destination.mkdir(parents=True, exist_ok=True)
        file_copy = destination / self._working_name
        copy(self.source_path, file_copy)
        if self.extension == "fastq":
            run(["gzip", str(file_copy)])

    @property
    def name(self):
        return f"{self.stem}.fastq.gz"

    @property
    def stem(self):
        read_designator = f"_R{self.read}" if self.read in (1, 2) else ""
        return f"{self.prefix}{self.sample}{read_designator}"

    @property
    def extension(self):
        return "fastq.gz" if self.source_path.name.endswith("gz") else "fastq"

    @property
    def _working_name(self):
        return f"{self.stem}.{self.extension}"
