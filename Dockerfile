# Base image
FROM debian

# Metadata
LABEl base.image="debian:latest"
LABEL software="PPIP"
LABEL software.version="1.1.0"
LABEL description="A dedicated software for identifying endogenous peptides based on peptidomics and RNA-Seq data"
LABEL documentation="https://shawn-xu.github.io/PPIP"
LABEL license="https://www.gnu.org/licenses/gpl.html"
LABEL tags="Proteomics"

MAINTAINER Shaohang Xu <xsh.skye@gmail.com>

ENV DEBIAN_FRONTEND noninteractive
ENV TRINITY_VERSION 2.6.6

#*# RUN echo "151.101.24.133 assets-cdn.github.com" >>/etc/hosts && \
#*#	echo "151.101.197.194 github.global.ssl.fastly.net" >>/etc/hosts && \
#*#	echo "52.74.223.119 www.github.com" >>/etc/hosts

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
	### NOTE: replace the mirror with "http://deb.debian.org/debian/" when tool release.
    bash -c 'echo -e "deb http://deb.debian.org/debian/ stable main non-free contrib\n" > /etc/apt/sources.list' && \
    #*# bash -c 'echo -e "deb http://mirrors.163.com/debian/ stable main non-free contrib\n" > /etc/apt/sources.list' && \
    cat /etc/apt/sources.list

RUN apt-get clean all && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        wget            \
        zip             \
		libbz2-dev    \
		liblzma-dev  \
        build-essential \
        openjdk-8-jre   \
        zlib1g-dev &&   \
    apt-get clean && \
    apt-get purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    #*# wget --quiet https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
        chmod 777 -R /opt/conda/ && \
    rm ~/miniconda.sh

RUN mkdir /data /config

# Add user biouser with password biouser
RUN groupadd fuse && \
    useradd --create-home --shell /bin/bash --user-group --uid 1000 --groups sudo,fuse biouser && \
    echo `echo "biouser\nbiouser\n" | passwd biouser` && \
    chown biouser:biouser /data && \
    chown biouser:biouser /config

ENV PATH=/opt/conda/bin:$PATH
ENV HOME=/home/biouser

## set up tool config and deployment area:
ENV BIN /usr/local/bin/
ENV LD_LIBRARY_PATH=/usr/local/lib
#dirs for self-tools and pipe scripts
ADD Auxtools /opt/Auxtools/
ADD Pipeline/ /opt/Pipeline

### install Trinity
#pandoc is essential for rmarkdown
#ADD Trinity-v${TRINITY_VERSION}.tar.gz /tmp/
RUN mv /opt/Pipeline/pipe ${BIN} && chmod +x /usr/local/bin/pipe && \
	echo "==> Install compile tools..."  && \
		apt-get update && apt-get install -y --no-install-recommends \
				less \ 
