FROM srhopkins/ipyrun

RUN apt-get update && apt-get install -y git

RUN mkdir -p /data/db
RUN wget -q https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-2.6.7.tgz -O mongodb.tgz && \
	tar xf mongodb.tgz -C /opt && \
	rm -f mongodb.tgz

WORKDIR /
COPY init.sh .
RUN chmod +x /init.sh

RUN pip install https://github.com/srhopkins/mongoqueue/zipball/master

RUN mkdir /notebooks
WORKDIR /notebooks

COPY examples.ipynb /notebooks/

ENTRYPOINT ["/init.sh"]
