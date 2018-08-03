# PPIP

## 1 A comprehensive framework for accurate and efficient endogenous peptide analysis

The **PPIP** is a pipeline made up of multiple steps for endogenous peptide analysis. It is based on popular open-source projects Docker, an open source technology used to package applications and their dependencies into a standardized and environment-agnostic software container. Currently, this image focus on the de novo identification of endogenous peptide (e.g. signal peptides or neuropeptides). 

***

## 2 Demo data used in this project

The demo data of this software can be downloaded from Google Drive. A MGF file and two fastq files were packaged with tar and subsequently compressed with gzip. 

Furthermore, we also provided two NCBI non-redundant protein sequence databases for the Blast annotation step. These two database were processed well in advance and divied into two categories: *Plant.fa* and *Animal.fa*. Users can select the appropriate database according to the actual situation. Of course, users also can customize their Blast database from another public source (e.g. [UniProt](http://www.uniprot.org/)).

[Click here to obtain demo data from Google Drive](https://drive.google.com/open?id=1tprERIRcRpK8Ngktom6w5V5XQoSM0jte). There are three files in the directory:
  1. *<font color="#5FA90A">PPIP_data.tar.gz</font>*: demo data of RNA-seq and MS2. 
  2. *<font color="#5FA90A">animal.fa.gz</font>*: animal sequences from NCBI non-redundant database for Blast.
  3. *<font color="#5FA90A">Plannt.fa.gz</font>*: plant sequences from NCBI non-redundant database for Blast.

A demo report which is generated after completing the entire process can be viewed through the following links: 

  [<font color="#dd0000">Click me to access the final demo report</font>](report/Scorpion.html)

***

## 3 Minimum system requirements to run PPIP natively in Linux or Mac:

- RAM: 10 GB (more is better)
- Processor: 1+ CPU (more is better)
- Hard Disk space: 20+ GB
- Internet connectivity: Faster is better when installing.

Also, you must enable Intel VT-x and AMD-V in your BIOS. Many people will already have Intel VT-x and AMD-V enabled though, so try to install **PPIP** first before worrying about this requirement. If necessary though, see the following for detailed instructions:

[How to Enable Intel VT-x in Your Computer’s BIOS or UEFI Firmware](http://www.howtogeek.com/213795/how-to-enable-intel-vt-x-in-your-computers-bios-or-uefi-firmware/)

Currently, it's possible that the Docker for Windows will trigger "input/output error" IO error when you run the PPIP container with large fastq files. This problem may be caused by the docker mount system in windows NTFS partions and couldn't be fixed for the moment. So we recommend running this program primarily on Linux..

***

## 4 Obtain the PPIP Docker image

### 4.1  Build the docker image by yourself

If you want to build the **PPIP** image by yourself, you need to clone the GitHub repository with following command at first. 

```sh
$ git clone git@github.com:Shawn-Xu/PPIP.git
```

Then enter the **PPIP** folder and type the following commands to build the images.

```sh
$ docker build --no-cache --rm -t shawndp/ppip .
```

However, for simplicity, we do not recommend building docker images from scratch because this process may take a long time and require a good network.

### 4.2  Pull the image from Docker Hub (highly recommend)

As mentioned before, a more easy and convienent way to get the image is pull it from the Docker Hub with docker. 

```sh
$ docker pull shawndp/ppip
```

***

## 5 Running PPIP

Before the process begins, it is necessary to create a new directory as a workspace at first. 

```sh
$ pw='ppip_workspace'
$ sample="demo"

$ mkdir -p ${pw}
```

Then, we have to create a Docker container and mount the workspace folder as the **</data/>** of the Docker container. In this instance, we set the **ppip** as the container name. Of course, you can rename it as your wish and keep it consistent in the following example.

```sh
$ docker create --name ppip -t -u $(id -u) -v=${PWD}/${pw}:/data/ shawndp/ppip  #create a container but not running
$ docker start ppip   #start the container
```

### 5.1 init

Since we have a workspace and an activated container, we will use the following commands to initialize these directories. 

```sh
$ docker exec ppip pipe init  --sample ${sample}
```

After that, we can list the contents of directories in a tree-like format with a linux command "tree". The comments after each line are used to explain the purpose of related files/directories.


```sh
$ tree ${pw}
├── config                          # cofiguration folder
│   ├── blastdb                    # the folder for deploying BLAST database (e.g. NCBI NR, Uniprot).
│   ├── fastq                      # the folder of RNA-seq fastq files used for denovo.
│   ├── msraw                      # the folder of MS2 files for 'msalign' step.
│   └── par                        # parameters folder
│       ├── MSGFPlus_Mods.txt     # the MS-GF+ configuration for modification.
│       └── comet.params          # the Comet parameter configuration.
├── out                             # the folder of final result
└── work                            # the scratch directory for working
```

Before the software start to run, we need to prepare the raw data or configuration files according to the following items:

- 1) Copy NGS data (*fq.gz) to the <config/fastq>;
- 2) Copy mass spectra data to the <config/msraw>;
- 3) Modify the 'MSGFPlus_Mods.txt' file appropriately in the <config/par> when you set the search engine argument to 'MSGFPlus';
- 4) Modify the 'comet.params' file appropriately in the <config/par> when you set the search engine argument to 'Comet';
- 5) Copy known protein sequence (e.g. NR, RefSeq, Uniprot) to the <config/blastdb> (Recommend);
- 6) Download the uniref90.annot.gz and uniref90.fasta.gz to the <config/sma3sdb> from www.bioinfocabd.upo.es/sma3s/db (Required if the annotation tool is configured to use Sma3s).

