# importing modules
import scrapy
from StringParser.StringParser import Parser
# regex
import re

# instantiating custom module.
# this is used for a very particular task caused by bad HTML in the page.
parser = Parser('NFC','ascii','utf8')

# creating Spider class
class Spider(scrapy.Spider):
    # assigning name. this will be used to call the spider in shell command.
    name = 'spider'

    # listing initial URLs
    start_urls = [
        'http://www.healthvermont.gov/health-professionals-systems/board-medical-practice/board-actions'
    ]

    # creating function that will be called once for every link in start_urls
    def parse(self,response):
        # selecting table element from root. this is where the data is.
        table = response.css('div.content table.data-table')
        # selecting all rows
        rows = table.css('tbody tr')

        # iterating over rows
        for row in rows:
            # get all cells in row
            cells = row.css('td')

            # parsing cells
            name = cells[0].css('::text').extract_first()
            license = cells[1].css('::text').extract_first()
            info = parser.unescape_html(self.extractWithRegex(cells[2],'<\/a>.*-\s(.*)\s-','*'))
            id = parser.normalizer(f"{name.split(',')[0]}-{license}-{'-'.join(info.split(' '))}").upper() # creates unique IDs that are used to compare w database
            date = self.extractWithRegex(cells[2],'-\s(\d{0,3}\/\d{0,3}\/\d{0,5})','*')
            date = parser.convert_to_datetime(date,'%m/%d/%Y')

            # creating object to be passed down to pipelines
            object = {
                'name':name,
                'id':id,
                'license':license,
                'year':self.extractWithRegex(cells[3],'(\d{4})','::text'),
                'date':date,
                'info':info,
                'action':cells[2].css('a::text').extract_first().strip(),
                'url':cells[2].css('a::attr(href)').extract_first(),
            }

            # remember to yield and not return!!!!
            yield object

    #########################################################
    ################## UTILS ################################
    #########################################################
    def extractWithRegex(self,sel,pat,qry):
        try:
            value = re.search(pat,sel.css(qry).extract_first()).group(1)
        except:
            value = 'N/A'

        return value
