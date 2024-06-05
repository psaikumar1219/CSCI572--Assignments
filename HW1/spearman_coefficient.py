from bs4 import BeautifulSoup
import time
from time import sleep
import requests
from random import randint
from html.parser import HTMLParser
import json
import concurrent.futures
import csv
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100Safari/537.36'}


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


read_hw1_file_path = "hw1.json"
with open(read_hw1_file_path, "r") as json_file:
    data = json.load(json_file)


yahoo_result = {}
for key, value in data.items():
	yahoo_result[key] = []
	for link in value:
		yahoo_result[key].append(trim_link(link))


# # print(yahoo_result["Some important facts on the respiratory system"])
# for link in yahoo_result[queries[59]]:
# 	print(link)

# print("------------------------")

# # print(google_result["Some important facts on the respiratory system"])
# for link in google_result[queries[59]]:
# 	print(link)

for query in queries:
	print(len(yahoo_result[query]))

print("-------------")



query_result = []
for _ in range(100):
    row = []
    for _ in range(4):
        row.append(0)
    query_result.append(row)


for i in range(100):
	query_result[i][0] = "Query " + str(i+1)

	google_links = google_result[queries[i]]
	yahoo_links = yahoo_result[queries[i]]

	ic = 0
	d_square = 0
	for k in range(len(yahoo_links)):
		yahoo_link = yahoo_links[k]

		try:
			index = google_links.index(yahoo_link)
			d_square += (index-k)*(index-k)
			ic += 1
		except:
			# print("link not found")
			ic = ic

	query_result[i][1] = ic
	query_result[i][2] = (ic/len(google_links))*100

	if ic == 0:
		query_result[i][3] = 0
	else:
		if ic == 1:
			if d_square==0:
				query_result[i][3] = 1
			else:
				query_result[i][3] = 0
		else:
			query_result[i][3] = 1 - (6*(d_square)/((ic)*((ic*ic)-1)))


num_queries = len(query_result)
sum_column1 = sum(row[1] for row in query_result)
sum_column2 = sum(row[2] for row in query_result)
sum_column3 = sum(row[3] for row in query_result)
average_column1 = sum_column1 / num_queries
average_column2 = sum_column2 / num_queries
average_column3 = sum_column3 / num_queries

csv_file_path = "hw1.csv"
header = ["Queries", "Number of Overlapping Results", "Percent Overlap", "Spearman Coefficient"]

with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(header)
    csv_writer.writerows(query_result)
    csv_writer.writerow(["Averages", average_column1, average_column2, average_column3])

