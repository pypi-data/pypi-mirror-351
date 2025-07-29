# CryEx

(This repository is private for now)
Paper Link: 

CryEx is a Python-based pipeline designed to identify and quantify cryptic exons from RNA-Seq datasets. The pipeline leverages StringTie for transcript assembly and detects cryptic exons.

**Highlights:**

●	A user-friendly python package for CryEx protocol to construct a comprehensive splicing landscape 

●	Identification and quantification of cryptic exons and annotated exons using RNA-Seq data

●	Customizable filtering parameters to enable differential splicing analysis at different resolutions

●	A framework for implementing data preprocessing, analysis, customization and visualization

<p align="center">
  <img src="CryEx_diagram.png" alt="CryEx Logo" width="66%" height="66%" />
</p>

## Table of Contents 📚
- [Installation 🔧](#installation-)
- [Usage 🚀](#usage-)
- [Input 📥](#input-)
- [Output 📤](#output-)
- [Troubleshooting 🛠️](#troubleshooting-)

## Installation 🔧 

Installation from the GitHub repository:

```
git clone https://github.com/giovanniquinones/CryEx
cd CryEx

# create a virtual environment from yaml file
conda env create -f cryex_env.yaml
conda activate CryEx_env

# install the package
pip install .
export PATH=/path/to/bin:$PATH 
```

Installation from PyPI:

```
pip install CryEx.v2
```

It is recommended to create a virtual environment before using `pip install` to obtain the dependencies.

### Dependencies 📦
- Python 3.8+
- stringtie
- multiprocess
- numpy
- pandas
- pysam
- subprocess

## Usage 🚀

After installation, you can use the CryEx command line tools. Below is an example of how to run the pipeline:

```
# Check if installed successfully
CryEx_stringtie --help 

# Identify cryptic and annotated exons
CryEx_stringtie -f ${FOFN.tsv} -o ${EXONS.GTF}

# Calculate splice junction usage
CryEx_junctions -f ${FOFN.tsv} -o ${JXN.BED}

# Calculate PSI
CryEx_psi_calculator -f ${FOFN.tsv} -e ${EXONS.GTF} -j ${JXN.BED.GZ} -o {PSI.TSV} 

# Calculate diffential splicing
CryEx_diff -f ${FOFN.tsv} -p {PSI.TSV} -o {DIFF.tsv}
```

An example of this pipeline can be found in the `test_data` directory of this repository.

## Input 📥 

FOFN should be tab separated and have the following columns:

```
SAMPLE	    BAM	                    STAR_SJ_OUT	                    GROUP
sample1    /path/to/sample1.bam     /path/to/sample1.SJ.out.tab     CTRL
sample2    /path/to/sample2.bam     /path/to/sample2.SJ.out.tab     KD
sample3    /path/to/sample3.bam     /path/to/sample3.SJ.out.tab     CTRL
sample4	   /path/to/sample4.bam     /path/to/sample4.SJ.out.tab     KD
```

If STAR_SJ_OUT is not provided, fill in with `na`.
For differential splicing, Cryex will use the 'GROUP' column.

## Output 📤

- CryEx_stringtie will output a standard GTF file with the identified cryptic and annotated exons.
- CryEx_junctions will output a BED file with the splice junctions and their usage.

```
chr21	9826943	    9826984	    hte1,hte2,hte3,hte4     10,1,7,11	+
chr21	9827330	    9874067	    hte1,hte2,hte3,hte4     1,0,0,0     +
chr21	9907492	    9908277	    hte1,hte2,hte3,hte4     63,47,35,49	-
chr21	9907462	    9909046	    hte1,hte2,hte3,hte4     1,0,0,0     -
chr21	9908432	    9909046	    hte1,hte2,hte3,hte4     12,19,11,8	-
```

- CryEx_psi_calculator will output a TSV file with the PSI values for each cryptic exon.

```
exon_type       chrom   exon_3ss    exon_5ss    strand  inclusion_n     exc_5ss exc_3ss exclusion_n SAMPLE  PSI
first_exon      chr21   9907191     9907492     -       97              9896772 9966321 1           r2      0.96
first_exon      chr21   9907191     9907492     -       67              9896772 9966321 0           r3      1.0
first_exon      chr21   9907191     9907492     -       99              9896772 9966321 0           r4      1.0
first_exon      chr21   9907191     9907492     -       97              9896772 9966321 3           r2      0.92
first_exon      chr21   9907191     9907492     -       67              9896772 9966321 0           r3      1.0
first_exon      chr21   9907191     9907492     -       99              9896772 9966321 0           r4      1.0
```
- CryEx_diff will output a TSV file with the differential splicing results.

```
exon_type	exon_coords	                flanking_jxns	    LLR     Pvalue	    Sig	    DeltaPSI    DIFF    PSIGroup1	PSIGroup2	CovGroup1	CovGroup2	Pvalue_Adj
last_exon	chr21:45458057-45462429:+	45457808,45472160	2.49	2.57e-02	True	-0.54	    ctrl-kd	0.01,0.02	0.56,0.54	238,219	    285,323	    1.00e+00
last_exon	chr21:45458057-45462454:+	45457808,45472160	2.49	2.57e-02	True	-0.54	    ctrl-kd	0.01,0.02	0.56,0.54	238,219	    285,323	    1.00e+00
first_exon	chr21:45514756-45516594:+	45514114,45518237	2.332	3.08e-02	True	-0.26	    ctrl-kd	0.02,0.02	0.2,0.36	206,210	    74,50	    1.00e+00
first_exon	chr21:45515067-45516594:+	45514114,45518237	2.332	3.08e-02	True	-0.28	    ctrl-kd	0.02,0.02	0.23,0.38	206,210	    74,50	    1.00e+00
middle_exon	chr21:45516486-45516594:+	45514114,45518237	2.332	3.08e-02	True	-0.48	    ctrl-kd	0.07,0.07	0.48,0.62	206,210	    74,50	    1.00e+00
middle_exon	chr21:47914042-47914146:+	47910632,47916900	2.408	2.82e-02	True	-0.71	    ctrl-kd	0.02,0.09	0.71,0.82	160,121	    168,173	    1.00e+00
```

## Troubleshooting 🛠️

Please submit your issues to the GitHub repository directly (under the Issues tab).

- Problem 1:

It fails to ‘pip install’ and return this error message “module ‘pip._vendor.platformdirs’ has no attribute ‘user_cache_dir’”.

Potential solution: 

•	Try ‘pip3 install’ instead of ‘pip install’

- Problem 2:

If fails to ‘CryEx_stringtie -f fofn.txt -o exons.gtf’ and return this error message “Segmentation fault”.

Potential solution: 

•	Run stringtie on each bam file one by one instead of multiple files in one run and concat the output GTF files.
