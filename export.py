import csv
import requests
import sys
import pandas as pd
def GetMetrixNames(url):
    response = requests.get('{0}/api/v1/label/__name__/values'.format(url))
    names = response.json()['data']
    #Return metrix names
    return [names[0]]
"""
Prometheus hourly data as csv.
"""
writer = csv.writer(sys.stdout)
if len(sys.argv) != 3:
    print('Usage: {0} http://localhost:9090'.format(sys.argv[0]))
    sys.exit(1)
metrixNames=[sys.argv[2]]
writeHeader=True
for metrixName in metrixNames:
     #now its hardcoded for hourly
      response = requests.get('{0}/api/v1/query'.format(sys.argv[1]),
      params={'query': metrixName+'[1h]'})
      print(response.json())