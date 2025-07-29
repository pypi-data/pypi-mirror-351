from src.MetricsParser import (
    SAMTOOLS_STATS,
    BAMSTATS,
    RNASEQC,
    PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS,
    PICARD_COLLECT_INSERT_SIZE_METRICS,
    PICARD_COLLECT_WGS_METRICS,
    FASTQC,
    NANOPLOT,
    VERIFYBAMID,
    KRAKEN2,
    MOSDEPTH,
    SOMALIER,
    TISSUE_CLASSIFIER,
    PIGEON_FILTER_JSON
)


########################################################################
# Metrics to extract from the output of each tool
########################################################################

samtools_stats_metrics = {
    "raw total sequences": {
        "key": "Total Sequences [Samtools]",
        "tooltip": "Total number of reads in a file, excluding supplementary and secondary reads",
        "derived_from": "samtools_stats:raw_total_sequences",
        "type": int,
        "visible": True,
    },
    "average length": {
        "key": "Average Read Length [Samtools]",
        "tooltip": "Ratio between total length and sequences",
        "derived_from": "samtools_stats:average_length",
        "type": float,
        "visible": True,
    },
    "maximum length": {
        "key": "Maximum Read Length [Samtools]",
        "tooltip": "Length of the longest read (includes hard-clipped bases).",
        "derived_from": "samtools_stats:maximum_length",
        "type": int,
        "visible": True,
    },
    "bases mapped": {
        "key": "Bases Mapped [Samtools]",
        "tooltip": "Number of processed bases that belong to reads mapped",
        "derived_from": "samtools_stats:bases_mapped",
        "type": int,
    },
    "sequences": {
        "key": "Processed Sequences [Samtools]",
        "tooltip": "Number of processed reads",
        "derived_from": "samtools_stats:sequences",
        "type": int,
    },
    "1st fragments": {
        "key": "1st Fragments [Samtools]",
        "tooltip": "Number of first fragment reads",
        "derived_from": "samtools_stats:1st_fragments",
        "type": int,
    },
    "last fragments": {
        "key": "Last Fragments [Samtools]",
        "tooltip": "Number of last fragment reads",
        "derived_from": "samtools_stats:last_fragments",
        "type": int,
    },
    "reads paired": {
        "key": "Reads Paired [Samtools]",
        "tooltip": "Number of paired reads, mapped or unmapped, that are neither secondary nor supplementary (paired-end technology bit set)",
        "derived_from": "samtools_stats:reads_paired",
        "type": int,
    },
    "reads mapped": {
        "key": "Reads Mapped [Samtools]",
        "tooltip": "Number of reads, paired or single, that are mapped",
        "derived_from": "samtools_stats:reads_mapped",
        "type": int,
    },
    "reads mapped and paired": {
        "key": "Reads Mapped and Paired [Samtools]",
        "tooltip": "Number of mapped paired reads (paired-end technology bit set with both mates mapped)",
        "derived_from": "samtools_stats:reads_mapped_and_paired",
        "type": int,
    },
    "reads properly paired": {
        "key": "Reads Properly Paired [Samtools]",
        "tooltip": "Number of mapped paired reads (proper-pair bit set, both mates mapped within the expected distance)",
        "derived_from": "samtools_stats:reads_properly_paired",
        "type": int,
    },
    "reads unmapped": {
        "key": "Reads Unmapped [Samtools]",
        "tooltip": "Number of unmapped reads",
        "derived_from": "samtools_stats:reads_unmapped",
        "type": int,
    },
    "reads duplicated": {
        "key": "Reads Duplicated [Samtools]",
        "tooltip": "Number of duplicate reads",
        "derived_from": "samtools_stats:reads_duplicated",
        "type": int,
    },
    "reads MQ0": {
        "key": "Reads MQ0 [Samtools]",
        "tooltip": "Number of mapped reads with mapping quality 0",
        "derived_from": "samtools_stats:reads_MQ0",
        "type": int,
    },
    "reads QC failed": {
        "key": "Reads QC-Failed [Samtools]",
        "tooltip": "Number of reads that failed the quality checks",
        "derived_from": "samtools_stats:reads_QC_failed",
        "type": int,
    },
    "non-primary alignments": {
        "key": "Non-Primary Alignments [Samtools]",
        "tooltip": "Number of secondary reads",
        "derived_from": "samtools_stats:non_primary_alignments",
        "type": int,
    },
    "supplementary alignments": {
        "key": "Supplementary Alignments [Samtools]",
        "tooltip": "Number of supplementary reads",
        "derived_from": "samtools_stats:supplementary_alignments",
        "type": int,
    },
    "pairs on different chromosomes": {
        "key": "Pairs on Different Chromosomes [Samtools]",
        "tooltip": "Number of pairs where one read is on one chromosome and the mate read is on a different chromosome",
        "derived_from": "samtools_stats:pairs_on_different_chromosomes",
        "type": int,
    },
    "percentage of properly paired reads (%)": {
        "key": "Percentage of Properly Paired Reads [Samtools]",
        "tooltip": "Percentage of properly paired reads",
        "derived_from": "samtools_stats:percentage_of_properly_paired_reads",
        "type": float,
        "visible": True,
    },
}

