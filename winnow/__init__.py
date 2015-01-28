#!/usr/bin/env python

from os import walk, access, F_OK, R_OK, X_OK, sep, mkdir, getcwd
from os.path import exists, isdir
from shutil import copy
from hashlib import md5
from socket import socket, SOCK_STREAM, AF_INET
from sys import exit, argv

__all__ = ["winnow"]

def make_winnowset(dirname):
    def compute_hash(filename, blocksize=1048576):
        engine = md5()
        with open(filename, "rb") as fh:
            buffer = fh.read(blocksize)
            while len(buffer) > 0:
                engine.update(buffer)
                buffer = fh.read(blocksize)
        return engine.hexdigest()
    
    def make_hashdict(directory):
        hashdict = {}
        for (dirpath, dirnames, filenames) in walk(directory):
            fullpaths = [dirpath + sep + X for X in filenames]
            for (fullpath, hashvalue) in [(X, compute_hash(X)) 
            for X in fullpaths if access(X, F_OK|R_OK)]:
                if hashvalue in hashdict:
                    hashdict[hashvalue].append(fullpath)
                else:
                    hashdict[hashvalue] = [fullpath]
        return hashdict
    
    movedict = { "Known" : {}, "Unknown" : {} }
    hashdict = make_hashdict(dirname)    
    hashes = list(hashdict.keys())

    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(("nsrllookup.com", 9120))
        sock.sendall("Version: 2.0\n".encode("ASCII"))
        response = sock.recv(1024).decode("ASCII").strip()
        if (response != "OK"):
            return None    
    
        while len(hashes) > 0:
            block = hashes[0:4000]
            hashes = hashes[4000:]
            query = "QUERY " + " ".join(block) + "\n"
            sock.sendall(query.encode("ASCII"))
            response = sock.recv(32768).decode("ASCII").strip().split()
            if response[0] != "OK":
                return None
                
            for index in range(len(response[1])):
                filenames = hashdict[block[index]]
                whichdict = None
                if response[1][index] == '0':
                    whichdict = movedict["Unknown"]
                else:
                    whichdict = movedict["Known"]
                if block[index] not in whichdict:
                    whichdict[block[index]] = []
                whichdict[block[index]] += filenames
        sock.sendall("BYE\n".encode("ASCII"))
    except:
        return None
    finally:
        sock.close()
    return movedict

def winnow(directory_name):
    """Walks through directory_name, determining MD5 checksums for each
    file therein.  On completion it uses the nsrllookup.com NSRL RDS
    lookup service to check for their presence in the NSRL RDS, and 
    creates two subdirectories of 'Known' and 'Unknown' off the current
    directory containing exemplars of all the known and unknown data
    found in the directory walk.
    
    :param directory_name:The directory to walk through
    :type directory_name:string
    :returns: bool -- it either succeeded or failed
    :raises: Nothing.  This function cannot raise errors.
    
    """
    try:
        mkdir(directory_name + sep + "Known")
        mkdir(directory_name + sep + "Unknown")
        winnowset = make_winnowset(directory_name)

        known = winnowset["Known"]
        unknown = winnowset["Unknown"]
    
        for hashvalue in known:
            exemplar = known[hashvalue][0]
            copy(exemplar, directory_name + sep + "Known" + sep + hashvalue)
        for hashvalue in unknown:
            exemplar = unknown[hashvalue][0]
            copy(exemplar, directory_name + sep + "Unknown" + sep + hashvalue)
        return True
    except Exception as e:
        print(e)
        return False
            
def launcher():
    if len(argv) < 2 or (not isdir(argv[1])) or\
        (not access(argv[1], F_OK|R_OK|X_OK)):
        print("Usage: " + argv[0] + " <dirname>")
        exit(-1)
    winnow(argv[1])
