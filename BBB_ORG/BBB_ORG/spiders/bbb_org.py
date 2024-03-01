import scrapy
import json
from ..BBB_FILE import bbb_sitemap_URLs


class BbbOrgSpider(scrapy.Spider):
    name = "bbb_orb"
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
        'X-API-Key': 'YOUR_API_KEY_HERE'  # Add your API key here
    }

    def start_requests(self):
        for url in bbb_sitemap_URLs:
            yield scrapy.Request(
                url=url,
                callback=self.parse_data,
                headers=self.headers,
            )

    def parse_data(self, response):
        response = response.replace(encoding='utf-8')

        script_text = response.xpath('//script[contains(text(),"window.__PRELOADED_STATE__")]/text()').get()
        if script_text[-1] == ';':
            script_text = script_text[:-1]
        script_text = script_text.replace('window.__PRELOADED_STATE__ = ', '').strip()
        json_row = json.loads(script_text)

        name = json_row['businessProfile']['names']['primary']
        full_address = json_row['businessProfile']['location']['formattedAddress']
        address = json_row['businessProfile']['location']['displayAddress']['addressLine1']
        city = json_row['businessProfile']['location']['displayAddress']['city']
        state = json_row['businessProfile']['location']['displayAddress']['stateCode']
        zip_code = json_row['businessProfile']['location']['displayAddress']['zipCode']
        phone1 = json_row['businessProfile']['contactInformation']['phoneNumber']
        phone2 = json_row['businessProfile']['contactInformation']['additionalPhoneNumbers']
        phone2 = phone2[0]['value'] if phone2 else None
        fax_number = json_row['businessProfile']['contactInformation']['additionalFaxNumbers']
        fax_number = fax_number[0]['value'] if fax_number else None
        yr_in_business = json_row['businessProfile']['orgDetails']['yearsInBusiness']
        category = json_row['businessProfile']['categories']['primaryCategoryName']
        try: website = json_row['businessProfile']['urls']['primary']
        except: website = None
        email1 = json_row['businessProfile']['contactInformation']['emailAddress']
        if email1: email1 = email1.replace('!~xK_bL!', '').replace('__at__', '@').replace('__dot__', '.')
        email2 = json_row['businessProfile']['contactInformation']['additionalEmailAddresses']
        email2 = email2[0]['value'] if email2 else None
        if email2: email2 = email2.replace('!~xK_bL!', '').replace('__at__', '@').replace('__dot__', '.')
        f_name = json_row['businessProfile']['contactInformation']['contacts']
        f_name = f_name[0]['name']['first'] if f_name else None
        l_name = json_row['businessProfile']['contactInformation']['contacts']
        l_name = l_name[0]['name']['last'] if l_name else None

        yield {
            'Company': name,
            'Full address': full_address,
            'Address': address,
            'City': city,
            'State': state,
            'Zip Code': zip_code,
            'First Name': f_name,
            'Last Name': l_name,
            'Phone': phone1,
            'Email': email1,
            'Fax': fax_number,
            'Alt Phones': phone2,
            'Alt Emails': email2,
            'Website': website,
            'Years in business': yr_in_business,
            'Category': category,
            'Link to Profile': response.url,
        }
