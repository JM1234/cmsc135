import subprocess
import socket

class TraceRT:
	def run_traceroute(self, hostnames, num_packets, output_filename):
	
		for hostname in hostnames:			
			traceroute = subprocess.Popen(["traceroute", '-A', '-q', num_packets, hostname], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	
		#socket.gethostbyaddr("IP")	#reverse dns lookup
		for line in iter(traceroute.stdout.readline, ""):
			print(line)

	def parse_traceroute(raw_traceroute_filename, output_filename) :
		pass


a= TraceRT()
a.run_traceroute(['google.com'], "5", "traceroute.json")
