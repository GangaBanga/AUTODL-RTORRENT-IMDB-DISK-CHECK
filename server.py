import os
import sys
import signal
import socket
import logging
import subprocess

logging.basicConfig(filename="checker_server.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

try:
	import config as cfg
except Exception as e:
	print("Error: Couldn't import config file:", e)
	logging.critical("server.py: Config Error: Couldn't import config file: " + str(e))
	sys.exit(1)

from threading import Thread
from queuer import CheckerQueue
from cacher import Cache

serverPath = os.path.join(os.path.abspath(os.getcwd()), sys.argv[0])
cmd = "pgrep -a python | grep " + sys.argv[0]
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pids = process.communicate()[0].splitlines()

if len(pids) > 1:
	[os.kill(int(pid.split()[0]), signal.SIGKILL) for pid in pids if serverPath in str(pid)]

if "/" not in sys.argv[0]:
	from remote_caller import SCGIRequest
	rtxmlrpc = SCGIRequest()
	print("Server is now running in the background.")
	rtxmlrpc.send("execute.throw.bg", ("", "python3", serverPath))
	sys.exit(0)

cache = Cache()
checkerQueue = CheckerQueue()
checkerQueue.createChecker(cache)

socketFile = cfg.socket_file
if os.path.exists(socketFile): os.remove(socketFile)

try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.bind(socketFile)
	s.listen(50)

	while True:
		clientsocket, address = s.accept()
		message = clientsocket.recv(2048).decode("utf-8").split("|:|")

		if "delete" in message:
			cache.deletedTorrents.append(message)
		else:
			checkerQueue.put(message)

except Exception as e:
	print(e)
	logging.critical("server.py: Server Error: Server closing: " + str(e))