picard_CollectAlignmentSummaryMetrics_metrics = {
    "PF_ALIGNED_BASES": {
        "key": "Aligned Bases [Picard]",
        "tooltip": "The total number of aligned bases",
        "derived_from": "picard_collect_alignment_summary_metrics:pf_aligned_bases",
        "type": int,
    },
    "PF_HQ_ALIGNED_BASES": {
        "key": "Aligned Bases (High Quality) [Picard]",
        "tooltip": "The number of aligned bases in reads that were mapped at high quality",
        "derived_from": "picard_collect_alignment_summary_metrics:pf_hq_aligned_bases",
        "type": int,
    },
    "PF_MISMATCH_RATE": {
        "key": "Aligned Bases Mismatch Rate [Picard]",
        "tooltip": "The fraction of bases mismatching the reference for all aligned bases",
        "derived_from": "picard_collect_alignment_summary_metrics:pf_mismatch_rate",
        "type": float,
        "visible": True,
    },
    "PF_HQ_ERROR_RATE": {
        "key": "Aligned Bases Mismatch Rate (High Quality) [Picard]",
        "tooltip": "The fraction of bases mismatching the reference in reads that were mapped at high quality",
        "derived_from": "picard_collect_alignment_summary_metrics:pf_hq_error_rate",
        "type": float,
    },
    "PF_INDEL_RATE": {
        "key": "Indel Rate [Picard]",
        "tooltip": "The number of insertion and deletion events per 100 aligned bases",
        "derived_from": "picard_collect_alignment_summary_metrics:pf_indel_rate",
        "type": float,
        "visible": True,
    },
    "MEAN_READ_LENGTH": {
        "key": "Mean Read Length [Picard]",
        "tooltip": "The mean length of the set of reads examined",
        "derived_from": "picard_collect_alignment_summary_metrics:mean_read_length",
        "type": float,
    },
    "SD_READ_LENGTH": {
        "key": "Read Length Standard Deviation [Picard]",
        "tooltip": "The standard deviation for the length of the set of reads examined",
        "derived_from": "picard_collect_alignment_summary_metrics:sd_read_length",
        "type": float,
    },
}

picard_CollectInsertSizeMetrics_metrics = {
    # [5]
    "MEAN_INSERT_SIZE": {
        "key": "Mean Insert Size [Picard]",
        "tooltip": "The mean insert size for the FR read pairs",
        "derived_from": "picard_collect_insert_size_metrics:mean_insert_size",
        "type": float,
    },
    # [6]
    "STANDARD_DEVIATION": {
        "key": "Insert Size Standard Deviation [Picard]",
        "tooltip": "Standard deviation of insert sizes for the FR read pairs",
        "derived_from": "picard_collect_insert_size_metrics:standard_deviation",
        "type": float,
    },
    # [7]
    "READ_PAIRS": {
        "key": "Total Number of Read Pairs [Picard]",
        "tooltip": "The total number of read pairs that were examined for the FR read pairs",
        "derived_from": "picard_collect_insert_size_metrics:read_pairs",
        "type": int,
    },
    # 'PAIR_ORIENTATION' [8]
}

picard_CollectWgsMetrics_metrics = {
    "MEAN_COVERAGE": {
        "key": "Mean Coverage (chr22) [Picard]",
        "tooltip": "The mean coverage of the genome (approximation using chr22 only)",
        "derived_from": "picard_collect_wgs_metrics:mean_coverage",
        "type": float,
        "visible": True,
    },
    "SD_COVERAGE": {
        "key": "Coverage Standard Deviation (chr22) [Picard]",
        "tooltip": "The standard deviation for the coverage (approximation using chr22 only)",
        "derived_from": "picard_collect_wgs_metrics:sd_coverage",
        "type": float,
        "visible": True,
    },
}

