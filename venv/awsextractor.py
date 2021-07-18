import requests
from bs4 import BeautifulSoup
import re
import csv
import yaml


class awsextractor:
    def __init__(self, url):
        self.url = url
        self.content = " "
        self.aws_dict = {}
        self.aws_line = []

    def load_page(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            self.content = page.content

    def get_content(self):
        return self.content

    def process_content(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        main_content = soup.find('div', {'id': 'main-content'})
        rows = main_content.findAll('tr')
        metric_name = ''
        self.aws_dict = {'type': 's3', 'keys': []}
        self.aws_list = []
        for row in rows:
            cols = row.findAll('td')
            if cols and len(cols) > 0:
                col = cols[0]
                original_metric_name = col.text.strip()
                metric_name_snake_case = self.snake_case(original_metric_name)
                metric_name = 'aws.s3.' + metric_name_snake_case
                self.aws_dict['keys'].append(
                    {'name': metric_name_snake_case, 'alias': 'dimension_' + original_metric_name})
            if cols and len(cols) > 1:
                col = cols[1]
                sections = col.findChildren('p', text=True)
                if sections and len(sections) > 0:
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
                self.add_to_list(self.aws_list, metric_name, metric_units, metric_stats, metric_desc)
                if metric_name.endswith('latency'):
                    for suffix in LATENCY_VALUES:
                        self.add_to_list(self.aws_list, metric_name + '.' + suffix, metric_units,
                                         metric_stats,
                                         self.update_description(metric_desc, suffix))

    def generate_csv(self):
        with open(CSV_FILE, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(METRIC_HEADERS)
            writer.writerows(self.aws_list)

    def generate_yaml(self):
        print(self.aws_dict)
        with open(YAML_FILE, 'w') as outfile:
            yaml.dump([self.aws_dict], outfile, default_flow_style=False)

    @staticmethod
    def update_description(desc, value):
        desc = desc.replace('per-request', value + ' per-request')
        desc = desc.replace('maximum', value)
        return desc

    @staticmethod
    def add_to_list(aws_list, metric_name, units, stats, description):
        print(metric_name, '||', units, '||', stats, '||', description)
        aws_list.append([metric_name, units, "", "", "", description, "", "s3", ""])

    @staticmethod
    def snake_case(input_string):
        if input_string:
            return re.sub(r'(?<!^)(?=[A-Z])', '_', input_string).lower()
        else:
            return input_string


if __name__ == "__main__":
    extractor = awsextractor('https://docs.aws.amazon.com/AmazonS3/latest/userguide/metrics-dimensions.html')
    extractor.load_page()
    extractor.process_content()
    extractor.generate_yaml()
    extractor.generate_csv()
