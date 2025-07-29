# ezfastq

Search a source directory for FASTQ files matching a list of given sample names and copy to a destination directory.


```
# Shell
ezfastq /path/to/data/ sample1 sample2 sample3 --workdir=path/to/dest/
ezfastq /opt/seq/ samplenames.txt --workdir=out/

# Python
import ezfastq
samples = ["sample1", "sample2", "sample3"]
source = "/path/to/seqs/"
dest = "new/path/"
ezfastq.api.copy(samples, source, workdir=dest)
```
