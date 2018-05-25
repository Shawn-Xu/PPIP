#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Version: 3.0
Author: XuShaohang
E-mail: xsh.skye@gmail.com
'''
import sys
import stat
import os
import shutil
import json
import tempfile
import subprocess
import argparse
import gzip
#import textwrap
    
#-------------------------------------------#
#               Class                       #
#-------------------------------------------#

class Json(object):
    '''
    Json handle
    '''
    def __init__(self):
        self.__file=""
    def setFile(self,f):
        self.__file=f
    def parse2dict(self):
        with gzip.GzipFile(self.__file, 'r') as f:
            return json.load(f)
def init_opt():
    parser = argparse.ArgumentParser(description="venomDB annotation tool!")
    parser.add_argument('-i', '--fasta',type=str, dest="fasta", required=True, help='the fata file for query!')
    parser.add_argument('-c', '--db',type=str, dest="db", required=True, help='the database file from venomDB (JSON)!')
    parser.add_argument('-o', '--outprefix',type=str, dest= "outprefix", required=False, default="demo", help='prefix of output file!')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help="set the debug mode (default: False)")
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    return args

#-------------------------------------------#
#               main function               #
#-------------------------------------------#

def main():
    #------parameter options--->
    args = init_opt()
    if args.db is None:  
        parser.error("Incorrect number of arguments, please check it with --help!")

    #### Json test start
    jsonObj = Json()
    jsonObj.setFile(args.db)
    venomdb=jsonObj.parse2dict()
    #### Json test end
    #print json.dumps(par, indent=4, sort_keys=True)
    #out=open(args.outprefix+"-sequence.fa", 'w')

    tmpdir = tempfile.mkdtemp()
    if(args.debug):
        print(tmpdir)
    tmpdb=os.path.join ( tmpdir, "venomdb-sequence.fa" )
    out=open(tmpdb, 'w')
    
    venom_desc_dict={}
    venom_name_dict={}
    for entry in venomdb:
        venom_desc_dict[entry['venomkb_id']]=entry['description']
        venom_name_dict[entry['venomkb_id']]=entry['name']
        out.write(">%s\n%s\n" %(entry['venomkb_id'],entry["aa_sequence"]))
    out.close()
    dbext = filter(lambda x: x.endswith(("phr", "pin", "psq")),os.listdir(tmpdir))
    if(len(dbext)<3):  #check db had been builded.
        cmd_chip1 = "makeblastdb -dbtype prot -in %(db)s -out %(db)s && \
                "% {'db': tmpdb}
    else:
        cmd_chip1 = ""
    #cmd_chip2 = ("blastp -db %(db)s -num_threads 1 -query %(msdir)s/%(sam)s-sequence.fa "
#            "-out %(atdir)s/%(sam)s.asn -outfmt 11 -evalue %(evalue)s %(opts)s && "
    cmd_chip2 = ("blastp -db %(db)s -num_threads 1 -query %(fasta)s "
            "-out venom.asn -outfmt 11 -evalue 0.00001 && "
            #"blast_formatter -archive venom.asn -outfmt 0 > venom-pairwise.txt && "
            #"blast_formatter -archive sc.asn -outfmt '7 qaccver saccver pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle' > sc-tabular.txt"
            "blast_formatter -archive venom.asn -outfmt 6 > venom-tabular.txt"
            ) %{
                'db': tmpdb,
                'fasta': args.fasta
            }
    command= cmd_chip1 + cmd_chip2
    if(args.debug):
        print(command)
    p=subprocess.Popen("bash -c \"%s\"" % (command), shell=True)
    p.wait()

    once_print={}   #temp dict for print id only once.
    final=open(args.outprefix+"-venom.tsv", 'w')
    final.write("Protein\tVenomkb_id\tPercentage_identical\tExpect_value\tVenom_name\tVenomkb_link\n")
    for line in open("venom-tabular.txt"):
        elem=line.rstrip().split("\t")
        if float(elem[2])<80:  # only display the query of identical matches >= 80%.
            continue
        #final.write("%s\t%s\t%s\t%s\t%s\t%s\n" %(elem[0],elem[1],elem[2],elem[10],venom_name_dict[elem[1]],"http://venomkb.org/"+elem[1]) )
        if(elem[0] in once_print):
            final.write("%s\t%s\t%s\t%s\t%s\t%s\n" %(" ",elem[1],elem[2],elem[10],venom_name_dict[elem[1]],"http://venomkb.org/"+elem[1]) )
        else:
            final.write("%s\t%s\t%s\t%s\t%s\t%s\n" %(elem[0],elem[1],elem[2],elem[10],venom_name_dict[elem[1]],"http://venomkb.org/"+elem[1]) )
            once_print[elem[0]]=1
    final.close()
    
    if(not args.debug):
        try:
            shutil.rmtree(tmpdir)
            os.remove("venom.asn")
            os.remove("venom-tabular.txt")
        except OSError:
            pass

    #print par[0]['venomkb_id'],"\t",par[0]["name"],"\t",par[0]["description"],"\t",par[0]["aa_sequence"]
    #print json.dumps(par[0], indent=4, sort_keys=True)


#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()
