from bs4 import BeautifulSoup
import time
from time import sleep
import requests
from random import randint
from html.parser import HTMLParser
import json
import concurrent.futures
import urllib.parse
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100Safari/537.36'}

class SearchEngine:
	@staticmethod
	def search(query, sleep=True):
		if sleep: # Prevents loading too many pages too soon
			time.sleep(randint(10, 100))
		temp_url = '+'.join(query.split()) #for adding + between words for the query
		url = 'http://www.search.yahoo.com/search?p=' + temp_url + '&b=3'
		# print(url)
		soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text,"html.parser")
		new_results = SearchEngine.scrape_search_result(soup)
		return new_results

	@staticmethod
	def scrape_search_result(soup):
		raw_results = soup.find_all("a", attrs = {"class" : "d-ib fz-20 lh-26 td-hu tc va-bot mxw-100p"})
		# print(raw_results)
		results = []
		#implement a check to get only 10 results and also check that URLs must not be duplicated
		count = 0
		links_set = set()
		for result in raw_results:
			link = result.get('href')
			trimmed_link = trim_link(link)
			if trimmed_link not in links_set:
				results.append(link)
				links_set.add(trimmed_link)
				count+=1
			if count==10:
				break
		return results


def process_batch(queries):
	yahoo_result = {}
	for query in queries:
		print(query)
		yahoo_result[query] = SearchEngine.search(query, True)
		for i in range(len(yahoo_result[query])):
			link = yahoo_result[query][i]
			start_index = link.find("RU=")
			if start_index != -1:
				start_index += 3  # Skip "RU="
				end_index = link.find("/", start_index)
				if end_index != -1:
					actual_url = link[start_index:end_index]
			decoded_url = urllib.parse.unquote(actual_url)
			yahoo_result[query][i] = decoded_url
	return yahoo_result

def trim_link(link):
	if link.startswith("http://"):
		link = link[7:]
	elif link.startswith("https://"):
		link = link[8:]
	if link.startswith("www."):
		link = link[4:]
	if link.endswith("/"):
		link = link[:-1]

	return link

queries = []
Q = "queries.txt"  # Replace with the path to your text file

with open(Q, "r") as file:
    for line in file:
        queries.append(line.strip())

# queries = queries[:10]
# print(queries)

GR = "google_results.txt"
google_result = {}
with open(GR, 'r') as json_file:
	data = json.load(json_file)
	for key, value in data.items():
		# print(key)
		google_result[key] = []
		for link in value:
			# print(link)
			google_result[key].append(trim_link(link))

# print(google_result["Codes to get weapons in poptropica"])



# result = SearchEngine.search("Some important facts on the respiratory system",False)
# print(len(result))
# for res in result:
# 	print(res)
# 	start_index = res.find("RU=")
# 	if start_index != -1:
# 		start_index += 3  # Skip "RU="
# 		end_index = res.find("/", start_index)
# 		if end_index != -1:
# 			actual_url = res[start_index:end_index]
# 	decoded_url = urllib.parse.unquote(actual_url)
# 	print("----")
# 	print(decoded_url)
# 	print("----")

# print("-----------------------")



batch_size = 10
query_batches = [queries[i:i + batch_size] for i in range(0, len(queries), batch_size)]

# Create a ThreadPoolExecutor with a maximum of 10 threads
max_threads = 10
with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
    # Process each batch concurrently
    results = list(executor.map(process_batch, query_batches))

# Combine results from all batches into a single dictionary
yahoo_result = {}
for result in results:
    yahoo_result.update(result)

# print(yahoo_result)

result_file_path = "hw1.json"

# Save the yahoo_result dictionary to a JSON file
with open(result_file_path, "w") as json_file:
    json.dump(yahoo_result, json_file)
