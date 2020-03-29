import django
django.setup()

import json, httpie, requests
from flatten_json import flatten
import pandas as pd
from pandas.io.json import json_normalize
import ijson


#from itertools import chain, starmap

#def flatten_json_iterative_solution(dictionary):    
#	def unpack(parent_key, parent_value):		
#		if isinstance(parent_value, dict):
#			for key, value in parent_value.items():
#				temp1 = parent_key + '_' + key
#				yield temp1, value
#		elif isinstance(parent_value, list):
#			i = 0 
#			for value in parent_value:
#				temp2 = parent_key + '_'+str(i) 
#				i += 1
#				yield temp2, value
#		else:
#			yield parent_key, parent_value    
#	# Keep iterating until the termination condition is satisfied
#	while True:
#		# Keep unpacking the json file until all values are atomic elements (not dictionary or list)
#		dictionary = dict(chain.from_iterable(starmap(unpack, dictionary.items())))
#		# Terminate condition: not any value in the json file is dictionary or list
#		if not any(isinstance(value, dict) for value in dictionary.values()) and not any(isinstance(value, list) for value in dictionary.values()):		    
#			break
#	return dictionary

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

URL = "http://127.0.0.1:8000/pola3r/project_metadata/?format=json"

r = requests.get(url=URL)
test = r.json()





objects = ijson.items(test,'meta.view.columns.item')
print(objects)
#columns = list(objects)
#print(columns[0])




#df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for k, v in test.items()}, axis=0)
#print(df)

#df = pd.Series(flatten_json_iterative_solution(test)).to_frame()
#print(df)