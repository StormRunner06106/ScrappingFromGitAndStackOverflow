import json
import time
from venv import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import csv




config_path = 'config.json'
proxies = {}
pageNum = 1
pageSize = 1

def get_github_link(profile_url):
    try:
        response = requests.get(profile_url, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find GitHub link in the profile page
        github_link = None
        for link in soup.find_all('a', href=True):
            if 'github.com' in link['href']:
                github_link = link['href']
                break
        
        return github_link
    except Exception as e:
        print(f"Error fetching GitHub link for {profile_url}: {e}")
        return None

def get_users(page=pageNum, pagesize=pageSize):
    url = "https://api.stackexchange.com/2.3/users"
    params = {
        'site': 'stackoverflow',
        'pagesize': pagesize,
        'page': page,
        'order': 'desc',
        'sort': 'reputation'
    }
    response = requests.get(url, params=params, proxies=proxies)
    return response.json()

def extract_username(github_url):
    path = urlparse(github_url).path
    return path.strip('/')

def get_github_user_info(github_url):
    headers = {
        'Authorization': f'token {access_token}'
    }
    username = extract_username(github_url)
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, proxies=proxies, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Returns user info as a dictionary
    else:
        return None

# Example: Get the first 100 users

if not os.path.exists(config_path):
    print(f"The configuration file {config_path} does not exist.")
else: 
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            proxies = {
                'http': f"http://{config['username']}:{config['password']}@{config['domain']}:{config['port']}",
                'https': f"http://{config['username']}:{config['password']}@{config['domain']}:{config['port']}"
            }
            print(proxies)
    except Exception as e:
        print(f"Error decoding JSON: {e}")



while True:
    users = get_users()
    if not users:
        break
    i = 0
    allUsers = []
    for user in users['items']:

        print(user)

        profile_url = user['link']
        github_link = get_github_link(profile_url)
        userItem = {
            'name': user['display_name'] if user['display_name'] is not None else ' ',
            'link': user['link'] if user['link'] is not None else ' ',
            'reputation': user['reputation'] if user['reputation'] is not None else 0
        }
        if 'location' in user:
            userItem['location'] = user['location'] if user['location'] is not None else ' '
        else:
            userItem['location'] = ' '

        if 'website_url' in user:
            userItem['website_url'] = user['website_url'] if user['website_url'] is not None else ' '
        else:
            userItem['website_url'] = ' '
        githubUser = {}
        if github_link:
            user_info = get_github_user_info(github_link)
            if user_info:
                userItem['email'] = user_info['email'] if user_info['email'] is not None else ' '
                userItem['githubName'] = user_info['name'] if user_info['name'] is not None else ' '
                userItem['blog'] = user_info['blog'] if user_info['blog'] is not None else ' '
                userItem['githubUrl'] = github_link
            else:
                userItem['githubName'] = ' '
                userItem['blog'] = ' '
                userItem['githubUrl'] = ' '

        allUsers.append(userItem)

        i += 1
        pageNum += 1


    csv_file = 'users.csv'
    file_exists = os.path.isfile(csv_file)

    keys = set()
    # Extract all possible keys from the JSON data
    keys = set()
    for user in allUsers:
        keys.update(user.keys())

    # Convert keys to a sorted list for consistent column order
    fieldnames = list(allUsers[0].keys())

    # Write to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header
        if not file_exists:
            writer.writeheader()
        
        # Write data rows
        writer.writerows(allUsers)




    print(f"CSV file '{csv_file}' created successfully.")







