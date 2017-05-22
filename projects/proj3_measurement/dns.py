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
	

		self.result = []
				
		f = open(hostname_filename, 'r')		
		hostnames = file.read(f)
		
		#hostnames = ["google.com", "twitter.com"]
		for hostname in hostnames.splitlines():
			print hostname
			if(dns_query_server == "None"):
				cmd = 'dig +trace +tries=1 +nofail ' + hostname
			else:
				cmd = 'dig ' + hostname +  ' @' +  dns_query_server

			proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
			out,err = proc.communicate()
		
			self.add_host(hostname, "connection timed out" not in out , out)
			self.append_json(output_filename, self.result[len(self.result)-1])

	def get_average_ttls(self, filename):
		raw_data = []
		
		for l in open(filename, 'r'):
			line = json.loads(l)	
			raw_data.append(line)
		
		server_ttl = self.compute_average(raw_data, 0)
		tld_ttl = self.compute_average(raw_data, 1)
		other_ttl = self.compute_average(raw_data, 2)
		terminating_entry = self.compute_average(raw_data,3)
		
		return [server_ttl, tld_ttl, other_ttl, terminating_entry]

	def get_average_times(self, filename):
		raw_data = []
		t_data = []		
		final_q = []

		for l in open(filename, 'r'):
			line = json.loads(l)	
			raw_data.append(line)

		li = self.agg_hosts(raw_data)		
	
		for k, v in li.iteritems():
			t_data.append([result[0]["Time in millis"] for result in v])			
			t_data.append([result[1]["Time in millis"] for result in  v])
			t_data.append([result[2]["Time in millis"] for result in v])
			final_q.append([result[3]["Time in millis"] for result in v])

		t_size = len(t_data)
		t_total = 0
		for i in t_data:
			temp_total = 0
			s = len(i)			
			for r in i:
				temp_total = temp_total + int(r)
			t_total = t_total + (temp_total/s)
		t_ave = t_total/t_size
		
		f_size = len(final_q)
		f_total = 0
		for i in final_q:
			temp_total = 0
			s = len(i)
			for r in i:
				temp_total = temp_total + int(r)
			f_total = f_total + (temp_total/s)
		f_ave = f_total/f_size
		
		return [t_ave, f_ave]

	def count_different_dns_responses(self, filename1, filename2):
		
		raw_data = []
		list1 = []
		list2 = []

		for l in open(filename1, 'r'):
			line = json.loads(l)	
			list1.append(line)

		for l in open(filename2, 'r'):
			line = json.loads(l)	
			list2.append(line)

		#how many times it changed within one query
		hosts = {}
		changed = []

		for v in list1:			
			hosts[v["Name"]] = []
			
			if v["Success"]:
				q = v["Queries"][3]["Answers"]
				hosts[v["Name"]].append(q[0]["Data"])
						
				for e in q: #for each data in query
					if e["Data"] not in hosts[v["Name"]]:
						if v["Name"] not in changed:
							changed.append(v["Name"]) 
						hosts[v["Name"]].append(e["Data"])
		val1 = len(changed)

		#how many times it changed within two files
		for v in list2:		
			if v["Success"]:

				try:
					q = v["Queries"][3]["Answers"]
				except IndexError:
					q= v["Queries"][0]["Answers"] #for server-specific answers
				for e in q:
					if e["Data"] not in hosts[v["Name"]]:
						if v["Name"] not in changed:
							changed.append(v["Name"]) 
						hosts[v["Name"]].append(e["Data"])
		
		return [val1, len(changed)]

	def generate_time_cdfs(self, json_filename, output_filename):
		X = [] #list
		colorstring = "krgy"
		category = ["Root", "TLD", "Other", "Terminating"] 
		t = []
		final_q = []

		raw_data = []
		for l in open(json_filename, 'r'):
			line = json.loads(l)	
			raw_data.append(line)
		
		li = self.agg_hosts(raw_data)

		for k, v in li.iteritems():
			server_q = [result[0]["Time in millis"] for result in v]			
			tld_q = [result[1]["Time in millis"] for result in  v]
			other_q = [result[2]["Time in millis"] for result in v]
			f_temp = [result[3]["Time in millis"] for result in v]
	
			t.extend(server_q)
			t.extend(tld_q)
			t.extend(other_q)
			final_q.extend(f_temp)

		f = plot.figure()

		#total time to resolve a site
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

		self.save_graph(output_filename, f)

	def save_graph(self, output_cdf_filename, f):
		from matplotlib.backends import backend_pdf
		with backend_pdf.PdfPages(output_cdf_filename) as pdf:
			pdf.savefig(f)

	def append_json(self, filename, data):
		with open(filename, 'a') as f:
			json.dump(data, f)
			f.write(os.linesep)

	def write_json(self, filename, data):
		with open(filename, 'w') as f:
			json.dump(data, f)

	def add_host(self, host, result, output):
			
		self.result.append ({ 
			"Name" : host, \
			"Success" : result
		})
		
		if (result):
				self.result[len(self.result)-1].update({"Queries" : self.get_queries(output)})

	def get_queries(self, output) :
		answers = []
		queries = []


		for line in output.splitlines():
			
			if line == ' ' :
				print "WHITESPACE"
			if (not line.startswith(';') and not line.startswith(';;')) :
				parse = line.split()
	
				try:				
					queried_name = parse[0]
					data = parse[4]
					_type = parse[3]
					ttl = parse[1]
					self.add_answer(answers, parse[0], parse[4], parse[3], parse[1])
				except IndexError:
					pass
			elif line.startswith(';; Query time'):
				time = re.search(';; Query time: (.+?) msec', line).group(1)
				
				self.add_query(queries, time, answers)
				answers= []
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

	def compute_average (self, l, i):
		
		_ttls = []
		hosts = self.agg_hosts(l, i)
		
		for a, v in hosts.iteritems():
			
			ttl=0
			s_answers = [li["Answers"] for li in v]
			for li in s_answers:
				s_ttl = [ m["TTL"] for m in li]	
			
			for i in s_ttl:
				try:
					ttl = ttl+ int(i)
				except ValueError:
					pass
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
					if i is not -1:
						hosts[result["Name"]].append(result["Queries"][i])
					else:
						hosts[result["Name"]].append(result["Queries"])

				except KeyError:
					hosts[result["Name"]] =[]
					if  i is not -1:
						hosts[result["Name"]].append(result["Queries"][i])					
					else:
						hosts[result["Name"]].append(result["Queries"])

		return hosts

a = DNS()

#a.run_dig("alexa_top_100", "dig_outside_server.json", "122.50.120.220")
#print a.get_average_ttls("dig_5.json")
#print a.get_average_times("dig_5.json")
#a.generate_time_cdfs("dig_5.json", "dns_plot_5.pdf")
print a.count_different_dns_responses("dns_output_1.json", "dig_outside_server.json")