>NOTE1: The input mass spectra formats can be mzML, mzXML, mzML, mgf, ms2, pkl and _dta.txt. In many case, [msconvert](http://proteowizard.sourceforge.net/tools/msconvert.html) can be used to convert all common raw formats into those open data formats described before.

>NOTE2: It is recommended to prepare the Blast database in the **<config/blastdb>** folder so that the bioactive peptides could get the relevant protein functional description. Otherwise, the procedure of protein entry anotation will be skipped. As for the common databases, NCBI NR could be obtained from [NCBI ftp server](https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz), and alternative manually annotated and non-redundant protein database could also be acquired from [UniProt Knowledgebase](ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz). 

A specific example that annotation tool is set as **KOBAS**:

```sh
$ tree ${pw}
├── config
│   ├── blastdb
│   │   └── Animal.fa
│   ├── fastq
│   │   ├── demo_1.fq.gz
│   │   └── demo_2.fq.gz
│   ├── msraw
│   │   └── demo.mgf
│   └── par
│       ├── MSGFPlus_Mods.txt
│       └── comet.params
├── out
└── work
```

And another configuration example where the annotation tool is set to **Sma3s**:

```sh
$ tree ${pw}
├── config
│   ├── blastdb
│   │   └── Animal.fa
│   ├── fastq
│   │   ├── demo_1.fq.gz
│   │   └── demo_2.fq.gz
│   ├── msraw
│   │   └── demo.mgf
│   ├── par
│   │   ├── MSGFPlus_Mods.txt
│   │   └── comet.params
│   └── sma3sdb
│       ├── uniref90.annot
│       └── uniref90.fasta
├── out
└── work
`

### 5.2 rnaqc

Type the command below for quanlity control and filter of RNA-seq reads.

```sh
$ docker exec ppip pipe rnaqc --fqdir config/fastq/ --sample ${sample}
```

It will go through all fastq files in a folder and then output three folders in **<work/qc>** folder: good, bad and QC folders, which contains good reads, bad reads and the QC results of each fastq file/pair.

### 5.3 denovo

Type the command below for de novo assembly of RNA-seq reads.

```sh
$ docker exec ppip pipe denovo  --left work/qc/good/demo_1.good.fq.gz --right work/qc/good/demo_2.good.fq.gz --max_memory 10G --sample ${sample} --threads 8
```

When completed, Trinity will create a **Trinity.fasta** file in the **<work/trinity/>** directory. This file will be used as the database for step **msalign**.

### 5.4 msalign

This command will choose MS-GF+ as the search engine for peptide identification.

```sh
$ docker exec ppip pipe msalign --input work/trinity/Trinity.fasta --sample ${sample} --spectrum config/msraw/demo.mgf --threads 8
```

Besides, you can choose Comet as the alternative search engine by setting '--engine Comet'. Please note that the parameters of Comet could only be modified through <config/par/comet.params>.

```sh
$ docker exec ppip pipe msalign --engine Comet --input work/trinity/Trinity.fasta --sample ${sample} --spectrum config/msraw/demo.mgf --threads 8
```

The corresponding result will be stored in the **<work/msalign/>** folder.

Moreover, if you had some bioactive peptide sequences collected from pubic sources, you can skip the step ***rnaqc** and **denovo**, and just start from the step **msalign** with the options *--input*. For example,

```sh
$ docker exec ppip pipe msalign --input config/customized.fasta  --sample ${sample} --spectrum config/msraw/demo.mgf --threads 8
```

Where *customized.fasta* is the user-collected database, which is either nucleic or amino-acid sequences with FASTA format. In this condition, it doesn't require the RNA-seq data to assembly the condidated transcripts any more.

### 5.5 annotate

Enter the following command to complete the functional annotation. This step consists of motif search, signal peptides prediction, functional annotation and BLAST similarity alignment.

```sh
$ docker exec ppip pipe annotate --sample ${sample} 
```

The corresponding result will be stored in the **<work/annotation/>** folder.

>NOTE3: The '--attool' option will determine which tools are used in the functional annotation step. The default argument '**0**', represents the KOBAS, will connect the KOBAS online server and finsh the annotation process without database configuration in the **<config/>** folder. Nevertheless, argument '**1**' will utilize Sma3s for the annotation. In this case, it's required to complete the local database configuration in <config/sma3sdb> with uniref90.annot.gz and uniref90.fasta.gz from [www.bioinfocabd.upo.es/sma3s/db](www.bioinfocabd.upo.es/sma3s/db) at first.

### 5.6 report

Type the command below for rendering HTML-based report.

```sh
$ docker exec ppip pipe report --sample ${sample}
```

At the end of this step, it will tidy up all of the previous results and produce a HTML-based document in the **<out/>** folder. And lots of modern browsers, such as Chrome, Firefox, Edge, can be used to access all the information in the report with the '*<sample>.html*' main page.

### 5.7 all

To simplify the usage of this pipeline, we provide a simple interface mainly intended to allow users to run the pipeline procedures from 2 to 6 in one step. In other words, you can just run the step "init" and step "all" to complete all procedures in the pipeline.

```sh
$ docker exec ppip pipe all --sample ${sample}
```

By the way, the code below is the command used to produce the example report and result of our paper.

```sh
docker exec ppip pipe all --threads 10 --max_memory 20G --sample Scorpion --fragid 3 --evalue 0.00001 --pretol 10ppm --attool 1
```

***

## 6 Output files

| Order | Task | Command | Output Files |
| ------ | ------ | ------ | ------ |
| 1 | Protect initialization | init | workspace for this project  |	
| 2 | Quality control of raw reads | rnaqc | one QC report and clean reads |	
| 3 | Short-read de novo assembly | denovo | one trasncripts file named "Trinity.fasta" |
| 4 | Peptide identification by scoring MS/MS spectra against database | msalign | mzIdentML and tsv list |
| 5 | Function annotion, motif search, signal peptides prediction ... ...  | annotate | (1) sample-go.tsv, gene ontology annotation; (2) sample-ko.tsv, pathway annotation; (3) sample-msa.html, multiple sequence alignment viewer; (4) sample-signalP.txt, signal peptides predict result; (5) blast_html/, the similarity protein sequence search result links; (6) sample-venom.tsv, venom annotation |
| 6 | Tidy the result and build the HTML-based report | report | A folder contains a HTML-report |

Alternatively, you can also simplely use a interface **all** to automaticly run the steps from order 2 to 6 at once.

***

## 7 Command line options

Type *'docker exec ppip pipe -h'* to get the option for running **PPIP** with various modes are shown below.

| Option | Definition |
| ------ | ------ | 
| Mode | Mode to run the pipleine for. Choose from ['init', 'rnaqc', 'denovo', 'msalign', 'annotate', 'report', 'all'] |


### 7.1 General options

These options are general arguments implemented in all of the modes.

| Option | Definition |
| ------ | ------ | 
| --sample Name | Sample name (default: None) |
| --threads nthreads | Number of threads (default: 1) |
| --timeout timeout | Maximum run time for commands (in seconds) (default: 10000000) |
| --workdir WORKDIR | Scratch directory for working (default: work) |
| --outdir OUTDIR | Output directory (default: out) |
| --start start | It re-starts executing the workflow/pipeline from the given step number. This can be used when the pipeline has crashed/stopped and one wants to re-run it from from the step where it stopped without re-running from the beginning the entire pipeline. 0 is for restarting automatically and 1 is the first step. (default: 0) |

### 7.2 Quality control for reads options

Type *'docker exec ppip pipe rnaqc -h'* for help.

| Option | Definition |
| ------ | ------ |
| --qctool qctool | The QC tool to use. (default: AfterQC) |
| --fqdir fq_directory | REQUIRED. The input dir of single-end or pair-end sequencing reads. For single-end sequencing, the filenames in the folder should be `*_1*` (e.g. test_1.fq.gz), otherwise you should specify `--read1_flag`. For pair-end sequencing, the filenames in the folder should be `*_1*` and `*_2*` (e.g. test_1.fq.gz and test_2.fq.gz), otherwise you should specify `--read1_flag` and `--read2_flag`. (default: config/fastq/) |
| --read1_flag R1 | specify the name flag of read1, which means a file with name *_1* is read1 file, (default: _1)|
| --read2_flag R2 | specify the name flag of read2, which means a file with name *_2* is read1 file, (default: _2)|
| --afterqc_opts afterqc_opts | Other options used for QC by AfterQC. (should be put between " ") (For detail options check https://github.com/OpenGene/AfterQC). (default: )|

### 7.3 Denovo assembly options

Type *'docker exec ppip pipe denovo -h'* for help.

| Option | Definition |
| ------ | ------ |
| --assembler assembler | The de novo assembler to use. (default: Trinity) |
| --left seq_1 | Comma-separated list of files containing mate 1s (filename usually includes _1), e.g. --left A_1.fq.gz,B_1.fq.gz. (default: ) |
| --right seq_2 | Comma-separated list of files containing mate 2s (filename usually includes _2), e.g. --right A_2.fq.gz,B_2.fq.gz. (default: ) |
| --single seq_u | Comma-separated list of files containing unpaired reads to be assembled, e.g. --single A.fq.gz,B.fq.gz. (default: ) |
| --max_memory memory | REQUIRED. suggested max memory to use by Trinity where limiting can be enabled. (default: 10G) |
| --trinity_opts trinity_opts | Other options used for assembly by Trinity. (should be put between " ") (For Trinity options check https://github.com/trinityrnaseq/trinityrnaseq/wiki). (default: ) |

### 7.4 Mass spectra alignment options


Type *'docker exec ppip pipe msalign -h'* for help.

#### 7.4.1 Precursor proteins of endogenous peptide construction options:

| Option | Definition |
| ------ | ------ |
| --input FilePath | REQUIRED. The database of fasta format from Trinty or user-defined file. (default: None) |
| --longest | Only keep the longest frame of six-frame translation. (default: False) |

#### 7.4.2 Mass spectra alignment options:

| Option | Definition |
| ------ | ------ |
| --engine EngineName | Set the search engine for MSMS identification: 'MSGFPlus' or 'Comet'. Please note that if you choose the Comet as the engine, the related search parameters can only be modified through the <config/par/comet.params> file. (default: MSGFPlus) |
| --spectrum SpectrumFile | REQUIRED. Spectrum file name. Currently, MS-GF+ supports the following file formats: mzML, mzXML, mzML, mgf, ms2, pkl and _dta.txt. (default: None) |
| --modfile FilePath | Modification file of MS-GF+. For more details, please check: https://github.com/sangtaekim/msgfplus/blob/master/doc/examples/Mods.txt (default: config/par/MSGFPlus_Mods.txt) |
| --max_memory max_memory | suggested max memory to use by MS-GF+ where limiting can be enabled. (default: 10G) |
| --inst MS2DetectorID | MS detector. Currently, MS-GF+ supports the following detectors: 0: Low-res LCQ/LTQ, 1: Orbitrap/FTICR, 2: TOF, 3: Q-Exactive. (default: 3) |
| --fragid FragmentMethodID | Fragmentation method identifier (used to determine the scoring model). 0: as written in the spectrum or CID if no info (Default), 1: CID, 2: ETD, 3: HCD, 4: Merge spectra from the same precursor (default: 0) |
| --enzyme (0-9) | 0: unspecific cleavage, 1: Trypsin, 2: Chymotrypsin, 3: Lys-C, 4: Lys-N, 5: glutamyl endopeptidase, 6: Arg-C, 7: Asp-N, 8: alphaLP, 9: no cleavage (default: 0) |
| --tda (0 ,1) | 0: don't search decoy database, 1: search decoy database (default: 1) |
| --ntt (0, 1 or 2) | Number of Tolerable Termini. E.g. For trypsin, 0: non-tryptic, 1: semi-tryptic, 2: fully-tryptic peptides only. (default: 0) |
| --pretol MassTolerance | Precursor mass tolerance. e.g. 2.5Da, 20ppm or 0.5Da, 2.5Da (default: 20ppm) |
| --minlen Length | Minimum peptide length to consider (default: 6) |
| --maxlen Length | Maximum peptide length to consider (default: 50) |
| --msgfplus_opts msgfplus_opts | Other options used for alignment by MS-GF+. (should be  put between " ") (For detailed options check https://omics.pnl.gov/software/ms-gf). (default: ) |

### 7.5 Annotation options

Type *'docker exec ppip pipe annotate -h'* for help.

#### 7.5.1 SignalP options

| Option | Definition |
| ------ | ------ |
| --nettype (0, 1) | Signalp 4.1 contains two types of neural networks: 0: SignalP-TM has been trained with sequences containing transmembrane segments in the data set; 1: SignalP-noTM has been trained without those sequences. (default: 0) |
| --dcutt [0-1] | The Signal-TM cutoff values (default: 0.5) |
| --dcutnt [0-1] | The Signal-noTM cutoff values (default: 0.45) |
| --orgtype (0, 1 or 2) | It is important for performance that you choose the correct organism group since the signal peptides of these three groups are known to differ from each other: 0: Eukaryotes; 1: Gram-negative bacteria; 2: Gram-positive bacteria; (default: 0) |
| --minsglen Length | Minimal predicted signal peptide length. SignalP 4.0 could, in rare cases, erroneously predict signal peptides shorter than 10 residues. The default minimum length is by default 10, but you can adjust it. Signal peptides shorter than 15 residues are very rare. If you want to disable this length restriction completely, enter 0 (zero). (default: 10) |
| --trunc Length | N-terminal truncation of input sequence By default, the predictor truncates each sequence to max. 70 residues before submitting it to the neural networks. If you want to predict extremely long signal peptides, you can try a higher value, or disable truncation completely by entering 0 (zero) (default: 70) |

#### 7.5.2 Gene ontology analysis options:

| Option | Definition |
| ------ | ------ |
| --attool attool | Specify the annotation tool to use. <0>: KOBAS, online tool. There's no need to prepare any files with this engine; <1>: Sma3s, local tool. It's required to download uniref90.annot.gz and uniref90.fasta.gz to 'config/Sma3sdb/' from http://www.bioinfocabd.upo.es/sma3s/db/ in advance.' (default: 0) |
| --orgname ORGANISM | Input the most appropriate organism name for annotation. For detailed alternative names, please check the column 'Organisms' in http://www.kegg.jp/kegg/catalog/org_list.html. (default: Homo sapiens (human)) |

#### 7.5.3 Blastp options

| Option | Definition |
| ------ | ------ |
| --evalue E-Value | Expectation value (E) threshold for saving hits. (default: 0.01) |
| --blastp_opts blastp_opts | Other options used for alignment by blastp. (should be put between " ") (For detailed options check ftp://ftp.ncbi.nlm.nih.gov/pub/factsheets/HowTo_BLASTGuide.pdf). (default: ) |

#### 7.5.4 Multiple sequence alignment options

| Option | Definition |
| ------ | ------ |
| --msa MSA | Specifies the MSA method that will be used: 0:'ClustalOmega'; 1: 'ClustalW'; 2: 'Muscle' (default:0) |

### 7.6 HTML report options

Type *'docker exec ppip pipe report -h'* for help.

| Option | Definition |
| ------ | ------ |
| --theme Theme | Specifies the markdown theme that will be used: 0: 'cayman'; 1: 'tactile'; 2: 'architec' 3: 'leonids' 4: 'hpstr' (default: 0)|

***

