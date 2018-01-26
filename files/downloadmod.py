#!/usr/bin/python

##
## downloadmod.py
## 
## Copyright (C) 2007 Philipp Keller
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys, re, os, datetime, time

temp_allmods_filename = '/var/tmp/allmods.txt'
temp_allmods_processed_filename = '/var/tmp/allmods.txt.processed'

# the mirror servers are much faster so exclude ftp.modland.com, modland.ziphoid.com somehow has a different ftp format
exclude_servers = ['ftp://ftp.modland.com', 'ftp://modland.ziphoid.com']

class BandwidthFile:
    """
    limits the file download to a certain amount of bytes per second and prints download stats
    """
    def __init__(self, filename, filesize, bytes_per_second = 20000, mode = "wb"):
        self.fp = open(filename, "wb")
        self.bytecounter = 0
        self.started = datetime.datetime.now()
        self.bytes_per_second = bytes_per_second
        self.filesize = filesize
        self.filename = filename

    def __del__(self):
        self.fp.close()
   
    def write(self, bytestring):
        self.bytecounter += len(bytestring)
        seconds_since_started = (datetime.datetime.now() - self.started).seconds + 1
        while (self.bytecounter / seconds_since_started) > self.bytes_per_second:
            seconds_since_started = (datetime.datetime.now() - self.started).seconds + 1
            time.sleep(0.1)
        self.fp.write(bytestring)
        if self.filesize == None:
            filesize_string = "(unknown size)"
        else:
            filesize_string = str(int(self.filesize) / 1024) + " KB"
        sys.stdout.write("\rdownloading %s (%i/%s, %i KB/s)" % (self.filename, (self.bytecounter / 1024), filesize_string, (self.bytecounter / seconds_since_started / 1024)))
        sys.stdout.flush()

def getServerNamePath():
    """
    return (server_name, path)
    """
    if not hasattr(getServerNamePath, "cache"):
        from ftplib import FTP
        import random
        try:
            ftp = FTP("ftp.modland.com")
            ftp.login()
            tempfile = os.tmpfile()
            mirrors = []
        
            def analyzeMirrors(line):
                line = line.strip()
                if re.match(".*ftp[, ].*", line):
                    server_name = re.findall("[^ ]+$", line)[0]
                    if server_name not in exclude_servers:
                        mirrors.append(server_name)
            
            ftp.retrlines("RETR /mirrors.txt", analyzeMirrors)
            server_name = random.sample(mirrors, 1)[0]
            print "taking mirror " + server_name
            tmp = tuple(server_name.split("//")[1].split("/", 1))
            if len(tmp) == 1:
                tmp = (tmp[0], "")
        except:
            tmp = ("ftp.modland.com", "")
        getServerNamePath.cache = tmp
    return getServerNamePath.cache

def recursive_download(ftp_directory, local_directory):
    from ftplib import FTP
    (server_name, server_path) = getServerNamePath()
    ftp = FTP(server_name)
    ftp.login()
    
    directories = [ftp_directory]
    files = []

    print
    
    sys.stdout.write("fetching directory listing %s" % ftp_directory)
    sys.stdout.flush()
    while len(directories) > 0:
        path = directories.pop(0)
        listing = []
        ftp.retrlines("LIST %s" % server_path + "/" + path, listing.append)
        for line in listing:
            parsed = line.split(None, 8)
            if parsed[0].startswith('d'):
                if not parsed[-1].startswith("."):
                    directories.append(path + "/" + parsed[-1])
            elif not parsed[0].startswith("total"):
                files.append(path + "/" + parsed[-1])
    sys.stdout.write(" (%i files)\n" % len(files))
    sys.stdout.flush()
    for filename in files:
        filename_path = filename[len(ftp_directory) + 1:]
        local_path = "/".join((local_directory + filename[len(ftp_directory) + 1:]).split("/")[:-1])
        local_filename = local_path + "/" + filename.split("/")[-1]        
        if (not os.path.exists(local_path)):
            os.makedirs(local_path)

            # write meta-file so mod2mp3 can write the according id3 tags
            album_name = local_path.split("/")[-1]
            if album_name == artist_name:
                album_name = ""
            fp = open(local_path + "/.ftp.modland.com_meta", "w")
            fp.write("artist: " + artist_name + "\n")
            fp.write("album: " + album_name + "\n")
            fp.close()

        try:
            ftp_filesize = ftp.size(server_path + "/" + filename)
        except:
            ftp_filesize = None
            
        # if the file already exists and is downloaded completely: don't download again
        if os.path.exists(local_filename) and os.stat(local_filename)[6] == ftp_filesize:
            print local_filename, "is already downloaded"
            continue
        
        f = BandwidthFile(local_filename, ftp_filesize)
        ftp.retrbinary('RETR '+server_path + "/" + filename, f.write)
        print
    ftp.quit()


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] == '--help' or sys.argv[1] == '-h':
        scriptname = os.path.basename(sys.argv[0])
        print "%s downloads all modules from ftp.modland.com (and its mirrors) from a certain artist" % scriptname
        print
        print """example: %s /base/path/to/modules "purple motion" """ % scriptname
        print "in this example, the directory /base/path/to/modules/purple motion/ will be created and all his modules will be stored there"
        sys.exit()
    
    artist_name = sys.argv[2]
    download_mod_path = "/" + sys.argv[1].strip("/") + "/"
    
    # download the newest allmods.txt if the file doesn't exist or is older than a month
    if not os.path.exists(temp_allmods_filename) or (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getctime(temp_allmods_filename))).days > 31:
        try:
            from ftplib import FTP
        
            # check if allmods.txt is up to date, sonst:
            (server_name, server_path) = getServerNamePath()
            ftp = FTP(server_name)
            ftp.login()
            files = ftp.nlst(server_path)
            print(files)
            allmods_file_zip = 'allmods.zip'
      
            print "downloading " + allmods_file_zip + "..."
            ftp.retrbinary('RETR ' + allmods_file_zip, open("/var/tmp/allmods.zip.tmp", 'wb').write)
            ftp.quit()
            os.system("unzip /var/tmp/allmods.zip.tmp -d /var/tmp")
            os.system("rm /var/tmp/allmods.zip.tmp")
        except Exception, e:
            import traceback
            traceback.print_exc()
            print "in the process of downloading the module list from %s the following error occurred:" % getServerNamePath()[0], e
            print "in order to use this downloader please install 'unrar' or donwload allmods_yyyy-mm-dd.rar from %s, unpack it and copy the extracted file to" % getServerNamePath()[0], temp_allmods_filename
            sys.exit()
    
    # process allmods.txt for faster search results
    if not os.path.exists(temp_allmods_processed_filename) or (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getctime(temp_allmods_processed_filename))).days > 7:
        paths = set()
        print "process %s into %s" % (temp_allmods_filename, temp_allmods_processed_filename)
        for line in open(temp_allmods_filename):
            line = line.strip("\n")
            if line.startswith("Modland statistics"):
                break
            [dummy, filename] = line.split("\t")
            processed_path = "/".join(filename.split("/")[:-1])
            paths.add(processed_path)
        
        processed = open(temp_allmods_processed_filename, "w")
        for path in paths:
            processed.write(path + "\n")
        processed.close()
    
    artist_name_lower = artist_name.lower()
    for line in open(temp_allmods_processed_filename):
        line = line.strip("\n")
        # if "/" + artist_name_lower + "/" in line.lower():
        if line.lower().endswith(artist_name_lower):
            recursive_download("/pub/modules/" + line, download_mod_path + artist_name + "/")
