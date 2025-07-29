# QC parser for SMaHT
Parses outputs of different QC tools and unifies them for the SMaHT portal

## Installation

Simply run `pip install qc-parser` to install the package. You need at least Python 3.8.

To develop this package, clone this repo, make sure `poetry` is installed on your system and run `make install`.

## Usage

After installation the following command can be run from the command line:

```
parse-qc \
    -n 'BAM Quality Metrics' \
    --metrics samtools /PATH/samtools.stats.txt \
    --metrics picard_CollectInsertSizeMetrics /PATH/picard_cis_metrics.txt \
    --additional-files /PATH/additional_output_1.pdf \
    --additional-files /PATH/additional_output_2.tsv \
    --output-zip metrics.zip
    --output-json qc_values.json
```
In this example, the tool will parse the Samtools output file `/PATH/samtools.stats.txt` and the Picard output file `/PATH/picard_cis_metrics.txt`. The values that are extracted from both files are specified in `src/metrics_to_extract.py`. All metrics are combined and stored in `qc_values.json` that is compatible with Tibanna_ff's generic QC functionality.

The `metrics.zip` will contain the following files:
```
samtools.stats.txt
picard_cis_metrics.txt
additional_output_1.pdf
additional_output_2.tsv
```

The currently supported QC tools are:
- samtools_stats (Samtools stats)
- picard_CollectAlignmentSummaryMetrics (Picard CollectAlignmentSummaryMetrics)
- picard_CollectInsertSizeMetrics (Picard CollectInsertSizeMetrics)
- picard_CollectWgsMetrics (Picard CollectWgsMetrics)
- bamstats (bamStats.py)
- fastqc (FastQC)
- rnaseqc (RNA-SeQC)
- nanoplot (NanoPlot)
- verifybamid2 (VerifyBamID2)
- kraken2 (Kraken2)
- mosdepth (mosdepth)
- somalier (Somalier)
- tissue_classifier (internal tissue classification tool for RNA-Seq data)

## Development

If you want to **extract a new metric from an already supported QC tool**, add the metric to the `src/metrics_to_extract.py` in the appropriate section.

If you want to **add suuport for a new QC tool**, you need to add a parser to `src/MetricsParser.py` and add the metrics you want to extract from the tool to  `src/metrics_to_extract.py`.

## Tests

The command `make test` will run local tests.


