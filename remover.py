# -*- coding: utf-8 -*-

import sys, os, time, shutil
from remotecall import xmlrpc

queue = sys.argv[1]
queue_position = sys.argv[2]
torrent_hash = sys.argv[3]
torrent_path = sys.argv[4]

def remover():
        t_hash = tuple([torrent_hash])
        xmlrpc('d.tracker_announce', t_hash)
        xmlrpc('d.open', t_hash)
        files = xmlrpc('f.multicall', (torrent_hash, '', 'f.frozen_path='))
        xmlrpc('d.erase', t_hash)

        if len(files) <= 1:
                os.remove(files[0][0])
        else:
                [os.remove(file[0]) for file in files]

                try:
                        os.rmdir(torrent_path)
                except:

                        for root, directories, files in os.walk(torrent_path, topdown=False):

                                try:
                                        os.rmdir(root)
                                except:
                                        pass

with open(queue, 'a+') as txt:
        txt.write(queue_position + '\n')

time.sleep(0.01)

with open(queue, 'r') as txt:
        queued = txt.read()

if queue_position not in queued:

        with open(queue, 'a+') as txt:
                txt.write(queue_position + '\n')
                
if queued[0] != queue_position:

        while True:

                try:
                        with open(queue, 'r') as txt:
                                queued = txt.read()

                        if queued[0] == queue_position:
                                break
                except:
                        pass

                time.sleep(0.01)

remover()
time.sleep(0.10)

with open(queue, 'r') as txt:
        queued = txt.read()

with open(queue, 'w') as txt:

        for number in queued.strip().split('\n'):

                if number != queue_position:
                        txt.write(number + '\n')

time.sleep(180)

try:
        os.remove(queue)
except:
        pass