bamstats_metrics = {
    "Estimate_Average_Coverage": {
        "key": "Estimated Average Coverage [bamstats]",
        "tooltip": "Estimated average coverage",
        "derived_from": "bamstats:estimate_average_coverage",
        "type": float,
        "visible": True,
    },
    "Total_Number_Of_Reads": {
        "key": "Total Number of Reads [bamstats]",
        "tooltip": "Total number of reads",
        "derived_from": "bamstats:total_number_of_reads",
        "type": int,
    },
    "Number_of_Uniquely_Aligned_Reads_with_Q_>=_10": {
        "key": "Uniquely Aligned Reads with Q>=10 [bamstats]",
        "tooltip": "Uniquely aligned reads with Q>=10",
        "derived_from": "bamstats:number_of_uniquely_aligned_reads_with_q_>=_10",
        "type": int,
    },
    "Number_of_Uniquely_Aligned_Reads_without_Dups_and_Q_>=_10": {
        "key": "Uniquely Aligned Reads without Duplicates with Q>=10 [bamstats]",
        "tooltip": "Uniquely aligned reads without duplicates with Q>=10",
        "derived_from": "bamstats:number_of_uniquely_aligned_reads_without_dups_and_q_>=_10",
        "type": int,
    },
}

rnaseqc_metrics = {
    "3' bias MAD_Std": {
        "key": "3' Bias, MAD Std [RNA-SeQC]",
        "tooltip": "3' Bias statistics (Median Absolute Deviation): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:3p_bias_mad_std",
        "type": float,
    },
    "3' bias Std": {
        "key": "3' Bias, Std [RNA-SeQC]",
        "tooltip": "3' Bias statistics (Std Deviation): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:3p_bias_std",
        "type": float,
    },
    "3' Bias, 25th Percentile": {
        "key": "3' Bias, 25th Percentile [RNA-SeQC]",
        "tooltip": "3' Bias statistics (25th percentile): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:3p_bias_25th_percentile",
        "type": float,
    },
    "3' Bias, 75th Percentile": {
        "key": "3' Bias, 75th Percentile [RNA-SeQC]",
        "tooltip": "3' Bias statistics (75th percentile): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:3p_bias_75th_percentile",
        "type": float,
    },
    "Genes used in 3' bias": {
        "key": "Genes used in 3' Bias [RNA-SeQC]",
        "tooltip": "The number of genes used in calculating 3' Bias statistics",
        "derived_from": "rnaseqc:genes_used_in_3p_bias",
        "type": int,
    },
    "Mean 3' bias": {
        "key": "Mean 3' Bias [RNA-SeQC]",
        "tooltip": "3' Bias statistics (Mean): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:mean_3p_bias",
        "type": float,
    },
    "Median 3' bias": {
        "key": "Median 3' Bias [RNA-SeQC]",
        "tooltip": "3' Bias statistics (Median): These aggregate statistics are based on the total coverage in 100 bp windows on both the 3' and 5' ends of a gene. The windows are both offset 150 bases into the gene. This computation is only performed on genes at least 600bp long and with at least 5 unambiguous reads. A gene with even coverage in both it's 3' and 5' windows would have a bias of 0.5; bias near 1 or 0 may indicate degradation",
        "derived_from": "rnaseqc:median_3p_bias",
        "type": float,
        "visible": True,
    },
    "Alternative Alignments": {
        "key": "Alternative Alignments [RNA-SeQC]",
        "tooltip": "The number of duplicate read entries providing alternative coordinates",
        "derived_from": "rnaseqc:alternative_alignments",
        "type": int,
    },
    "Base Mismatch": {
        "key": "Base Mismatch [RNA-SeQC]",
        "tooltip": 'The total number of mismatched bases (as determined by the "NM" tag) of all mapped reads divided by the total aligned length of all mapped reads',
        "derived_from": "rnaseqc:base_mismatch",
        "type": float,
    },
    "Chimeric Reads": {
        "key": "Chimeric Reads [RNA-SeQC]",
        "tooltip": "The number of chimeric reads",
        "derived_from": "rnaseqc:chimeric_reads",
        "type": int,
    },
    "Duplicate Rate of Mapped": {
        "key": "Duplicate Rate of Mapped [RNA-SeQC]",
        "tooltip": "The proportion of all reads which were marked as PCR/optical duplicates out of all mapped reads; excludes secondary and vendor QC failed reads",
        "derived_from": "rnaseqc:duplicate_rate_of_mapped",
        "type": float,
    },
    "End 1 Antisense": {
        "key": "End 1 Antisense [RNA-SeQC]",
        "tooltip": "The number of reads marked as First in the pair that were sequenced in the antisense direction",
        "derived_from": "rnaseqc:end_1_antisense",
        "type": int,
    },
    "End 1 Mapping Rate": {
        "key": "End 1 Mapping Rate [RNA-SeQC]",
        "tooltip": "The proportion of paired reads which were marked as First in the pair out of all mapped reads",
        "derived_from": "rnaseqc:end_1_mapping_rate",
        "type": float,
    },
    "End 1 Mismatch Rate": {
        "key": "End 1 Mismatch Rate [RNA-SeQC]",
        "tooltip": 'The proportion of mismatched bases (as determined by the "NM" tag) belonging to reads marked as First in the pair, divided by the total aligned length of all mapped reads marked as First in the pair',
        "derived_from": "rnaseqc:end_1_mismatch_rate",
        "type": float,
    },
    "End 1 Sense": {
        "key": "End 1 Sense [RNA-SeQC]",
        "tooltip": "The number of reads marked as First in the pair that were sequenced in the sense direction",
        "derived_from": "rnaseqc:end_1_sense",
        "type": int,
    },
    "End 1 Sense Rate": {
        "key": "End 1 Sense Rate [RNA-SeQC]",
        "tooltip": "The proportion of reads marked as First in the pair which intersected with a Sense Strand feature out of all reads marked as First in the pair which intersected with any features",
        "derived_from": "rnaseqc:end_1_sense_rate",
        "type": float,
    },
    "End 2 Antisense": {
        "key": "End 2 Antisense [RNA-SeQC]",
        "tooltip": "The number of reads marked as Second in the pair that were sequenced in the antisense direction",
        "derived_from": "rnaseqc:end_2_antisense",
        "type": int,
    },
    "End 2 Mapping Rate": {
        "key": "End 2 Mapping Rate [RNA-SeQC]",
        "tooltip": "The proportion of paired reads which were marked as Second in the pair out of all mapped reads",
        "derived_from": "rnaseqc:end_2_mapping_rate",
        "type": float,
    },
    "End 2 Mismatch Rate": {
        "key": "End 2 Mismatch Rate [RNA-SeQC]",
        "tooltip": 'The proportion of mismatched bases (as determined by the "NM" tag) belonging to reads marked as Second in the pair, divided by the total aligned length of all mapped reads marked as Second in the pair',
        "derived_from": "rnaseqc:end_2_mismatch_rate",
        "type": float,
    },
    "End 2 Sense": {
        "key": "End 2 Sense [RNA-SeQC]",
        "tooltip": "The number of reads marked as Second in the pair that were sequenced in the sense direction",
        "derived_from": "rnaseqc:end_2_sense",
        "type": int,
    },
    "End 2 Sense Rate": {
        "key": "End 2 Sense Rate [RNA-SeQC]",
        "tooltip": "The proportion of reads marked as Second in the pair which intersected with a Sense Strand feature out of all reads marked as Second in the pair which intersected with any features",
        "derived_from": "rnaseqc:end_2_sense_rate",
        "type": float,
    },
    "Estimated Library Complexity": {
        "key": "Estimated Library Complexity [RNA-SeQC]",
        "tooltip": "An estimation of the number of unique cDNA fragments present in the library. This computation follows the same formula as Picard EstimateLibraryComplexity",
        "derived_from": "rnaseqc:estimated_library_complexity",
        "type": int,
        "visible": True,
    },
    "Exonic Rate": {
        "key": "Exonic Rate [RNA-SeQC]",
        "tooltip": "The proportion of mapped reads for which all aligned segments unambiguously aligned to exons of the same gene",
        "derived_from": "rnaseqc:exonic_rate",
        "type": float,
    },
    "Exonic/Intron ratio": {
        "key": "Exonic/Intron Ratio [RNA-SeQC]",
        "tooltip": "The proportion of exonic and intronic reads",
        "derived_from": "rnaseqc:exonic_intron_ratio",
        "type": float,
        "visible": True,
    },
    "Expression Profiling Efficiency": {
        "key": "Expression Profiling Efficiency [RNA-SeQC]",
        "tooltip": 'The proportion of exonic reads (see "Exonic Rate") out of all reads which were not secondary alignments or platform/vendor QC failing reads',
        "derived_from": "rnaseqc:expression_profiling_efficiency",
        "type": float,
    },
    "Exons with >0 reads": {
        "key": "Exons with >0 Reads [RNA-SeQC]",
        "tooltip": "The number of exons with >0 reads",
        "derived_from": "rnaseqc:exons_with_>0_reads",
        "type": int,
    },
    "Exons with >=2 reads": {
        "key": "Exons with >=2 Reads [RNA-SeQC]",
        "tooltip": "The number of exons with >=2 reads",
        "derived_from": "rnaseqc:exons_with_>2_reads",
        "type": int,
    },
    "Exons with >=10 reads": {
        "key": "Exons with >=10 Reads [RNA-SeQC]",
        "tooltip": "The number of exons with >=10 reads",
        "derived_from": "rnaseqc:exons_with_>10_reads",
        "type": int,
    },
    "Failed Vendor QC": {
        "key": "Failed Vendor QC [RNA-SeQC]",
        "tooltip": "The number of reads that failed vendor QC",
        "derived_from": "rnaseqc:failed_vendor_qc",
        "type": int,
    },
    "Genes Detected": {
        "key": "Genes Detected [RNA-SeQC]",
        "tooltip": "The number of genes which had at least 5 unambiguous reads",
        "derived_from": "rnaseqc:genes_detected",
        "type": int,
        "visible": True,
    },
    "Genes with >0 reads": {
        "key": "Genes with >0 Reads [RNA-SeQC]",
        "tooltip": "The number of genes with >0 reads",
        "derived_from": "rnaseqc:genes_with_>0_reads",
        "type": int,
    },
    "Genes with >=2 reads": {
        "key": "Genes with >=2 Reads [RNA-SeQC]",
        "tooltip": "The number of genes with >=2 reads",
        "derived_from": "rnaseqc:genes_with_>2_reads",
        "type": int,
    },
    "Genes with >=10 reads": {
        "key": "Genes with >=10 Reads [RNA-SeQC]",
        "tooltip": "The number of genes with >=10 reads",
        "derived_from": "rnaseqc:genes_with_>10_reads",
        "type": int,
    },
    "Intergenic Rate": {
        "key": "Intergenic Rate [RNA-SeQC]",
        "tooltip": "The proportion of mapped reads for which none of the aligned segments intersected any genes",
        "derived_from": "rnaseqc:intergenic_rate",
        "type": float,
        "visible": True,
    },
    "Intragenic Rate": {
        "key": "Intragenic Rate [RNA-SeQC]",
        "tooltip": 'The sum of exonic and intronic rates (see "Exonic Rate" and "Intronic Rate")',
        "derived_from": "rnaseqc:intragenic_rate",
        "type": float,
        "visible": True,
    },
    "Intronic Rate": {
        "key": "Intronic Rate [RNA-SeQC]",
        "tooltip": "The proportion of mapped reads for which all aligned segments unambiguously aligned to the same gene, but none of which intersected any exons of the gene",
        "derived_from": "rnaseqc:intronic_rate",
        "type": float,
        "visible": True,
    },
    "Mapped Reads": {
        "key": "Mapped Reads [RNA-SeQC]",
        "tooltip": "The number of mapped reads",
        "derived_from": "rnaseqc:mapped_reads",
        "type": int,
        "visible": True,
    },
    "Mapped Unique Reads": {
        "key": "Mapped Unique Reads [RNA-SeQC]",
        "tooltip": "The number of uniquely mapped reads",
        "derived_from": "rnaseqc:mapped_unique_reads",
        "type": int,
    },
    "Mapping Rate": {
        "key": "Mapping Rate [RNA-SeQC]",
        "tooltip": "The proportion of all reads which were mapped, and not secondary alignments or platform/vendor QC failing reads",
        "derived_from": "rnaseqc:mapping_rate",
        "type": float,
        "visible": True,
    },
    "Read Length": {
        "key": "Read Length [RNA-SeQC]",
        "tooltip": "The longest aligned length observed in any read",
        "derived_from": "rnaseqc:read_length",
        "type": int,
    },
    "rRNA Rate": {
        "key": "rRNA Rate [RNA-SeQC]",
        "tooltip": 'The proportion of mapped reads (see "Mapped Reads") which at least partially intersected with an annotated rRNA gene',
        "derived_from": "rnaseqc:rrna_rate",
        "type": float,
        "visible": True,
    },
    "rRNA Reads": {
        "key": "rRNA Reads [RNA-SeQC]",
        "tooltip": "The number of rRNA reads",
        "derived_from": "rnaseqc:rrna_reads",
        "type": int,
    },
    "Total Mapped Pairs": {
        "key": "Total Mapped Pairs [RNA-SeQC]",
        "tooltip": "The number of total mapped pairs",
        "derived_from": "rnaseqc:total_mapped_pairs",
        "type": int,
        "visible": True,
    },
    "Total Reads": {
        "key": "Total Alignments [RNA-SeQC]",
        "tooltip": "The number of total alignments, including secondary alignments or platform/vendor QC failing reads",
        "derived_from": "rnaseqc:total_reads",
        "type": int,
        "visible": True,
    },
    "Unique Rate of Mapped": {
        "key": "Unique Rate of Mapped [RNA-SeQC]",
        "tooltip": "The proportion of reads which were not marked as PCR/optical duplicates out of all mapped reads",
        "derived_from": "rnaseqc:unique_rate_of_mapped",
        "type": float,
    },
    "Unpaired Reads": {
        "key": "Unpaired Reads [RNA-SeQC]",
        "tooltip": "The number of unpaired reads",
        "derived_from": "rnaseqc:unpaired_reads",
        "type": int,
    },
}

