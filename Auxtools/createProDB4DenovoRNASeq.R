
library(data.table)
library(Biostrings)

#' @title Create protein database based on the transcripts from de novo 
#' reconstruction of transcriptome from RNA-seq data
#' @description Create protein database based on the transcripts from de novo 
#' reconstruction of transcriptome from RNA-seq data. 
#' @param infa A FASTA format file containing transcript sequences 
#' (such as derived from de novo transcriptome assembly by Trinity)
#' @param bool_use_3frame A logical variable indicating whether to translate the 
#' raw sequences with 3-frame (forward). Default is 6-frame translation (FALSE).
#' @param outmtab A txt format file containing the novel transcripts information
#' @param outfa The output fasta format protein sequence file 
#' @param bool_get_longest When it's set as TRUE, only the longest protein sequences will be 
#' retained after the raw sequences are translated with 3-frame or 6-frame. 
#' Otherwise, all the protein sequences with longer than 30 aa will be retained.
#' @param make_decoy A logical variable indicating whether to add the decoy sequences.
#' @param decoy_tag The prefix of decoy sequence IDs.
#' @param outfile_name Output file name
#' @return The database file(s)
#' @export
#' @examples
#' transcript_seq_file <- system.file("extdata/input", "Trinity.fasta",package="PGA")
#' createProDB4DenovoRNASeq(infa=transcript_seq_file)
createProDB4DenovoRNASeq<-function(infa="./trinity.fasta",
                       bool_use_3frame=FALSE,
                       outmtab="novel_transcripts_ntx.tab",
                       outfa="./novel_transcripts_ntx.fasta",
                       bool_get_longest=TRUE,
                       make_decoy=FALSE,
                       decoy_tag="#REV#",
                       outfile_name="test"){
    options(stringsAsFactors=FALSE)
    if(file.exists(outfa)){
        file.remove(outfa)
    }
    #var_tag <- "DNO"
    cumIndex <-0   
    dna_seq_forward<-readDNAStringSet(infa)
    names(dna_seq_forward)<-gsub(" .+","",names(dna_seq_forward))  #get the id, remove the description
    
    message("....... Proteomic database construction ! ............")
    # forward strand
    peptides_f1<-suppressWarnings(translate(dna_seq_forward,
                                            if.fuzzy.codon="solve"))
    peptides_f2<-suppressWarnings(translate(subseq(dna_seq_forward,start=2),
                                            if.fuzzy.codon="solve"))
    peptides_f3<-suppressWarnings(translate(subseq(dna_seq_forward,start=3),
                                            if.fuzzy.codon="solve"))  
    
    novel_cds_f1 <- .get_30aa_splited_seq(peptides_f1)
    novel_cds_f2 <- .get_30aa_splited_seq(peptides_f2)
    novel_cds_f3 <- .get_30aa_splited_seq(peptides_f3)   
    novel_cds_f1[,c("Strand","Frame","ID"):=list(a="+",
                                                 b="1",
                                                 c=paste(id,"+","F1",
                                                         Substring,
                                                         sep="|")),
                 by=.(id,Substring)]
    
    novel_cds_f2[,c("Strand","Frame","ID"):=list(a="+",
                                                 b="2",
                                                 c=paste(id,"+","F2",
                                                         Substring,
                                                         sep="|")),
                 by=.(id,Substring)]
    
    novel_cds_f3[,c("Strand","Frame","ID"):=list(a="+",
                                                 b="3",
                                                 c=paste(id,"+","F3",
                                                         Substring,
                                                         sep="|")),
                 by=.(id,Substring)]
    
    # reverse strand
    if(!bool_use_3frame)
    {
        dna_seq_reverse<-reverseComplement(dna_seq_forward)
        peptides_r1<-suppressWarnings(translate(dna_seq_reverse,
                                                if.fuzzy.codon="solve"))
        peptides_r2<-suppressWarnings(translate(subseq(dna_seq_reverse,start=2),
                                                if.fuzzy.codon="solve"))
        peptides_r3<-suppressWarnings(translate(subseq(dna_seq_reverse,start=3),
                                                if.fuzzy.codon="solve"))
        novel_cds_r1 <- .get_30aa_splited_seq(peptides_r1)
        novel_cds_r2 <- .get_30aa_splited_seq(peptides_r2)
        novel_cds_r3 <- .get_30aa_splited_seq(peptides_r3)   
        novel_cds_r1[,c("Strand","Frame","ID"):=list(a="-",
                                                     b="1",
                                                     c=paste(id,"-","F1",
                                                             Substring,
                                                             sep="|")),
                     by=.(id,Substring)]
        
        novel_cds_r2[,c("Strand","Frame","ID"):=list(a="-",
                                                     b="2",
                                                     c=paste(id,"-","F2",
                                                             Substring,
                                                             sep="|")),
                     by=.(id,Substring)]
        
        novel_cds_r3[,c("Strand","Frame","ID"):=list(a="-",
                                                     b="3",
                                                     c=paste(id,"-","F3",
                                                             Substring,
                                                             sep="|")),
                     by=.(id,Substring)]
        all_pep<-rbindlist(list(novel_cds_f1,novel_cds_f2,novel_cds_f3,
                                novel_cds_r1,novel_cds_r2,novel_cds_r3))
    }else
    {
        all_pep<-rbindlist(list(novel_cds_f1,novel_cds_f2,novel_cds_f3))
    }
    all_pep[,Index:=paste("NTX",cumIndex+.I,sep="")]
    
    if(bool_get_longest){
        #final_all_pep<-all_pep[,.(pep=seq[nchar(seq)==max(nchar(seq))],
        #ID=ID[nchar(seq)==max(nchar(seq))]),by=.(id)]
        final_all_pep<-all_pep[,.(pep=seq[nchar(seq)==max(nchar(seq))],
                                  ID=ID[nchar(seq)==max(nchar(seq))],
                                  Index=Index[nchar(seq)==max(nchar(seq))],
                                  Strand=Strand[nchar(seq)==max(nchar(seq))],
                                  Frame=Frame[nchar(seq)==max(nchar(seq))],
                                  start=start[nchar(seq)==max(nchar(seq))],
                                  end=end[nchar(seq)==max(nchar(seq))],
                                  Substring=Substring[nchar(seq)==max(nchar(seq))]),
                               by=.(id)]
        
        
        if(file.exists(outmtab)){
            write.table(subset(final_all_pep,
                               select=c(Index,id,Strand,Frame,start,end,Substring)),
                        file=outmtab, sep='\t', quote=FALSE, row.names=FALSE,
                        append=TRUE,col.names=FALSE)
        }else{
            write.table(subset(final_all_pep,
                               select=c(Index,id,Strand,Frame,start,end,Substring)),
                        file=outmtab, sep='\t', quote=FALSE, row.names=FALSE)
        }
        
        #final_all_pep<-all_pep[,.(pep=seq[which.max(nchar(seq))],ID=ID[which.max(nchar(seq))]),by=.(id)]
        #final_all_pep[,output:=paste('>',Index,"|",ID,'\n',pep,sep=''),
        final_all_pep[,output:=paste('>',Index,'\n',pep,sep=''),
                      by=.(ID)]
        write(final_all_pep$output,file=outfa,append=TRUE)
    }else{
        if(file.exists(outmtab)){
            write.table(subset(all_pep,
                               select=c(Index,id,Strand,Frame,start,end,Substring)),
                        file=outmtab, sep='\t', quote=FALSE, row.names=FALSE,
                        append=TRUE,col.names=FALSE)
        }else{
            write.table(subset(all_pep,
                               select=c(Index,id,Strand,Frame,start,end,Substring)),
                        file=outmtab, sep='\t', quote=FALSE, row.names=FALSE)
        }
        all_pep[,output:=paste('>',Index,'\n',seq,sep=''),by=.(ID)]
        write(all_pep$output,file=outfa,append=TRUE)
    }
    
    #add var tag, add decoy sequence
    if(make_decoy){
		xset_for<-readAAStringSet(outfa)
    	xset_rev<-xset_for
    	#names(xset_for)=paste(var_tag,"|",names(xset_for),sep="")
    	#names(xset_rev)=paste(decoy_tag,var_tag,"|",names(xset_rev),sep="")
    	names(xset_rev)=paste(decoy_tag,"|",names(xset_rev),sep="")
    	xset_rev<-reverse(xset_rev)
    	
    	outfile<-paste(outfile_name,"_pga.fasta",sep="")
    	writeXStringSet(xset_for,outfile)
        writeXStringSet(xset_rev,outfile,append=TRUE)
    	message("Write protein sequences to file: ",outfile)
    }
}

.get_30aa_splited_seq<-function(translated_seq){
    df<-as.data.frame(translated_seq)
    df["id"]<-rownames(df)
    colnames(df)<-c("raw","id")
    dt<-setDT(df)
    
    dt_split<-dt[,.(seq=unlist(strsplit(raw, "\\*"))),by=.(id,raw)]
    #must be 1L, not 1
    dt_split[, cumlen := cumsum((nchar(seq)+1L)), by=list(id, raw)]  
    dt_split[, c("start","end"):=list(cumlen-nchar(seq),cumlen-1L), 
             by=list(id, raw)]
    #remove the pep less than 30AA .
    sub.dt_split<-subset(dt_split,(end-start)>=29)  
    #add column "Substring"
    sub.dt_split[,Substring:=seq(1,.N),by=.(id,raw)] 
    sub.dt_split
    
}

