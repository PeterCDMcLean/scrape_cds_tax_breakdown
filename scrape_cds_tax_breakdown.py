'''
MIT License

Copyright (c) 2019 PeterCDMcLean

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
# Python Scraper for CDS Innovations Tax Breakdown Service

CDS Innovations provides a service which consolidates tax information for various mutual funds, ETFS, and other trusts/partnerships

Visit:
https://services.cds.ca/applications/taxforms/taxforms.nsf/Pages/-EN-LimitedPartnershipsandIncomeTrusts?Open

Users should read CDS Innovations Terms of Service:
https://services.cds.ca/applications/taxforms/taxforms.nsf/Pages/-EN-agree

This script allows uses to quickly aggregate T3-tax-form fund distribution information for given CUSIPs and Tax Years.
In my opinion, this script does not violate CDS Innovation terms of service as users are required to run this script
on their own and with no intermediate service or assistance. It's simply a more efficient way to collect the data.

# Warning!
Use of the information provided by this script does not provide any gaurentee of the accuracy or correctness of the information.
Nor does the author provide any gaurentee of the functionality of this script. Users should be exercise their own caution.
Users should take particular care when funds issue revised forms to CDS website. 

# Dependencies

Tool            Tested Version
python          3.7.0

pip install xlrd
pip install beautifulsoup4

Library          Tested Version
xlrd             1.1.0
beautifulsoup4   4.7.1

# Behavior

This script will download the required year's tax information forms to the local execution directory to act as a cache.
Distribution data is output to STDOUT in CSV format.

Example:

Gather T3 info for CUSIP 12345678 for tax year 2019
```
python scrape_cds_tax_breakdown.py --cusip 12345678 --year 2019
```

```
Gather T3 info for CUSIP 12345678 and 87654321 for tax years 2018, 2019
```
python scrape_cds_tax_breakdown.py --cusip 12345678 87654321 --year 2018 2019
```

'''
from mmap import mmap,ACCESS_READ
from xlrd import open_workbook
import argparse
import urllib.request
import urllib.parse
import os
from bs4 import BeautifulSoup
import sys
import tempfile
from pathlib import Path
import shutil
from collections import namedtuple
from datetime import datetime

csv_headers = [
	'Symbol',
	'CUSIP',
	'Total$ per unit',
	'Record date',
	'Payment date',
	'Total cash per unit',
	'Total non-cash per unit',
	'Total income per unit allocated',
	'Capital Gain',
	'Actual Amount Eligible Dividends',
	'Actual Amount Non-Eligible Dividends',
	'Foreign Business Income',
	'Foreign Non-Business Income',
	'Other Income (Investment Income)',
	'Return of Capital'
]

