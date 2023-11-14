import requests
import time
import re
from bs4 import BeautifulSoup

class Cricbuzz():
	def __init__(self):
		pass

	def crawl_url(self,url):
		try:
			r = requests.get(url).json()
			return r
		except Exception:
			raise

	def players_mapping(self,mid):
		url = "https://www.cricbuzz.com/live-cricket-scores/75549/sl-vs-afg-30th-match-icc-cricket-world-cup-2023" + mid
		match = self.crawl_url(url)
		players = match.get('players')
		d = {}
		for p in players:
			d[int(p['id'])] = p['name']
		t = {}
		t[int(match.get('team1').get('id'))] = match.get('team1').get('name')
		t[int(match.get('team2').get('id'))] = match.get('team2').get('name')
		return d,t

	def matchinfo(self,mid):

		url = f'https://m.cricbuzz.com/cricket-scorecard/{mid}'

		response = requests.get(url)
		html = response.text

		soup = BeautifulSoup(html, 'html.parser')

		data = {}  # Create a dictionary to store the extracted data

		# Find all div elements with class 'cb-list-item'
		items = soup.find_all("div", class_="cb-list-item")

		for item in items:
			title_element = item.find("h3", class_="ui-li-heading")
			content_element = item.find("div", class_="list-content")

			if title_element and content_element:
				title = title_element.get_text(strip=True)
				content = content_element.get_text(strip=True)

				# Add the data to the dictionary
				data[title] = content

		# Print the extracted data
		for key, value in data.items():
			print(f"{key}: {value}")


	def matches(self):

		url = "https://m.cricbuzz.com"

		# Send an HTTP request to the URL and get the content
		response = requests.get(url)

		if response.status_code == 200:
			# Parse the HTML content using BeautifulSoup
			soup = BeautifulSoup(response.text, 'html.parser')

			# Find all anchor elements with a "href" attribute containing match IDs and names
			match_links = soup.find_all("a", href=re.compile(r"/cricket-commentary/(\d+)/([^/]+)-[^/]+-[^/]+-\d+"))

			# Extract and print the match names and match IDs
			for link in match_links:
				match_url = link["href"]
				match_name = re.search(r"/cricket-commentary/(\d+)/([^/]+)-[^/]+-[^/]+-\d+", match_url).group(2)
				match_id = re.search(r"/cricket-commentary/(\d+)/([^/]+)-[^/]+-[^/]+-\d+", match_url).group(1)
				print(f"Match Name: {match_name}, Match ID: {match_id}")

		else:
			print("Request failed with status code:", response.status_code)
	
	def summary(self,mid):

		# URL of the page you want to scrape
		url = f"https://m.cricbuzz.com/cricket-match-summary/{mid}"

		# Send an HTTP GET request to the URL
		response = requests.get(url)

		if response.status_code == 200:
			# Parse the HTML content using BeautifulSoup
			soup = BeautifulSoup(response.content, 'html.parser')

			# Find all the elements with class "miniscore-data"
			miniscore_data = soup.find_all(class_="miniscore-data")

			# Loop through the miniscore data elements and format the summary info
			for element in miniscore_data:
				summary_info = element.get_text()
				# Replace consecutive spaces with a single space and format the output
				summary_info = ' '.join(summary_info.split())
				summary_info = summary_info.replace('Batting', '\nBatting\n').replace('Bowling', '\nBowling\n').replace(' ', ' ')
				print(summary_info)
		else:
			print("Failed to retrieve the page. Status code:", response.status_code)

	def result(self,mid):
		# Define the URL
		url = f"https://m.cricbuzz.com/cricket-commentary/{mid}"
		# print("url for the match is \n",url)

		# Send an HTTP request to the URL and get the content
		response = requests.get(url)

		if response.status_code == 200:
			# Parse the HTML content using BeautifulSoup
			soup = BeautifulSoup(response.text, 'html.parser')

			# Find the specific h3 element that contains the desired header value
			result = soup.find("h3", class_="ui-li-heading")
			score = soup.find("div", class_="col-xs-9 col-lg-9 dis-inline")

			if result or score:
				# Extract and print the desired header value
				result_text = result.get_text(strip=True)
				score_text = score.get_text(strip=True)
				print("Result of the Match:")
				print(result_text)
				print(score_text)
			else:
				print("Header not found on the page.")
		else:
			# print(url)
			print("Request failed with status code :", response.status_code)


	def find_match(self,id):
		url = "http://mapps.cricbuzz.com/cbzios/match/livematches"
		crawled_content = self.crawl_url(url)
		matches = crawled_content['matches']

		for match in matches:
			if match['match_id'] == id:
				return match
		return None

	def livescore(self,mid):
		# URL of the cricket commentary page
		url = f"https://m.cricbuzz.com/cricket-commentary/{mid}"

		# Send a GET request to the URL
		response = requests.get(url)

		# Check if the request was successful (status code 200)
		if response.status_code == 200:
			# Parse the HTML content using BeautifulSoup
			soup = BeautifulSoup(response.text, 'html.parser')

			# Find divs with class "list-group"
			list_group_divs = soup.find_all('div', class_='list-group')

			# Extract and print data from divs 1, 2, and 3
			for i, div in enumerate(list_group_divs[:3], 1):

				# Extract relevant information based on the structure of the HTML
				if i == 1:
					header = div.find('h4', class_='cb-list-item ui-header ui-branding-header')
					print("Match Header: ", header.text.strip())

				elif i == 2:
					status_div = div.find('div', class_='col-xs-12 col-lg-12 dis-inline')
					status = status_div.find('div', class_='cbz-ui-status')
					print("Match Status: ", status.text.strip())

				elif i == 3:
					teams_score_div = div.find('div', class_='miniscore-data ui-match-scores-branding')
					# soup = teams_score_div
					team_scores = soup.select('.miniscore-teams')[0].get_text(strip=True)
					print(f"Team Scores:  {team_scores}")

					# Extracting and displaying current run rate
					crr = soup.select('.crr')[0].get_text(strip=True)
					print(f"Current Run Rate: {crr}")

					# Extracting and displaying batting details
					batting_table = soup.select('.table-condensed')[0]
					batting_rows = batting_table.select('tr')[1:]  # Skip the header row

					print("\nBatting Details:")
					for row in batting_rows:
						columns = row.select('td')
						player_name = columns[0].get_text(strip=True)
						runs = columns[1].get_text(strip=True)
						fours = columns[2].get_text(strip=True)
						sixes = columns[3].get_text(strip=True)
						strike_rate = columns[4].get_text(strip=True)

						print(f"{player_name}: {runs} runs, {fours} fours, {sixes} sixes, Strike Rate: {strike_rate}")

					# Extracting and displaying bowling details
					bowling_table = soup.select('.table-condensed')[1]
					bowling_rows = bowling_table.select('tr')[1:]  # Skip the header row

					print("\nBowling Details:")
					for row in bowling_rows:
						columns = row.select('td')
						bowler_name = columns[0].get_text(strip=True)
						overs = columns[1].get_text(strip=True)
						maidens = columns[2].get_text(strip=True)
						runs_given = columns[3].get_text(strip=True)
						wickets = columns[4].get_text(strip=True)

						print(f"{bowler_name}: {overs} overs, {maidens} maidens, {runs_given} runs, {wickets} wickets")

					# Extracting and displaying partnership, last wicket, and recent balls
					partner_info = soup.select('.ui-branding-style-partner .list-content')[0].get_text(strip=True)
					print(f"\nPartner Information:\n{partner_info}")

				# print("\n" + "=" * 50 + "\n")  # Separation line
				print("\n")

		else:
			print(f"Failed to retrieve the content. Status code: {response.status_code}")

	def commentary(self,mid):
		# data = {}
		# URL of the cricket commentary page
		url = f"https://m.cricbuzz.com/cricket-commentary/{mid}"

		# Send a GET request to the URL
		response = requests.get(url)

		# Check if the request was successful (status code 200)
		if response.status_code == 200:
			# Parse the HTML content using BeautifulSoup
			soup = BeautifulSoup(response.text, 'html.parser')

			# Extracting and displaying commentary
			commentary_items = soup.select('.cb-list-item:not(.cbz_ads) .list-content .commtext')
			print("\nCommentary:")
			for item in commentary_items:
				commentary_text = item.get_text(strip=True)
				print(commentary_text)
		else:
			print(f"Failed to retrieve the content. Status code: {response.status_code}")

	def scorecard(self,mid):

		# URL to fetch
		url = f"https://m.cricbuzz.com/cricket-scorecard/{mid}"

		# Send an HTTP GET request to the URL
		response = requests.get(url)

		# Check if the request was successful
		if response.status_code == 200:
			# Parse the HTML content
			soup = BeautifulSoup(response.text, 'html.parser')

			# Find and extract the relevant section with the team details and batting/bowling statistics
			inn_1 = soup.find('div', id='inn_1')

			# Extract the AFG and AUS team information
			teams = inn_1.find_all('div', class_='cb-list-item ui-header ui-header-small')
			for team in teams:
				print(team.get_text())

			print("\n")
			# Extract batting and bowling statistics
			tables = inn_1.find_all('table', class_='table table-condensed')
			for table in tables:
				rows = table.find_all('tr')
				for row in rows:
					columns = row.find_all('td')
					row_text = " ".join(column.get_text() for column in columns)
					print(row_text)
				print("\n")
			# print("\n")

			inn_2 = soup.find('div', id='inn_2')

			# Extract the AFG and AUS team information
			teams = inn_2.find_all('div', class_='cb-list-item ui-header ui-header-small')
			for team in teams:
				print(team.get_text())

			print("\n")
			# Extract batting and bowling statistics
			tables = inn_2.find_all('table', class_='table table-condensed')
			for table in tables:
				rows = table.find_all('tr')
				for row in rows:
					columns = row.find_all('td')
					row_text = " ".join(column.get_text() for column in columns)
					print(row_text)
				print("\n")
			# print("\n")


		else:
			print("Failed to retrieve the web page. Status code:", response.status_code)

	def fullcommentary(self,mid):
		data = {}
		try:
			url =  "https://www.cricbuzz.com/match-api/"+mid+"/commentary-full.json"
			comm = self.crawl_url(url).get('comm_lines')
			d = []
			for c in comm:
				if "comm" in c:
					d.append({"comm":c.get("comm"),"over":c.get("o_no")})
			data['fullcommentary'] = d
			return data
		except Exception:
			raise
	def players(self,mid):
		data = {}
		try:
			url =  "https://www.cricbuzz.com/match-api/"+mid+"/commentary.json"
			players = self.crawl_url(url).get('players')
			d = []
			for c in players:
				if "player" in c:
					d.append({"id":c.get("id"),"f_name":c.get("f_name"),"name":c.get("name"),"bat_style":c.get("bat_style"),"bowl_style":c.get("bowl_style")})
			data['players'] = d
			return data
		except Exception:
			raise
