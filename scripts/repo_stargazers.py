### Script to get GitHub profile data of all Stargazers of a given GitHub repository
###
###	by Max Woolf (@minimaxir)

import json
import csv
import requests
import datetime
import time
import yaml
from urllib.request import urlopen, Request

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

access_token = config['access_token']
project_name = config['current']
repo = config[project_name]['full_name']

fields = ["user_id", "username", "num_followers", "num_following", "num_repos","created_at","star_time","email"]
page_number = 0
users_processed = 0
stars_remaining = True
list_stars = []

print("Gathering Stargazers for %s..." % repo)

###
###	This block of code creates a list of tuples in the form of (username, star_time)
###	for the Statgazers, which will laterbe used to extract full GitHub profile data
###

while stars_remaining:
    query_url = "https://api.github.com/repos/%s/stargazers?page=%s&access_token=%s" % (repo, page_number, access_token)

    req = Request(query_url)
    req.add_header('Accept', 'application/vnd.github.v3.star+json')
    response = urlopen(req)
    data = json.loads(str(response.read(), 'utf8'))

    for user in data:
        print(user)
        username = user['user']['login']

        star_time = datetime.datetime.strptime(user['starred_at'],'%Y-%m-%dT%H:%M:%SZ')
        star_time = star_time + datetime.timedelta(hours=-5) # EST
        star_time = star_time.strftime('%Y-%m-%d %H:%M:%S')

        list_stars.append((username, star_time))

    if len(data) < 25:
    	stars_remaining = False

    page_number += 1

print("Done Gathering Stargazers for %s!" % repo)

list_stars = list(set(list_stars)) # remove dupes

print("Now Gathering Stargazers' GitHub Profiles...")

###
###	This block of code extracts the full profile data of the given Stargazer
###	and writes to CSV
###

with open('%s-stargazers.csv' % repo.split('/')[1], 'w') as stars:

    stars_writer = csv.writer(stars)
    stars_writer.writerow(fields)

    for user in list_stars:
        username = user[0]

        query_url = "https://api.github.com/users/%s?access_token=%s" % (username, access_token)

        req = Request(query_url)
        response = urlopen(req)
        data = json.loads(str(response.read(), 'utf8'))

        user_id = data['id']
        num_followers = data['followers']
        num_following = data['following']
        num_repos = data['public_repos']
        email = data.get('email', 'None')

        created_at = datetime.datetime.strptime(data['created_at'],'%Y-%m-%dT%H:%M:%SZ')
        created_at = created_at + datetime.timedelta(hours=-5) # EST
        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')

        stars_writer.writerow([user_id, username, num_followers, num_following, num_repos, created_at, user[1], email])

        users_processed += 1

        if users_processed % 100 == 0:
        	print("%s Users Processed: %s" % (users_processed, datetime.datetime.now()))
        time.sleep(1) # stay within API rate limit of 5000 requests / hour + buffer
