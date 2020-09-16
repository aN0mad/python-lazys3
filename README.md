# python-lazys3

A rewrite of https://github.com/nahamsec/lazys3 into python.

### Usage
```
python3 lazys3.py -h
usage: lazys3.py [-h] [-c] [-d DOMAIN] [-e ENVIRONMENT] [-p] [-o OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -c, --color           Display results with color
  -d DOMAIN, --domain DOMAIN
                        Domain name to bruteforce
  -e ENVIRONMENT, --environment ENVIRONMENT
                        Add to default environment list (seperated by comma):
                        ['dev', 'development', 'stage', 's3', 'staging',
                        'prod', 'production', 'test']
  -p, --permutations    Just print the permuatations and do not resolve the
                        requests
  -o OUTFILE, --outfile OUTFILE
                        Specify a file to save the output too
```
