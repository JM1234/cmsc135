import subprocess
import shlex
import re
import json 

class DNS:

	def run_dig(self, hostname_filename, output_filename, dns_query_server="None"):
	
		self.host = []
		self.result = []
				
		f = open('alexa_top_100', 'r')		
		hostnames = file.read(f)
		
		#hostnames = ["twitter.com", "google.com"]
		for hostname in hostnames.split():
			print hostname
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

	def get_average_times(self, filename):
	
		with open(filename, 'r') as f:			
			raw_data = json.load(f)

		server_ttl = {}
		total_ave_ttl = 0
		host_count = 0
		answer_count = 0
		answer_ave = 0

		self.average_root_servers(raw_data)
		
	def average_root_servers(self, list):
		
		server_ttls = []
		server_tld = []
		

		q = [result["Queries"][0] for result in list if result["Success"]]
		
		for a in q:
			ttl=0
		
			s_ttl = [li["TTL"] for li in a["Answers"]]
		
			for t in s_ttl:
				ttl = ttl+ int(t)

			server_ttls.append(ttl / len(s_ttl))
		
	def generate_time_cdfs(json_filename, output_filename):
		pass

	def count_different_dns_responses(filename1, filename2):
		pass

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)


a = DNS()

a.run_dig("alexa_top_100", "dig.json")
#a.get_average_times("dig.json")
