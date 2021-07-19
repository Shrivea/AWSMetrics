import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv
import yaml

res = requests.get('https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html')
UNITS_ = 'Units:'
CSV_FILE = 'AWS.EC2.csv'
YAML_File = 'AWS.EC2.yaml'
METRIC_HEADERS = ['metric_name', 'metric_unit', 'description']
lineadder = ['Minimum', 'Maximum', 'Average']

CODE_MAP = {
    'CPUUtilization': 'aws.ec2.cpu_utilization',
    'EBSIOBalance%': 'aws.ec2.ebs_io_balance%',
    'CPUCreditUsage': 'aws.ec2.cpu_credit_usage',
    'CPUCreditBalance': 'aws.ec2.cpu_credit_balance',
    'CPUSurplusCreditBalance': 'aws.ec2.cpu_surplus_credit_balance',
    'CPUSurplusCreditsCharged': 'aws.ec2.cpu_surplus_credits_charged',
    'EBSReadOps': 'aws.ec2.ebs_read_ops',
    'EBSWriteOps': 'aws.ec2.ebs_write_ops',
    'EBSWriteBytes': 'aws.ec2.ebs_write_bytes',
    'EBSReadBytes': 'aws.ec2.ebs_read_bytes',
    'EBSIobalance%': 'aws.ec2.ebs_iobalance%',
    'EBSBytesbalance%': 'aws.ec2.ebs_byte_balance%'
}



