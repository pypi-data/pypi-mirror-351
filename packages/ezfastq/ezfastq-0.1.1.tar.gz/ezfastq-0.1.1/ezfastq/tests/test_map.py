# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ezfastq.map import SampleFastqMap
from ezfastq.pair import PairMode
from importlib.resources import files
import pytest


def test_seqmap_basic(simple_case):
    seq_map = SampleFastqMap.new(["1-1", "1-2", "1-3", "1-4"], simple_case)
    expected = [
        simple_case / "1-1_S1_L001_R1_001.fastq.gz",
        simple_case / "1-1_S1_L001_R2_001.fastq.gz",
    ]
    observed = seq_map["1-1"]
    assert observed == expected
    assert "1-2" in seq_map
    assert "1-3" in seq_map
    assert "1-4" in seq_map
    assert "1-5" not in seq_map
    assert len(list(seq_map)) == 4


def test_seqmap_single(single_end_case):
    seq_map = SampleFastqMap.new(
        ["1-1", "1-2", "1-3"], single_end_case, pair_mode=PairMode.SingleEnd
    )
    assert seq_map["1-1"] == [single_end_case / "1-1_S1_L001_R1_001.fastq.gz"]
    assert "1-2" in seq_map
    assert "1-3" in seq_map
    assert "1-4" not in seq_map


def test_sample_not_found(simple_case):
    message = "sample 1-5: found 0 FASTQ files"
    with pytest.raises(FileNotFoundError, match=message):
        SampleFastqMap.new(["1-1", "1-2", "1-3", "1-4", "1-5"], simple_case)


def test_single_end_mismatch(single_end_case):
    message = r"sample 1-1: found 1 FASTQ file\(s\), expected 2 in paired-end mode"
    with pytest.raises(ValueError, match=message):
        SampleFastqMap.new(["1-1", "1-2", "1-3"], single_end_case, pair_mode=PairMode.PairedEnd)


def test_nested_sample_names():
    sample_names = [f"sample{n+1}" for n in range(12)]
    message = "one sample name cannot be a substring of another sample name: sample1 vs sample10"
    with pytest.raises(ValueError, match=message):
        SampleFastqMap.new(sample_names, ".")


def test_missing_dir():
    sample_names = [f"sample{n+1}" for n in range(9)]
    with pytest.raises(FileNotFoundError):
        SampleFastqMap.new(sample_names, "/a/b/c/BogusDir")


def test_dir_is_file():
    sample_names = [f"sample{n+1}" for n in range(9)]
    file_path = files("ezfastq") / "tests" / "data" / "flat" / "test2_R1.fq.gz"
    with pytest.raises(NotADirectoryError):
        SampleFastqMap.new(sample_names, file_path)


@pytest.fixture
def simple_case(tmp_path):
    for sample in range(1, 5):
        for end in (1, 2):
            fastq = tmp_path / f"1-{sample}_S{sample}_L001_R{end}_001.fastq.gz"
            fastq.touch()
    return tmp_path


@pytest.fixture
def single_end_case(tmp_path):
    for sample in range(1, 4):
        fastq = tmp_path / f"1-{sample}_S{sample}_L001_R1_001.fastq.gz"
        fastq.touch()
    return tmp_path