fastqc_metrics = {
    "Basic Statistics": {
        "key": "Basic Statistics [FastQC]",
        "tooltip": "Basic statistics for the file analyzed",
        "derived_from": "fastqc:basic_statistics",
        "type": str,
    },
    "Per base sequence quality": {
        "key": "Per Base Sequence Quality [FastQC]",
        "tooltip": "The mean quality value (Phred Score) across each base position in the read",
        "derived_from": "fastqc:per_base_sequence_quality",
        "type": str,
    },
    "Per tile sequence quality": {
        "key": "Per Tile Sequence Quality [FastQC]",
        "tooltip": "The quality scores from each tile across all of bases",
        "derived_from": "fastqc:per_tile_sequence_quality",
        "type": str,
    },
    "Per sequence quality scores": {
        "key": "Per Sequence Quality Scores [FastQC]",
        "tooltip": "The number of reads with average quality scores",
        "derived_from": "fastqc:per_sequence_quality_scores",
        "type": str,
    },
    "Per base sequence content": {
        "key": "Per Base Sequence Content [FastQC]",
        "tooltip": "The proportion of each base position for which each of the four normal DNA bases has been called",
        "derived_from": "fastqc:per_base_sequence_content",
        "type": str,
    },
    "Per sequence GC content": {
        "key": "Per Sequence GC Content [FastQC]",
        "tooltip": "The average GC content of reads",
        "derived_from": "fastqc:per_sequence_gc_content",
        "type": str,
    },
    "Per base N content": {
        "key": "Per Base N Content [FastQC]",
        "tooltip": "The percentage of base calls at each position for which an N was called",
        "derived_from": "fastqc:per_base_n_content",
        "type": str,
    },
    "Sequence Length Distribution": {
        "key": "Sequence Length Distribution [FastQC]",
        "tooltip": "The distribution of sequence length over all sequences",
        "derived_from": "fastqc:sequence_length_distribution",
        "type": str,
    },
    "Sequence Duplication Levels": {
        "key": "Sequence Duplication Levels [FastQC]",
        "tooltip": "The relative level of duplication found for every sequence",
        "derived_from": "fastqc:sequence_duplication_levels",
        "type": str,
    },
    "Overrepresented sequences": {
        "key": "Overrepresented Sequences [FastQC]",
        "tooltip": "The total amount of overrepresented sequences",
        "derived_from": "fastqc:overrepresented_sequences",
        "type": str,
    },
    "Adapter Content": {
        "key": "Adapter Content [FastQC]",
        "tooltip": "The cumulative percentage of adapter sequences at each position",
        "derived_from": "fastqc:adapter_content",
        "type": str,
    },
    "Total Sequences": {
        "key": "Total Sequences [FastQC]",
        "tooltip": "Total number of sequences",
        "derived_from": "fastqc:total_sequences",
        "type": int,
    },
    "Sequence Length": {
        "key": "Sequence Length [FastQC]",
        "tooltip": "Length of sequences",
        "derived_from": "fastqc:sequence_length",
        "type": [int, str],
    },
}

