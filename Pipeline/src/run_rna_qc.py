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

def run_afterqc(fqdir="", r1_flag="", r2_flag="",
                start=0, sample= "",afterqc_opts="",
                workdir=None, outdir=None, timeout=TIMEOUT,nthreads=1):
    logger.info("Automatic Filtering, Trimming, Error Removing and Quality Control for fastq data for %s"%sample)

    work_qc=os.path.join(workdir,"qc")
    create_dirs([work_qc])

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase QC work directory for %s" % sample
        command="rm -rf %s/*" % (
            work_qc)
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    qc_log = os.path.join(work_qc, "qc.log")
    qc_log_fd = open(qc_log, "w")

    #seq_argument="-%s -%s %s "%(file_format,read_type,seq_argument)
    
    msg = "QC for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command="%s %s -d %s --read1_flag %s --read2_flag %s -g %s -b %s -r %s %s" % (
            "python", "/opt/AfterQC/after.py", fqdir, r1_flag, r2_flag, work_qc+"/good/", work_qc+"/bad/", work_qc+"/qc_report/", afterqc_opts)
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=qc_log_fd, cmd_log=qc_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    out_qc=os.path.join(outdir,"qc")
    create_dirs([out_qc])
    msg="Copy qc html report to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        qclist = filter(lambda x: x.endswith(("html")) ,os.listdir( "%s/qc_report/"%work_qc ))
        if len(qclist)>0 :
            #command=" && ".join(map(lambda x: "cp %s/qc_report/%s %s/" % (work_qc, x, out_qc), qclist))
            command= "cp %s %s/"  % (" ".join(map(lambda x: "%s/qc_report/%s" % (work_qc, x), qclist)), out_qc)
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=qc_log_fd, cmd_log=qc_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1


def run_rna_qc(qctool="AfterQC",fqdir="", r1_flag="", r2_flag="",
                start=0, sample= "", afterqc_opts= "",
                workdir=None, outdir=None, timeout=TIMEOUT, ignore_exceptions=False):
    if qctool.upper()=="AFTERQC":
        try:
            run_afterqc(fqdir=fqdir, r1_flag=r1_flag, r2_flag=r2_flag,
                          start=start, sample= sample, afterqc_opts=afterqc_opts,
                          workdir=workdir, outdir=outdir, timeout=timeout)
        except Exception as excp:
            logger.info("Run AfterQC failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
    return os.EX_OK
