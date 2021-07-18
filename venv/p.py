import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv
import yaml

res = requests.get('https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html')

CSV_FILE = 'c1.csv'
METRIC_HEADERS = ['metric_name', 'metric_nameunit', 'description']
lineadder = ['Minimum','Maximum','Average']
soup = BeautifulSoup(res.text, 'html.parser')
match = soup.find('div', {'id': 'main-content'})
rows = match.findAll('tr')
#cols =match.findAll('td')
#print(cols[0].text)
for i in rows:
    cols= i.findAll('td')
    if cols and len(cols)>0:
        col = cols[0]
        metric_name = col.text.strip()
        print(col.text.strip())

        idx = 0
        metric_desc = ''
        metric_stats = ''
        metric_units = ''
        for section in sections:
            if section:
                section_string = section.string.strip()
                if section_string and idx == 0:
                    section_string = " ".join(section_string.split())
                    section_string = section_string.replace('\n', '')
                    metric_desc = section_string
                elif section_string.startswith(VALID_STATISTICS_):
                    metric_stats = section_string.replace(VALID_STATISTICS_, '').strip()
                    metric_stats = " ".join(metric_stats.split())
                    metric_stats = metric_stats.replace('\n', '')
                elif section_string.startswith(UNITS_):
                    metric_units = section_string.replace(UNITS_, '').strip()
            idx = idx + 1
            if metric_desc and metric_stats and metric_units:
                metric_units = metric_units.lower()
                if metric_units != 'count':
                    metric_units = 'gauge'