nanoplot_metrics = {
    "Mean read length": {
        "key": "Mean Read Length [NanoPlot]",
        "tooltip": "Mean length of the reads",
        "derived_from": "nanoplot:mean_read_length",
        "type": float,
    },
    "Mean read quality": {
        "key": "Mean Read Quality [NanoPlot]",
        "tooltip": "Mean quality of the reads",
        "derived_from": "nanoplot:mean_read_quality",
        "type": float,
    },
    "Median read length": {
        "key": "Median Read Length [NanoPlot]",
        "tooltip": "Median length of the reads",
        "derived_from": "nanoplot:median_read_length",
        "type": float,
    },
    "Median read quality": {
        "key": "Median Read Quality [NanoPlot]",
        "tooltip": "Median quality of the reads",
        "derived_from": "nanoplot:median_read_quality",
        "type": float,
    },
    "Number of reads": {
        "key": "Reads Number [NanoPlot]",
        "tooltip": "Total number of reads",
        "derived_from": "nanoplot:number_of_reads",
        "type": int,
    },
    "Read length N50": {
        "key": "Read Length N50 [NanoPlot]",
        "tooltip": "Read length N50. Represents the length of the shortest read in the group of longest sequences that together represent (at least) 50% of the nucleotides in the set of sequences",
        "derived_from": "nanoplot:read_length_n50",
        "type": float,
    },
    "STDEV read length": {
        "key": "Read Length STDEV [NanoPlot]",
        "tooltip": "Standard deviation of the reads length",
        "derived_from": "nanoplot:stdev_read_length",
        "type": float,
    },
    "Total bases": {
        "key": "Total Bases [NanoPlot]",
        "tooltip": "Total number of bases",
        "derived_from": "nanoplot:total_bases",
        "type": int,
    },
    ">Q5": {
        "key": "Reads >Q5 [NanoPlot]",
        "tooltip": "Percentage of reads above quality Q5",
        "derived_from": "nanoplot:percentage_reads_above_q5",
        "type": float,
    },
    ">Q7": {
        "key": "Reads >Q7 [NanoPlot]",
        "tooltip": "Percentage of reads above quality Q7",
        "derived_from": "nanoplot:percentage_reads_above_q7",
        "type": float,
    },
    ">Q10": {
        "key": "Reads >Q10 [NanoPlot]",
        "tooltip": "Percentage of reads above quality Q10",
        "derived_from": "nanoplot:percentage_reads_above_q10",
        "type": float,
    },
    ">Q12": {
        "key": "Reads >Q12 [NanoPlot]",
        "tooltip": "Percentage of reads above quality Q12",
        "derived_from": "nanoplot:percentage_reads_above_q12",
        "type": float,
    },
    ">Q15": {
        "key": "Reads >Q15 [NanoPlot]",
        "tooltip": "Percentage of reads above quality Q15",
        "derived_from": "nanoplot:percentage_reads_above_q15",
        "type": float,
    },
}

