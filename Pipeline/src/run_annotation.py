import os
from external_cmd import TimedExternalCmd
from defaults import *
from utils import *
from shutil import copyfile

FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
logFormatter = logging.Formatter(FORMAT)
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

def annotate_ver1(sample="",start=0, 
                nettype="0", dcutt="0.5", dcutnt="0.45", orgtype="0", minsglen="10", trunc="70",
                orgname="", blastp_opts="", evalue="", msa="",
                workdir=None, outdir=None, timeout=TIMEOUT, nthreads=1, kobas=True):
    logger.info("Annotation for precursor proteins of polypeptides for %s"%sample)

    work_annot=os.path.join(workdir,"annotation")
    create_dirs([work_annot])
    work_msalign=os.path.join(workdir,"msalign")

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase annotation work directory for %s" % sample
        command="rm -rf %s/*" % (
            work_annot)
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    annot_log = os.path.join(work_annot, "annotation.log")
    annot_log_fd = open(annot_log, "w")

    msg = "Predicting the presence and location of signal peptide cleavage sites in amino acid sequences for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("casperjs /opt/Auxtools/spider/signalP.js --fasta=%(msdir)s/%(sam)s-sequence.fa "
                "--outfile=%(atdir)s/%(sam)s-signalP.txt --minlen=\"%(mlen)s\" "
                "--method=\"%(nettype)s\" --orgtype=\"%(orgtype)s\" "
                "--dcut=\"user\" --notm=%(dcutnt)s --tm=%(dcutt)s --trunc=%(trunc)s") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'mlen': minsglen,
                    'nettype': nettype,
                    'orgtype': orgtype,
                    'dcutt': dcutt,
                    'dcutnt': dcutnt,
                    'trunc': trunc
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Annotating precursor protein function for %s"%sample
    if start<=step and kobas:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("casperjs /opt/Auxtools/spider/kobas.js --fasta=%(msdir)s/%(sam)s-sequence.fa "
                "--species='%(orgname)s' --outfile=%(atdir)s/%(sam)s-kobas.txt && "
                "python /opt/Auxtools/kobas_post_process.py -i %(atdir)s/%(sam)s-kobas.txt -o %(atdir)s/%(sam)s ") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'orgname': orgname
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Multiple sequence alignment for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("python /opt/Auxtools/msa.py -i %(msdir)s/%(sam)s-sequence.fa "
                "-m %(msa)s -o %(atdir)s/%(sam)s-msa.html ") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'msa': msa
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Venom annotation for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("python /opt/Auxtools/venomkb/venomkb_annot.py -i %(msdir)s/%(sam)s-sequence.fa "
                "-c /opt/Auxtools/venomkb/venomkb_proteins_06272017.json.gz -o %(atdir)s/%(sam)s ") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Similar sequence blast for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        falist = filter(lambda x: x.endswith(("fa","fasta")) ,os.listdir(BLASTDB_DIR))
        if(len(falist)==0):
            logger.warn("There is no blast database file(*.fa or *.fasta) in the '%s' directory!" % (BLASTDB_DIR))
            logger.warn("Skipping step %d: %s"%(step,msg))
        if(len(falist)>1):
            logger.warn("Only one blast database file is allowed in the '%s' directory!" % (BLASTDB_DIR))
            logger.warn("Skipping step %d: %s"%(step,msg))

        dbext = filter(lambda x: x.endswith(("phr", "pin", "psq")),os.listdir("./config/blastdb/"))
        if(len(dbext)<3):  #check db had been builded.
            cmd_chip1 = "makeblastdb -dbtype prot  -in %(path)s/%(db)s  -out %(path)s/%(db)s && \
                "% {
                    'path': BLASTDB_DIR,
                    'db': falist[0]
                }
        else:
            cmd_chip1 = ""
        cmd_chip2 = ("blastp -db %(path)s/%(db)s -num_threads %(nthreads)s -query %(msdir)s/%(sam)s-sequence.fa "
                "-out %(atdir)s/%(sam)s.asn -outfmt 11 -evalue %(evalue)s %(opts)s && "
                "blast_formatter -archive %(atdir)s/%(sam)s.asn -outfmt 0 > %(atdir)s/%(sam)s-pairwise.txt && "
                "blast_formatter -archive %(atdir)s/%(sam)s.asn -outfmt '7 qaccver saccver pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle' > %(atdir)s/%(sam)s-tabular.txt && "
                "python /opt/Auxtools/BlasterJS/src/blast2html.py -i %(atdir)s/%(sam)s-pairwise.txt "
                "-o %(atdir)s/blast_html/")% {
                    'path': BLASTDB_DIR,
                    'db': falist[0],
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'orgname': orgname,
                    'evalue': evalue,
                    'opts': blastp_opts,
                    'nthreads': nthreads
                }

        command= cmd_chip1 + cmd_chip2
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1
    
    out_annot = os.path.join(outdir,"annotation")
    create_dirs([out_annot])
    msg="Copy annotation result to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        if os.path.exists("%s/%s-signalP.txt"% (work_annot,sample)):
            command = ("cp %(indir)s/%(sam)s-msa.html %(indir)s/%(sam)s-venom.tsv "
				"%(indir)s/%(sam)s-signalP.txt %(outdir)s/")%{
				"indir": work_annot,
				"sam": sample,
				"outdir": out_annot
            }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)

        if os.path.exists("%s/blast_html"% (work_annot)):
            copy_and_overwrite("%s/blast_html"% (work_annot), "%s/blast_html/"% (out_annot))
    
        tmpin = "%s/%s-tabular.txt" % (work_annot, sample)
        tmpout = "%s/%s-tabular.txt" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
        tmpin = "%s/%s-go.tsv" % (work_annot, sample)
        tmpout = "%s/%s-go.tsv" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
        tmpin = "%s/%s-ko.tsv" % (work_annot, sample)
        tmpout = "%s/%s-ko.tsv" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
        tmpin = "%s/%s-kobas.txt" % (work_annot, sample)
        tmpout = "%s/%s-kobas.txt" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)

    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    return os.EX_OK

