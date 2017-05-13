import subprocess
import socket
import time
import re
import json
import os

class TraceRT:
	
	def run_traceroute(self, hostnames, num_packets, output_filename):
		
		timestamp = int(time.time())
		self.host = {}
		self.hop = []

		self.host['timestamp'] = timestamp
		for hostname in hostnames:	
			self.host[hostname] = []
			traceroute = subprocess.Popen(["traceroute", '-A', '-q', num_packets, hostname], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
			for line in iter(traceroute.stdout.readline, ""):
					
				if not line.startswith('traceroute'):
									
					print line
					m= line.split()
					asn = 'None'
					ip = m[1]
					name = m[2].strip('()')
					if (m[3] != "[*]"):			
						asn = m[3].strip('[]')	

					self.addHop(hostname, name, ip, asn)

			result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self.hop)]
			self.host[hostname].append(result)		
		self.append_file(output_filename, self.host)

	def addHop(self, host, name, ip, asn):
		
		self.hop.append( { \
			'name' : name, \
			'ip' : ip, \
			'ASN' : asn \
			} )

	def append_file(self, filename, data):
		with open(filename, 'a') as f:
			json.dump(data, f)
			f.write(os.linesep)

	#def write_json(self, file_name, data):
		#with open(file_name, 'w') as f:
		#	json.dump(data, f)	
			
	def parse_traceroute(raw_traceroute_filename, output_filename) :
		pass


"""
	def gethostname(self, ip):
		if socket.gethostname().find('.')>=0:
			return socket.gethostname()
		else:
			return socket.gethostbyaddr(socket.gethostname())[0]
"""

a= TraceRT()
a.run_traceroute(['twitter.com'], "5", "tr_a.json")