verifybamid_metrics = {
    "FREEMIX(Alpha)": {
        "key": "Estimate of Contamination [VerifyBamID2]",
        "tooltip": "Sequence-only estimate of contamination (0-1 scale)",
        "derived_from": "verifybamid:freemix_alpha",
        "type": float,
    },
}

kraken2_metrics = {
    9606: { # NCBI taxonomic ID number
        "key": "Percentage Human Sequences [Kraken2]",
        "tooltip": "Percentage of reads classified as Homo Sapiens",
        "derived_from": "kraken2:taxonomic_id_9606",
        "type": float,
    },
    2: { # NCBI taxonomic ID number
        "key": "Percentage Bacterial Sequences [Kraken2]",
        "tooltip": "Percentage of reads classified as Bacteria",
        "derived_from": "kraken2:taxonomic_id_2",
        "type": float,
    },
    10239: { # NCBI taxonomic ID number
        "key": "Percentage Viral Sequences [Kraken2]",
        "tooltip": "Percentage of reads classified as Viruses",
        "derived_from": "kraken2:taxonomic_id_10239",
        "type": float,
    },
}

mosdepth_metrics = {
    "total": {
        "key": "Estimated Average Coverage [mosdepth]",
        "tooltip": "Estimated average coverage",
        "derived_from": "mosdepth:total",
        "type": float,
    },
}

