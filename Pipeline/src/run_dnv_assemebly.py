import os
from external_cmd import TimedExternalCmd
from defaults import *
from utils import *

FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
logFormatter = logging.Formatter(FORMAT)
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

def run_trinity(seq_1="", seq_2="", seq_u="",
                start=0, sample= "", nthreads=1,
                trinity_opts="", max_mem="20G",
                workdir=None, outdir=None, timeout=TIMEOUT):
    logger.info("Running de novo assembly (TRINITY) for %s"%sample)
    
    #dirname="trinity_"+sample  #Triniy's output directory must contain the word 'trinity' as a safety precaution
    work_trinity=os.path.join(workdir,"trinity")
    create_dirs([work_trinity])

    #check the fq
    if seq_1 and seq_2:
        for s1 in seq_1.split(","):
            if not os.path.exists(s1):
                logger.error("Aborting!")
                raise Exception("No Mate 1 sequence file %s"%s1)
            if not s1.endswith(".fq.gz"):
                logger.error("Aborting! Please ensure the suffix of fastq files is <*>.fq.gz")
                raise Exception("Fastq format error %s"%s1)

        for s2 in seq_2.split(","):
            if not os.path.exists(s2):
                logger.error("Aborting!")
                raise Exception("No Mate 2 sequence file %s"%s2)
            if not s2.endswith(".fq.gz"):
                logger.error("Aborting! Please ensure the suffix of fastq files is <*>.fq.gz")
                raise Exception("Fastq format error %s"%s2)

        seq_argument="--left %s --right %s"%(seq_1,seq_2)
        '''
        cor_1=chainMap(seq_1.split(",")).
            map(lambda x: os.path.basename(x)).
            map(lambda x: re.sub(r'(.+)\.(fq|fastq)(\.gz)?', r'\1', x)).
            map(lambda x: work_trinity + "/corfq/"+ x +".cor.fq.gz")
        scor_1=",".join(cor_1)
        cor_2=chainMap(seq_2.split(",")).
            map(lambda x: os.path.basename(x)).
            map(lambda x: re.sub(r'(.+)\.(fq|fastq)(\.gz)?', r'\1', x)).
            map(lambda x: work_trinity + "/corfq/"+ x +".cor.fq.gz")
        scor_2=",".join(cor_2)
        '''
    elif seq_u:
        for su in seq_u.split(","):
            if not os.path.exists(su):
                logger.error("Aborting!")
                raise Exception("No unpaired sequence file %s"%su)
            if not su.endswith(".fq.gz"):
                logger.error("Aborting! Please ensure the suffix of fastq files is <*>.fq.gz")
                raise Exception("Fastq format error %s"%su)

        seq_argument="--single %s"%(seq_u)

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase Trinity work directory for %s"%sample
        #Trinity's running status is stored with the hidden files. It's necessary to delete these hidden file before the rerun of Trinity. Note that '*' couldn't match the hidden files.
        command="rm -rf %(wk)s/* %(wk)s/.*" % {   
                'wk': work_trinity}
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    trinity_log = os.path.join(work_trinity, "trinity.log")
    trinity_log_fd = open(trinity_log, "w")

    #seq_argument="-%s -%s %s "%(file_format,read_type,seq_argument)
    
    msg = "Run Trinity for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command="Trinity --seqType fq --max_memory %s --CPU %s  --output %s %s %s" % (
            max_mem, nthreads, work_trinity, seq_argument, trinity_opts)
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=trinity_log_fd, cmd_log=trinity_log, msg=msg, timeout=timeout)   
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    out_trinity=os.path.join(outdir,"trinity")
    create_dirs([out_trinity])
    msg="Copy trinity transcripts to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        if os.path.exists("%s/Trinity.fasta"%work_trinity):
            command = "cp %s/Trinity.fasta %s/"%(work_trinity, out_trinity)
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=trinity_log_fd, cmd_log=trinity_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1


    return os.EX_OK

def run_dnv_assemebly(assembler="Trinity",
                      seq_1="", seq_2="", seq_u="", 
                      start=0, sample= "", nthreads=1,
                      trinity_opts="", max_mem="20G",
                      workdir=None, outdir=None, timeout=TIMEOUT, ignore_exceptions=False):
    if assembler.upper()=="TRINITY":
        try:
            run_trinity(
                          seq_1=seq_1, seq_2=seq_2, seq_u=seq_u,
                          start=start, sample= sample, nthreads=nthreads,
                          trinity_opts=trinity_opts, max_mem=max_mem,
                          workdir=workdir, outdir=outdir, timeout=timeout)
        except Exception as excp:
            logger.info("Run trinity failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
    return os.EX_OK
