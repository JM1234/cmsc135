import subprocess
import shlex
import re

class DNS:

	def run_dig(self, hostname_filename, output_filename, dns_query_server="None"):
	
		self.host = []
		self.result = []
		
		hostname = "www.google.com"

		if(dns_query_server == "None"):
			cmd = 'dig +trace +tries=1 +nofail ' + hostname
		else:
			cmd = 'dig ' + hostname +  " dns_query_server"

		proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
		out,err = proc.communicate()
		
		self.add_host(hostname, "connection timed out" not in out , out)
		self.write_json(output_filename, self.result)

	def add_host(self, host, result, output):
		self.result.append ({ 
			"Name" : host, \
			"Success" : result	
		})
		
		if (result):
			self.result[len(self.result)-1]["Queries"] = self.get_queries(output)
	
	def get_queries(self, output) :
		answers = []
		queries = []

		for line in output.splitlines():
			if not line.startswith(';'):
				
				parse = line.split()
				try:				
					queried_name = parse[0]
					data = parse[4]
					_type = parse[3]
					ttl = parse[1]
					self.add_answer(answers, parse[0], parse[4], parse[3], parse[1])
				except IndexError:
					pass
			elif line.startswith(';; Received'):	
				time = re.search('in (.+?) ms', line).group(1)
				self.add_query(queries, time, answers)
				answers= []
				
		return queries

	def add_query(self, list, time, answers):
		list.append( {
			"Time in millis" : time, \
			"Answers" : answers
			})

	def add_answer(self, list, name, data, _type, ttl):
		list.append({
			"Queried name" : name, \
			"Data" : data, \
			"Type" : _type, \
			"TTL" : ttl 
		})

	def get_average_ttls(filename):
		with open(filename, 'r') as f:			
			self.raw_data = json.load(f)
		
	def average_root_servers()

	def get_average_times(filename):
		pass

	def generate_time_cdfs(json_filename, output_filename):
		pass

	def count_different_dns_responses(filename1, filename2):
		pass

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)

a = DNS()

a.run_dig(['google.com'], "dig.json")
