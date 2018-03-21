#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: XuShaohang
E-mail:xushaohang@deepxomics.com
Company: DeepXOmics
'''
import sys,argparse
from itertools import groupby
import re
import petl as etl
from collections import OrderedDict
#-------------------------------------------#
#               functions                   #
#-------------------------------------------#
def init_opt(): 
    parser = argparse.ArgumentParser(description="fasta extract tool")
    parser.add_argument('-o', '--outprefix',type=str, dest= "outprefix", required=False, default="demo", help='prefix of output file (default: demo)')
    parser.add_argument('-q', '--pepqvalue',type=str, dest= "qvalue", required=False, default="0.01", help='peptide qvalue (default: 0.01)')
    parser.add_argument('-i', '--input',type=str, dest="input", required=True, help='MSGFPlus result(*.tsv) (REQUIRED)')
    parser.add_argument('-d', '--database',type=str, dest="db", required=True, help='database file (REQUIRED)')
    if len(sys.argv)==1:  
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    return args


def get_rawseq(seq):
    seq1=re.sub(r'^[\w-]\.(.+)\.[\w-]$',r"\1",seq)
    seq2=re.sub("[\d\.\+]+",r"",seq1)
    return seq2

def fasta_iter(fasta_name):
    """
    given a fasta file. yield tuples of header, sequence
    """
    fh = open(fasta_name)
    # ditch the boolean (x[0]) and just keep the header or sequence since
    # we know they alternate.
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq

def xls_tidy(xls,qvalue):
    d=etl.fromtsv(xls)
    sd=etl.select(d,lambda x: float(x.PepQValue) <=float(qvalue))
    psmsummary=sd

    ssd=etl.cut(sd, 'Peptide', 'Protein', 'PepQValue')
    #remove the mod info in peptide.
    ssd=etl.transform.regex.sub(ssd,'Peptide', r'^[\w-]\.(.+)\.[\w-]$', r'\1')
    ssd=etl.transform.regex.sub(ssd,'Peptide', r'[\d\.\+]+', r'')

    aggregation = OrderedDict()
    aggregation['SpecCount'] = len
    cssd=etl.aggregate(ssd, 'Peptide', aggregation)

    fssd=etl.groupselectfirst(ssd, key=('Peptide','Protein',"PepQValue"))
    aggregation = OrderedDict()
    aggregation['Protein'] = 'Protein', etl.strjoin(';')
    aggregation['PepQValue'] = 'PepQValue', etl.strjoin(';')
    assd=etl.aggregate(fssd, 'Peptide', aggregation)
    pepsummary=etl.join(assd, cssd, key='Peptide')

    return (psmsummary, pepsummary)

#-------------------------------------------#
#               main function               #
#-------------------------------------------#

def main():
    args = init_opt()
    (psmsummary, pepsummary)=xls_tidy(args.input,args.qvalue)
    etl.totsv(psmsummary, args.outprefix+"-psmSummary.tsv")
    etl.totsv(pepsummary, args.outprefix+"-pepSummary.tsv")

    out=open(args.outprefix+"-sequence.fa", 'w')
    proid={x.split(";")[0]:True for x in pepsummary['Protein']}  #get the first protein id
    for header, seq in fasta_iter(args.db):
        if(header in proid):
            out.write(">%s\n%s\n" %(header,seq))
    out.close()
#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()


