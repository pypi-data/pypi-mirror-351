# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ezfastq.fastq import FastqFile
from importlib.resources import files
from pathlib import Path
import pytest


def test_fastq_file_basic():
    infile = FastqFile(Path("/opt/data/seq/s1-R1.fq"), "sample1", 1)
    assert infile.sample == "sample1"
    assert infile.read == 1
    assert infile.name == "sample1_R1.fastq.gz"
    assert infile.extension == "fastq"
    assert str(infile) == '"s1-R1.fq" = "sample1_R1.fastq.gz"'


@pytest.mark.parametrize(
    "prefix, file_name",
    [
        ("caseXYZ_", "caseXYZ_sample2_R1.fastq.gz"),
        ("ProjXYZ_", "ProjXYZ_sample2_R1.fastq.gz"),
    ],
)
def test_fastq_file_prefix(prefix, file_name):
    infile = FastqFile(Path("/data/runs/XYZ/s2-R1.fq.gz"), "sample2", 1, prefix)
    assert infile.name == file_name
    assert infile.extension == "fastq.gz"


def test_fastq_file_copy(tmp_path):
    inpath = files("ezfastq") / "tests" / "data" / "flat" / "test1_S1_L001_R1_001.fastq.gz"
    infile = FastqFile(inpath, "test1", 1)
    infile.copy(tmp_path)
    file_copy = tmp_path / "test1_R1.fastq.gz"
    assert file_copy.is_file()


def test_fastq_file_check_and_copy(tmp_path):
    destination = tmp_path / "seq"
    inpath = files("ezfastq") / "tests" / "data" / "flat" / "test1_S1_L001_R2_001.fastq.gz"
    infile = FastqFile(inpath, "test1", 2)
    was_copied = infile.check_and_copy(destination)
    assert was_copied
    file_copy = tmp_path / "seq" / "test1_R2.fastq.gz"
    assert file_copy.is_file()
    was_copied = infile.check_and_copy(destination)
    assert not was_copied
