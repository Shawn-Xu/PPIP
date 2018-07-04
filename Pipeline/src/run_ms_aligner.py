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

def run_msgfplus(input="", longest=False,
              spectrum="",instrument="3",enzyme="0",decoy="1", fragid="0",
              pretol="20ppm",minlen=6,maxlen=50,modfile="",ntt="0",
              start=0, sample= "", nthreads=1,
              msgfplus_opts="", max_mem="10G",
              workdir=None, outdir=None, timeout=TIMEOUT):

    logger.info("Running mass spectra alignment (MSGFPlus) for %s"%sample)
    
    work_msalign=os.path.join(workdir,"msalign")
    create_dirs([work_msalign])

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase msalign work directory for %s"%sample
        command="rm -rf %s/*" % (
            work_msalign)
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    msalign_log = os.path.join(work_msalign, "msalign.log")
    msalign_log_fd = open(msalign_log, "w")

    #determine wether the fasta is nucleotide or amino acid format.
    tmpfile=open(input)
    tmpline=tmpfile.readlines()[1] #get second line 
    is_na=True
    if len(set(tmpline.strip()))>4: 
        is_na=False

    msg = "Run PGA database creator for %s"%sample
    if start<=step and is_na:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command="Rscript /opt/Auxtools/run_dbcreator.R %s %s %s %s" % (
            input, longest, work_msalign, sample)
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)   
    elif start<=step and not is_na:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("mkdir -p %(wk)s/database/ && cp %(db)s %(wk)s/database/%(sam)s.ntx.fasta") % {
                'db': input,
                'wk' : work_msalign,
                'sam' : sample
            }
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Run MSGFPlus for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("java -jar /opt/MSGFPlus/MSGFPlus.jar  -s %(spectrum)s "
                "-o %(dir)s/%(sam)s.mzid -d %(dir)s/database/%(sam)s.ntx.fasta -m %(fragid)s "
                "-t %(pretol)s -inst %(inst)s -e %(eyz)s -ntt %(ntt)s -tda %(tda)s -minLength %(minl)s "
                "-maxLength %(maxl)s -thread %(th)s -mod %(modfile)s") % {
                        'spectrum': spectrum,
                        'dir':work_msalign,
                        'sam':sample,
                        "pretol": pretol,
                        "inst": instrument,
                        "eyz": enzyme,
                        "tda": decoy,
                        "ntt": ntt,
                        "minl": minlen,
                        "maxl": maxlen,
                        'modfile': modfile,
                        "fragid": fragid,
                        'th': nthreads
                        }
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Converts MS-GF+ output (.mzid) into the tsv format (.tsv) for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("java -cp /opt/MSGFPlus/MSGFPlus.jar  edu.ucsd.msjava.ui.MzIDToTsv "
                "-i %(dir)s/%(sam)s.mzid -o %(dir)s/%(sam)s-rawSummary.tsv "
                "-showQValue 1 -showDecoy 0 -unroll 1") % {
                    'dir':work_msalign,
                    'sam':sample,
                    }
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Tidy identification result and get precursor protein for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("python /opt/Auxtools/fasta_preparation.py -i %(dir)s/%(sam)s-rawSummary.tsv "
                "-d %(dir)s/database/%(sam)s.ntx.fasta -o %(dir)s/%(sam)s") % {
                'dir': work_msalign,
                'sam': sample
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1


    out_msalign=os.path.join(outdir,"msalign")
    out_database=os.path.join(outdir,"database")
    create_dirs([out_msalign, out_database])
    msg="Copy novel sequence database and  MS identification result(s) to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        if os.path.exists("%s/%s-pepSummary.tsv"% (work_msalign, sample)):
            command = "cp %(dir)s/%(sam)s-pepSummary.tsv %(dir)s/%(sam)s-psmSummary.tsv %(dir)s/%(sam)s-sequence.fa %(out)s/"%{
                    'dir': work_msalign,
                    'sam': sample,
                    'out': out_msalign
                    }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
        if os.path.exists("%s/database/%s.ntx.fasta"% (work_msalign, sample)):
            command = "cp %(dir)s/database/%(sam)s.ntx.fasta %(out)s/" % {
                'dir': work_msalign,
                'sam': sample,
                'out': out_database
            }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
 
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1
 

    return os.EX_OK

def run_comet(input="", longest=False, spectrum="",
              start=0, sample= "", nthreads=1,
              workdir=None, outdir=None, timeout=TIMEOUT):

    logger.info("Running mass spectra alignment (Comet) for %s"%sample)
    
    work_msalign=os.path.join(workdir,"msalign")
    create_dirs([work_msalign])

    step=0
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        msg = "Erase msalign work directory for %s"%sample
        command="rm -rf %s/*" % (
            work_msalign)
        command="bash -c \"%s\""%command        
        cmd = TimedExternalCmd(command, logger, raise_exception=False)
        retcode = cmd.run(msg=msg, timeout=timeout)
    step+=1

    msalign_log = os.path.join(work_msalign, "msalign.log")
    msalign_log_fd = open(msalign_log, "w")

    #determine wether the fasta is nucleotide or amino acid format.
    tmpfile=open(input)
    tmpline=tmpfile.readlines()[1] #get second line 
    is_na=True
    if len(set(tmpline.strip()))>4: 
        is_na=False

    msg = "Run PGA database creator for %s"%sample
    if start<=step and is_na:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command="Rscript /opt/Auxtools/run_dbcreator.R %s %s %s %s" % (
            input, longest, work_msalign, sample)
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)   
    elif start<=step and not is_na:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("mkdir -p %(wk)s/database/ && cp %(db)s %(wk)s/database/%(sam)s.ntx.fasta") % {
                'db': input,
                'wk' : work_msalign,
                'sam' : sample
            }
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Run Comet for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("/opt/comet.2018011.linux.exe -Pconfig/par/comet.params -N%(dir)s/%(sam)s "
                "-D%(dir)s/database/%(sam)s.ntx.fasta  %(spectrum)s ") % {
                        'spectrum': spectrum,
                        'dir':work_msalign,
                        'sam':sample
                        }
        command="bash -c \"%s\""%command      
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1

    msg = "Tidy identification result and get precursor protein for %s"%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        command=("Rscript /opt/Auxtools/comet_fdr.R %(dir)s/%(sam)s %(dir)s/database/%(sam)s.ntx.fasta ") % {
                'dir': work_msalign,
                'sam': sample
                }
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1


    out_msalign=os.path.join(outdir,"msalign")
    out_database=os.path.join(outdir,"database")
    create_dirs([out_msalign, out_database])
    msg="Copy novel sequence database and  MS identification result(s) to output directory for %s."%sample
    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        if os.path.exists("%s/%s-pepSummary.tsv"% (work_msalign, sample)):
            command = "cp %(dir)s/%(sam)s-pepSummary.tsv %(dir)s/%(sam)s-psmSummary.tsv %(dir)s/%(sam)s-sequence.fa %(out)s/"%{
                    'dir': work_msalign,
                    'sam': sample,
                    'out': out_msalign
                    }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
        if os.path.exists("%s/database/%s.ntx.fasta"% (work_msalign, sample)):
            command = "cp %(dir)s/database/%(sam)s.ntx.fasta %(out)s/" % {
                'dir': work_msalign,
                'sam': sample,
                'out': out_database
            }
            cmd = TimedExternalCmd(command, logger, raise_exception=True)
            retcode = cmd.run(cmd_log_fd_out=msalign_log_fd, cmd_log=msalign_log, msg=msg, timeout=timeout)
 
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1
 

    return os.EX_OK



