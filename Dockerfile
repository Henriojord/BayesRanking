FROM debian:8.1

MAINTAINER Henrio Jordan

# Create directories ---------------------------------------------------------------------------------------
RUN mkdir -p /robocup/payload/ && mkdir -p /robocup/shared/

# Install dependencies -------------------------------------------------------------------------------------
RUN apt-get update && apt-get install -y wget build-essential dh-autoreconf \
libboost-dev zlib1g-dev zlib1g flex libboost-filesystem-dev libboost-system-dev \
python3 python3-dev python3-pip python3-gdbm python3-tk screen git gfortran libopenblas-dev liblapack-dev \
libfreetype6-dev pkg-config

# Install Bison 2.7.1 --------------------------------------------------------------------------------------
ADD payload/libbison-dev_2.7.1.dfsg-1_amd64.deb /robocup/payload/
ADD payload/bison_2.7.1.dfsg-1_amd64.deb /robocup/payload/
RUN dpkg -i /robocup/payload/libbison-dev_2.7.1.dfsg-1_amd64.deb && dpkg -i /robocup/payload/bison_2.7.1.dfsg-1_amd64.deb \
    && rm /robocup/payload/libbison-dev_2.7.1.dfsg-1_amd64.deb && rm /robocup/payload/bison_2.7.1.dfsg-1_amd64.deb

# Install RCSSServer ---------------------------------------------------------------------------------------
ADD payload/rcssserver-15.3.0_dockercompiled.tar.gz /robocup/payload/
RUN cd /robocup/payload/rcssserver-15.3.0/ && make install
RUN echo "/usr/local/share" >> /etc/ld.so.conf && echo "/usr/local/lib" >> /etc/ld.so.conf && ldconfig
RUN cd /robocup/ && rcssserver || true