somalier_metrics = {
    "relatedness": {
        "key": "Identity Check [Somalier]",
        "tooltip": "Identity check results based on estimated relatedness. Marked as FAILED if any sample shows no relatedness",
        "derived_from": "somalier:relatedness",
        "type": str,
    }
}

tissue_classifier_metrics = {
    "Predicted tissue 1": {
        "key": "Predicted Tissue 1 [Tissue Classifier]",
        "tooltip": "Predicted tissue from gene expression TPM values (highest probability)",
        "derived_from": "tissue_classifier:predicted_tissue_1",
        "type": str,
    },
    "Probability predicted tissue 1": {
        "key": "Probability of Predicted Tissue 1 [Tissue Classifier]",
        "tooltip": "Probability of predicted tissue 1",
        "derived_from": "tissue_classifier:probability_predicted_tissue_1",
        "type": float,
    },
    "Predicted tissue 2": {
        "key": "Predicted Tissue 2 [Tissue Classifier]",
        "tooltip": "Predicted tissue from gene expression TPM values (2nd highest probability)",
        "derived_from": "tissue_classifier:predicted_tissue_2",
        "type": str,
    },
    "Probability predicted tissue 2": {
        "key": "Probability of Predicted Tissue 2 [Tissue Classifier]",
        "tooltip": "Probability of predicted tissue 2",
        "derived_from": "tissue_classifier:probability_predicted_tissue_2",
        "type": float,
    },
     "Predicted tissue 3": {
        "key": "Predicted Tissue 3 [Tissue Classifier]",
        "tooltip": "Predicted tissue from gene expression TPM values (3rd highest probability)",
        "derived_from": "tissue_classifier:predicted_tissue_3",
        "type": str,
    },
    "Probability predicted tissue 3": {
        "key": "Probability of Predicted Tissue 3 [Tissue Classifier]",
        "tooltip": "Probability of predicted tissue 3",
        "derived_from": "tissue_classifier:probability_predicted_tissue_3",
        "type": float,
    },
}

