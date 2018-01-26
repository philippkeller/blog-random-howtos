#!/usr/bin/python

##
## mod2mp3.py
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


import os, re, sys, select

module_players = []

module_players.append(dict(name="xmp",
                           command="xmp --quiet -d file -o output.wav",
                           outputfile="output.wav",
                           outputtype="wave",
                           formats=["XM", "MOD", "MOD", "M15", "IT", "S3M", "STM", "STX", "MTM", "MTN", "IMF", "PTM", "MDL", "ULT", "MMD", "PTM", "EMOD", "OKT", "SFX", "FAR", "STIM", "FC-M", "KSM", "WN", "PM", "KRIS", "UNIC", "P60A", "PRU1", "PRU2", "PM01", "PM10", "PM18", "PM20", "PM40", "AC1D", "PP10", "XANN", "ZEN", "NP", "DI", "MP", "FNK", "AMD", "RADCRB", "ALM", "FT"],
                           title_command="""xmp --load-only %s 2>&1 | grep "Module title" | cut -d : -f 2 | sed 's/^[[:space:]]*//g' | sed 's/[[:space:]]*$//g';""",
                           timeout=600,
                           ))
module_players.append(dict(name="adplay",
                           command="adplay -o -O disk -d music.wav",
                           outputfile="music.wav",
                           outputtype="wave",
                           formats=["A2M", "AMD", "BAM", "CFF", "CMF", "D00", "DFM", "DMO", "DRO", "DTM", "HSC", "HSP", "IMF", "KSM", "LAA", "LDS", "M", "MAD", "MID", "MKJ", "MSC", "MTK", "RAD", "RAW", "RIX", "ROL", "S3M", "SA2", "SAT", "SCI", "SNG", "XAD", "XMS", "XSM"],
                           title_command=None,
                           timeout=120,
                        ))


def getCommandOutput(command):
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data

def timeout_command(command, timeout):
    import subprocess, datetime, os, time, signal
    """call shell-command and either return its output or kill it if it doesn't normally exit within timout seconds and return None"""
    print(command)
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            while 1:
                os.waitpid(-1, os.WNOHANG)
    return process.stdout.read()

if len(sys.argv) == 1 or sys.argv[1] == '--help' or sys.argv[1] == '-h':
    scriptname = os.path.basename(sys.argv[0])
    print "%s converts a bunch of modules into mp3s" % scriptname
    print
    print "usage:"
    print "ls *.* > modules.txt"
    print "%s modules.txt" % scriptname
    sys.exit()

# find out which module players are installed
available_module_players = []
for module_player in module_players:
    if os.system("which %s > /dev/null" % module_player['name']) == 0:
        available_module_players.append(module_player)

if len(module_player) == 0:
    print "error: no module players found. Please install one of the following players:"
    print " - \n".join([player['name'] for player in module_players])
    sys.exit()

if os.system("which lame > /dev/null") != 0:
    print "you need to install lame (lame.sourceforge.net) in order to convert the modules to mp3"
    sys.exit()

mod2mp3_ending = re.compile("\.[a-zA-Z0-9]*$")

def array_walk_convert_module(dummy, dirname, filenames):
    for filename in filenames:
        convert_module(dirname + "/" + filename)

def convert_module(module_filename):
    suffix = module_filename.split(".")[-1].upper()

    module_player = None

    newfilename, matched = mod2mp3_ending.subn(".mp3", module_filename)
    if os.path.exists(newfilename):
        return
    
    # find out which module player can convert the module to wave
    for available_module_player in available_module_players:
        if suffix in available_module_player['formats']:
            module_player = available_module_player
            break

    if module_player is None:
        print "error: no module player found to decode", module_filename
        return

    title = ".".join(module_filename.split(".")[0:-1]).split("/")[-1]
    if module_player['title_command'] is not None:
        title_tmp = getCommandOutput(module_player["title_command"] % re.escape(module_filename)).strip()
        if title_tmp.strip() != "":
            title = title_tmp
        
    sys.stdout.write("\r " * 75)
    sys.stdout.write("\rconverting %s: mod2wav (%s)" % (module_filename, module_player["name"]))
    sys.stdout.flush()

    try:
        # some module players (adplay) sometimes seems to hang: set a timeout
        command_as_list = re.split(r"(?<=[^\\]) ", module_player["command"])
        output = timeout_command(['nice'] + command_as_list + [module_filename], module_player['timeout'])
        if output is None:
            print "%s had a hanger (was processing for %i minutes). File %s couldn't be converted" % (module_player['name'], (module_player_timeout / 60), module_filename)
            return
    except KeyboardInterrupt:
        if os.path.exists(module_player["outputfile"]):
            os.system("rm %s" % module_player["outputfile"])
        sys.exit()

    artist_name = None
    album_name = None

    meta_filename = os.path.dirname(module_filename)
    if meta_filename != "":
        meta_filename += "/"
    meta_filename += ".ftp.modland.com_meta"
    if os.path.exists(meta_filename):
        for line in open(meta_filename):
            line = line.strip()
            [key, val] = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if key.lower() == "artist":
                artist_name = val
            elif key.lower() == "album":
                album_name = val
                
    lame_options = ""
    if module_player["outputtype"] == "raw":
        lame_options = "-r -x"
    id3_options = ""
    if artist_name is not None and artist_name.strip() != "":
        id3_options += " --ta %s" % re.escape(artist_name)
    if album_name is not None and album_name.strip() != "":
        id3_options += " --tl %s" % re.escape(album_name)

    sys.stdout.write("\r " * 75)
    sys.stdout.write("\rconverting %s: wav2mp3 (%s)" % (module_filename, "lame"))
    sys.stdout.flush()
        
    exit_status = os.system("nice lame -V7 --nohist %s --quiet --tt %s %s %s music.mp3 >/dev/null 2>/dev/null" % (lame_options, re.escape(title), id3_options, module_player["outputfile"]))
    if exit_status != 0:
        print "lame exited unexpectedly, exit"
        if os.path.exists(module_player["outputfile"]):
            os.system("rm %s" % module_player["outputfile"])
        if os.path.exists("music.mp3"):
            os.system("rm music.mp3")
        sys.exit()
    if matched > 0:
        os.system("mv music.mp3 %s" % re.escape(newfilename))
        os.system("rm %s" % module_player["outputfile"])
    else:
        print "error: filename %s is not valid. conversion failed" % line

    print


basedir = os.path.expanduser(sys.argv[1])
os.path.walk(basedir, array_walk_convert_module, None)
    
