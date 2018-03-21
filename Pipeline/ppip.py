#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: XuShaohang
E-mail:xushaohang@deepxomics.com
Company: DeepXOmics
'''
import sys
import argparse
from src.main import run_pipeline
from src.defaults import *
from src._version import __version__

#-------------------------------------------#
#               main function               #
#-------------------------------------------#
def main():
    #The first layer parameters
    main_parser = argparse.ArgumentParser(description="Run Polypeptide Pipeline",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    mode_parser = main_parser.add_argument_group("Mode input options")
    mode_parser.add_argument("mode",  metavar="Mode",
            help="Mode to run the pipleine for. Choose from %s"%list(["init","rnaqc","denovo", "msalign", "annotate", "report", "all"]), choices=MODES)
    mode_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    args = main_parser.parse_args(sys.argv[1:2])
    mode = args.mode
    #The second layer parameters
    parser = argparse.ArgumentParser(description="Run Polypeptide Pipeline in %s mode"%mode, prog= " ".join(sys.argv[0:2]),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    general_parser = parser.add_argument_group("General input options")
    general_parser.add_argument("mode", metavar=mode,
                                choices=MODES)
    general_parser.add_argument("--sample", metavar="Name",dest="sample", help="Sample name", required=True)
    general_parser.add_argument("--threads", type=int, metavar="nthreads", dest="threads", help="Number of threads", default=1)
    general_parser.add_argument("--timeout", type=int, metavar="timeout", help="Maximum run time for commands (in seconds)", default=TIMEOUT)   
    general_parser.add_argument("--workdir", help="Scratch directory for working", default="work")
    general_parser.add_argument("--outdir" , help="Output directory", default="out")
    general_parser.add_argument("--start", metavar="start",dest="start", type=int,
                              help="It re-starts executing the workflow/pipeline \
                                    from the given step number. This can be used when the pipeline \
                                    has crashed/stopped and one wants to re-run it from \
                                    from the step where it stopped without re-running from \
                                    the beginning the entire pipeline. 0 is for restarting \
                                    automatically and 1 is the first step." \
                              , default=0)

    if mode == "rnaqc":
        qc_parser = parser.add_argument_group("Quality control options")
        qc_parser.add_argument("--qctool", metavar="qctool",
                                help="The QC tool to use.", default="AfterQC")
        qc_parser.add_argument("--fqdir", metavar="fq_directory",dest="fqdir",
                                  help="REQUIRED. The input dir of single-end or pair-end sequencing reads. For single-end sequencing,\
                                    the filenames in the folder should be `*_1*` (e.g. test_1.fq.gz), otherwise you should specify `--read1_flag`.\
                                    For pair-end sequencing, the filenames in the folder should be `*_1*` and `*_2*` \
                                    (e.g. test_1.fq.gz and test_2.fq.gz), otherwise you should specify `--read1_flag` and `--read2_flag`.\
                                    ", default="config/fastq/")
        qc_parser.add_argument("--read1_flag", metavar="R1",dest="r1_flag",
                                  help="specify the name flag of read1, \
                                          which means a file with name *_1* is read1 file,\
                                   ", default="_1")
        qc_parser.add_argument("--read2_flag", metavar="R2",dest="r2_flag",

                                  help="specify the name flag of read2, \
                                          which means a file with name *_2* is read1 file,\
                                   ", default="_2")
        qc_parser.add_argument("--afterqc_opts", metavar="afterqc_opts",dest="afterqc_opts",
                                  help="Other options used for QC by AfterQC. \
                                  (should be put between \" \") \
                                  (For detail options check https://github.com/OpenGene/AfterQC).", 
                                  default="")


    elif mode == "denovo":
        dnv_parser = parser.add_argument_group("De novo Assembly options")
        dnv_parser.add_argument("--assembler", metavar="assembler",
                                help="The de novo assembler to use.", default="Trinity")
        dnv_parser.add_argument("--left", metavar="seq_1", dest="seq_1",
                                  help="Comma-separated list of files containing mate 1s (filename usually includes _1),\
                                   e.g. --left A_1.fq.gz,B_1.fq.gz.", default="")
        dnv_parser.add_argument("--right", metavar="seq_2", dest="seq_2",
                                  help="Comma-separated list of files containing mate 2s (filename usually includes _2),\
                                   e.g. --right A_2.fq.gz,B_2.fq.gz.", default="")
        dnv_parser.add_argument("--single", metavar="seq_u", dest="seq_u",
                                  help="Comma-separated list of files containing unpaired reads to be assembled,\
                                   e.g. --single A.fq.gz,B.fq.gz.", default="")
        dnv_parser.add_argument("--max_memory", metavar="memory", dest="max_mem",
                                  help="REQUIRED. suggested max memory to use by Trinity where limiting can be enabled.", default="10G")
        dnv_parser.add_argument("--trinity_opts", metavar="trinity_opts", dest="trinity_opts",
                                  help="Other options used for assembly by Trinity. \
                                  (should be put between \" \") \
                                  (For Trinity options check https://github.com/trinityrnaseq/trinityrnaseq/wiki).", 
                                  default="")
    elif mode == "msalign":
        align_parser = parser.add_argument_group("Precursor proteins of polypeptides creator (PGA) options")
        align_parser.add_argument("--input", metavar="FilePath", dest="input", required=True,
                                  help="REQUIRED. The database of fasta format from Trinty or user-defined file.")
        align_parser.add_argument("--longest", dest="get_longest", action='store_true',
                                  help="Only keep the longest frame of six-frame translation.")

        align_parser = parser.add_argument_group("Mass spectra alignment options")
        align_parser.add_argument("--engine", metavar="EngineName",
                                help="The ms search engine to use.", default="MSGFPlus")
        align_parser.add_argument("--spectrum", metavar="SpectrumFile", dest="spectrum", required=True,
                help="REQUIRED. Spectrum file name. Currently, MS-GF+ supports the following file formats: mzML, mzXML, mzML, mgf, ms2, pkl and _dta.txt.")
        align_parser.add_argument("--modfile", metavar="FilePath", help=" \
                Modification file of MS-GF+. \
                For more details, please check: https://github.com/sangtaekim/msgfplus/blob/master/doc/examples/Mods.txt",default="config/par/MSGFPlus_Mods.txt")
        align_parser.add_argument("--max_memory", metavar="max_memory", dest="max_mem",
                                  help="suggested max memory to use by MS-GF+ where limiting can be enabled.", default="10G")
        align_parser.add_argument("--inst", metavar="MS2DetectorID", dest="instrument",
                help="MS detector. Currently, MS-GF+ supports the following detectors: 0: Low-res LCQ/LTQ, 1: Orbitrap/FTICR, 2: TOF, 3: Q-Exactive. ", default="3")
        align_parser.add_argument("--fragid", metavar="FragmentMethodID", dest="fragid",
                help="Fragmentation method identifier (used to determine the scoring model). \
                        0: as written in the spectrum or CID if no info (Default), \
                        1: CID, \
                        2: ETD, \
                        3: HCD, \
                        4: Merge spectra from the same precursor", default="0")
        align_parser.add_argument("--enzyme", metavar="(0-9)", help=" \
                0: unspecific cleavage, \
                1: Trypsin, 2: Chymotrypsin, 3: Lys-C, \
                4: Lys-N, 5: glutamyl endopeptidase, 6: Arg-C, \
                7: Asp-N, 8: alphaLP, 9: no cleavage", dest="enzyme", default="0")                             
        align_parser.add_argument("--tda", metavar="(0 ,1)", help=" \
                0: don't search decoy database,\
                1: search decoy database", dest="decoy", default="1")                             
        align_parser.add_argument("--ntt", metavar="(0, 1 or 2)", help=" \
                Number of Tolerable Termini.\
                 E.g. For trypsin, 0: non-tryptic, 1: semi-tryptic, 2: fully-tryptic peptides only.\
                 ", dest="ntt", default="0")
        align_parser.add_argument("--pretol", metavar="MassTolerance", help="Precursor mass tolerance. \
                e.g. 2.5Da, 20ppm or 0.5Da, 2.5Da", dest="pretol", default="20ppm")                             
        align_parser.add_argument("--minlen", metavar="Length", help=" \
                Minimum peptide length to consider", dest="minlen", default="6")                             
        align_parser.add_argument("--maxlen", metavar="Length", help=" \
                Maximum peptide length to consider", dest="maxlen", default="50")
        align_parser.add_argument("--msgfplus_opts", metavar="msgfplus_opts", dest="msgfplus_opts",
                                  help="Other options used for alignment by MS-GF+. \
                                  (should be put between \" \") \
                                  (For detailed options check https://omics.pnl.gov/software/ms-gf).", 
                                  default="")
    elif mode == "annotate":
        annot_parser = parser.add_argument_group("SignalP options")
        annot_parser.add_argument("--nettype", metavar="(0, 1)", help=" \
                Signalp 4.1 contains two types of neural networks:\
                0: SignalP-TM has been trained with sequences containing transmembrane segments in the data set; \
                1: SignalP-noTM has been trained without those sequences. \
                ", dest="nettype", default="0") #project
        annot_parser.add_argument("--dcutt", metavar="[0-1]", help=" \
                The Signal-TM cutoff values", dest="dcutt", default="0.5")                      
        annot_parser.add_argument("--dcutnt", metavar="[0-1]", help=" \
                The Signal-noTM cutoff values", dest="dcutnt", default="0.45")                      
        annot_parser.add_argument("--orgtype", metavar="(0, 1 or 2)", help=" \
                It is important for performance that you choose the correct organism group since the signal peptides of these three groups are known to differ from each other:\
                0: Eukaryotes; \
                1: Gram-negative bacteria; \
                2: Gram-positive bacteria; \
                ", dest="orgtype", default="0") #project

        annot_parser.add_argument("--minsglen", metavar="Length", help=" \
                Minimal predicted signal peptide length.\
                SignalP 4.0 could, in rare cases, erroneously predict signal peptides shorter than 10 residues. \
                The default minimum length is by default 10, but you can adjust it. \
                Signal peptides shorter than 15 residues are very rare. \
                If you want to disable this length restriction completely, enter 0 (zero). \
                ", dest="minsglen", default="10")                      
        annot_parser.add_argument("--trunc", metavar="Length", help=" \
                N-terminal truncation of input sequence\
                By default, the predictor truncates each sequence to max. 70 \
                residues before submitting it to the neural networks. \
                If you want to predict extremely long signal peptides, \
                you can try a higher value, or disable truncation completely by entering 0 (zero) \
                ", dest="trunc", default="70") 
        annot_parser = parser.add_argument_group("Gene ontology analysis options")
        annot_parser.add_argument("--attool", metavar="attool", dest="attool", 
                help="Specify the annotation tool to use. \
                <0>: KOBAS, online tool. There's no need to prepare any files with this engine;\
                <1>: Sma3s, local tool. It's required to download uniref90.annot.gz and uniref90.fasta.gz to 'config/Sma3sdb/' from http://www.bioinfocabd.upo.es/sma3s/db/ in advance.' \
                ", default="0")
        annot_parser.add_argument("--orgname", metavar="ORGANISM", help=" \
                This parameter works only when the annotation tool is set as <0>:KOBAS. \
                Input the most appropriate organism name for annotation. \
                For detailed alternative names, please check the column 'Organisms' in  http://www.kegg.jp/kegg/catalog/org_list.html. \
                ", dest="orgname", default="Homo sapiens (human)") 

        annot_parser = parser.add_argument_group("Blastp options")
        annot_parser.add_argument("--evalue", metavar="E-Value", help=" \
                Expectation value (E) threshold for saving hits. \
                ", dest="evalue", default="0.01") 
        annot_parser.add_argument("--blastp_opts", metavar="blastp_opts", dest="blastp_opts",
                                  help="Other options used for alignment by blastp. \
                                  (should be put between \" \") \
                                  (For detailed options check ftp://ftp.ncbi.nlm.nih.gov/pub/factsheets/HowTo_BLASTGuide.pdf).", 
                                  default="")
        annot_parser = parser.add_argument_group("Multiple sequence alignment options")
        annot_parser.add_argument("--msa", metavar="MSA", help=" \
                Specify the MSA method that will be used: \
                0: 'ClustalOmega';\
                1: 'ClustalW'; \
                2: 'Muscle' \
                ", dest="msa", default="0") 

    elif mode == "report":
        report_parser = parser.add_argument_group("Html report options")
        report_parser.add_argument("--theme", metavar="Theme", help=" \
                Specify the markdown theme that will be used: \
                0: 'cayman'; \
                1: 'tactile'; \
                2: 'architec' \
                3: 'leonids' \
                4: 'hpstr' \
                ", dest="theme", default="0") 



    elif mode == "all":
        whole_parser = parser.add_argument_group("Stage options")
        whole_parser.add_argument("--stage", metavar="stage",dest="stage", type=int,
                              help="It re-starts the specific stage of the workflow/pipeline \
                                    from the given stage number. This can be used when the pipeline \
                                    has crashed/stopped and one wants to re-run it from \
                                    from the stage where it stopped without re-running from \
                                    the beginning the entire pipeline. \
                                    0: start from 'rnaqc'; \
                                    1: start from 'denovo'; \
                                    2: start from 'msalign'; \
                                    3: start from 'annotate'; \
                                    4: start from 'report'. \
                              ", default=0)

        whole_parser = parser.add_argument_group("Quality control options")
        whole_parser.add_argument("--qctool", metavar="qctool",
                                help="The QC tool to use.", default="AfterQC")
        whole_parser.add_argument("--fqdir", metavar="fq_directory",dest="fqdir",
                                  help="REQUIRED. The input dir of single-end or pair-end sequencing reads. For single-end sequencing,\
                                    the filenames in the folder should be `*_1*` (e.g. test_1.fq.gz), otherwise you should specify `--read1_flag`.\
                                    For pair-end sequencing, the filenames in the folder should be `*_1*` and `*_2*` \
                                    (e.g. test_1.fq.gz and test_2.fq.gz), otherwise you should specify `--read1_flag` and `--read2_flag`.\
                                    ", default="config/fastq/")
        whole_parser.add_argument("--read1_flag", metavar="R1",dest="r1_flag",
                                  help="specify the name flag of read1, \
                                          which means a file with name *_1* is read1 file,\
                                   ", default="_1")
        whole_parser.add_argument("--read2_flag", metavar="R2",dest="r2_flag",

                                  help="specify the name flag of read1, \
                                          which means a file with name *_2* is read1 file,\
                                   ", default="_2")
        whole_parser.add_argument("--afterqc_opts", metavar="afterqc_opts",dest="afterqc_opts",
                                  help="Other options used for QC by AfterQC. \
                                  (should be put between \" \") \
                                  (For detail options check https://github.com/OpenGene/AfterQC).", 
                                  default="")

        whole_parser = parser.add_argument_group("De novo Assembly options")
        whole_parser.add_argument("--assembler", metavar="assembler",
                                help="The de novo assembler to use.", default="Trinity")
        whole_parser.add_argument("--left", metavar="seq_1", dest="seq_1",
                                  help="Comma-separated list of files containing mate 1s (filename usually includes _1),\
                                   e.g. --left A_1.fq.gz,B_1.fq.gz.", default="")
        whole_parser.add_argument("--right", metavar="seq_2", dest="seq_2",
                                  help="Comma-separated list of files containing mate 2s (filename usually includes _2),\
                                   e.g. --right A_2.fq.gz,B_2.fq.gz.", default="")
        whole_parser.add_argument("--single", metavar="seq_u", dest="seq_u",
                                  help="Comma-separated list of files containing unpaired reads to be assembled,\
                                   e.g. --single A.fq.gz,B.fq.gz.", default="")
        whole_parser.add_argument("--max_memory", metavar="memory", dest="max_mem",
                                  help="suggested max memory to use by whole pipeline", default="10G")
        whole_parser.add_argument("--trinity_opts", metavar="trinity_opts", dest="trinity_opts",
                                  help="Other options used for assembly by Trinity. \
                                  (should be put between \" \") \
                                  (For Trinity options check https://github.com/trinityrnaseq/trinityrnaseq/wiki).", 
                                  default="")

        whole_parser = parser.add_argument_group("Precursor proteins of polypeptides creator (PGA) options")
        whole_parser.add_argument("--input", metavar="FilePath", dest="input",
                                  help="The fasta file from Trinty.",default="")
        whole_parser.add_argument("--longest", dest="get_longest", action='store_true',
                                  help="Only keep the longest frame of six-frame translation.")

        whole_parser = parser.add_argument_group("Mass spectra alignment options")
        whole_parser.add_argument("--engine", metavar="EngineName",
                                help="The ms search engine to use.", default="MSGFPlus")
        whole_parser.add_argument("--spectrum", metavar="SpectrumFile", dest="spectrum",
                help="Spectrum file name. Currently, MS-GF+ supports the following file formats: mzML, mzXML, mzML, mgf, ms2, pkl and _dta.txt.")
        whole_parser.add_argument("--modfile", metavar="FilePath", help=" \
                Modification file of MS-GF+. \
                For more details, please check: https://github.com/sangtaekim/msgfplus/blob/master/doc/examples/Mods.txt",default="config/par/MSGFPlus_Mods.txt")
        whole_parser.add_argument("--inst", metavar="MS2DetectorID", dest="instrument",
                help="MS detector. Currently, MS-GF+ supports the following detectors: 0: Low-res LCQ/LTQ, 1: Orbitrap/FTICR, 2: TOF, 3: Q-Exactive. ", default="3")
 
        whole_parser.add_argument("--enzyme", metavar="(0-9)", help=" \
                0: unspecific cleavage, \
                1: Trypsin, 2: Chymotrypsin, 3: Lys-C, \
                4: Lys-N, 5: glutamyl endopeptidase, 6: Arg-C, \
                7: Asp-N, 8: alphaLP, 9: no cleavage", dest="enzyme", default="0")                             
        whole_parser.add_argument("--fragid", metavar="FragmentMethodID", dest="fragid",
                help="Fragmentation method identifier (used to determine the scoring model). \
                        0: as written in the spectrum or CID if no info (Default), \
                        1: CID, \
                        2: ETD, \
                        3: HCD, \
                        4: Merge spectra from the same precursor", default="0")
        whole_parser.add_argument("--tda", metavar="(0 ,1)", help=" \
                0: don't search decoy database,\
                1: search decoy database", dest="decoy", default="1")                             
        whole_parser.add_argument("--ntt", metavar="(0, 1 or 2)", help=" \
                Number of Tolerable Termini.\
                 E.g. For trypsin, 0: non-tryptic, 1: semi-tryptic, 2: fully-tryptic peptides only.\
                 ", dest="ntt", default="0")
        whole_parser.add_argument("--pretol", metavar="MassTolerance", help="Precursor mass tolerance. \
                e.g. 2.5Da, 20ppm or 0.5Da, 2.5Da", dest="pretol", default="20ppm")                             
        whole_parser.add_argument("--minlen", metavar="Length", help=" \
                Minimum peptide length to consider", dest="minlen", default="6")                             
        whole_parser.add_argument("--maxlen", metavar="Length", help=" \
                Maximum peptide length to consider", dest="maxlen", default="50")
        whole_parser.add_argument("--msgfplus_opts", metavar="msgfplus_opts", dest="msgfplus_opts",
                                  help="Other options used for alignment by MS-GF+. \
                                  (should be put between \" \") \
                                  (For detailed options check https://omics.pnl.gov/software/ms-gf).", 
                                  default="")

        whole_parser = parser.add_argument_group("SignalP options")
        whole_parser.add_argument("--nettype", metavar="(0, 1)", help=" \
                Signalp 4.1 contains two types of neural networks:\
                0: SignalP-TM has been trained with sequences containing transmembrane segments in the data set; \
                1: SignalP-noTM has been trained without those sequences. \
                ", dest="nettype", default="0") #project
        whole_parser.add_argument("--dcutt", metavar="[0-1]", help=" \
                The Signal-TM cutoff values", dest="dcutt", default="0.5")                      
        whole_parser.add_argument("--dcutnt", metavar="[0-1]", help=" \
                The Signal-noTM cutoff values", dest="dcutnt", default="0.45")                      
        whole_parser.add_argument("--orgtype", metavar="(0, 1 or 2)", help=" \
                It is important for performance that you choose the correct organism group since the signal peptides of these three groups are known to differ from each other:\
                0: Eukaryotes; \
                1: Gram-negative bacteria; \
                2: Gram-positive bacteria; \
                ", dest="orgtype", default="0") #project
        whole_parser.add_argument("--minsglen", metavar="Length", help=" \
                Minimal predicted signal peptide length.\
                SignalP 4.0 could, in rare cases, erroneously predict signal peptides shorter than 10 residues. \
                The default minimum length is by default 10, but you can adjust it. \
                Signal peptides shorter than 15 residues are very rare. \
                If you want to disable this length restriction completely, enter 0 (zero). \
                ", dest="minsglen", default="10")                      
        whole_parser.add_argument("--trunc", metavar="Length", help=" \
                N-terminal truncation of input sequence\
                By default, the predictor truncates each sequence to max. 70 \
                residues before submitting it to the neural networks. \
                If you want to predict extremely long signal peptides, \
                you can try a higher value, or disable truncation completely by entering 0 (zero) \
                ", dest="trunc", default="70") 
        whole_parser = parser.add_argument_group("Gene ontology analysis options")
        whole_parser.add_argument("--attool", metavar="attool", dest="attool", 
                 help="Specify the annotation tool to use. \
                <0>: KOBAS, online tool. There's no need to prepare any files with this engine;\
                <1>: Sma3s, local tool. It's required to download uniref90.annot.gz and uniref90.fasta.gz to 'config/Sma3sdb/' from http://www.bioinfocabd.upo.es/sma3s/db/ in advance.' \
                ", default="0")
 
        whole_parser.add_argument("--orgname", metavar="ORGANISM", help=" \
                This parameter works only when the annotation tool is set as <0>:KOBAS. \
                Input the most appropriate organism name for annotation. \
                For detailed alternative names, please check the column 'Organisms' in  http://www.kegg.jp/kegg/catalog/org_list.html. \
                ", dest="orgname", default="Homo sapiens (human)") 
        whole_parser = parser.add_argument_group("Blastp options")
        whole_parser.add_argument("--evalue", metavar="E-Value", help=" \
                Expectation value (E) threshold for saving hits. \
                ", dest="evalue", default="0.01") 
        whole_parser.add_argument("--blastp_opts", metavar="blastp_opts", dest="blastp_opts",
                                  help="Other options used for alignment by blastp. \
                                  (should be put between \" \") \
                                  (For detailed options check ftp://ftp.ncbi.nlm.nih.gov/pub/factsheets/HowTo_BLASTGuide.pdf).", 
                                  default="")
        whole_parser = parser.add_argument_group("Multiple sequence alignment options")
        whole_parser.add_argument("--msa", metavar="MSA", help=" \
                Specify the MSA method that will be used: \
                0: 'ClustalOmega';\
                1: 'ClustalW'; \
                2: 'Muscle' \
                ", dest="msa", default="0") 

        whole_parser = parser.add_argument_group("Html report options")
        whole_parser.add_argument("--theme", metavar="Theme", help=" \
                Specify the markdown theme that will be used: \
                0: 'cayman'; \
                1: 'tactile'; \
                2: 'architec' \
                3: 'leonids' \
                4: 'hpstr' \
                ", dest="theme", default="0") 

    args = parser.parse_args() 
    sys.exit(run_pipeline(args,parser))
#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()
