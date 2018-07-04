args = commandArgs(trailingOnly=TRUE)
#args[1] -> sample name, e.g. "Scropion"
#args[2] -> the protein database

library(data.table)
library(Biostrings)
library(tidyr)
library(dplyr)
#d<-fread("./brain.txt")
tryCatch({
	pth<-paste0(args[1], ".txt")
	data_code <- sprintf("cat %s|perl -lane 'if(/^CometVersion/){next}elsif(/^scan/){print \"$_\tdummy\"}else{print}'", pth)
	#data_code <- sprintf("cat %s|perl -lane 'if(/^CometVersion/){next}else{print}'", pth)
	d<-fread( data_code)
},error=function(e){cat("ERROR : input file of ",paste0(args[1], ".txt")," didn't exist!\n")})
#d[,V19:=NULL]
#d[,V18:=NULL]
d[,modifications:=NULL]
d[,dummy:=NULL]
#colnames(d)<-c("scan","num","charge","exp_neutral_mass","calc_neutral_mass","Evalue","xcorr",
#			   "delta_cn","sp_score","ions_matched","ions_total",
#			   "plain_peptide","modified_peptide","prev_aa","next_aa","protein","protein_count")
d[,target_count:=sum(!grepl("DECOY_",unlist(strsplit(protein,",")))),by=.(scan)]
setnames(d, "e-value", "Evalue")
setorder(d, "Evalue")  #sort by Evalue
ud<-d[ !duplicated(d$modified_peptide), ]   #take the first row within 'each modified_peptide'

evr<-new.env()
evr$dhit<-0
evr$thit<-0
fdr<-function (tc)
{
	if(tc>0)
	{
		evr$thit=evr$thit+1
	}
	else
	{
		evr$dhit=evr$dhit+1
	}
	evr$dhit/evr$thit
}
ud[,fdr:=fdr(target_count),by=.(scan)]
if(FALSE)
{
	test<-ud$fdr
	png("fdr_distribution.png",width=600,height=600)
	plot(test[test<=0.01],type="l",main="FDR distribution",xlab="order",ylab="FDR")
	dev.off()
}

rud<-ud[nrow(ud):1,]  #reverse the data.table
fdr<-rud$fdr
fdr<-c(100,fdr)   #add a big e-value number at the head.
for (i in 2:length(fdr))  #qvalue smooth
{
	if(fdr[i]>fdr[i-1])
	{
		fdr[i]=fdr[i-1]
	}
}
qvalue<-fdr[-1]   #remove the big e-value.

if(FALSE)
{
	png("qvalue_distribution.png",width=600,height=600)
	plot(rev(qvalue[qvalue<=0.01]),type="l",main="Qvalue distribution",xlab="order",ylab="Qvalue")
	dev.off()
}
rud$qvalue<-qvalue

fud<-rud[nrow(rud):1,] #reverse the data.table again
fud<-fud[target_count!=0]  #filter decoy entry
fud[,protein:=paste(grep("DECOY_",unlist(strsplit(protein,",")),value=TRUE,invert=TRUE),collapse=";"),by=.(scan)]  #remove DECOY_ ID in protein items

identified_pep_set<-unique(fud[qvalue<=0.01]$plain_peptide)

#psm-summary.txt
psm_E_threshold<-tail(fud[qvalue<=0.01],n=1)$Evalue  #get the PSM evalue of Pepvalue==0.01
psmsummary<-d[Evalue<=psm_E_threshold] %>% filter(target_count!=0) %>% select(-target_count)
write.table(psmsummary,file=paste0(args[1], "-psmSummary.tsv"),quote=F,sep="\t",row.names=F)

#qvalue and PPM of all spectra
rawsummary<-fud %>%mutate(ppm=(exp_neutral_mass-calc_neutral_mass)/calc_neutral_mass*10^6 )
setnames(rawsummary,"ppm","PrecursorError(ppm)")
setnames(rawsummary,"qvalue","PepQValue")
write.table(rawsummary,file=paste0(args[1], "-rawSummary.tsv"),quote=F,sep="\t",row.names=F)

sc_dict<-psmsummary %>% group_by(plain_peptide) %>%   summarise(SpecCount=n()) #get spectrum count of each peptide
pepsummary<-fud[qvalue<=0.01] %>% select(plain_peptide,protein,qvalue) %>%group_by(plain_peptide,protein) %>% summarise(qvalue=min(qvalue)) %>% arrange(qvalue) %>% left_join(sc_dict,by=c("plain_peptide"="plain_peptide"))

colnames(pepsummary)<-c("Peptide","Protein","PepQValue","SpecCount")
write.table(pepsummary,file=paste0(args[1], "-pepSummary.tsv"),quote=F,sep="\t",row.names=F)

setDT(pepsummary)
pid<-unique(pepsummary[,.(primary=unlist(strsplit(Protein,";"))[1]),by=.(Peptide)]$primary)
tryCatch({
	faobj<-readAAStringSet(args[2])
},error=function(e){cat("ERROR : input file of ",args[2]," didn't exist!\n")})

subfa<-faobj[names(faobj) %in% pid]
writeXStringSet(subfa,paste0(args[1], "-sequence.fa"))
