import argparse
from colorama import Style, Fore
import requests
import sys

ENVIRONMENTS = ['dev', 'development', 'stage', 's3', 'staging', 'prod', 'production', 'test']
prefix_wordlist_file = "common_bucket_prefixes.txt"

# Class for storing bucket information
class S3:
	def __init__(self, s3_bucket):
		self.bucket = s3_bucket
		self.domain = f"http://{s3_bucket}.s3.amazonaws.com"
		self.code = ""

	# Make request to bucket to get status code
	def query(self):
		req = requests.get(self.domain, timeout=5)
		self.code = req.status_code

# Class for handling the scanning and bucket provisioning
class Scanner:
	def __init__(self, wordlist):
		self.scanner_wordlist = wordlist
	
	def getWordlist(self):
		return self.scanner_wordlist

# Read in wordlist for bruteforcing
def read_prefix_wordlist(prefix_wordlist_file):
	with open(prefix_wordlist_file, 'r') as inFile:
		prefix_wordlist_file = inFile.read().splitlines()
	return prefix_wordlist_file

# Return the raw permutation of the domain
def permutation_raw(common_prefix):
	return common_prefix

# Return the permutations for the list of common prefixes, 
# the environment wordlist and the supplied prefix wordlist
def permutation_envs(common_prefix, prefix_wordlist):
	strings = ['{0}-{1}-{2}', '{0}-{1}.{2}', '{0}-{1}{2}', '{0}.{1}-{2}', '{0}.{1}.{2}']
	permuatation_env_arr = []
	for word in prefix_wordlist:
		for environment in ENVIRONMENTS:
			for string in strings:
				permuatation_env_arr.append(string.format(common_prefix, word, environment))
	return permuatation_env_arr

# Return the permutations for the common prefixes and the supplied prefix wordlist
def permutation_host(common_prefix, prefix_wordlist):
	strings = ['{0}.{1}', '{0}-{1}', '{0}{1}']
	permutation_host_array = []
	for word in prefix_wordlist:
		for string in strings:
			permutation_host_array.append(string.format(common_prefix, word))
			permutation_host_array.append(string.format(word, common_prefix))
	return permutation_host_array

# Print data in Green
def printGreen(domain, code, logfile):
	stdOut = f'{Fore.GREEN}{domain}: {code}{Style.RESET_ALL}'
	if logfile != None:
		logfile.write(stdOut+"\n")
	print(stdOut)

# Print data in Yellow
def printYellow(domain, code, logfile):
	stdOut = f'{Fore.YELLOW}{domain}: {code}{Style.RESET_ALL}'
	if logfile != None:
		logfile.write(stdOut+"\n")
	print(stdOut)

# Print data in Red
def printRed(domain, code, logfile):
	stdOut = f'{Fore.RED}{domain}: {code}{Style.RESET_ALL}'
	if logfile != None:
		logfile.write(stdOut+"\n")
	print(stdOut)

# Print data for the -p, --permutations flag
def printPerm(domain, logfile):
	stdOut = f'{domain}'
	if logfile != None:
		logfile.write(stdOut+"\n")
	print(stdOut)

def main():
	# Command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--color", help="Display results with color", action="store_true")
	parser.add_argument("-d","--domain", help="Domain name to bruteforce")
	parser.add_argument("-e", "--environment", help="Add to default environment list (seperated by comma): ['dev', 'development', 'stage', 's3', 'staging', 'prod', 'production', 'test']")
	parser.add_argument("-p", "--permutations", help="Just print the permuatations and do not resolve the requests", action="store_true")
	parser.add_argument("-o", "--outfile", help="Specify a file to save the output too")
	
	args = parser.parse_args()

	if args.domain == None:
		parser.print_help()
		print("")
		print("ERROR: -d, --domain was not specified")
		sys.exit(1)
	else:
		common_prefix = str(args.domain)
	
	if args.outfile != None:
		OUTFILE = args.outfile
	else:
		OUTFILE = None
	
	if args.environment == None:
		additions = str(args.environment).split(",")
		for add in additions:
			ENVIRONMENTS.append(add.rstrip().strip(" "))
	else:
		pass
	
	PERMS = args.permutations
	COLORS = args.color

	# Program variables
	possible_buckets = []
	s3_objects = []

	# Setup bucket wordlist
	prefix_wordlist = read_prefix_wordlist(prefix_wordlist_file)
	possible_buckets.append(permutation_raw(common_prefix))
	possible_buckets.extend(permutation_envs(common_prefix, prefix_wordlist))
	possible_buckets.extend(permutation_host(common_prefix, prefix_wordlist))
	print("Possible buckets: "+str(len(possible_buckets)))
	
	#print(str(possible_buckets))
	
	# Create scanner object and bucket objects
	scanner = Scanner(possible_buckets)
	
	# Create log file if it is passed in
	if OUTFILE != None:
		outFileHandle = open(OUTFILE, 'w')
	else:
		outFileHandle = None

	# Create all bucket objects and query or print permuation
	for bucket in scanner.getWordlist():
		s3_obj = S3(bucket)
		if PERMS == False:
			s3_obj.query()
		else:
			printPerm(s3_obj.domain, outFileHandle)
			continue

		s3_objects.append(s3_obj)
		if COLORS == True:
			if s3_obj.code == 200:
				printGreen(s3_obj.domain, s3_obj.code, outFileHandle)
			elif s3_obj.code != 404:
				printYellow(s3_obj.domain, s3_obj.code, outFileHandle)
			else:
				printRed(s3_obj.domain, s3_obj.code, outFileHandle)
		else:
			print(f"{s3_obj.domain}: {s3_obj.code}")

	# Close the log file
	if OUTFILE != None:
		outFileHandle.close()
			

if __name__ == "__main__":
	main()