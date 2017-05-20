import subprocess
import shlex
import re
import json 
import matplotlib.pyplot as plot
from bisect import bisect_left
import os

class discrete_cdf:
		
	def __init__(self,data):
		self._data = data
		self._data_len = float(len(data))

	def __call__(self,point):
		return (len(self._data[:bisect_left(self._data, point)]) / 
		self._data_len)

class DNS:

	def run_dig(self, hostname_filename, output_filename, dns_query_server="None"):
	
		self.host = []
		self.result = []
				
		f = open(hostname_filename, 'r')		
		hostnames = file.read(f)
		#hostnames = ["google.com", "twitter.com"]

		for hostname in hostnames.split():
			print hostname
			if(dns_query_server == "None"):
				cmd = 'dig +trace +tries=1 +nofail ' + hostname
			else:
				cmd = 'dig ' + hostname +  " dns_query_server"

			proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
			out,err = proc.communicate()
		
			self.add_host(hostname, "connection timed out" not in out , out)

		self.append_json(output_filename, self.result)

	def get_average_ttls(self, filename):
	
		with open(filename, 'r') as f:			
			raw_data = json.load(f)

		server_ttl = self.compute_average(raw_data, 0)
		tld_ttl = self.compute_average(raw_data, 1)
		other_ttl = self.compute_average(raw_data, 2)
		terminating_entry = self.compute_average(raw_data,3)

		return [server_ttl, tld_ttl, other_ttl, terminating_entry]

	def get_average_times(self, filename):
		with open(filename, 'r') as f:			
			raw_data = json.load(f)
		
		li = self.agg_hosts(raw_data)

		server_q = [result["Queries"][0]["Time in millis"] for result in li]
		tld_q = [result["Queries"][1]["Time in millis"] for result in  li]
		other_q = [result["Queries"][2]["Time in millis"] for result in li]
		final_q = [result["Queries"][3]["Time in millis"] for result in li]

		size = len(server_q) + len(tld_q) + len(other_q)
	
		total=0
		final=0
		for i in range(0, len(server_q)):
			total = total+ int(server_q[i]) + int(tld_q[i]) + int(other_q[i])
			final = final + int (final_q[i])
		time_resolved = total/size 
		ave_final = final/len(final_q)

		return [time_resolved, ave_final]

	def count_different_dns_responses(self, filename1, filename2):
		
		with open(filename1, 'r') as f:
			list1 = json.load(f)

		with open(filename2, 'r') as f:
			list2 = json.load(f)
		
		#how many times it changed within one query
		hosts = {}
		changed = []

		for v in list1:			
			hosts[v["Name"]] = []

			if v["Success"]:
				q = v["Queries"][3]["Answers"]
				hosts[v["Name"]].append(q[0]["Data"])
				
				for e in q:
					if e["Data"] not in hosts[v["Name"]]:
						if v["Name"] not in changed:
							changed.append(v["Name"]) 
						hosts[v["Name"]].append(e["Data"])
		count1 = len(changed)
		print "Value 1: " + str(count1)
		
		#how many times it changed within two files
		for v in list2:		
			if v["Success"]:
				q = v["Queries"][3]["Answers"]
			
				for e in q:
					if e["Data"] not in hosts[v["Name"]]:
						if v["Name"] not in changed:
							changed.append(v["Name"]) 
						hosts[v["Name"]].append(e["Data"])
		print "Value 2: " + str(len(changed))

	def generate_time_cdfs(self, json_filename, output_filename):
		X = [] #list
		colorstring = "krgy"
		category = ["Root", "TLD", "Other", "Terminating"] 
		t = []

		try:
			with open(json_filename, 'r' ) as f: 
				raw_data = json.load(f)
		except IOError:
			print "File not found."
		
		li = self.agg_hosts(raw_data)

		server_q = [result["Queries"][0]["Time in millis"] for result in li ]
		tld_q = [result["Queries"][1]["Time in millis"] for result in li]
		other_q = [result["Queries"][2]["Time in millis"] for result in li]
		final_q = [result["Queries"][3]["Time in millis"] for result in li]

		#total time to resolve a site
		t.extend(server_q)
		t.extend(tld_q)
		t.extend(other_q)
		t.extend(final_q)
		
		X = map(int, t)
		cdf =  discrete_cdf(sorted(X))
		n = max(X)
		xvalues = range(0, int(n))
		yvalues = [cdf(point) for point in xvalues]
		
		plot.plot(xvalues, yvalues, color = "blue", label = "Total Time to Resolve a Site")

		#terminating query	
		final = map(int, final_q)
		cdf =  discrete_cdf(sorted(final))
		n = max(final)
		xvalues = range(0, int(n))
		yvalues = [cdf(point) for point in xvalues]
		
		plot.plot(xvalues, yvalues, color = "orange", label = "Time to Resolve the Final Request")
				
		plot.legend()
		plot.grid()
		plot.xlabel("seconds")
		plot.ylabel("Cumulative Fraction")
		plot.show()

		self.save_graph(output_cdf_filename, f)

	def save_graph(self, output_cdf_filename, f):
		from matplotlib.backends import backend_pdf
		with backend_pdf.PdfPages(output_cdf_filename) as pdf:
			pdf.savefig(f)

	def append_json(self, filename, data):
		with open(filename, 'a') as f:
			json.dump(data, f)
			#f.write(os.linesep)

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)

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

	def compute_average (self, list, i):
		
		_ttls = []
		hosts = self.agg_hosts(list, i)

		for li in hosts:
			ttl=0
			s_ttl = [li["TTL"] for li in a["Answers"]]
			
			for i in s_ttl:
				ttl = ttl+ int(i)

			_ttls.append(ttl/len(s_ttl))
			
		ave=0
		for li in _ttls:
			ave = ave+li			
	
		return ave/len(_ttls)

	def agg_hosts(self, list, i=-1):
		hosts ={}

		for result in list:
			if result["Success"]:
				try:
					if i != -1:
						hosts[result["Name"]].append(result["Queries"][i])
					else:
						hosts[result["Name"]].append(result["Queries"])

				except KeyError:
					hosts[result["Name"]] =[]
					if  i!= -1:
						hosts[result["Name"]].append(result["Queries"][i])					
					else:
						hosts[result["Name"]].append(result["Queries"])

		return hosts

a = DNS()

a.run_dig("alexa_top_100", "dig_5.json")
#a.get_average_ttls("dig.json")
#a.get_average_times("dig.json")
#a.generate_time_cdfs("dig.json", "dns_plot.pdf")
#a.count_different_dns_responses("dig.json", "dig2.json")
