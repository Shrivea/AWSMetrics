import requests
from bs4 import BeautifulSoup
import re
import yaml
import csv

UNITS_ = 'Units:'
VALID_STATISTICS_ = 'Valid statistics:'
LATENCY_VALUES = ['minimum', 'maximum', 'p50', 'p90', 'p95', 'p99', 'p99.99']

METRIC_HEADERS = ["metric_name", "metric Stats"]
YAML_FILE = "AWS.ELB.yaml"
CSV_FILE = "AWS.ELB.csv"
CSV2 = "AWS.Elb(2).csv"
CODE_MAP = {
    'DesyncMitigationMode_NonCompliant_Request_Count': 'desync_mitigation_mode_non_compliant_request_count',
    'aws.elbdesync_mitigation_mode__non_compliant__request__count': 'aws.elbdesync_mitigation_mode_non_compliant_request_count',
    'HTTPCode_ELB_4xx': 'http_code_elb_4xx',
    'HTTPCode_ELB_5xx': 'http_code_elb_xx',
    'EstimatedALBActiveConnectionCount': 'aws.elb.estimated_alb_active_connection_count',
    'EstimatedALBConsumedLCUs': 'aws.elb.estimated_alb_consumed_lcus',
    'EstimatedALBNewConnectionCount': 'aws.elb.estimated_alb_new_connection_count',
    'HTTPCode_Backend_2XX,                                                   HTTPCode_Backend_3XX,                                                   HTTPCode_Backend_4XX,                                                   HTTPCode_Backend_5XX'
    : 'http_code_backend_2xx_http_code_backend_3xx_http_code_backend_4xx_http_code_backend_5xx'

}


