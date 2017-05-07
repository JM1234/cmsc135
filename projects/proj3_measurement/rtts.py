import subprocess
import re
import json
import pprint

class RTTS:	

	def run_ping(self, hostnames, num_packets, raw_ping_output_filename="rtts_a.json", agg_ping_output_filename="b.json") :
		
		try:
			with open(raw_ping_output_filename, 'r') as f:			
				self.raw_data = json.load(f)
		except IOError:
			self.raw_data = {}
		try:
			with open(agg_ping_output_filename, 'r') as f:
				self.agg_data = json.load(f)
		except IOError:
			self.agg_data = {}
		
		print "Pinging sites..."
		#ping hostnames
		for hostname in hostnames:			
			try:	
			
				response = subprocess.check_output(
					['ping', '-c', str(num_packets), hostname],
					stderr=subprocess.STDOUT, #get all output
					universal_newlines = True #return string not bytes
				)			
			except subprocess.CalledProcessError:
				response = "None"
			self.set_rtt(hostname, response, num_packets)
			continue
		
		print "Aggregating results"
		
		print " Hosts: " + str(len(self.raw_data))
		self.agg_ping(self.raw_data, num_packets)
		
		#store results
		#print "Writing raw_ping of length " + str(len(self.raw_data)) \
		#	+ "agg_data of length " + str(len(self.agg_data))
		self.write_json(raw_ping_output_filename, self.raw_data) 
		self.write_json(agg_ping_output_filename, self.agg_data)
		print "Done writing."

	def plot_median_rtt_cdf ():
		pass
	def plot_ping_cdf (self) :
		pass

	def set_rtt(self, hostname, response, num_packets):

		self.raw_data[hostname]=[] #what if existing na?		
		#print "..." +hostname
		
		for line in response.split():
			try:
				found = re.search('time=(.+?) ms', line).group(1)			
				self.raw_data[hostname].append(float(found))
			except AttributeError:
				continue

		i = num_packets - len(self.raw_data[hostname])		
		if i>0 :
			b = i*[-1.0]		
			self.raw_data[hostname].extend(b)
		print hostname

	def write_json(self, file_name, data):
		with open(file_name, 'w') as f:
			json.dump(data, f)

	def store_agg_ping(self, hostname, droprate=-1, max_rtt=-1, mid=-1):
		self.agg_data[hostname] = {
			'drop_rate' : droprate, \
 			'max_rtt' : max_rtt, \
			'median_rtt' : mid \
			}

	def agg_ping(self, data, num_packets):
		
		for k, v in data.items():
			droprate = float(v.count(-1.0)*100 / num_packets)
					
			if (droprate<100):
				res = self.remove_null(sorted(v))	
				maximum = max(res)
				median = self.compute_median(res)
				self.store_agg_ping(k, droprate, maximum, median)
			else:
				self.store_agg_ping(k)

	def compute_median(self, list):
		if (len(list) %2 != 0 ):
			i = len(list)/2			
			return list[i]
		else: 
			i = len(list)/2
			return (float(list[i-1]) + float(list[i])) / 2
	
	#remove null responses
	def remove_null(self, list):
		try:
			list.reverse()				
			return list[:list.index(-1.0)]
		except ValueError:
			return list

a= RTTS()
try:
	f = open('alexa_top_100', 'r')		
	hosts = file.read(f)
except IOError:
	hosts = {}

#hosts = ['google.com', 'todayhumor.co.kr', 'zanvarsity.ac.tz', 'taobao.com']
print "Running..."
#print "HOSTS: " + str(len(hosts.split()))
a.run_ping(hosts.split(), 100, 'rtts_a_raw.json', 'rtts_a_agg.json' )
