import json
import os
import subprocess
import tarfile
import sys

from threading import Thread

# directory in which to unpack packages
# (should be a separate partition and properly sandboxed)
DIR_PREFIX = "tmp"

class ProcessHandler():
    last_line = ""

    def __init__(self, args):
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def communicate(self,input_list):
        for data in input_list:
            self.process.stdin.write(data)

    def readline(self): 
        def readline_threaded():
            self.last_line = self.process.stdout.readline()
        t = Thread(target=readline_threaded)
        t.start()
        t.join(0.5) 
        if t.isAlive():
            print "ERROR"
        return self.last_line


class GameMaster(object):

    """
    Creates a new GameMaster with two strings, one path
    to each .tar object. 

    The .tar should contain a manifest.json in the root
    directory.
    """
    def __init__(self, players):
        self.players = players
    
        for i, player in enumerate(self.players):
            player_tar = tarfile.open(player)
            player_tar.extractall(os.path.join(DIR_PREFIX, "/%d"%(i,)))

        config_paths = [os.path.join(DIR_PREFIX, "/%d/manifest.json"%(i)) for i in xrange(len(self.players))]

        files = []
        # open the config files
        for p in config_paths:
            files.append(open(p))
        # JSON parse them
        configs = map(json.load, files)
        # and close them
        for f in files:
            f.close()

        # make the players talk!
        players_bin_args = [["python", os.path.abspath(os.path.join(DIR_PREFIX, "/%d/%s"%(i, configs[i]['executable'],)))]
                            for i in xrange(len(self.players))]
        
        self.processes = [ProcessHandler(pba) for pba in players_bin_args]

class GuessTheNumberMaster(GameMaster):
    def __init__(self, players):
        GameMaster.__init__(self, players)
    
    def playMatch(self):
        # p1 thinks about a number
        self.processes[0].communicate("think\n")
        number = int(self.processes[0].readline())
        
        # p2 tries to guess the number
        self.processes[1].communicate("guess\n")
        guessed = int(self.processes[1].readline())

        print "thought about " + str(number) + ", guessed " + str(guessed)
