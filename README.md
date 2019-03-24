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
Use of the information provided by this script does not provide any guarantee of the accuracy or correctness of the information.
Nor does the author provide any guarantee of the functionality of this script. Users should be exercise their own caution.
Users should take particular care when funds issue revised forms to CDS website. 
See the MIT License for more legal-ese that protects me from getting sued.

# Dependencies

| Tool           | Tested Version |
| -------------- | -------------- |
| python         | 3.7.0          |

See: https://www.python.org/downloads/

pip install xlrd
pip install beautifulsoup4

| Library        | Tested Version |
| -------------- | -------------- |
| xlrd           | 1.1.0          |
| beautifulsoup4 | 4.7.1          |

# Behavior

This script will download the required year's tax information forms to the local execution directory to act as a cache.
Distribution data is output to STDOUT in CSV format.

Example:

Gather T3 info for CUSIP 12345678 for tax year 2019
```
$ python scrape_cds_tax_breakdown.py --cusip 12345678 --year 2019
```

```
Gather T3 info for CUSIP 12345678 and 87654321 for tax years 2018, 2019
```
$ python scrape_cds_tax_breakdown.py --cusip 12345678 87654321 --year 2018 2019
```