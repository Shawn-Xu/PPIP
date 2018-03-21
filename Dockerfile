# Base image
FROM debian

# Metadata
LABEl base.image="debian:latest"
LABEL software="PPIP"
LABEL software.version="1.0"
LABEL description="A dedicated software for identifying endogenous peptides based on peptidomics and RNA-Seq data"
LABEL documentation="https://github.com/xxxx"
LABEL license="https://www.gnu.org/licenses/gpl.html"
LABEL tags="Proteomics"

# Maintainer
MAINTAINER Shaohang Xu <xsh.skye@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bkp && \
	#require modification
    bash -c 'echo -e "deb http://mirrors.163.com/debian/ stable main non-free contrib\n" > /etc/apt/sources.list' && \
    cat /etc/apt/sources.list

RUN apt-get clean all && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        wget            \
        zip             \
        build-essential \
        openjdk-8-jre   \
        zlib1g-dev &&   \
    apt-get clean && \
    apt-get purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    #wget --quiet https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
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

#ENV PATH=$PATH:/home/biouser/bin
ENV PATH=/opt/conda/bin:$PATH
ENV HOME=/home/biouser

## set up tool config and deployment area:
ENV BIN /usr/local/bin/

#dirs for self-tools and pipe scripts
ADD Auxtools /opt/Auxtools/
ADD Pipeline/ /opt/Pipeline

#install Trinity
#pandoc is essential for rmarkdown
ADD Trinity-v2.5.0.tar.gz /tmp/
RUN mv /opt/Pipeline/pipe ${BIN} && chmod +x /usr/local/bin/pipe && \
	echo "==> Install compile tools..."  && \
		apt-get update && apt-get install -y --no-install-recommends \
				less \ 
#				libexpat1-dev \
				pandoc \
				git \
				blast2 \
				rsync && \
	echo "==> Download, compile, and install..."  && \  
		#wget "https://github.com/trinityrnaseq/trinityrnaseq/archive/Trinity-v2.5.0.tar.gz" | tar zxv  && \ 
		cd /tmp/trinityrnaseq-Trinity-v2.5.0/ && \
		make && \
		make plugins && \ 
		make install && \ 
		cd ../ && rm -rf trinityrnaseq-Trinity-v2.5.0/ Trinity-v2.5.0.tar.gz && \
		cd /opt/ && git clone https://github.com/OpenGene/AfterQC.git && \
	echo "==> Clean up..."  && \   
		apt-get remove -y --auto-remove rsync git && \
		apt-get clean                                  && \   
		rm -rf /var/lib/apt/lists/*

#install MSGFPLUS and bowtie。Trinity require Bowtie.
#*#ADD bowtie2-2.3.3.1-linux-x86_64.zip /tmp/
#*#ADD MSGFPlus.zip /opt/
RUN echo "==> Install compile tools..."  && \
		apt-get update && apt-get install -y --no-install-recommends \
				unzip && \
	echo "==> Download, compile, and install..."  && \  
		wget https://omics.pnl.gov/sites/default/files/MSGFPlus.zip -O /opt/MSGFPlus.zip && \
		cd /opt && unzip MSGFPlus.zip -d MSGFPlus && \
		cd /tmp && \
		wget https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.3.3.1/bowtie2-2.3.3.1-linux-x86_64.zip/download -O /tmp/bowtie2-2.3.3.1-linux-x86_64.zip && \
		unzip bowtie2-2.3.3.1-linux-x86_64.zip && \
		mv /tmp/bowtie2-2.3.3.1-linux-x86_64/bowtie2*  $BIN && \
	echo "==> Clean up..."  && \   
		apt-get remove -y --auto-remove unzip && \
		apt-get clean                                  && \   
		rm -rf /var/lib/apt/lists/* /opt/MSGFPlus.zip /tmp/bowtie2-2.3.3.1-linux-x86_64*

#install PhantomJS and casperjs. Taobao registry was uesed in China for net acceleration。
RUN wget https://npm.taobao.org/dist/phantomjs/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
#*# RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /tmp/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
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
ENV TRINITY_HOME /usr/local/bin/trinityrnaseq-Trinity-v2.5.0/
#NOTE: The python packages which are installed by pip will be stored in /home/biouser/.local/bin and /home/biouser/.local/lib.
ENV PATH=${TRINITY_HOME}:/home/biouser/.local/bin:${PATH}    

USER biouser
##以下三行为清华源,实际提交时要注释掉,换成默认的管方源
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
RUN conda config --set show_channel_urls yes

#NOTE: r-xml of conda is required for XML of R packages.
#中间的中科大镜像最后发布时可以去掉
# gcc, gxx(g++) and gfortran is essential for the compilation of MSA. It can be removed after the completion of compilation.
RUN	conda install gcc_linux-64 gcc_impl_linux-64 binutils_linux-64 binutils_impl_linux-64 gxx_linux-64 gxx_impl_linux-64 gfortran_impl_linux-64 gfortran_linux-64\ 
	petl r=3.4.2 r-ggplot2 r-xml && \
    R -e 'source("https://bioconductor.org/biocLite.R");   repos <- getOption("repos");repos["CRAN"] <- "https://mirrors.ustc.edu.cn/CRAN/";options(repos = repos); options(BioC_mirror = "https://mirrors.ustc.edu.cn/bioc/");biocLite(c("Biostrings","data.table","msa","rmarkdown","prettydoc","ggplot2","plotly","kableExtra","treemapify","ggthemes"));' && \
	conda remove gcc_linux-64 gcc_impl_linux-64 binutils_linux-64 binutils_impl_linux-64 gxx_linux-64 gxx_impl_linux-64 gfortran_impl_linux-64 gfortran_linux-64 && \ 
	conda clean -y --all && rm -rf /tmp/* 

WORKDIR /data