def annotate_ver2(sample="",start=0, 
                nettype="0", dcutt="0.5", dcutnt="0.45", orgtype="0", minsglen="10", trunc="70",
                orgname="", blastp_opts="", evalue="", msa="",
                workdir=None, outdir=None, timeout=TIMEOUT, nthreads=1):
    logger.info("Annotation for precursor proteins of polypeptides for %s"%sample)

    work_annot=os.path.join(workdir,"annotation")
    create_dirs([work_annot])
    work_msalign=os.path.join(workdir,"msalign")

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase annotation work directory for %s" % sample
        command="rm -rf %s/*" % (
            work_annot)
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    annot_log = os.path.join(work_annot, "annotation.log")
    annot_log_fd = open(annot_log, "w")

    msg = "Predicting the presence and location of signal peptide cleavage sites in amino acid sequences for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("casperjs /opt/Auxtools/spider/signalP.js --fasta=%(msdir)s/%(sam)s-sequence.fa "
                "--outfile=%(atdir)s/%(sam)s-signalP.txt --minlen=\"%(mlen)s\" "
                "--method=\"%(nettype)s\" --orgtype=\"%(orgtype)s\" "
                "--dcut=\"user\" --notm=%(dcutnt)s --tm=%(dcutt)s --trunc=%(trunc)s") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'mlen': minsglen,
                    'nettype': nettype,
                    'orgtype': orgtype,
                    'dcutt': dcutt,
                    'dcutnt': dcutnt,
                    'trunc': trunc
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Annotating precursor protein function for %s"%sample
    sma3sfa = filter(lambda x: x.endswith(("fa","fasta")) ,os.listdir(SMA3SDB_DIR))
    sma3sat = filter(lambda x: x.endswith(("annot")) ,os.listdir(SMA3SDB_DIR))
    sma3sfagz = filter(lambda x: x.endswith(("fa.gz","fasta.gz")) ,os.listdir(SMA3SDB_DIR))
    sma3satgz = filter(lambda x: x.endswith(("annot.gz")) ,os.listdir(SMA3SDB_DIR))
 
    if(len(sma3sfa)==1 and len(sma3sat)==1):
        if start<=step:
            logger.info("--------------------------STEP %s--------------------------"%step)
            command=("mkdir -p %(atdir)s/sma3s/ && "
                    "ln -sf /data/%(ssdir)s/%(dbfa)s %(atdir)s/sma3s/%(dbfa)s && "
                    "ln -sf /data/%(ssdir)s/%(dbat)s %(atdir)s/sma3s/%(dbat)s && "
                    "cp %(msdir)s/%(sam)s-sequence.fa %(atdir)s/sma3s/ &&"
                    "cd %(atdir)s/sma3s/ && "
                    "perl /opt/Auxtools/sma3s_v2.pl -i %(sam)s-sequence.fa -d %(dbfa)s -go -goslim -p 0.00001 -num_threads %(nthreads)s && "
                    "cd -") % {
                        'msdir': work_msalign,
                        'atdir': work_annot,
                        'ssdir': SMA3SDB_DIR,
                        'dbfa': sma3sfa[0],
                        'dbat': sma3sat[0],
                        'sam': sample,
                        'nthreads': nthreads
                    }
            command="bash -c \"%s\""%command
            cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
            retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
        else:
            logger.info("Skipping step %d: %s"%(step,msg))

    elif(len(sma3sfagz)==1 and len(sma3satgz)==1):
        if start<=step:
            logger.info("--------------------------STEP %s--------------------------"%step)
            command=("mkdir -p %(atdir)s/sma3s/ && "
                    "gzip -dc %(ssdir)s/%(dbatgz)s > %(atdir)s/sma3s/%(dbat)s && "
                    "gzip -dc %(ssdir)s/%(dbfagz)s > %(atdir)s/sma3s/%(dbfa)s && "
                    "cp %(msdir)s/%(sam)s-sequence.fa %(atdir)s/sma3s/ &&"
                    "cd %(atdir)s/sma3s/ && "
                    "perl /opt/Auxtools/sma3s_v2.pl -i %(sam)s-sequence.fa -d %(dbfa)s -go -goslim -p 0.00001 -num_threads %(nthreads)s && "
                    "cd -") % {
                        'msdir': work_msalign,
                        'atdir': work_annot,
                        'ssdir': SMA3SDB_DIR,
                        'dbfagz': sma3sfagz[0],
                        'dbatgz': sma3satgz[0],
                        'dbfa': os.path.splitext(sma3sfagz[0])[0],
                        'dbat': os.path.splitext(sma3satgz[0])[0],
                        'sam': sample,
                        'nthreads': nthreads
                    }
            command="bash -c \"%s\""%command
            cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
            retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
        else:
            logger.info("Skipping step %d: %s"%(step,msg))
    else:
        logger.warn("Two Sma3s database files(uniref90.annot and uniref90.fasta) did not exist in the '%s' directory! Please obtain it from http://www.bioinfocabd.upo.es/sma3s/db/" % (BLASTDB_DIR))
        logger.warn("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Multiple sequence alignment for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("python /opt/Auxtools/msa.py -i %(msdir)s/%(sam)s-sequence.fa "
                "-m %(msa)s -o %(atdir)s/%(sam)s-msa.html ") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'msa': msa
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Venom annotation for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("python /opt/Auxtools/venomkb/venomkb_annot.py -i %(msdir)s/%(sam)s-sequence.fa "
                "-c /opt/Auxtools/venomkb/venomkb_proteins_06272017.json.gz -o %(atdir)s/%(sam)s ") % {
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Similar sequence blast for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        falist = filter(lambda x: x.endswith(("fa","fasta")) ,os.listdir(BLASTDB_DIR))
        if(len(falist)==0):
            logger.warn("There is no blast database file(*.fa or *.fasta) in the '%s' directory!" % (BLASTDB_DIR))
            logger.warn("Skipping step %d: %s"%(step,msg))
        if(len(falist)>1):
            logger.warn("Only one blast database file is allowed in the '%s' directory!" % (BLASTDB_DIR))
            logger.warn("Skipping step %d: %s"%(step,msg))

        dbext = filter(lambda x: x.endswith(("phr", "pin", "psq")),os.listdir("./config/blastdb/"))
        if(len(dbext)<3):  #check db had been builded.
            cmd_chip1 = "makeblastdb -dbtype prot  -in %(path)s/%(db)s  -out %(path)s/%(db)s && \
                "% {
                    'path': BLASTDB_DIR,
                    'db': falist[0]
                }
        else:
            cmd_chip1 = ""
        cmd_chip2 = ("blastp -db %(path)s/%(db)s -num_threads %(nthreads)s -query %(msdir)s/%(sam)s-sequence.fa "
                "-out %(atdir)s/%(sam)s.asn -outfmt 11 -evalue %(evalue)s %(opts)s && "
                "blast_formatter -archive %(atdir)s/%(sam)s.asn -outfmt 0 > %(atdir)s/%(sam)s-pairwise.txt && "
                "blast_formatter -archive %(atdir)s/%(sam)s.asn -outfmt '7 qaccver saccver pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle' > %(atdir)s/%(sam)s-tabular.txt && "
                "python /opt/Auxtools/BlasterJS/src/blast2html.py -i %(atdir)s/%(sam)s-pairwise.txt "
                "-o %(atdir)s/blast_html/")% {
                    'path': BLASTDB_DIR,
                    'db': falist[0],
                    'msdir': work_msalign,
                    'atdir': work_annot,
                    'sam': sample,
                    'orgname': orgname,
                    'evalue': evalue,
                    'opts': blastp_opts,
                    'nthreads': nthreads
                }

        command= cmd_chip1 + cmd_chip2
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1
    
    out_annot = os.path.join(outdir,"annotation")
    create_dirs([out_annot])
    msg="Copy annotation result to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        if os.path.exists("%s/%s-signalP.txt"% (work_annot,sample)):
            command = ("cp %(indir)s/%(sam)s-msa.html %(indir)s/%(sam)s-venom.tsv "
				"%(indir)s/%(sam)s-signalP.txt %(outdir)s/")%{
				"indir": work_annot,
				"sam": sample,
				"outdir": out_annot
            }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=annot_log_fd, cmd_log=annot_log, msg=msg, timeout=timeout)

        if os.path.exists("%s/blast_html"% (work_annot)):
            copy_and_overwrite("%s/blast_html"% (work_annot), "%s/blast_html/"% (out_annot))
    
        tmpin = "%s/%s-tabular.txt" % (work_annot, sample)
        tmpout = "%s/%s-tabular.txt" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
        
        tsvlist = filter(lambda x: x.endswith(("tsv")) ,os.listdir(os.path.join(work_annot,"sma3s")))
        logger.info(tsvlist)
        summary = filter(lambda x: x.endswith(("summary.tsv")), tsvlist)[0]
        tsvtab = filter(lambda x: not x.endswith(("summary.tsv")), tsvlist)[0]

        tmpin = "%s" % os.path.join(work_annot,"sma3s",summary)
        tmpout = "%s/%s-sma3s-summary.tsv" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
        tmpin = "%s" % os.path.join(work_annot,"sma3s",tsvtab)
        tmpout = "%s/%s-sma3s-table.tsv" % (out_annot, sample)
        if os.path.exists(tmpin):
            copyfile(tmpin, tmpout)
 
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    return os.EX_OK