#				libexpat1-dev \
				libncurses5-dev \
				pandoc \
				git \
				blast2 \
				rsync && \

	echo "==> Download, compile, and install ..."  && \  
		wget https://github.com/samtools/samtools/releases/download/1.7/samtools-1.7.tar.bz2 -O /tmp/samtools-1.7.tar.bz2 && \
		#wget http://192.168.1.2:6677/dl/samtools-1.7.tar.bz2 -O /tmp/samtools-1.7.tar.bz2 && \
		tar xvf /tmp/samtools-1.7.tar.bz2 -C /tmp/ && \
		cd /tmp/samtools-1.7/ && \
		./configure && make && make install && \
		rm -rf /tmp/samtools-1.7/ && \
		wget https://github.com/gmarcais/Jellyfish/releases/download/v2.2.7/jellyfish-2.2.7.tar.gz -O /tmp/jellyfish-2.2.7.tar.gz && \
		#wget http://192.168.1.2:6677/dl/jellyfish-2.2.7.tar.gz -O /tmp/jellyfish-2.2.7.tar.gz && \
		tar xvf /tmp/jellyfish-2.2.7.tar.gz -C /tmp/ && \
		cd /tmp/jellyfish-2.2.7/ && \
		./configure && make && make install && \
		rm -rf /tmp/jellyfish-2.2.7/ && \
		wget https://github.com/COMBINE-lab/salmon/releases/download/v0.9.1/Salmon-0.9.1_linux_x86_64.tar.gz -O /opt/Salmon-0.9.1_linux_x86_64.tar.gz && \
		#wget http://192.168.1.2:6677/dl/Salmon-0.9.1_linux_x86_64.tar.gz -O /opt/Salmon-0.9.1_linux_x86_64.tar.gz && \
		cd /opt/ && tar xvf Salmon-0.9.1_linux_x86_64.tar.gz && \
		ln -s /opt/Salmon-latest_linux_x86_64/bin/salmon $BIN/.  && \
	echo "==> Download, compile, and install..."  && \  
		wget "https://github.com/trinityrnaseq/trinityrnaseq/archive/Trinity-v${TRINITY_VERSION}.tar.gz" -O /tmp/Trinity-v${TRINITY_VERSION}.tar.gz  && \ 
		#wget http://192.168.1.2:6677/dl/Trinity-v${TRINITY_VERSION}.tar.gz -O /tmp/Trinity-v${TRINITY_VERSION}.tar.gz  && \
		tar xvf /tmp/Trinity-v${TRINITY_VERSION}.tar.gz -C /tmp/ && \
		cd /tmp/trinityrnaseq-Trinity-v${TRINITY_VERSION}/ && \
		make && \
		make plugins && \ 
		make install && \ 
		rm -rf /tmp/trinityrnaseq-Trinity-v${TRINITY_VERSION}/ /tmp/Trinity-v${TRINITY_VERSION}.tar.gz && \
		cd /opt/ && git clone https://github.com/OpenGene/AfterQC.git && \
	echo "==> Clean up..."  && \   
		apt-get remove -y --auto-remove rsync git && \
		apt-get clean                                  && \   
		rm -rf /var/lib/apt/lists/*  && rm -rf /tmp/* && rm /opt/Salmon-0.9.1_linux_x86_64.tar.gz

#install MSGFPLUS and bowtie。Trinity require Bowtie.
RUN echo "==> Install compile tools..."  && \
		apt-get update && apt-get install -y --no-install-recommends \
				unzip && \
	echo "==> Download, compile, and install..."  && \  
		wget https://omics.pnl.gov/sites/default/files/MSGFPlus.zip -O /opt/MSGFPlus.zip && \
		#wget http://192.168.1.2:6677/dl/MSGFPlus.zip -O /opt/MSGFPlus.zip  && \
		cd /opt && unzip MSGFPlus.zip -d MSGFPlus && \
		cd /tmp && \
		wget https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.3.3.1/bowtie2-2.3.3.1-linux-x86_64.zip/download -O /tmp/bowtie2-2.3.3.1-linux-x86_64.zip && \
		#wget http://192.168.1.2:6677/dl/bowtie2-2.3.3.1-linux-x86_64.zip -O /tmp/bowtie2-2.3.3.1-linux-x86_64.zip  && \
		unzip bowtie2-2.3.3.1-linux-x86_64.zip && \
		mv /tmp/bowtie2-2.3.3.1-linux-x86_64/bowtie2*  $BIN && \
		wget https://excellmedia.dl.sourceforge.net/project/comet-ms/comet_2018011.zip -O /opt/comet_2018011.zip && \
		#wget http://192.168.1.2:6677/dl/comet_2018011.zip -O /opt/comet_2018011.zip  && \
		cd /opt && unzip comet_2018011.zip comet.2018011.linux.exe && chmod +x comet.2018011.linux.exe && \
	echo "==> Clean up..."  && \   
		apt-get remove -y --auto-remove unzip && \
		apt-get clean                                  && \   
		rm -rf /var/lib/apt/lists/* /opt/MSGFPlus.zip /tmp/bowtie2-2.3.3.1-linux-x86_64* /opt/comet_2018011.zip

#install PhantomJS and casperjs. Taobao registry was uesed in China for net acceleration。
#*# RUN wget https://npm.taobao.org/dist/phantomjs/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
	tar xvf /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /tmp && \
    cp /tmp/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/phantomjs-2.1.1-linux-x86_64 /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2  && \
	wget https://github.com/casperjs/casperjs/tarball/1.1.0 -O /tmp/casperjs-1.1.0.tar.gz && \
	tar xvf /tmp/casperjs-1.1.0.tar.gz -C /opt/ && \
	wget http://www.bioinfocabd.upo.es/sma3s/sma3s_v2.pl -O /opt/Auxtools/sma3s_v2.pl && \
	#raname。
	mv /opt/casperjs* /opt/casperjs && \
	ln -sf /opt/casperjs/bin/casperjs /usr/local/bin/casperjs && \
	rm -rf /tmp/casperjs-1.1.0.tar.gz

#add Trinity ENV
ENV TRINITY_HOME /usr/local/bin/trinityrnaseq-Trinity-v${TRINITY_VERSION}/
#NOTE: The python packages which are installed by pip will be stored in /home/biouser/.local/bin and /home/biouser/.local/lib.
ENV PATH=${TRINITY_HOME}:/home/biouser/.local/bin:${PATH}    

USER biouser
##NOTE: *** the tsinghua mirror could be deleted ***
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
RUN conda config --set show_channel_urls yes

#NOTE: r-xml of conda is required for XML of R packages.
# gcc, gxx(g++) and gfortran is essential for the compilation of MSA. It can be removed after the completion of compilation.
# Trinity 2.6.6 require the python numpy package.
RUN	conda install gcc_linux-64 gcc_impl_linux-64 binutils_linux-64 binutils_impl_linux-64 gxx_linux-64 gxx_impl_linux-64 gfortran_impl_linux-64 gfortran_linux-64 \ 
	petl r=3.4.2 r-ggplot2 r-xml numpy && \
	R -e 'source("https://bioconductor.org/biocLite.R"); biocLite(c("Biostrings","data.table","msa","rmarkdown","prettydoc","ggplot2","plotly","kableExtra","treemapify","ggthemes"));' && \
    #*# R -e 'options(useHTTPS=FALSE, BioC_mirror="http://bioconductor.org");source("http://bioconductor.org/biocLite.R"); repos <- getOption("repos");repos["CRAN"] <- "https://mirrors.ustc.edu.cn/CRAN/";options(repos = repos); options(BioC_mirror = "https://mirrors.ustc.edu.cn/bioc/");biocLite(c("Biostrings","data.table","msa","rmarkdown","prettydoc","ggplot2","plotly","kableExtra","treemapify","ggthemes"));' && \
	conda remove gcc_linux-64 gcc_impl_linux-64 binutils_linux-64 binutils_impl_linux-64 gxx_linux-64 gxx_impl_linux-64 gfortran_impl_linux-64 gfortran_linux-64 && \ 
	conda clean -y --all && rm -rf /tmp/* 

WORKDIR /data
