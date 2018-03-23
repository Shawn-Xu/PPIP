#--fasta is the required par, another par is optional.
casperjs signalP.js  --fasta=test.fasta
casperjs signalP.js  --fasta=test.fasta --dcut=user --notm=0.35

casperjs kobas.js --fasta=test.fasta --species="Mus musculus (mouse)"

perl web_blast.pl -i test.fasta
