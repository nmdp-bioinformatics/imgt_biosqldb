# -*- coding: utf-8 -*-
#
#    create_imgtdb.py
#    Copyright (c) 2017 Be The Match operated by National Marrow Donor Program. All Rights Reserved.
#
#    This library is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or (at
#    your option) any later version.
#
#    This library is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; with out even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#    License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library;  if not, write to the Free Software Foundation,
#    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#    > http://www.fsf.org/licensing/licenses/lgpl.html
#    > http://www.opensource.org/licenses/lgpl-license.php
#

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
    url = 'https://raw.githubusercontent.com/ANHIG/IMGTHLA/' + db + '/hla.dat'
    dat = ".".join([db, "hla", "dat"])
    urllib.request.urlretrieve(url, dat)
    return dat


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

    parser.add_argument("-r", "--releases",
                        help="Number of releases",
                        default=4,
                        type=int)

    args = parser.parse_args()
    releases = args.releases

    if args.verbose:
        verbose = True
    else:
        verbose = False

    try:
        versions_url = "https://www.ebi.ac.uk/ipd/imgt/hla/docs/release.html"
        df = pd.read_html(versions_url)[0]
        x = df.columns
        dblist = [l.replace(".", '')
                  for l in df[x[0]].tolist()[0:releases]]
    except ValueError as err:
        db_error = "Failed to load DB list: {0}".format(err)
        logging.info(db_error)
        logging.info("Defaulting to Latest")
        dblist = ["Latest"]

    # Connecting to mysql DB
    server = BioSeqDatabase.open_database(driver="pymysql", user="root",
                                          passwd="my-secret-pw", host="localhost",
                                          db="bioseqdb")

    if verbose:
        dbversions_str = ",".join(dblist)
        logging.info("IMGT/HLA DB Versions = " + dbversions_str)

    # Looping through DB verions
    for dbv in dblist:

        # Downloading hla.dat file
        hladat = download_dat(dbv)

        if verbose:
            logging.info("Finished downloading hla.dat file for " + str(dbv))

        # Downloading allele list
        allele_list = download_allelelist(dbv)

        if verbose:
            logging.info("Finished downloading allele list for " + str(dbv))

        hla_names = {}
        try:
            # File formats change...
            s = "," if dbv == "3260" or dbv == "3270" else " "
            with open(allele_list, 'r') as f:
                for line in f:
                    line = line.rstrip()
                    accession, name = line.split(s)
                    hla_names.update({accession: name})
            f.close()
            if verbose:
                nalleles = len(hla_names.keys())
                logging.info("Finished loading " + str(nalleles)
                             + " alleles for " + str(dbv))
        except ValueError as err:
            list_error = "Allelelist error: {0}".format(err)
            logging.error(list_error)
            server.close()
            os.remove(hladat)
            os.remove(allele_list)
            sys.exit()

        # Loading sequence data from hla.dat file
        try:
            seq_list = SeqIO.parse(hladat, "imgt")
        except ValueError as err:
            read_error = "Read dat error: {0}".format(err)
            logging.error(read_error)
            server.close()
            os.remove(hladat)
            os.remove(allele_list)
            sys.exit()

        new_seqs = {"A": [], "B": [], "C": [], "DRB1": [],
                    "DQB1": [], "DRB3": [], "DRB4": [], "DRB5": [],
                    "DQA1": [], "DPA1": [], "DPB1": []}

        # Changing the sequence name to
        # the HLA allele name instead of the accession
        for seq in seq_list:
            if seq.name in hla_names:
                loc, allele = hla_names[seq.name].split("*")
                if loc in new_seqs:
                    hla_name = "HLA-" + hla_names[seq.name]
                    seq.name = hla_name
                    new_seqs[loc].append(seq)

        dbsp = list(dbv)
        descr = ".".join([dbsp[0], dbsp[1]+dbsp[2], dbsp[3]])

        if verbose:
            logging.info("Loaded IMGT dat file " + descr)

        # Looping through and loading each locus
        for locus in new_seqs:
            dbname = dbv + "_" + locus
            dbdescription = "IMGT/HLA " + descr + " " + locus
            db = server.new_database(dbname, description=dbdescription)
            try:
                count = db.load(new_seqs[locus])
            except:
                load_fail = sys.exc_info()[0]
                logging.error("Faild to load " + load_fail)
                server.close()
                os.remove(hladat)
                os.remove(allele_list)
                sys.exit()

            if verbose:
                logging.info("Loaded " + str(count) + " for " + dbname)

            # Commiting data to mysql db
            server.commit()

        # Removing hla.dat and allele list files
        os.remove(hladat)
        os.remove(allele_list)

        if verbose:
            logging.info("Finished loading " + descr)

    server.close()

if __name__ == '__main__':
    """The following will be run if file is executed directly,
    but not if imported as a module"""
    main()


