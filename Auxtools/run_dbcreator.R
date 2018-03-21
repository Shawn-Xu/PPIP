source("/opt/Auxtools/createProDB4DenovoRNASeq.R")
args = commandArgs(trailingOnly=TRUE)

db<-paste0(args[3], "/database")
if(!dir.exists(db))
{
	dir.create(db)
}
outmtab<-paste0(db, "/", args[4], ".ntx.tab")
outfa<-paste0(db, "/", args[4], ".ntx.fasta")
createProDB4DenovoRNASeq(infa=args[1],bool_get_longest=args[2],make_decoy=F, outfile_name=args[3], outmtab=outmtab, outfa=outfa)

