import subprocess
import socket
import time
import re

class TraceRT:
	
	def run_traceroute(self, hostnames, num_packets, output_filename):
		
		timestamp = int(time.time())
		self.host = {}

		for hostname in hostnames:	
			traceroute = subprocess.Popen(["traceroute", '-I', '-A', '-q', num_packets, hostname], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		hop={}
		for line in iter(traceroute.stdout.readline, ""):
					
			if not line.startswith('traceroute'):
				print line
				m= line.split()
				print m[1]
				name= self.gethostname(m[1])
				print name				

	def gethostname(self, ip):
		if socket.gethostname().find('.')>=0:
			return socket.gethostname()
		else:
			return socket.gethostbyaddr(socket.gethostname())[0]

	def parse_traceroute(raw_traceroute_filename, output_filename) :
		pass

a= TraceRT()
a.run_traceroute(['upd.edu.ph'], "5", "traceroute.json")
