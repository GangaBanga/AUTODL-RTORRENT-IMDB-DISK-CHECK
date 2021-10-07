import socket
from xmlrpc import client as xmlrpclib
from urllib import parse as urllib
from config import scgi


class SCGIRequest:

	def send(self, methodName, params):
		xmlReq = xmlrpclib.dumps(params, methodName)
		scgiReq = self.addSCGIHeaders(xmlReq).encode("utf-8")

		try:
			host, port = scgi.split(":")
			addrInfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
			s = socket.socket(*addrInfo[0][:3])
			s.connect(addrInfo[0][4])
		except:
			s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			s.connect(scgi)

		s.send(scgiReq)
		sFile = s.makefile()
		data = resp = sFile.read(1024)

		while data:
			data = sFile.read(1024)
			resp += data

		s.close()
		scgiResp = urllib.unquote(resp)
		xmlResp = "".join(scgiResp.split("\n")[4:])
		return xmlrpclib.loads(xmlResp)[0][0]

	@staticmethod
	def encodeNetstring(string):
		return "%d:%s," % (len(string), string)

	@staticmethod
	def makeHeaders(headers):
		return "\x00".join(["%s\x00%s" % h for h in headers]) + "\x00"

	@staticmethod
	def addSCGIHeaders(data):
		headers = SCGIRequest.makeHeaders([("CONTENT_LENGTH", str(len(data))), ("SCGI", "1")])
		encHeaders = SCGIRequest.encodeNetstring(headers)
		return encHeaders + data
