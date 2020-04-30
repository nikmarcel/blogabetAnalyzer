from __future__										import 	print_function
import  time
import 	datetime

from 	bet_markets    								import  set_market_and_bet

from 	bs4 										import 	BeautifulSoup

from 	selenium.webdriver 							import 	Chrome
from    selenium.webdriver.support.wait     		import 	WebDriverWait
from    selenium.webdriver.chrome.options   		import 	Options
from 	selenium.webdriver.common.keys 				import 	Keys
from 	selenium.webdriver.common.by 				import 	By
from 	selenium.webdriver.support 					import 	expected_conditions as EC



class Blogabet(object):
	email 		=	''
	password 	=	''
	driver 		=	None

	logged_in 	=	False
	
	def __init__(self, email, password):
		self.email  	=	email
		self.password  	=	password

		self.driver 	=	self.get_driver()


	def get_driver(self):
		options 	= 	Options()
		options.add_argument('--headless')
		
		return Chrome(executable_path='chromedriver.exe', chrome_options=options)


	def blogabet_login(self):

		#	Login info
		email 		=	self.email
		password	=	self.password	

		self.driver.get('https://blogabet.com/')

		#	Login 
		login_button	=	'.//*[contains(text(), "LOG IN")]'
		WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, login_button))).click()

		login_form 		=	WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.CLASS_NAME, "form-horizontal")))	
		
		time.sleep(0.6)
		print('Login into blogabet...')
		time.sleep(0.6)
		login_form.find_elements_by_tag_name('input')[0].send_keys(email)
		time.sleep(0.6)
		login_form.find_elements_by_tag_name('input')[1].send_keys(password + Keys.TAB + Keys.RETURN)
		print('Login done')

		self.logged_in 	=	True
		time.sleep(3)
		



	def go_to_tipster_page(self, tipster):
		try:
			self.driver.get('https://{}.blogabet.com/'.format(tipster))

			try:
				WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Win rate")]')))
				return True
			except:
				if 'Blog not found' in driver.page_source:
					raise Exception('Blog not found for tipster: {}'.format(tipster))
				else:
					raise Exception('Could not get tipster page')

		except Exception as e:
			raise Exception(e)


	def scrape_tipster(self, tipster):
		#	Scrape tipster stats from its blog page. Method returns a dict with stats
		if not self.logged_in:
			self.blogabet_login()

		driver 	=	self.driver

		tipster_dict 	=	{'name':tipster}
		self.go_to_tipster_page(tipster)

		tipster_dict['n_picks']		=	driver.find_element_by_id('header-picks').get_attribute('innerHTML').strip()
		tipster_dict['profit']		=	driver.find_element_by_id('header-profit').get_attribute('innerHTML').strip()
		tipster_dict['yield']		=	driver.find_element_by_id('header-yield').get_attribute('innerHTML').strip()
		tipster_dict['n_followers']	=	driver.find_element_by_id('header-followers').get_attribute('innerHTML').strip()
	
	                              
		WebDriverWait(driver,50).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Blog menu")]'))).click()

		options_menu 	=	WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "modal-body blog-menu")]')))
		time.sleep(1)

		#	Entramos en el menú de estadísticas
		options_menu.find_elements_by_tag_name('a')[1].click()

		stats_categories 	=	['SPORTS', 'STAKES', 'BOOKIES', 'ODDS RANGE']
		for sc in stats_categories:
			#	Comprobamos si el menú esta desplegado
			collapse 		=	WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "{}")]'.format(sc)))).find_element_by_xpath('../../..').find_element_by_id('collapse{}alltime'.format(sc.lower().replace(' ', '_')))
			collapse_class	=	collapse.get_attribute('class')

			table 			=	collapse.find_element_by_tag_name('table')

			sc_dicts		=	[]											
			table_headers 	=	table.find_elements_by_tag_name('th')		#	encabezados de la tabla
			regs 			=	table.find_elements_by_tag_name('tr')[1:]	#	cada uno de los registros de la tabla

			for r in regs:
				cols 			=	[]
				col_0 	=	r.find_element_by_tag_name('td').get_attribute('innerHTML').replace('\n','')[28:].strip()
				if 'Bet365' in col_0: col_0 = 'Bet365'
				cols.append(col_0)
				for col in r.find_elements_by_tag_name('td')[1:]:
					try:
						col = 	col.find_element_by_tag_name('span').get_attribute('innerHTML').strip()
					except:
						col = 	col.get_attribute('innerHTML').strip()

					cols.append(col)

				ths 	=	[]
				sc_dict	=	{}											#	diccionario para almacenar cada registro de la tabla
				for th in table_headers:
					sc_dict[th.get_attribute('innerHTML').strip().lower().replace(' ', '_').replace('.','').replace('stakes', 'stake').replace('sports', 'sport').replace('bookies', 'bookie')] 	=	cols[table_headers.index(th)] 
			
				sc_dicts.append(sc_dict)

			tipster_dict[sc.lower()]	=	sc_dicts
			
		return tipster_dict

			 

	def get_last_pick_in_feed(self, my_tipsters=True):
		#	Si my_tipsters = False, obtiene los picks del feed general de blogabet, en vez de aquellos de los tipsters a los que seguimos
		if my_tipsters:
			WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "My tipsters")]'))).click()

		time.sleep(2)

		media_list_xpath	=	'.//*[contains(@class, "media-list")]'

		#	Elementos html correspondientes a los picks
		picks_in_feed		=	WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, media_list_xpath))).find_elements_by_tag_name('li')
		try:
			last_pick_in_feed 	= 	self.get_pick_from_html(picks_in_feed[0])
		except Exception as e:
			raise(e)

		return last_pick_in_feed


	def get_picks_in_feed(self, my_tipsters=True):
		#	El parámetro opcional 'my_tipsters' indica si queremos tomar los picks de los tipsters a los
		#	que seguimos o del feed general de blogabet
		#	Pinchamos en 'my tipsters'
		if my_tipsters:
			WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "My tipsters")]'))).click()
			time.sleep(2)

		picks_in_feed 		=	[]
		media_list_xpath	=	'.//*[contains(@class, "media-list")]'
		picks_in_feed_elem	=	WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, media_list_xpath))).find_elements_by_tag_name('li')

		for p in picks_in_feed_elem:
			try:
				picks_in_feed.append(get_pick_from_html(p)) 	
			except Exception as e:
				#print(e)
				pass

		return picks_in_feed


	def get_pick_from_html(self, elem):
		#	Recibe el elemento <li> en el que se encuentra el pick del feed y forma el objeto
		pick 	=	{}

		soup 	=	BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')

		if 'Click here to see the pick' in soup:
			#	Pinchamos en 'here' y scrapeamos el pick 
			return None

		pick['url']		=	soup.find('a', {'class':'report enable-tooltip'})['data-url']
		pick['tipster']	=	pick['url'].split('.')[0].split('//')[1]
		
		if soup.find('i', {'class':'fa-plus-square'}):
			pick['type']=	'combo_pick'
			return pick
		
		pick['match']	=	soup.find('a', {'href':pick['url']}).text.replace(' - ',' v ')

		pick_odds 		=	soup.find('div', {'class':'pick-line'}).text
		pick['pick']	=	pick_odds.split('@')[0].strip()
		pick['odds']	=	pick_odds.split('@')[1].strip()
		pick['stake']	=	soup.find('span', {'class':'label label-default'}).text.strip()
		pick['booker']	=	soup.find('a', {'class':'label label-primary'}).text.strip()

		type_kickoff	=	soup.findAll('small', {'class':'text-muted'})[1].text.strip()

		pick['type']	=	type_kickoff.split('/')[0].strip() + ' - ' + type_kickoff.split('/')[1].strip()
		pick['kickoff']	=	type_kickoff.split('/')[2].strip().replace('Kick off: ','')
		pick['isLive']	=	('Livebet' in pick['type'])

		pick['placed_stake']	=	'not_set'

		pick['date']	=	datetime.datetime.now().replace(microsecond=0)

		try:
			pick['market']	=	''
			pick['bet']		=	''
			pick 			=	set_market_and_bet(pick)
			
			return pick
		
		except:
			return pick
			

	def compare_picks(self, p, p_):
		#	Boolean. Check 'url' attribute from pick to tell whter they are the same
		return p['url'] == p_['url']


	def print_pick(self, p):
		try:
			to_print 	=	'''-----------------------------------------------------------------------------------------------------------\nMATCH: {}	\nPICK: {}	\t 	MARKET: {} - BET: {} \nStake: {} (placed_stake: {})	Odds: {} \t isLive: {} \t Tipster: {}\n-----------------------------------------------------------------------------------------------------------'''.format(p['match'], p['pick'], p['market'], p['bet'], p['stake'], p['placed_stake'], p['odds'], p['isLive'], p['tipster'])
			print(to_print)
		except Exception as e:
			print('Could not print pick ({})'.format(e))


	def watch_blogabet_feed(self):
		#	Watch blogabet feed and 
		
		driver 	=	self.driver
		
		if not self.logged_in:
			self.blogabet_login()

		#	We get the last pck in our feed to compare
		pd 	= 	self.get_last_pick_in_feed(my_tipsters=True)
		print('Last pick in feed: ')
		self.print_pick(pd)
		#	We set a refresh time to watch the feed
		refresh_time 	= 	20
		print('Watching blogabet feed...')
		
		while True:
			pd_ 	=	self.get_last_pick_in_feed(my_tipsters=True)		
			#	If most recent pick changes...
			if not self.compare_picks(pd, pd_): 
				print('Watch a new pick in feed ({})'.format(datetime.datetime.now().replace(microsecond=0)))
				#	Here, we can set some action to do with new pick
				self.print_pick(pd_)
				#	Return a dict with pick information
				#return pd_

			time.sleep(refresh_time)
			driver.refresh()