class AWSEc2Extractor:
    def __init__(self, url):
        self.url = url
        self.content = ""
        self.aws_dict = {}
        self.aws_list = []

    def load_page(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            self.content = page.content

    def get_content(self):
        return self.content

    def process_content(self):
        soup = BeautifulSoup(res.text, 'html.parser')
        # match = soup.find('div', {'id': 'main-content'})
        # tbodyone = match.find('tbody')
        self.aws_dict = {'type': 'EC2', 'keys': []}
        matchone = soup.findAll('table')
        rows = matchone[0].findAll('tr')
        tableonerows = matchone[1].findAll('tr')
        tabletworows = matchone[2].findAll('tr')
        tablethreerows = matchone[3].findAll('tr')
        match = soup.find('table', id="w627aac21c19c15c11b5")
        matchrows = match.findAll('tr')
        tablefourrows = matchone[4].findAll('tr')
        table5 = matchone[5].findAll('tr')

        for i in rows:
            cols = i.findAll('td')
            if cols and len(cols) > 0:
                col = cols[0]
                ogmetric_name = col.text.strip()
                metric_name = 'aws.ec2.' + self.convertToSnakeCase(ogmetric_name)
                met_desc = ''
                met_unit = ''
                met_stats = ''
                if metric_name.startswith('cpu'):  # redo this
                    metric_name = metric_name.replace('cpu', 'cpu_')  # redo this
                if ogmetric_name in CODE_MAP.keys():
                    metric_name= CODE_MAP[ogmetric_name]
                coloftone = cols[1]
                secon = coloftone.findChildren('p')
                if secon and len(secon) > 0:
                    idx = 0
                    for u in secon:
                        descriptions = u.findAll(text=True)
                        var1 = ' '.join(descriptions)
                        var1 = var1.replace('\n', '')
                        var2 = ' '.join(var1.split())
                        # print(var2)
                        if var2 and idx == 0 and not var2.startswith('Units') and not var2.startswith('Statistics'):
                            met_desc = var2
                        elif var2.startswith('Units'):
                            met_unit = var2
                            if 'Count' not in met_unit:
                                met_unit = 'guage'
                            else:
                                met_unit = 'count'
                        elif var2.startswith('Statistics'):
                            met_stats = var2
                        else:
                            met_stats = ''
                        idx + idx + 1
                    self.add_to_list(self.aws_list, metric_name, met_unit, met_desc)

                    if met_stats:
                        self.add_to_list(self.aws_list, metric_name + "_min", met_unit, met_desc + "_min")
                        self.add_to_list(self.aws_list, metric_name + "_max", met_unit, met_desc + "_max")
                        self.add_to_list(self.aws_list, metric_name + "_avg", met_unit, met_desc + "_avg")

                    # print(metric_name+" : ",met_desc," : "+met_unit)

                # print(metric_name)
        for e in matchrows:
            colsthree = e.findAll('td')
            if colsthree and len(colsthree) > 0:
                met_unitone = ''
                met_descone = ''
                colthree = colsthree[0]
                ogmetricthree_name = colthree.text.strip()
                metric_namethree = 'aws.ec2.' + self.convertToSnakeCase(ogmetricthree_name) # redo this
                    # print(metric_namethree)
                # print(metric_namethree)
                if ogmetricthree_name in CODE_MAP.keys():
                    metric_namethree = CODE_MAP[ogmetricthree_name]
                coloftthree = colsthree[1]
                seconthree = coloftthree.findChildren('p')
                if seconthree and len(seconthree) > 0:
                    idx = 0
                    for z in seconthree:
                        descriptionsthree = z.findAll(text=True)
                        varz = ' '.join(descriptionsthree)
                        varz = varz.replace('\n', '')
                        vary = ' '.join(varz.split())
                        # print(var2)
                        if vary and idx == 0 and not vary.startswith('Units') and not vary.startswith('Statistics'):
                            met_descone = vary
                        elif vary.startswith('Units'):
                            met_unitone = vary
                            if 'Count' not in met_unitone:
                                met_unitone = 'guage'
                            else:
                                met_unitone = 'count'
                        idx + idx + 1
                    self.add_to_list(self.aws_list, metric_namethree, met_unitone, met_descone)

        for j in tabletworows:
            colstwo = j.findAll('td')
            if colstwo and len(colstwo) > 0:
                met_desctwo = ''
                met_units2 = ''
                met_stats2 = ''
                coltwo = colstwo[0]
                ogmetrictwo_name = coltwo.text.strip()
                metric_nametwo = 'aws.ec2.' + self.convertToSnakeCase(ogmetrictwo_name)
                #print(CODE_MAP.keys())
                #print(ogmetrictwo_name)
                #break
                if ogmetrictwo_name in CODE_MAP.keys():

                    metric_nametwo = CODE_MAP[ogmetrictwo_name]
                # print(metric_nametwo)
                colofttwo = colstwo[1]
                secontwo = colofttwo.findChildren('p')
                idx = 0
                if secontwo and len(secontwo) > 0:

                    for o in secontwo:
                        descriptionsthwo = o.findAll(text=True)
                        varh = ' '.join(descriptionsthwo)
                        varh = varh.replace('\n', '')
                        vara = ' '.join(varh.split())
                        # print(var2)
                        if vara and idx == 0 and not vara.startswith('Units') and not vara.startswith('Statistics'):
                            met_desctwo = vara
                        elif vara.startswith('Units'):
                            met_units2 = vara
                            if 'Count' not in met_units2:
                                met_units2 = 'guage'
                            else:
                                met_units2 = 'count'
                        elif 'statistic' in vara:
                            met_stats2 = vara
                        idx = idx + 1

                    self.add_to_list(self.aws_list, metric_nametwo, met_units2, met_desctwo)
                    if met_stats2:
                        self.add_to_list(self.aws_list, metric_nametwo + "_min", met_units2, met_desctwo + "_min")
                        self.add_to_list(self.aws_list, metric_nametwo + "_max", met_units2, met_desctwo + "_max")
                        self.add_to_list(self.aws_list, metric_nametwo + "_avg", met_units2, met_desctwo + "_avg")


        for w in tablethreerows:
            colsfour = w.findAll('td')
            if colsfour and len(colsfour) > 0:
                met_descone4 = ''
                met_unitone4 = ''
                colfour = colsfour[0]
                ogmetricfour_name = colfour.text.strip()
                metric_namefour = 'aws.ec2.' + self.convertToSnakeCase(ogmetricfour_name)
                if metric_namefour.startswith('cpu'):  # redo this
                    metric_namefour = metric_namefour.replace('cpu', 'cpu_')  # redo this
                # print(metric_namefour)
                if ogmetricfour_name in CODE_MAP.keys():
                    metric_namefour = CODE_MAP[ogmetricfour_name]
                colofour = colsfour[1]
                secon4 = colofour.findChildren('p')
                if secon4 and len(secon4) > 0:
                    idx = 0
                    for b in secon4:
                        descriptions4 = b.findAll(text=True)
                        vare = ' '.join(descriptions4)
                        vare = vare.replace('\n', '')
                        vart = ' '.join(vare.split())
                        # print(var2)
                        if vart and idx == 0 and not vart.startswith('Units'):
                            met_descone4 = vart
                        elif vart.startswith('Units'):
                            met_unitone4 = vart
                            if 'Count' not in met_unitone4:
                                met_unitone4 = 'guage'
                            else:
                                met_unitone4 = 'count'
                        idx + idx + 1
                    self.add_to_list(self.aws_list, metric_namefour, met_unitone4, met_descone4)
        for s in tablefourrows:
            colsfive = s.findAll('td')
            if colsfive and len(colsfive) > 0:
                met_desconefive = ''
                met_unitonefive = ''
                met_statsone = ''
                colfive = colsfive[0]
                ogmetricfive_name = colfive.text.strip()
                metric_namefive = 'aws.ec2.' + self.convertToSnakeCase(ogmetricfive_name)
                if metric_namefive.startswith('cpu'):  # redo this
                    metric_namefive = metric_namefive.replace('cpu', 'cpu_')  # redo this
                if ogmetricfive_name in CODE_MAP.keys():
                    metric_namefive = CODE_MAP[ogmetricfive_name]
                # print(metric_namefive)
                coloftfive = colsfive[1]
                seconfive = coloftfive.findChildren('p')
                if seconfive and len(seconfive) > 0:
                    idx = 0
                    for q in seconfive:
                        descriptionsfive = q.findAll(text=True)
                        varq = ' '.join(descriptionsfive)
                        varq = varq.replace('\n', '')
                        varr = ' '.join(varq.split())
                        # print(var2)
                        if varr and idx == 0 and not varr.startswith('Units'):
                            met_desconefive = varr
                        elif varr.startswith('Units'):
                            met_unitonefive = varr
                            if 'Count' not in met_unitonefive:
                                met_unitonefive = 'guage'
                            else:
                                met_unitonefive = 'count'
                        elif 'statistics' in varr:
                            met_statsone = varr
                        idx + idx + 1
                    self.add_to_list(self.aws_list, metric_namefive, met_unitonefive, met_desconefive)
                    if met_statsone:
                        self.add_to_list(self.aws_list, metric_namefive + "_min", met_unitonefive,
                                         met_desconefive + "_min")
                        self.add_to_list(self.aws_list, metric_namefive + "_max", met_unitonefive,
                                         met_desconefive + "_max")
                        self.add_to_list(self.aws_list, metric_namefive + "_avg", met_unitonefive,
                                         met_desconefive + "_avg")
        for d in table5[1:]:
            colssix = d.findAll('td')
            if colssix and len(colssix) > 0:
                met_desconesix = ''
                met_statsonesix = ''
                met_unitonesix = ''
            colsix = colssix[0]
            ogmetricsix_name = colsix.text.strip()
            metric_namesix = 'aws.ec2.' + self.convertToSnakeCase(ogmetricsix_name)
            coloftsix = colssix[1]
            seconsix = coloftsix.findChildren('p')
            if seconsix and len(seconsix) > 0:
                idx = 0
                for p in seconsix:
                    descriptionssix = p.findAll(text=True)
                    varp = ' '.join(descriptionssix)
                    varp = varp.replace('\n', '')
                    var = ' '.join(varp.split())
                    # print(var2)
                    if var and idx == 0 and not var.startswith('Units'):
                        met_desconesix = varr
                    elif var.startswith('Units'):
                        met_unitonesix = varr
                    elif var.startwith('Statistics:'):
                        met_statsonesix = varr
                    idx + idx + 1
                self.add_to_list(self.aws_list, metric_namesix, met_unitonesix, met_desconesix)
                if met_statsonesix:
                    self.add_to_list(self.aws_list, metric_namesix + "_min", met_unitonesix,
                                     met_desconefive + "_min")
                    self.add_to_list(self.aws_list, metric_namesix + "_max", met_unitonesix,
                                     met_desconefive + "_max")
                    self.add_to_list(self.aws_list, metric_namesix + "_avg", met_unitonesix,
                                     met_desconefive + "_avg")

    def generate_csv(self):

        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(METRIC_HEADERS)
            writer.writerows(self.aws_list)

    def generate_yaml(self):

        #print(self.aws_dict)
        with open('AWS_ELB.yaml', 'w') as outfile:
            yaml.dump([self.aws_dict], outfile, default_flow_style=False)

    @staticmethod
    def add_to_list(aws_list, metric_name, met_units, description):

        print(metric_name, "||", met_units, "||", description, )
        aws_list.append([metric_name, met_units, "", "", "", description, "", "ec2", ""])

    @staticmethod
    def snake_case(input_string):

        if input_string:
            return re.sub(r'(?<!^)(?=[A-Z])', '_', input_string).lower()
        else:
            return input_string

    @staticmethod
    def convertToSnakeCase(name):
        s1 = re.sub('(.^_)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


if __name__ == "__main__":
    extractor = AWSEc2Extractor('https://docs.aws.amazon.com/AmazonS3/latest/userguide/metrics-dimensions.html')
    extractor.load_page()
    extractor.process_content()
    extractor.generate_yaml()
    extractor.generate_csv()

