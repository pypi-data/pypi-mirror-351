########################################################################
# Metrics to calculate in a postprocessing step from the extracted metrics
########################################################################

samtools_stats_calculated_metrics = [
    {
        "key": "Percentage of Reads Paired [Samtools]",
        "tooltip": "Percentage of paired reads, mapped or unmapped, that are neither secondary nor supplementary (paired-end technology bit set) out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_paired",
        "type": float,
        "formula": "{samtools_stats:reads_paired}/{samtools_stats:sequences}*100",
        "visible": True,
    },
    {
        "key": "Percentage of Reads Mapped [Samtools]",
        "tooltip": "Percentage of reads, paired or single, that are mapped out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_mapped",
        "type": float,
        "formula": "{samtools_stats:reads_mapped}/{samtools_stats:sequences}*100",
        "visible": True,
    },
    {
        "key": "Percentage of Reads Mapped and Paired [Samtools]",
        "tooltip": "Percentage of mapped and paired reads (paired-end technology bit set with both mates mapped) out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_mapped_and_paired",
        "type": float,
        "formula": "{samtools_stats:reads_mapped_and_paired}/{samtools_stats:sequences}*100",
        "visible": True,
    },
    {
        "key": "Percentage of Reads Unmapped [Samtools]",
        "tooltip": "Percentage of unmapped reads out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_unmapped",
        "type": float,
        "formula": "{samtools_stats:reads_unmapped}/{samtools_stats:sequences}*100",
    },
    {
        "key": "Percentage of Reads Duplicated [Samtools]",
        "tooltip": "Percentage of duplicated reads out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_duplicated",
        "type": float,
        "formula": "{samtools_stats:reads_duplicated}/{samtools_stats:sequences}*100",
        "visible": True,
    },
    {
        "key": "Percentage of Reads MQ0 [Samtools]",
        "tooltip": "Percentage of mapped reads with mapping quality 0 (MQ0) out of processed reads",
        "derived_from": "samtools_stats_postprocessed:percentage_reads_MQ0",
        "type": float,
        "formula": "{samtools_stats:reads_MQ0}/{samtools_stats:sequences}*100",
        "visible": True,
    },
]

bamstats_calculated_metrics = [
    {
        "key": "Percentage of Uniquely Aligned Reads with Q>=10 [bamstats]",
        "tooltip": "Percentage of uniquely aligned reads with Q>=10",
        "derived_from": "bamstats_postprocessed:percentage_number_of_uniquely_aligned_reads_with_q_>=_10",
        "type": float,
        "formula": "{bamstats:number_of_uniquely_aligned_reads_with_q_>=_10}/{bamstats:total_number_of_reads}*100",
        "visible": True,
    },
    {
        "key": "Percentage of Uniquely Aligned Reads without Duplicates with Q>=10 [bamstats]",
        "tooltip": "Percentage of uniquely aligned reads without duplicates with Q>=10",
        "derived_from": "bamstats_postprocessed:percentage_number_of_uniquely_aligned_reads_without_dups_and_q_>=_10",
        "type": float,
        "formula": "{bamstats:number_of_uniquely_aligned_reads_without_dups_and_q_>=_10}/{bamstats:total_number_of_reads}*100",
        "visible": True,
    },
]

rnaseqc_calculated_metrics = [
    {
        "key": "Percentage of Chimeric Reads [RNA-SeQC]",
        "tooltip": "Percentage of chimeric reads out of mapped reads",
        "derived_from": "rnaseqc_postprocessed:percentage_chimeric_reads",
        "type": float,
        "formula": "{rnaseqc:chimeric_reads}/{rnaseqc:mapped_reads}*100",
        "visible": True,
    }
]
