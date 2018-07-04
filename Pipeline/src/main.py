# -*- coding: UTF-8 -*-
from collections import defaultdict
import sys
import os

from defaults import *
from _version import __version__
from run_annotation import run_annotation
from run_dnv_assemebly import run_dnv_assemebly
from run_ms_aligner import run_ms_aligner
from run_rna_qc import run_rna_qc
from run_report import run_report

from utils import *
import logging

import urllib2

def run_pipeline(args,parser):

    mode = args.mode
    create_dirs([args.workdir, args.outdir, os.path.join(args.workdir,"logs")])
    log_file=os.path.join(args.workdir,"logs","run-%s-%s-%s.log"%(
        args.sample,
        mode,
        time.strftime("%Y%m%d-%H%M%S")))
    FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=log_file, filemode="w")
    logFormatter = logging.Formatter(FORMAT)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    logger.info("Running Popypeptide Pipeline %s" % __version__)
    logger.info("Command-line %s" % (" ".join(sys.argv)))
    logger.info("Arguments are " + str(args))
    logger.info("Run log will be saved in " + log_file)
    logger.info("Run in mode: " + mode)

    #check the KOBAS is valid
    KobasIsValid=True
    url="http://kobas.cbi.pku.edu.cn/"
    req = urllib2.Request(url)
    if mode=="annotate" and args.attool == "0":  #test the server only when the KOBAS is used.
        try:
            resp = urllib2.urlopen(req, timeout=15)
        except urllib2.URLError:
            KobasIsValid=False
            logger.warning("The http://kobas.cbi.pku.edu.cn/ is not accessible currently. This pipeline will skip the KOBAS annotation process!")
     
    #Simple check for arguments
    if mode=="rnaqc" or mode=="all":
        if len(filter(lambda x : x.endswith(("fq","gz")),os.listdir(args.fqdir)))<1:
            parser.print_help()
            logger.error("Input directory of fastq files(*.fq or *.fq.gz) are missing.")
            return os.EX_USAGE

    #start to run
    if mode == "init":
        structure = ["config/fastq","config/msraw","config/par", BLASTDB_DIR, SMA3SDB_DIR]
        copy_and_overwrite("/opt/Pipeline/par/", "config/par/")
        create_dirs(structure)

        tmpinfo="\nPlease complete the following preparation steps before starting the pipeline:\n"+ \
                "    1) Copy NGS data (*fq.gz) to the <%s>;\n"+\
                "    2) Copy mass spectra data to the <%s>;\n"+\
                "    3) Modify the 'MSGFPlus_Mods.txt' file appropriately in the <%s> when you set the search engine argument to 'MSGFPlus';\n" +\
                "    4) Modify the 'comet.params' file appropriately in the <%s> when you set the search engine argument to 'Comet';\n" +\
                "    5) Copy known protein sequence (e.g. NR, RefSeq, Uniprot) to the <%s> (Recommend).\n" +\
                "    6) Download the uniref90.annot.gz and uniref90.fasta.gz to the <%s> from www.bioinfocabd.upo.es/sma3s/db (Required if the annotation tool is configured to use Sma3s).\n"
        logger.info(tmpinfo % (structure[0],structure[1],structure[2], structure[2],structure[3], structure[4]) )

    elif mode=="rnaqc":
        run_rna_qc(qctool=args.qctool,fqdir=args.fqdir,
                r1_flag=args.r1_flag, r2_flag=args.r2_flag,
                start=args.start, sample= args.sample,afterqc_opts=args.afterqc_opts,
                workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)

    elif mode=="denovo":
        if not args.assembler.upper()=="TRINITY":
            logger.error("%s is not supported. \
                    \nThe supported de novo assembler(s) are: %s."%(args.assembler,DNV_ASSEMBLERS))
            return os.EX_USAGE
        logger.info("Running de novo assembly step using %s"%args.assembler)
        run_dnv_assemebly(assembler=args.assembler,
                seq_1=args.seq_1, seq_2=args.seq_2, seq_u=args.seq_u,
                start=args.start, sample= args.sample, nthreads=args.threads,
                trinity_opts=args.trinity_opts, max_mem=args.max_mem,
                workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)

    elif mode=="msalign":
        if args.engine.upper()=="MSGFPLUS":
            logger.info("Running mass spectra alignment step using %s"%args.engine)
            run_ms_aligner(engine=args.engine,
                    input=args.input, longest=args.get_longest,
                    spectrum=args.spectrum, instrument=args.instrument, enzyme=args.enzyme, fragid=args.fragid,
                    decoy=args.decoy, pretol=args.pretol, minlen=args.minlen, maxlen=args.maxlen, modfile=args.modfile, ntt=args.ntt,
                    start=args.start, sample= args.sample, nthreads=args.threads,
                    msgfplus_opts=args.msgfplus_opts, max_mem=args.max_mem,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)
        elif args.engine.upper()=="COMET":
            logger.info("Running mass spectra alignment step using %s"%args.engine)
            run_ms_aligner(engine=args.engine,
                    input=args.input, longest=args.get_longest,spectrum=args.spectrum,
                    start=args.start, sample= args.sample, nthreads=args.threads,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)
        else:
            logger.error("%s is not supported. \
                    \nThe supported mass spectra aligner(s) are: %s."%(args.engine,MS_ALIGNER))
            return os.EX_USAGE

    elif mode=="annotate":
        logger.info("Running polypeptides annotation step")
        run_annotation(start=args.start, sample= args.sample, 
                nettype=args.nettype, dcutt=args.dcutt, dcutnt=args.dcutnt, orgtype=args.orgtype, minsglen=args.minsglen, trunc=args.trunc,
                orgname=args.orgname, blastp_opts=args.blastp_opts, evalue=args.evalue, msa=args.msa, attool=args.attool,
                nthreads=args.threads,workdir=args.workdir, outdir=args.outdir, timeout=args.timeout, kobas=KobasIsValid)

    elif mode=="report":
        logger.info("Running html report render step")
        run_report(start=args.start, sample= args.sample, theme=args.theme,
                workdir=args.workdir, outdir=args.outdir, timeout=args.timeout, kobas=KobasIsValid)

    elif mode=="all":
        logger.info("Running the whole pipeline!")
        current_stage=0
        if args.stage<=current_stage:
            logger.info("==========================STAGE %s: %s=========================="% (current_stage,"rnaqc"))
            run_rna_qc(qctool=args.qctool,fqdir=args.fqdir,
                    r1_flag=args.r1_flag, r2_flag=args.r2_flag,
                    start=args.start, sample= args.sample,afterqc_opts=args.afterqc_opts,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)
        else:
            logger.info("Skipping stage 'rnaqc'")
        current_stage+=1

        if args.stage<=current_stage:
            logger.info("==========================STAGE %s: %s=========================="% (current_stage,"denovo"))
            folder=os.path.join(args.workdir,"qc/good/")
            fqs = filter(lambda x: x.endswith(("gz","fq")),os.listdir(folder))
            fq1s = filter(lambda x: args.r1_flag in x,fqs)
            fq2s = filter(lambda x: args.r2_flag in x,fqs)
            fqu=""
            fq1=""
            fq2=""
            if args.seq_1 or args.seq_2 or args.seq_u:
                fqu=args.seq_u
                fq1=args.seq_1
                fq2=args.seq_2
            else:
                if len(fq2s)==0:  #unpaired 
                    fqu = ",".join(map(lambda x: os.path.join(folder, x),fq1s ))
                else:  #paired 
                    fq1 = ",".join(map(lambda x: os.path.join(folder, x),fq1s ))
                    fq2 = ",".join(map(lambda x: os.path.join(folder, x),fq2s ))

            run_dnv_assemebly(assembler=args.assembler,
                    seq_1=fq1, seq_2=fq2, seq_u=fqu,
                    start=args.start, sample= args.sample, nthreads=args.threads,
                    trinity_opts=args.trinity_opts, max_mem=args.max_mem,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)
        else:
            logger.info("Skipping stage 'denovo'")
        current_stage+=1

        if args.stage<=current_stage:
            logger.info("==========================STAGE %s: %s=========================="% (current_stage,"msalign"))
            if args.input:
                trinity_fa=args.input
            else:
                trinity_fa=os.path.join(args.workdir,"trinity/Trinity.fasta")
            if args.spectrum:
                specfile=args.spectrum
            else:
                folder="config/msraw/"
                msfiles = filter(lambda x: x.endswith((".mzML", ".mzXML", ".mgf", ".ms2", ".pkl","_dta.txt")),os.listdir(folder))
                if len(msfiles)<1:
                    logger.error("Aborting!")
                    raise Exception("One MSMS file is required in the 'config/msraw/'!")
                if len(msfiles)>1:
                    logger.error("Aborting!")
                    raise Exception("Only one MSMS file is allowed in the 'config/msraw/'!")
                specfile=os.path.join(folder,msfiles[0])


            run_ms_aligner(engine=args.engine,
                    input=trinity_fa, longest=args.get_longest,
                    spectrum=specfile, instrument=args.instrument, enzyme=args.enzyme, fragid=args.fragid,
                    decoy=args.decoy, pretol=args.pretol, minlen=args.minlen, maxlen=args.maxlen, modfile=args.modfile, ntt=args.ntt,
                    start=args.start, sample= args.sample, nthreads=args.threads,
                    msgfplus_opts=args.msgfplus_opts, max_mem=args.max_mem,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout)
        else:
            logger.info("Skipping stage 'msalign'")
        current_stage+=1

        if args.stage<=current_stage:
            logger.info("==========================STAGE %s: %s=========================="% (current_stage,"annotate"))
            run_annotation(start=args.start, sample= args.sample, 
                    nettype=args.nettype, dcutt=args.dcutt, dcutnt=args.dcutnt, orgtype=args.orgtype, minsglen=args.minsglen, trunc=args.trunc,
                    orgname=args.orgname, blastp_opts=args.blastp_opts, evalue=args.evalue, msa=args.msa, attool=args.attool,
                    nthreads=args.threads,workdir=args.workdir, outdir=args.outdir, timeout=args.timeout, kobas=KobasIsValid)
        else:
            logger.info("Skipping stage 'annotate'")
        current_stage+=1


        if args.stage<=current_stage:
            logger.info("==========================STAGE %s: %s=========================="% (current_stage,"report"))
            run_report(start=args.start, sample= args.sample, theme=args.theme,
                    workdir=args.workdir, outdir=args.outdir, timeout=args.timeout, kobas=KobasIsValid)
        else:
            logger.info("Skipping stage 'report'")
        current_stage+=1
        logger.info("Finish the whole pipeline!")

    else:
        logger.error("wrong mode %s"%(mode))
        return os.EX_USAGE

    logger.info("Run log is saved in " + log_file)
    logger.info("All Done!")

    return os.EX_OK
