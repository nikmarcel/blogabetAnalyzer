from __future__										import 	print_function
import  time
import 	datetime
import sys


from 	bet_markets    								import  set_market_and_bet

from 	bs4 										import 	BeautifulSoup
from 	pymongo 									import 	MongoClient

from 	selenium.webdriver 							import 	FirefoxOptions, Firefox
from    selenium.webdriver.support.wait     		import 	WebDriverWait
from    selenium.webdriver.chrome.options   		import 	Options
from 	selenium.webdriver.common.keys 				import 	Keys
from 	selenium.webdriver.common.by 				import 	By
from 	selenium.webdriver.support 					import 	expected_conditions as EC

import 	blogabet
from 	stats 										import 	Tipster



try:

	bb 	=	blogabet.Blogabet('punmuky007@gmail.com', 'bet12345')
	tipster_stats 	=	bb.scrape_tipster('georgebell22')
	print(tipster_stats)
	bb.driver.close()

except:
	bb.driver.close()