pigeon_filter_json_metrics = {
    "total_unique_genes": {
        "key": "Unique Genes [Pigeon]",
        "tooltip": "Number of unique genes",
        "derived_from": "pigeon_filter_json:total_unique_genes",
        "type": int,
    },
    "total_unique_genes_known": {
        "key": "Known Unique Genes [Pigeon]",
        "tooltip": "Number of known unique genes",
        "derived_from": "pigeon_filter_json:total_unique_genes_known",
        "type": int,
    },
    "total_unique_transcripts": {
        "key": "Unique Transcripts [Pigeon]",
        "tooltip": "Number of unique transcripts",
        "derived_from": "pigeon_filter_json:total_unique_transcripts",
        "type": int,
    },
    "total_unique_transcripts_known": {
        "key": "Known Unique Transcripts [Pigeon]",
        "tooltip": "Number of known unique transcripts",
        "derived_from": "pigeon_filter_json:total_unique_transcripts_known",
        "type": int,
    },
    "total_unique_transcripts_novel_greater_1tpm": {
        "key": "Novel Unique Transcripts > 1TMP [Pigeon]",
        "tooltip": "Number of novel unique transcripts > 1 TPM",
        "derived_from": "pigeon_filter_json:total_unique_transcripts_novel_greater_1tpm",
        "type": int,
    },
    "flnc_mapped_genome": {
        "key": "FLNC Mapped Genome [Pigeon]",
        "tooltip": "Number of full-length non-chimeric reads mapped to genome",
        "derived_from": "pigeon_filter_json:flnc_mapped_genome",
        "type": int,
    },
    "flnc_mapped_transcriptome": {
        "key": "FLNC Mapped Transcriptome [Pigeon]",
        "tooltip": "Number of full-length non-chimeric reads mapped to transcriptome",
        "derived_from": "pigeon_filter_json:flnc_mapped_transcriptome",
        "type": int,
    },
    "flnc_mapped_transcriptome_excluding_ribomito": {
        "key": "FLNC Mapped Transcriptome, NO Ribosomal-Mitochondria [Pigeon]",
        "tooltip": "Number of full-length non-chimeric reads mapped to transcriptome, excluding ribosomal and mitochondria",
        "derived_from": "pigeon_filter_json:flnc_mapped_transcriptome_excluding_ribomito",
        "type": int,
    },
    "transcripts_fsm": {
        "key": "Transcripts FSM [Pigeon]",
        "tooltip": "Number of transcripts classified as full-splice matches",
        "derived_from": "pigeon_filter_json:transcripts_fsm",
        "type": int,
    },
    "transcripts_ism": {
        "key": "Transcripts ISM [Pigeon]",
        "tooltip": "Number of transcripts classified as incomplete-splice matches",
        "derived_from": "pigeon_filter_json:transcripts_ism",
        "type": int,
    },
    "transcripts_nic": {
        "key": "Transcripts NIC [Pigeon]",
        "tooltip": "Number of transcripts classified as novel in catalog",
        "derived_from": "pigeon_filter_json:transcripts_nic",
        "type": int,
    },
    "transcripts_nnc": {
        "key": "Transcripts NNC [Pigeon]",
        "tooltip": "Number of transcripts classified as novel NOT in catalog",
        "derived_from": "pigeon_filter_json:transcripts_nnc",
        "type": int,
    },
    "percent_reads_fsm": {
        "key": "Reads FSM [Pigeon]",
        "tooltip": "Percentage of reads classified as full-splice matches",
        "derived_from": "pigeon_filter_json:percent_reads_fsm",
        "type": float,
    },
    "percent_reads_ism": {
        "key": "Reads ISM [Pigeon]",
        "tooltip": "Percentage of reads classified as incomplete-splice matches",
        "derived_from": "pigeon_filter_json:percent_reads_ism",
        "type": float,
    },
    "percent_reads_nic": {
        "key": "Reads NIC [Pigeon]",
        "tooltip": "Percentage of reads classified as novel in catalog",
        "derived_from": "pigeon_filter_json:percent_reads_nic",
        "type": float,
    },
    "percent_reads_nnc": {
        "key": "Reads NNC [Pigeon]",
        "tooltip": "Percentage of reads classified as novel NOT in catalog",
        "derived_from": "pigeon_filter_json:percent_reads_nnc",
        "type": float,
    },
}

metrics = {
    SAMTOOLS_STATS: samtools_stats_metrics,
    BAMSTATS: bamstats_metrics,
    RNASEQC: rnaseqc_metrics,
    PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS: picard_CollectAlignmentSummaryMetrics_metrics,
    PICARD_COLLECT_INSERT_SIZE_METRICS: picard_CollectInsertSizeMetrics_metrics,
    PICARD_COLLECT_WGS_METRICS: picard_CollectWgsMetrics_metrics,
    FASTQC: fastqc_metrics,
    NANOPLOT: nanoplot_metrics,
    VERIFYBAMID: verifybamid_metrics, 
    KRAKEN2: kraken2_metrics,
    MOSDEPTH: mosdepth_metrics,
    SOMALIER: somalier_metrics,
    TISSUE_CLASSIFIER: tissue_classifier_metrics,
    PIGEON_FILTER_JSON: pigeon_filter_json_metrics
}