def aggregate(csv_list, years, cusips):
	for year in years:
		assert (year >= 2007 and year < 2025)
		cds_base_url = 'https://services.cds.ca/applications/taxforms/taxforms.nsf'
		cds_retreive_str = 'T3-' + str(year)
		cached_cds = Path(cds_retreive_str + '.html')
		try:
			cached_cds_abs = cached_cds.resolve(strict=True)
			cached_cds_file = open(cached_cds,"rb")
			print('Cached')
		except FileNotFoundError:
			print('Fetching')
			with urllib.request.urlopen(cds_base_url + '/PROCESSED-EN-?OpenView&Start=1&Count=3000&RestrictToCategory=' + cds_retreive_str) as response:
			   cached_cds_file = open(cached_cds,"wb+")
			   shutil.copyfileobj(response, cached_cds_file)
			   cached_cds_file.seek(0)


		soup = BeautifulSoup(cached_cds_file, 'html5lib')

		tables = soup.find_all('table')
		table = tables[5]

		#for child in table.recursiveChildGenerator():
		#	name = getattr(child, "name", None)
		#	if name is not None:
		#		print (name)
		#	elif not child.isspace(): # leaf node, don't print spaces
		#		print (child)

		rows = table.find_all('tr')
		headers = rows[0].find_all('td')

		cusip_column = -1;
		date_column = -1;
		form_column = -1;
		for i in range(0, len(headers)):
			if(headers[i].text.strip() == "Date"):
				date_column = i
			if(headers[i].text.strip() == "CUSIP"):
				cusip_column = i
			if(headers[i].text.strip() == "Form"):
				form_column = i

		assert (cusip_column != -1 and form_column != -1 and date_column != -1)

		#Remove headers
		rows.pop(0)

		cusip_lookup = dict()
		cusip_dates = dict()

		datestrf = '%m/%d/%Y %H:%M:%S'
		for tr in rows:
			cols = tr.find_all('td')
			date_cell = datetime.strptime(cols[date_column].find('span', {'class':'Date'}).text.strip(), datestrf)
			cusip_cell = cols[cusip_column].find('span', {'class':'Cusip'}).text.strip()
			href_cell = cols[form_column ].find('a', href=True, recursive=True)['href']
			if cusip_cell in cusip_lookup:
				#print('!!!!!!!!!!!DUPLICATE ENTRY!!!!!!!!!!!!' + cusip_cell)
				#print('Compare ' + date_cell.strftime(datestrf) + ' with ' + cusip_dates[cusip_cell].strftime(datestrf))
				if (date_cell > cusip_dates[cusip_cell]):
					#print('Chose ' + date_cell.strftime(datestrf) + ' ' + href_cell)
					cusip_lookup[cusip_cell] = cds_base_url + '/' + href_cell
					cusip_dates [cusip_cell] = date_cell
			else:
				cusip_lookup[cusip_cell] = cds_base_url + '/' + href_cell
				cusip_dates [cusip_cell] = date_cell
			#print('CUSIP ' + cusip + ' HREF ' + href)
		for cusip in cusips:
			try:
				print(cusip_lookup[cusip])

				xls_file = os.path.basename(urllib.parse.urlparse(cusip_lookup[cusip]).path)

				cached_xls = Path(xls_file)
				try:
					cached_xls_abs = cached_xls.resolve(strict=True)
					#cached_xls_file = open(cached_xls,"rb")
					print('Cached')
				except FileNotFoundError:
					print('Fetching')
					with urllib.request.urlopen(cusip_lookup[cusip]) as response:
					   cached_xls_file = open(cached_xls,"wb+")
					   shutil.copyfileobj(response, cached_xls_file)
					   cached_xls_file.close()
					   #cached_xls_file.seek(0)

				print(xls_file)

				wb = open_workbook(cached_xls)


				sheet = wb.sheet_by_index(0)

				symbol = sheet.cell(4,12).value

				for x in range(0, 14):
					col = 3+x;
					if sheet.cell(18,col).value == '':
						break;
					csv_row = list()
					csv_row.append(symbol                  );
					csv_row.append(cusip                   );
					csv_row.append(sheet.cell(18,col).value);
					csv_row.append(sheet.cell(19,col).value);
					csv_row.append(sheet.cell(20,col).value);
					csv_row.append(sheet.cell(21,col).value);
					csv_row.append(sheet.cell(22,col).value);
					csv_row.append(sheet.cell(23,col).value);
					csv_row.append(sheet.cell(24,col).value);
					csv_row.append(sheet.cell(25,col).value);
					csv_row.append(sheet.cell(26,col).value);
					csv_row.append(sheet.cell(27,col).value);
					csv_row.append(sheet.cell(28,col).value);
					csv_row.append(sheet.cell(29,col).value);
					csv_row.append(sheet.cell(31,col).value);
					csv_list.append(csv_row)
			except KeyError:
				print('CUSIP not found: ' + str(cusip))
	
	csv_list.sort(key=lambda csv_row: csv_row[4])

parser = argparse.ArgumentParser(description='Fetch and consolidate CUSIP distribution data')
parser.add_argument('--year', type=int, nargs='+', help='Tax year(s) to look up')
parser.add_argument('--cusip', type=str, nargs='+', help='CUSIP ID(s) to look up')

args = parser.parse_args()

csv_list=list()

aggregate(csv_list, args.year, args.cusip)

all_headers=''
for x in csv_headers:
	all_headers += x + ','
print(all_headers)
for x in csv_list:
	row = ''
	for y in x:
		if (isinstance(y, float)):
			row += '{0:f}'.format(y) + ','
		else:
			row += str(y) + ','
	print(row)
