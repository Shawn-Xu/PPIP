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

def run_rmarkdown(start=0, sample= "", theme= "",
                workdir=None, outdir=None, timeout=TIMEOUT,nthreads=1, kobas=True):
    logger.info("Get rmarkdown report for %s"%sample)

    report_log = os.path.join(workdir, "report.log")
    report_log_fd = open(report_log, "w")

    step=0
    msg = "Get report for %s"%sample

    sma3s_summary = "%s/%s-sma3s-summary.tsv" %(os.path.join(outdir,"annotation"), sample)
    sma3s_table = "%s/%s-sma3s-table.tsv" %(os.path.join(outdir,"annotation"), sample)
    sma3s_go = "%s/%s-go.tsv" %(os.path.join(outdir,"annotation"), sample)
    sma3s_ko = "%s/%s-ko.tsv" %(os.path.join(outdir,"annotation"), sample)
    engine=""
    if os.path.exists(sma3s_go and sma3s_ko):
        engine="0"
    elif os.path.exists(sma3s_summary and sma3s_table):
        engine="1"
    else:
        logger.error("The files of annotation did not existed!")
        os._exit(-1)

    if start<=step:
        logger.info("--------------------------STEP %s--------------------------"%step)
        
        if kobas:  #convert to str
            kobas="1"
        else:
            kobas="0"

        command='''\
        python /opt/Auxtools/rmd_creator.py -i %(in)s -w %(work)s \
        -t /opt/Auxtools/rmarkdown/template.Rmd \
        -s %(sam)s -o %(in)s/%(sam)s.Rmd -m %(theme)s -k %(kobas)s -e %(engine)s && \
        R -e 'rmarkdown::render(\\"%(in)s/%(sam)s.Rmd\\")' && \
        rm %(in)s/%(sam)s.Rmd \
        ''' % {
                    'in': outdir,
                    'work': workdir,
                    'sam': sample,
                    'theme': theme,
                    'kobas': kobas,
                    'engine': engine
            }
        logger.info(command)
        command="bash -c \"%s\""%command
        cmd = TimedExternalCmd(command, logger, raise_exception=True, env_dict={"OMP_NUM_THREADS":str(nthreads)})
        retcode = cmd.run(cmd_log_fd_out=report_log_fd, cmd_log=report_log, msg=msg, timeout=timeout)
    else:
        logger.info("Skipping step %d: %s"%(step,msg))
    step+=1


def run_report(start=0, sample= "", theme="",
                workdir=None, outdir=None, timeout=TIMEOUT, ignore_exceptions=False, kobas=True):
    if str(theme)=="0":
        theme = "cayman"
    elif str(theme)=="1":
        theme = "tactile"
    elif str(theme)=="2":
        theme = "architect"
    elif str(theme)=="3":
        theme = "leonids"
    elif str(theme)=="4":
        theme = "hpstr"

    try:
        run_rmarkdown(start=start, sample=sample, theme=theme,
                      workdir=workdir, outdir=outdir, timeout=timeout, kobas=kobas)
    except Exception as excp:
        logger.info("Run report failed!")
        logger.error(excp)
        if not ignore_exceptions:
            raise Exception(excp)
    return os.EX_OK
