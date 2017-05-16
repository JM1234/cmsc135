import subprocess
import re
import json
import pprint
import matplotlib.pyplot as plot
from bisect import bisect_left


class discrete_cdf:
		
	def __init__(self,data):
		self._data = data
		self._data_len = float(len(data))

	def __call__(self,point):
		return (len(self._data[:bisect_left(self._data, point)]) / 
		self._data_len)

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
		self.write_json(raw_ping_output_filename, self.raw_data) 
		self.write_json(agg_ping_output_filename, self.agg_data)
		print "Done writing."
	
	def set_rtt(self, hostname, response, num_packets):
		
		self.raw_data[hostname]=[] #what if existing na?		
		
		for line in response.splitlines():
			try:
				found = re.search('time=(.+?) ms', line).group(1)	
				self.raw_data[hostname].append(float(found))
			except AttributeError:
				continue

		i = num_packets - len(self.raw_data[hostname])		
		if i>0 :
			b = i*[-1.0]		
			self.raw_data[hostname].extend(b)
		print hostname + str(self.raw_data[hostname])
		
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

	def plot_median_rtt_cdf(self, agg_ping_results_filename, output_cdf_filename):
	
		X=[] #median_val	
		
		try:
			with open(agg_ping_results_filename, 'r') as f:			
				results = json.load(f)
		except IOError:
				print "File not found."
		 
		for k, v in results.iteritems():
			if (v['drop_rate'] != 100.00):		
				X.append(v['median_rtt'])
		
		cdf =  discrete_cdf(sorted(X))
		n = max(X)
		xvalues = range(0, int(n))
		yvalues = [cdf(point) for point in xvalues]
		
		f = plot.figure()
		plot.plot(xvalues, yvalues, label = "Median CDF")
		plot.legend()
		plot.grid()
		plot.xlabel("seconds")
		plot.ylabel("Cumulative Fraction")
		plot.show()

		self.save_graph(output_cdf_filename, f)

	def plot_ping_cdf(self, raw_ping_results_filename, output_cdf_filename):
		X = [] #list
		colorstring = "kbgry"
		i=0

		try:
			with open(raw_ping_results_filename, 'r' ) as f: 
				result = json.load(f)
		except IOError:
			print "File not found."

		f = plot.figure()
		for k, v in result.iteritems():
			i+=1
			X = v

			cdf =  discrete_cdf(sorted(X))
			n = max(X)
			xvalues = range(0, int(n))
			yvalues = [cdf(point) for point in xvalues]
			
			plot.plot(xvalues, yvalues, color = colorstring[i], label = k)
		
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

	
a= RTTS()

"""
###part 1

try:
	f = open('alexa_top_100', 'r')		
	hosts = file.read(f)
except IOError:
	hosts = {}

hosts = ['google.com', 'todayhumor.co.kr', 'zanvarsity.ac.tz', 'taobao.com']
print "Running..."
#print "HOSTS: " + str(len(hosts.split()))
"""
a.run_ping(['google.com'], 5, 'trial.json', 'trial_agg.json' )

#a.plot_median_rtt_cdf("rtts_a_agg.json", "rtts_a_plot.pdf")

#a.plot_ping_cdf("rtts_b_raw.json", "rtts_b_plot.pdf")