class AWSS3Extractor:
    def __init__(self, url):
        self.url = url
        self.content = ""
        self.aws_dict = {}
        self.aws_list = []
        self.aws_list2 = []

    def load_page(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            self.content = page.content

    def get_content(self):
        return self.content

    def process_content(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        tableone = soup.find('table', id="w282aac21b7c13b5")
        rowsone = tableone.findAll('tr')
        metric_name = ''
        self.aws_dict = {'type': 'elb', 'keys': []}
        self.aws_list = []
        for row in rowsone[1:]:
            metric_desc = ''
            metric_statistics = ''
            metric_reporting_criteria = ''
            metric_example = ''

            cols = row.findAll('td')
            col = cols[0]

            allChildren = col.findAll(text=True)
            originalmetricname = col.text.strip().replace('\n', '')
            metric_name = 'aws.elb.' + self.snake_case(originalmetricname)
            originalmetricname = originalmetricname.replace('\t', '')
            self.aws_list2.append([originalmetricname])

            if allChildren and len(allChildren)> 1 :
                #  print(allChildren[2])
                var11 = ' '.join(allChildren)
                var11 = var11.replace('\n', '')
                var22 = ' '.join(var11.split())
                firstComma = var22.find(',')
                secondComma = var22.find(',', firstComma + 2)
                thirdComma = var22.find(',', secondComma + 2)
                firstString = var22[0:firstComma]
                secondString = var22[firstComma:secondComma]
                thirdString = var22[secondComma:thirdComma]
                fourthString = var22[thirdComma:]
                secondString = secondString.replace(', ','')
                thirdString = thirdString.replace(', ','')
                fourthString = fourthString.replace(', ','')
                firstString = secondString.replace(' ','')
                secondString = thirdString.replace(' ','')
                thirdString = fourthString.replace(' ','')

                stringsArray = ['aws.elb.'+firstString.lower() ,'aws.elb.'+secondString.lower(),'aws.elb.'+thirdString.lower() ,'aws.elb.'+fourthString.lower()]
                for op in stringsArray:
                    sections = colone.findChildren('p')
                    if sections and len(sections) > 0:
                        idx = 0
                        for sect in sections:
                            descriptions = sect.findAll(text=True)
                            var1 = ' '.join(descriptions)
                            var1 = var1.replace('\n', '')
                            var2 = ' '.join(var1.split())
                            if var2 and idx == 0:
                                metric_desc = var2
                    self.add_to_list(self.aws_list, op, metric_desc, )
                    self.add_to_list(self.aws_list, op + "_min", metric_desc + "_min")
                    self.add_to_list(self.aws_list, op + "_max", metric_desc + "_max")
                    self.add_to_list(self.aws_list, op + "_avg", metric_desc + "_avg")


            else:
                if originalmetricname in CODE_MAP.keys():
                    metric_name = 'aws.elb.' + CODE_MAP[originalmetricname]
                if metric_name == 'aws.elb.h_t_t_p_code__e_l_b_4_x_x':
                    metric_name = str('aws.elb.' + 'http_code_elb_4xx')
                if metric_name == 'aws.elb.h_t_t_p_code__e_l_b_5_x_x':
                    metric_name = str('aws.elb.' + 'http_code_elb_5xx')
                colone = cols[1]
                sections = colone.findChildren('p')
                if sections and len(sections) > 0:
                    idx = 0
                    for sect in sections:
                        descriptions = sect.findAll(text=True)
                        var1 = ' '.join(descriptions)
                        var1 = var1.replace('\n', '')
                        var2 = ' '.join(var1.split())
                        if var2 and idx == 0:
                            metric_desc = var2
                        elif var2.startswith('Reporting criteria'):
                            metric_reporting_criteria = var2
                        elif var2.startswith('Example'):
                            metric_example = var2
                        idx = idx + 1
                    self.add_to_list(self.aws_list, metric_name, metric_desc, )
                    self.add_to_list(self.aws_list, metric_name + "_min", metric_desc + "_min")
                    self.add_to_list(self.aws_list, metric_name + "_max", metric_desc + "_max")
                    self.add_to_list(self.aws_list, metric_name + "_avg", metric_desc + "_avg")



        matchtwo = soup.find('table', id="w282aac21b7c13c11")
        matchtworows = matchtwo.findAll('tr')
        for j in matchtworows[1:]:
            cols = j.findAll('td')
            col = cols[0]
            colone = cols[1]
            coltext = col.text.strip()
            self.aws_list2.append([coltext])
            met_name = 'aws.elb.' + self.snake_case(col.text.strip())
            if coltext in CODE_MAP.keys():
                met_name = CODE_MAP[coltext]

            met_desc = (colone.text.strip())
            # print(met_desc)
            self.add_to_list(self.aws_list, met_name, met_desc)
        mathcthree = soup.find('table', id="w282aac21b7c15b5")
        matchthreerows = mathcthree.findAll('tr')
        for l in matchthreerows[1:]:
            colson = l.findAll('td')
            coly = colson[0]
            colones = colson[1]
            met_nameone = 'aws.elb.' + self.snake_case(coly.text.strip())
            if coly in CODE_MAP.keys():
                met_nameone = CODE_MAP[coly]
            self.aws_dict['keys'].append(
                {'name': met_nameone, 'alias': 'dimension_' + coly.text.strip()})
            # print(met_name)
            met_descone = (colone.text.strip())
            # print(met_desc)



    def generate_csv(self):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(METRIC_HEADERS)
            writer.writerows(self.aws_list)

    def generate_csv2(self):
        with open(CSV2, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(METRIC_HEADERS)
            writer.writerows(self.aws_list2)

    def generate_yaml(self):
        # print(self.aws_dict)
        with open(YAML_FILE, 'w') as outfile:
            yaml.dump([self.aws_dict], outfile, default_flow_style=False)

    @staticmethod
    def update_description(desc, value):
        desc = desc.replace('per-request', value + ' per-request')
        desc = desc.replace('maximum', value)
        return desc

    @staticmethod
    def add_to_list(aws_list, metric_name, description):
        print(metric_name, "||", description, )
        aws_list.append([metric_name, "", "", "", "", description, "", "elb", ""])

    @staticmethod
    def snake_case(input_string):
        if input_string:
            return re.sub(r'(?<!^)(?=[A-Z])', '_', input_string).lower()
        else:
            return input_string


if __name__ == "__main__":
    extractor = AWSS3Extractor(
        'https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-cloudwatch-metrics.html')
    extractor.load_page()
    extractor.process_content()
    extractor.generate_yaml()
    extractor.generate_csv()
    extractor.generate_csv2()