def run_ms_aligner(engine="MSGFPlus",
              spectrum="",instrument="3",enzyme="0",decoy="1",fragid="0",
              pretol="20ppm",minlen=6,maxlen=50,modfile="",ntt="0",
              input="", longest=False,
              start=0, sample="", nthreads=1,
              msgfplus_opts="", max_mem="20G",
              workdir=None, outdir=None, timeout=TIMEOUT, ignore_exceptions=False):

    if engine.upper()=="MSGFPLUS":
        try:
            run_msgfplus(input=input, longest=longest,
                          spectrum=spectrum,instrument=instrument, enzyme=enzyme, decoy=decoy, fragid=fragid,
                          pretol=pretol, minlen=minlen, maxlen=maxlen, modfile=modfile,ntt=ntt,
                          start=start, sample= sample, nthreads=nthreads,
                          msgfplus_opts=msgfplus_opts, max_mem=max_mem,
                          workdir=workdir, outdir=outdir, timeout=timeout)
        except Exception as excp:
            logger.info("Run mass spectra alignment (MS-GF+) failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
    if engine.upper()=="COMET":
        try:
            run_comet(input=input, longest=longest, spectrum=spectrum,
                          start=start, sample= sample, nthreads=nthreads,
                          workdir=workdir, outdir=outdir, timeout=timeout)
        except Exception as excp:
            logger.info("Run mass spectra alignment (Comet) failed!")
            logger.error(excp)
            if not ignore_exceptions:
                raise Exception(excp)
 
    return os.EX_OK
