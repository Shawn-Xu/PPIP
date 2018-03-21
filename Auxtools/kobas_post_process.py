#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: XuShaohang
E-mail:xushaohang@deepxomics.com
Company: DeepXOmics
'''
import sys,argparse
import re
#-------------------------------------------#
#               functions                   #
#-------------------------------------------#
def init_opt(): 
    parser = argparse.ArgumentParser(description="KOBAS result post-processing tool!")
    parser.add_argument('-o', '--outprefix',type=str, dest= "outprefix", required=False, default="demo", help='prefix of output file (default: demo)')
    parser.add_argument('-i', '--input',type=str, dest="input", required=True, help='KOBAS output result (REQUIRED)')
    if len(sys.argv)==1:  
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    return args

def kobas_tidy(xls, prefix):
    fh = open(xls)
    block = ""

    kobas_list=[]
    for line in fh:
        if line.startswith("////"):
            kobas_list.append(block)
            block = ""
        else:
            block += line
    
    summary_raw=kobas_list.pop(0)

    koout=open(prefix+"-ko.tsv", 'w')
    koout.write("ID\tGeneID\tGeneName\tHyperlink\n")
    for line in summary_raw.split("\n"):
        if re.search(r'^\w', line): 
            elem=line.strip().split("\t")
            if len(elem)==2 and re.search(r'\|', elem[1]):
                arr=elem[1].split("|") 
                koout.write("%s\t%s\t%s\t%s\n" % (elem[0],arr[0],arr[1],arr[2] ))
    koout.close()

    dict_go={}
    for block in kobas_list:
        lines=block.split("\n")
        preID=None
        goslim_label = False
        for line in lines:
            regobj = re.search(r'^Query:\s+(\w.+)', line)
            if regobj is not None:
                preID=regobj.group(1)
            
            regobj = re.search(r'\t([^\t]+)\tGene Ontology Slim\t([\w:]+)', line)
            if regobj is not None:
                go=regobj.group(2)+"~"+regobj.group(1)
                if go in dict_go:
                    dict_go[go].append(preID)
                else:
                    dict_go[go]=[preID]
    goout=open(prefix+"-go.tsv", 'w')
    goout.write("GO\tIDs\tIDCount\n")
    for key,arr in dict_go.items():
        goout.write("%s\t%s\t%s\n"%(key,";".join(arr),len(arr)  ) )
    goout.close()

#-------------------------------------------#
#               main function               #
#-------------------------------------------#

def main():
    args = init_opt()
    kobas_tidy(args.input, args.outprefix)
#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()


