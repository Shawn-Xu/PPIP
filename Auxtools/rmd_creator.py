#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: XuShaohang
E-mail:xushaohang@deepxomics.com
Company: DeepXOmics
'''
import sys,argparse,os
from string import Template

#-------------------------------------------#
#                   class                   #
#-------------------------------------------#
class MyTemplate(Template):
    """
    set new delimiter for my template
    """
    delimiter = '@'

#-------------------------------------------#
#               functions                   #
#-------------------------------------------#
def init_opt(): 
    '''This is the argument parser wrapper function!!!'''
    parser = argparse.ArgumentParser(description="A dummy program")
    parser.add_argument('-v', dest='verbose', action='store_true', help="set verbose")
    parser.add_argument('-o', '--output', type=str, dest= "output", required=False, default="rmarkdown.Rmd", help='output rmarkdown file')
    parser.add_argument('-i', '--inputdir', type=str, dest="inputdir", required=True, help='polypep result (out) directory (REQUIRED)')
    parser.add_argument('-w', '--workdir', type=str, dest="workdir", required=True, help='polypep workspace (work) directory (REQUIRED)')
    parser.add_argument('-m', '--theme', type=str, dest="theme", required=False, help='rmarkdown theme', default="cayman")
    parser.add_argument('-s', '--sample', type=str, dest="sample", required=True, help='sample name')
    parser.add_argument('-t', '--template', type=str, dest="template", help='rmarkdown template', default="/opt/Auxtools/template.Rmd")
    parser.add_argument('-k', '--kobas', type=str, dest="kobas", required=False, help='KOBAS is valid or not (0: OKOBAS server is healthy; 1: KOBAS server is not accessible)', default="1")
    parser.add_argument('-e', '--engine', type=str, dest="engine", required=False, help='The engine used for annotation (0: KOBAS; 1: Sma3s)', default="0")
    if len(sys.argv)==1:   #print help info when there is no flag
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    return args

#-------------------------------------------#
#               main function               #
#-------------------------------------------#

def main():
    args = init_opt()

    if args.engine == "0":
        if args.kobas == "0":
            blast_chapter_number = "3.3"
            getKobas="False"
            kobas_code="FALSE"
        else:
            blast_chapter_number = "3.4"
            getKobas="True"
            kobas_code="TRUE"
        getSma3s="False"
        sma3s_code="FALSE"

    elif args.engine == "1":
        blast_chapter_number = "3.4"
        getSma3s="True"
        sma3s_code="TRUE"
        getKobas="False"
        kobas_code="FALSE"

    qc_chapter=""
    qcdir="qc/"
    qcdir = os.path.join(args.inputdir,qcdir)
    if os.path.exists(qcdir):
        htmls = filter(lambda x: x.endswith(("html","htm")),os.listdir(qcdir))
        if len(htmls)>0:
            links = map(lambda x: "  + [%s](qc/%s)" % (x,x),htmls)
            qc_chapter+="Quality control and filtering of sequencing reads is one of the most important steps in the pre-processing of sequencing reads. In this sub-section, the AfterQC (https://github.com/OpenGene/AfterQC), a tool with functions to profile sequencing errors and correct most of them, plus highly automated quality control and data filtering features will be used. \n\n"

            qc_chapter+="<details><summary>Click me to view the QC report</summary>\n<p>\n"
            qc_chapter += "\n".join(links)
            qc_chapter += "\n</p>\n</details>\n"
        else:
            qc_chapter="Skip this chapter because there is no NGS data."


    blast_chapter=""
    htmldir="annotation/blast_html/"
    htmldir = os.path.join(args.inputdir,htmldir)
    if os.path.exists(htmldir):
        htmls = filter(lambda x: x.endswith(("html","htm")),os.listdir(htmldir))
        if len(htmls)>0:
            links = map(lambda x: "  + [%s](annotation/blast_html/%s)" % (x,x),htmls)
            blast_chapter="## %s Similarity search\n\n" %(blast_chapter_number)
            blast_chapter+="A BLAST search allows users to infer the function of a sequence from similar sequences.  A tab-delimited table is available from the link below.\n\n"

            blast_chapter+="[Download the tabular table of BLAST](annotation/%s-tabular.txt)\n\n" %(args.sample)
            blast_chapter+="Besides, this tool also provides a graphic summary and some description for each alignment between the query sequence and the sequence hits from the database.\n\n"
            blast_chapter+="<details><summary>Click me to view the detail</summary>\n<p>\n"
            blast_chapter += "\n".join(links)
            blast_chapter += "\n</p>\n</details>\n"

    template=open(args.template)
    src=MyTemplate(template.read())
    substitution={
            "theme": args.theme,
            "kobas": getKobas,
            "sma3s": getSma3s,
            "kobas_code": kobas_code,
            "sma3s_code": sma3s_code,
            "raw": "/data/%s/msalign/%s-rawSummary.tsv" %(args.workdir, args.sample),
            "psm": "msalign/%s-psmSummary.tsv" %(args.sample),
            "pep": "msalign/%s-pepSummary.tsv" %(args.sample),
            "msa": "annotation/%s-msa.html" %(args.sample),
            "sgp": "annotation/%s-signalP.txt" %(args.sample),
            "go": "annotation/%s-go.tsv" %(args.sample),
            "ko": "annotation/%s-ko.tsv" %(args.sample),
            "sma3s_summary": "annotation/%s-sma3s-summary.tsv" % (args.sample),
            "sma3s_tab": "annotation/%s-sma3s-table.tsv" % (args.sample),
            "ngsqc": qc_chapter,
            "blast": blast_chapter
            }
    text=src.substitute(substitution)
    out=open(args.output, "w")
    out.write(text)
    out.close()

#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()


