import subprocess
import shlex
import re
import json 

class DNS:

	def run_dig(self, hostname_filename, output_filename, dns_query_server="None"):
	
		self.host = []
		self.result = []
		
		#with open(raw_ping_output_filename, 'r') as f:			
		#	hostnames = json.load(f)

		hostnames= ["google.com"]
		for hostname in hostnames:

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
		#print raw_data[0]["Name"]
		#print raw_data[0]["Success"]
		#print raw_data[0]["Queries"][0]["Answers"][0]["Queried name"] #loop queries, loop answers

	def average_root_servers(self, list):
		server_ttl ={}

		for h in range(0, len(list)):
			if list[h]["Success"] is True:
				server_ttl[list[h]["Name"]] = {}
				print list[h]["Name"]		
				for q in range(0, len(list[h]["Queries"])):
					for a in range(0, len(list[h]["Queries"][q]["Answers"])):
						print (list[h]["Queries"][q]["Answers"][a]["Queried name"])
						#condition: if list[h]["Queries"][q]["Answer"][a]["Queried name"] is not ".", compute average

	def generate_time_cdfs(json_filename, output_filename):
		pass

	def count_different_dns_responses(filename1, filename2):
		pass

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)


a = DNS()

#a.run_dig("alexa_top_100.txt", "dig.json")
a.get_average_times("dig.json")
