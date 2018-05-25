#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: Shaohang Xu
E-mail: xsh.skye@gmail.com
'''
import sys,argparse
import subprocess
import textwrap
import os
import tempfile

#-------------------------------------------#
#               functions                   #
#-------------------------------------------#
def init_opt():
    parser = argparse.ArgumentParser(description="MSA program")
    parser.add_argument('-i', '--input',type=str, dest="input", required=True, help='Input sequences. The file must be in FASTA format. (REQUIRED)')
    parser.add_argument('-m', '--method',type=str, dest= "method", required=False, default="ClustalOmega", help='Specifies the multiple sequence alignment to be used; currently, "ClustalW", "ClustalOmega", and "Muscle" are supported. (default: ClustalOmega)')
    parser.add_argument('-o', '--output',type=str, dest= "output", required=False, default="msa.html", help='output html filename (default: msa.html)')
    parser.add_argument('-d', dest='debug', action='store_true', help="set the debug mode (default: False)")
    if len(sys.argv)==1:   #print help info when there is no flag
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    return args
#-------------------------------------------#
#               main function               #
#-------------------------------------------#

def main():
    tmpdir = tempfile.mkdtemp()
    tmpfa=os.path.join ( tmpdir, "tmp.fa" )
    tmpr=os.path.join ( tmpdir, "tmp.R" )

    args=init_opt()
    rscript=textwrap.dedent(r"""
    library(msa)
    mySequences <- readAAStringSet("%s")
    myalign<-msa(mySequences,method="%s")
    myFa<-as(myalign, "BStringSet")
    writeXStringSet(myFa,"%s", format="fasta")
    """) % (args.input, args.method, tmpfa)
    rfile=open(tmpr, 'w')
    rfile.write(rscript)
    rfile.flush()  #Make sure the output is complete
    print("Rscript --vanilla %s" %(tmpr))
    p=subprocess.Popen("Rscript --vanilla %s" % (tmpr), shell=True)
    p.wait()

    try:
        os.remove("msa.html")
    except OSError:
        pass
    msafile=open(args.output,"w+")
    msafile.write(textwrap.dedent(r"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="description" content="MSA">
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <title>MSA viewer</title>
    </head>
    <body>
        <script src="https://cdn.bio.sh/msa/latest/msa.min.gz.js"></script>
        <div id="msa">Loading Multiple Alignment...</div>
        <pre style="display: none" id="fasta-file">
    """))
    count=0
    for line in open(tmpfa):
        msafile.write(line)
        count+=1
    height=225 
    if count>=50:
        height=600

    msafile.write(textwrap.dedent(r"""
    </pre>
    <script>
    var fasta = document.getElementById("fasta-file").innerText;

    var m = msa({
        el: document.getElementById("msa"),
        seqs: msa.io.fasta.parse(fasta),
        bootstrapMenu: true,
        vis: {
            conserv: false,
            overviewbox: false,
            seqlogo: true
        },
        zoomer: {
            alignmentHeight: %s
        }
    });
    m.render();
    </script>
    </body>
    </html>
    """) % (height))
    if(not args.debug):
        try:
            #os.remove(tmpr)
            #os.remove(tmpfa)
            os.removedirs(tmpdir)
        except OSError:
            pass

    #-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()
