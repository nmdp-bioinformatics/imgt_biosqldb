import re
import os
import sys
import logging
import argparse
import pandas as pd
import urllib.request
from Bio import SeqIO
from BioSQL import BioSeqDatabase

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)

def download_dat(db):
    file = '/Users/mmaiers/src/GFE/IMGT/patched/' + db + '/hla.dat'
    return file


def download_allelelist(db):
    url = 'https://raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/Allelelist.' + db + '.txt'
    alist = ".".join([db, "Allelelist", "txt"])
    urllib.request.urlretrieve(url, alist)
    return alist


def main():
    """This is run if file is directly executed, but not if imported as
    module. Having this in a separate function  allows importing the file
    into interactive python, and still able to execute the
    function for testing"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Option for running in verbose",
                        action='store_true')

    parser.add_argument("-n", "--number",
                        required=False,
                        help="Number of IMGT/DB releases",
                        default=1,
                        type=int)

    parser.add_argument("-r", "--releases",
                        required=False,
                        help="IMGT/DB releases",
                        type=str)

    args = parser.parse_args()
    releases = args.releases
    number = args.number

    if args.verbose:
        verbose = True
    else:
        verbose = False

    if releases:
        dblist = [db for db in releases.split(",")]
    else:
        try:
            versions_url = "https://www.ebi.ac.uk/ipd/imgt/hla/docs/release.html"
            df = pd.read_html(versions_url)[0]
            x = df.columns
            dblist = [l.replace(".", '')
                      for l in df[x[0]].tolist()[0:number]]
        except ValueError as err:
            db_error = "Failed to load DB list: {0}".format(err)
            logging.info(db_error)
            logging.info("Defaulting to Latest")
            dblist = ["Latest"]

    # Connecting to mysql DB
    server = BioSeqDatabase.open_database(driver="sqlite3", db="bioseqdb")

    if verbose:
        dbversions_str = ",".join(dblist)
        logging.info("IMGT/HLA DB Versions = " + dbversions_str)

    # Looping through DB verions
    for dbv in dblist:

        # Downloading hla.dat file
        hladat = download_dat(dbv)

        if verbose:
            logging.info("Finished downloading hla.dat file for " + str(dbv))

        # Loading sequence data from hla.dat file
        try:
            seq_list = list(SeqIO.parse(hladat, "imgt"))
        except:
            #read_error = "Read dat error: {0}".format(err)
            logging.error("ERROR LOADING!!")
            server.close()
            os.remove(hladat)
            os.remove(allele_list)
            sys.exit()

        for seq in seq_list:
            print(",".join([seq.name, seq.id, dbv]))

        if verbose:
            logging.info("Loaded IMGT dat file " + descr)

        if verbose:
            logging.info("Finished loading " + descr)

    server.close()

if __name__ == '__main__':
    """The following will be run if file is executed directly,
    but not if imported as a module"""
    main()


