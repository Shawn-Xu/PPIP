#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Version: 1.0
Author: Shaohang Xu
E-mail: xsh.skye@gmail.com
'''
import sys,argparse,os
import re
import textwrap

#-------------------------------------------#
#                   class                   #
#-------------------------------------------#
def myreadlines(f, delimiter):  # a generator with a specified delimiter for newline
    buf = ""
    while True:
        while delimiter in buf:
            pos = buf.index(delimiter)
            yield buf[:pos]
            buf = buf[pos + len(delimiter):]
        chunk = f.read(4096)
        if not chunk:
            yield buf
            break
        buf += chunk

#-------------------------------------------#
#               functions                   #
#-------------------------------------------#
def init_opt(): 
    '''This is the argument parser wrapper function!!!'''
    parser = argparse.ArgumentParser(description="A dummy program")
    parser.add_argument('-o', '--outdir',type=str, dest= "outdir", required=False, default="blast_html", help='output directory (default: blast_html')
    parser.add_argument('-i', '--input',type=str, dest="input", required=True, help='Blast pairwiser file(REQUIRED)')
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
    #for line in open(args.input):
    #    print line.strip()
    homedir=sys.path[0]
    with open(args.input) as f:
        if not os.path.exists(args.outdir):
            os.makedirs(args.outdir)
        js1=open(homedir+"/../js/blaster.min.js").read()
        js2=open(homedir+"/../js/html2canvas.min.js").read()
        for block in myreadlines(f, "Query="):
            if block.startswith("BLAST"):
                continue
            block="Query="+block
            lines=block.split("\n")
            ID=re.search(r'Query= ([\S]+)', lines[0]).group(1)
            invaild_symbol = re.search(r'[^\w]', ID)
            if invaild_symbol:
                print("ERROR: Protein ID could not include invaild symbol, such as: '|,?,+,!...'");
                sys.exit(-2);

            out=open(args.outdir+"/"+ID+".html", 'w')
            out.write(textwrap.dedent(r"""<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous" />
            </head>
            <body>
            <div id="blast-multiple-alignments"></div>
            <div id="blast-alignments-table"></div>
            <div id="blast-single-alignment"></div>
            
            <script type="text/javascript">%s</script>
            <script type="text/javascript">%s</script>
            <script type="text/javascript">
            var alignments=[
            """) % (js1,js2))

            for line in lines:
                out.write('"%s",\n' %(line))
            out.write(textwrap.dedent(r"""].join('\n');
            var blasterjs = require("biojs-vis-blasterjs");
            var instance = new blasterjs({
                string: alignments,
                multipleAlignments: "blast-multiple-alignments",
                alignmentsTable: "blast-alignments-table",
                singleAlignment: "blast-single-alignment",
             });
            </script>
            </body>
            </html>
            """))
            out.close()

#-------------------------------------------#
#       executable code of non-imported     #
#-------------------------------------------#
if __name__=="__main__":
    main()


