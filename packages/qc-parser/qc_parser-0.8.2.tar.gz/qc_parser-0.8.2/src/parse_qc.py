########################################################################
#
#   Authors:
#       Michele Berselli
#       Harvard Medical School
#       berselli.michele@gmail.com
#
#       Alexander Veit
#       Harvard Medical School
#       alexander_veit@hms.harvard.edu
#
#   Script to parse the output from several QC tools to generate
#       portal-compatible Quality Metric (QM) objects
#
########################################################################

import click
from src.QMGeneric import QMGeneric
from src.MetricsParser import Parser


@click.command()
@click.help_option("--help", "-h")
@click.option(
    "-n",
    "--qm-name",
    required=True,
    type=str,
    help="Name of the Quality Metric",
)
@click.option(
    "-m",
    "--metrics",
    required=True,
    type=str,
    nargs=2,
    multiple=True,
    help="QC tool and File that will be parsed",
)
@click.option(
    "-a",
    "--additional-files",
    required=False,
    type=str,
    multiple=True,
    help="Files that will be added to the zip archive",
)
@click.option(
    "--output-json",
    required=True,
    type=str,
    default="qc_values.json",
    help="File name of the output JSON file",
)
@click.option(
    "--output-zip",
    required=True,
    type=str,
    default="metrics.zip",
    help="File name of the output zip file",
)
def parse_qc(qm_name, metrics, additional_files, output_json, output_zip):
    """
    This script gathers metrics from different tools and creates a QualityMetricGeneric item compatible JSON.

    Example usage:
    parse-qc \
        -n 'BAM Quality Metrics' \
        --metrics samtools /PATH/samtools.stats.txt \
        --metrics picard_CollectInsertSizeMetrics /PATH/picard_cis_metrics.txt \
        --additional-files /PATH/additional_output_1.pdf \
        --additional-files /PATH/additional_output_2.tsv \
        --output-zip metrics.zip
        --output-json qc_values.json

    This command will parse samtools and picard_CollectInsertSizeMetrics metrics from the files provided for each
    tool and create a qc.json file. It will also create a zip archive with all 4 provided files.

    """
    all_files = list(additional_files) if additional_files else []
    qmg = QMGeneric(qm_name)

    for m in metrics:
        tool_name, metrics_file = m
        all_files.append(metrics_file)

        parser = Parser(tool_name, metrics_file)
        qm_values = parser.parse()
        qmg.add_values(qm_values)

    # Write JSON object
    qmg.write_json(output_json)
    # Create Archive after removing duplicates
    all_files = list(set(all_files))
    qmg.create_archive(all_files, output_zip)


if __name__ == "__main__":
    parse_qc()