def run_annotation(sample= "", start="0", nthreads=1,
                nettype="0", dcutt="0.5", dcutnt="0.45", orgtype="0", minsglen="10", trunc="70",
                orgname="", blastp_opts="", evalue="", msa="", attool="0",
                workdir=None, outdir=None, timeout=TIMEOUT, ignore_exceptions=False, kobas=True):

    if str(nettype)=="0":
        nettype = "best"
    elif str(nettype)=="1":
        nettype = "notm"

    if str(orgtype)=="0":
        orgtype = "euk"
    elif str(orgtype)=="1":
        orgtype = "gram-"
    elif str(orgtype)=="2":
        orgtype = "gram+"

    if str(msa)=="0":
        msa = "ClustalOmega"
    elif str(msa)=="1":
        msa = "ClustalW"
    elif str(msa)=="2":
        msa = "Muscle"

    if attool=="0":
        try:
            annotate_ver1(sample = sample, start=start, nthreads=nthreads,
                    nettype = nettype, dcutt=dcutt, dcutnt=dcutnt, orgtype=orgtype, minsglen=minsglen, trunc=trunc,
                    orgname = orgname, blastp_opts=blastp_opts, evalue=evalue, msa=msa,
                    workdir=workdir, outdir=outdir, timeout=timeout, kobas=kobas)
        except Exception as excp:
            logger.info("Run annotation failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
    elif attool=="1":
        try:
            annotate_ver2(sample = sample, start=start, nthreads=nthreads,
                    nettype = nettype, dcutt=dcutt, dcutnt=dcutnt, orgtype=orgtype, minsglen=minsglen, trunc=trunc,
                    orgname = orgname, blastp_opts=blastp_opts, evalue=evalue, msa=msa,
                    workdir=workdir, outdir=outdir, timeout=timeout)
        except Exception as excp:
            logger.info("Run annotation failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
 
    return os.EX_OK
