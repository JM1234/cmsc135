import subprocess
import socket
import time
import re
import json
import os

class TraceRT:
	

	def run_traceroute(self, hostnames, num_packets, output_filename):		
		
		timestamp = int(time.time())
		time_ = "timestamp: "  +str(timestamp)
		self.append_file(output_filename, time_)

		for hostname in hostnames:

			traceroute = subprocess.Popen(["traceroute", '-A', '-q', num_packets, hostname], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

			for line in iter(traceroute.stdout.readline, ""):		
				self.append_file(output_filename, line)
			
	def parse_traceroute(self, raw_traceroute_filename, output_filename):
		self.hop = []
		self.host = {}

		for l in open(raw_traceroute_filename, 'r'):
			line = json.loads(l)	
			
			if line.startswith('timestamp: '):
				self.host['timestamp'] = line.split()[1]
			
			elif line.startswith('traceroute'):
				hostname = re.search('traceroute to (.+?) \([1-9]', line).group(1)
				self.host[hostname]=[]
				self.hop = []
				
			elif not line.startswith('traceroute'):				
				#print line
				m= line.split()
				asn = 'None'
				name = m[1]
				ip = m[2].strip('()')
				if (m[3] != "[*]"):			
					asn = m[3].strip('[]')	
				self.addHop(hostname, name, ip, asn)
		
			#print self.hop
			result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self.hop)]
			#self.host[hostname].append(result)		
		print self.host
		self.append_file(output_filename, self.host)

	def addHop(self, host, name, ip, asn):
		self.hop.append( { \
			'name' : name, \
			'ip' : ip, \
			'ASN' : asn \
			} )
		self.host[host].append(self.hop[len(self.hop)-1])

	def append_file(self, filename, data):
		with open(filename, 'a') as f:
			json.dump(data, f)
			f.write(os.linesep)

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)	

a= TraceRT()

#a.run_traceroute(['tpr-route-server.saix.net', 'route-server.ip-plus.net', 'route-views.oregon-ix.net', 'route-views.on.bb.telus.com.'], "5", "tr_servers.json")
a.run_traceroute(['zanvarsity.ac.tz'], "5", "tr_zanvarsity.json")
a.parse_traceroute("tr_zanvarsity.json", "tr_a.json")