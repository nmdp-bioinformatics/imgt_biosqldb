# imgt_biosqldb
The IMGT/HLA sequence database persisted in a mysql BioSQL DB

## Overview
This repository contains code for building a BioSQL database with the IMGT/HLA sequence data. The database is generated with the `create_imgtdb.py` script and is built in a Docker image using the `Dockerfile`. This database is utilized by the sequence annotation (SeqAnn) python package for quickly retrieving sequence records as BioPython SeqRecord objects. Please refer to the documentation on the [IMGT/HLA GitHub](https://github.com/ANHIG/IMGTHLA) repository for any questions about the sequence data.

## Docker
This database can be run locally by building it from the Dockerfile or by pulling a prebuilt image from Docker Hub. Pulling from Docker Hub is the quickest option if you don't need to increase the number of release loaded into the database.

## Pulling from Docker Hub
```bash
docker pull nmdpbioinformatics/imgt_biosqldb
docker run -d --name imgt_biosqldb -p 3306:3306 \
    -e MYSQL_ROOT_PASSWORD=my-secret-pw nmdpbioinformatics/imgt_biosqldb
```
The *-d* flag runs the service in "detached-mode" in the background and *-p* specifies what ports to expose. Make sure the ports you expose are not already in use. If the docker container is successfuly executed then typing ``docker ps -a`` will show a new container labeled **imgt_biosqldb** running. In order for this to run you must set the `MYSQL_ROOT_PASSWORD` variable. [Click here](https://hub.docker.com/r/nmdpbioinformatics/imgt_biosqldb/) for more information on the publically available docker image. 


## Building locally
```bash
git clone https://github.com/nmdp-bioinformatics/imgt_biosqldb
cd nmdp-bioinformatics/imgt_biosqldb
docker build -t imgt_biosqldb:latest --build-arg RELEASES="3310,3320" .
docker run -d --name imgt_biosqldb -p 3306:3306 \
    -e MYSQL_ROOT_PASSWORD=my-secret-pw imgt_biosqldb:latest
```
This will build the docker image locally but changes the number of IMGT/HLA `RELEASES` loaded from three to five. This has only been tested for the last five IMGT/HLA releases. Some of the formats start to change a little when you go father back with the IMGT/HLA releases. Therefore, errors may occur when trying to build with more than five releases.

## Accessing the database
```
# pip install pymysql biopython
>>> import pymysql
>>> from BioSQL import BioSeqDatabase
>>> server = BioSeqDatabase.open_database(driver="pymysql", user="root",
...                                       passwd="my-secret-pw", host="localhost",
...                                       db="bioseqdb")
>>> db = server['3310_A']
>>> seqrecord = db.lookup(name="HLA-A*01:01:01:01")
>>> seqrecord
DBSeqRecord(seq=DBSeq('CAGGAGCAGAGGGGTCAGGGCGAAGTCCCAGGGCCCCAGGCGTGGCTCTCAGGG...AAA', DNAAlphabet()), id='HLA00001.1', name='HLA-A*01:01:01:01', description='HLA-A*01:01:01:01, Human MHC Class I sequence', dbxrefs=['EMBL:AJ278305', 'EMBL:AL645935', 'EMBL:CR759913', 'EMBL:EU445470', 'EMBL:GU812295', 'EMBL:HG794373', 'EMBL:M24043', 'EMBL:X55710', 'EMBL:Z93949'])
```
When you have the `imgt_biosqldb` docker container running locally you can access it with any programming language that has a mysql connector. This is an example of accessing the database with python using the BioSeqDatabase class from the biopython package. Please refer to the [sequence annotation](https://github.com/nmdp-bioinformatics/SeqAnn) repository for more examples of how to use this database.

### Related Links

 * [The Immuno Polymorphism Database (IPD)](https://www.ebi.ac.uk/ipd/)
 * [Sequence Annotation](https://github.com/nmdp-bioinformatics/SeqAnn)
 * [Feature Service](https://github.com/nmdp-bioinformatics/service-feature)
 * [GFE DB](https://github.com/nmdp-bioinformatics/gfe-db)


### IMGT Reference
James Robinson, Jason A. Halliwell, Hamish McWilliam, Rodrigo Lopez, Steven G. E. Marsh; **IPD—the Immuno Polymorphism Database**, *Nucleic Acids Research*, Volume 41, Issue D1, 1 January 2013, Pages D1234–D1240, https://doi.org/10.1093/nar/gks1140
