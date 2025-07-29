# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ezfastq.copier import FastqCopier
from importlib.resources import files
import pytest

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


SEQ_PATH_1 = files("ezfastq") / "tests" / "data" / "flat"
SEQ_PATH_2 = files("ezfastq") / "tests" / "data" / "nested"


def test_copier_basic():
    sample_names = ["test1", "test2"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    observed = [fqfile.source_path.name for fqfile in copier]
    expected = [
        "test1_S1_L001_R1_001.fastq.gz",
        "test1_S1_L001_R2_001.fastq.gz",
        "test2_R1.fq.gz",
        "test2_R2.fq.gz",
    ]
    print(observed)
    assert observed == expected


def test_copier_copy(tmp_path):
    sample_names = ["test1", "test2"]
    # First pass: copy all 4
    copier1 = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    copier1.copy_files(tmp_path)
    assert len(copier1.copied_files) == 4
    assert len(copier1.skipped_files) == 0
    assert len(list(tmp_path.glob("*_R?.fastq.gz"))) == 4
    # Second pass: none are re-copied
    copier2 = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    copier2.copy_files(tmp_path)
    assert len(copier2.copied_files) == 0
    assert len(copier2.skipped_files) == 4
    # Third pass: delete one and make sure it is the only one re-copied
    (tmp_path / "test2_R2.fastq.gz").unlink()
    copier3 = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    copier3.copy_files(tmp_path)
    assert len(copier3.copied_files) == 1
    assert copier3.copied_files[0].name == "test2_R2.fastq.gz"
    assert len(copier3.skipped_files) == 3


def test_copier_prefix(tmp_path):
    sample_names = ["test2", "test3"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1, prefix="abc_")
    copier.copy_files(tmp_path)
    assert len(list(tmp_path.glob("abc_*.fastq.gz"))) == 4


def test_copier_str_basic(tmp_path):
    sample_names = ["test1", "test2", "test3"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    copier.copy_files(tmp_path)
    observed = str(copier)
    expected = """
[CopiedFiles]
"test1_S1_L001_R1_001.fastq.gz" = "test1_R1.fastq.gz"
"test1_S1_L001_R2_001.fastq.gz" = "test1_R2.fastq.gz"
"test2_R1.fq.gz" = "test2_R1.fastq.gz"
"test2_R2.fq.gz" = "test2_R2.fastq.gz"
"test3-reads-r1.fastq" = "test3_R1.fastq.gz"
"test3-reads-r2.fastq" = "test3_R2.fastq.gz"
"""
    assert observed.strip() == expected.strip()


def test_copier_str_noop(tmp_path):
    sample_names = ["test1", "test2", "test3"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    assert str(copier) == ""


def test_copier_str_allskip(tmp_path):
    sample_names = ["test1"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    (tmp_path / "test1_R1.fastq.gz").touch()
    (tmp_path / "test1_R2.fastq.gz").touch()
    copier.copy_files(tmp_path)
    observed = str(copier)
    expected = """
[SkippedFiles]
already_copied = [
    "test1_S1_L001_R1_001.fastq.gz",
    "test1_S1_L001_R2_001.fastq.gz",
]
"""
    assert observed.strip() == expected.strip()


def test_copier_str_mixed(tmp_path):
    sample_names = ["test1", "test2", "test3"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_2)
    (tmp_path / "test2_R1.fastq.gz").touch()
    (tmp_path / "test2_R2.fastq.gz").touch()
    copier.copy_files(tmp_path)
    observed = str(copier)
    expected = """
[CopiedFiles]
"test1_S1_L001_R1_001.fastq.gz" = "test1_R1.fastq.gz"
"test1_S1_L001_R2_001.fastq.gz" = "test1_R2.fastq.gz"
"test3-reads-r1.fastq" = "test3_R1.fastq.gz"
"test3-reads-r2.fastq" = "test3_R2.fastq.gz"

[SkippedFiles]
already_copied = [
    "test2_R1.fq.gz",
    "test2_R2.fq.gz",
]
"""
    assert observed.strip() == expected.strip()


def test_copier_str_roundtrip(tmp_path):
    sample_names = ["test1", "test2", "test3"]
    copier = FastqCopier.from_dir(sample_names, SEQ_PATH_1)
    (tmp_path / "test2_R1.fastq.gz").touch()
    (tmp_path / "test2_R2.fastq.gz").touch()
    copier.copy_files(tmp_path)
    copy_log = tmp_path / "log.toml"
    with open(copy_log, "w") as fh:
        print(copier, file=fh)
    with open(copy_log, "rb") as fh:
        copy_data = tomllib.load(fh)
    assert len(copy_data["CopiedFiles"]) == 4
    assert copy_data["CopiedFiles"]["test1_S1_L001_R1_001.fastq.gz"] == "test1_R1.fastq.gz"
    observed = copy_data["SkippedFiles"]["already_copied"]
    expected = ["test2_R1.fq.gz", "test2_R2.fq.gz"]
    assert observed == expected
