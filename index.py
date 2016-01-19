import os
import logging
import wsgiref.handlers
import datetime
import random
import math
import string
import urllib
#pip install pygeoip

# gi = pygeoip.GeoIP("GeoIP.dat")
# gi.country_code_by_addr()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template 
from google.appengine.ext import db

from gaesessions import get_current_session

from google.appengine.api import urlfetch

# NumScenarios=7	#Change this as I see fit, not including demo scenario
# NumTrials=8

################################################################################
################################################################################
######################## Data Classes for Database #############################
################################################################################
################################################################################

#Different classes in datastore

# class User(db.Model):
# 	account =			db.StringProperty()
# 	usernum =			db.IntegerProperty()
# 	browser =			db.StringProperty()
# 	Completion_Code =	db.IntegerProperty()
# 	created =			db.DateTimeProperty(auto_now=True)
# 	sex =				db.IntegerProperty()
# 	ethnicity =			db.IntegerProperty()
# 	race =				db.IntegerProperty()

# class ScenarioData(db.Model):
# 	user  =				db.ReferenceProperty(User)
# 	usernum =			db.IntegerProperty()
# 	account =			db.StringProperty()
# 	created =			db.DateTimeProperty(auto_now=True)
# 	sc =				db.IntegerProperty()
# 	conditionWithin =	db.IntegerProperty()
# 	data =				db.ListProperty(int)
# 	strength =			db.ListProperty(int)
# 	duration =			db.ListProperty(int)

class SurveyData(db.Model):
	Gender = 			db.IntegerProperty()
	MOOCBefore = 		db.IntegerProperty()
	BrowserLanguage = 	db.StringProperty()
	# DetectIP = 			db.StringProperty()

# class pygeoip.GeoIP(GeoIP.dat,flags=0,cache=True)
	# country_code_by_addr();


#This stores the current number of participants who have ever taken the study.
#see https://developers.google.com/appengine/docs/python/datastore/transactions
#could also use get_or_insert
#https://developers.google.com/appengine/docs/python/datastore/modelclass#Model_get_or_insert
class NumOfUsers(db.Model):
	counter = db.IntegerProperty(default=0)

#Increments NumOfUsers ensuring strong consistency in the datastore
@db.transactional
def create_or_increment_NumOfUsers():
	obj = NumOfUsers.get_by_key_name('NumOfUsers', read_policy=db.STRONG_CONSISTENCY)
	if not obj:	
		obj = NumOfUsers(key_name='NumOfUsers')
	obj.counter += 1
	x=obj.counter
	obj.put()
	return(x)

################################################################################
################################################################################
########################### From Book Don't Touch ##############################
################################################################################
################################################################################
# One line had to be updated for Python 2.7
# http://stackoverflow.com/questions/16004135/python-gae-assert-typedata-is-stringtype-write-argument-must-be-string
# A helper to do the rendering and to add the necessary
# variables for the _base.htm template

def doRender(handler, tname = 'index.htm', values = { }):
	temp = os.path.join(
		os.path.dirname(__file__),
		'templates/' + tname)
	if not os.path.isfile(temp):
		return False
	# Make a copy of the dictionary and add the path and session
	newval = dict(values)
	newval['path'] = handler.request.path
	# handler.session = Session()
	# if 'username' in handler.session:
	# newval['username'] = handler.session['username']

	outstr = template.render(temp, newval)
	handler.response.out.write(unicode(outstr))  #### Updated for Python 2.7
	return True

################################################################################
################################################################################
################### Create Data to Show to Participants ########################
################################################################################
################################################################################

# Creates data with differing contingencies, depending on conditionWithin

# def createData(contingency):
# 	if contingency==0:
# 		data = [1,1,1,1,4,4,4,4]    # deltaP = 1, powPC = 1 (DEMO)
# 	if contingency==1:
# 		data = [2,2,2,2,3,3,3,4]    # deltaP = -.75, powPC = -1
# 	if contingency==2:
# 		data = [1,2,2,2,3,3,3,4]    # deltaP = -.5, powPC = -.67
# 	if contingency==3:
# 		data = [1,2,2,2,3,3,4,4]    # deltaP = -.25, powPC = -.5
# 	if contingency==4:
# 		data = [1,1,2,2,3,3,4,4]    # deltaP = 0, powPC = 0
# 	if contingency==5:
# 		data = [1,1,1,2,3,3,4,4]    # deltaP = .25, powPC = .5
# 	if contingency==6:
# 		data = [1,1,1,2,3,4,4,4]    # deltaP = .5, powPC = .67
# 	if contingency==7:
# 		data = [1,1,1,1,3,4,4,4]    # deltaP = .75, powPC = 1

# 	return random.sample(data,len(data))

################################################################################
################################################################################
###################### Handlers for Individual Pages ###########################
################################################################################
################################################################################

################################################################################
############################## ScenarioHandler #################################
################################################################################
		
# class ScenarioHandler(webapp.RequestHandler):
# 	def get(self):
# 		session = get_current_session()
# 		sc = session.get('scenario')
# 		usernum = session.get('usernum')
# 		conditionWithin = session.get('conditionWithin')
# 		data = createData(conditionWithin[sc])
		
# 		doRender(
# 			self, 'scenario.htm', 
# 			{'usernum': usernum,
# 			'sc': sc,
# 			'conditionWithin': conditionWithin,
# 			'data': data})
		
# 	def post(self):
# 		self.session=get_current_session()
# 		sc=self.session['scenario']
# 		data=self.request.get('data')
# 		data=map(int,data.split(","))
# 		strength=self.request.get('strength')
# 		strength=map(int,strength.split(","))
# 		duration=self.request.get('duration')
# 		duration=map(int,duration.split(","))
		
# 		newinput = ScenarioData(user=self.session['userkey'],
# 			usernum=self.session['usernum'], 
# 			account=self.session['username'],
# 			conditionWithin=self.session['conditionWithin'][sc],
# 			sc=sc,
# 			data=data,
# 			strength=strength,
# 			duration=duration);

# 		newinput.put()
		
# 		logging.info('Data Added')
# 		self.session['scenario']+=1
# 		scenario=self.session['scenario']
	
# 		if scenario==1: #Instructions after trial scenario
# 			doRender(self,'instructions1.htm')
# 		if scenario > 1 and scenario<=NumScenarios: #Real experiment
# 			doRender(self,'newscenario.htm',{'sc':sc})
# 		if scenario > NumScenarios: #Done with scenarios, move on to demographics.
# 			doRender(self, 'demographics.htm')


################################################################################
############################## Small Handlers ##################################
################################################################################

# class LogoutHandler(webapp.RequestHandler):
# 	def get(self):
# 		self.session=get_current_session()
# 		self.session.__delitem__(self, 'username')
# 		self.session.__delitem__(self, 'userkey')
# 		self.session.__delitem__(self, 'sc')
	
# 		doRender(self, 'index.htm')


# class MainHandler(webapp.RequestHandler):
# 	def get(self):
# 		if doRender(self,self.request.path) :
# 			return
	
# 		doRender(self,'index.htm')

# class DataHandler(webapp.RequestHandler):
# 	def get(self):
# 		doRender(
# 			self, 
# 			'datalogin.htm',
# 			{})

# 	def post(self):
# 		password=self.request.get('password')
# 		if password == "kws10":
# 			que=db.Query(ScenarioData)
# 			que.order("usernum").order("sc")
# 			d=que.fetch(limit=10000)
	
# 			que2=db.Query(User)
# 			que2.order("usernum")
# 			u=que2.fetch(limit=10000)
	
# 			doRender(
# 				self, 
# 				'data.htm',
# 				{'d': d, 'u': u, 'NumScenarios':NumScenarios})
		
# 		else:
# 			doRender(
# 				self, 
# 				'dataloginfail.htm',
# 				{})
		
# class QualifyHandler(webapp.RequestHandler):
# 	def get(self):
# 		self.session=get_current_session()
# 		doRender(
# 			self, 
# 			'qualify.htm')
	
# class DNQHandler(webapp.RequestHandler):
# 	def get(self):
# 		doRender(self, 'do_not_qualify.htm')    

# class Instructions1Handler(webapp.RequestHandler):
# 	def get(self):
# 		doRender(self, 'instructions1.htm')

# class Instructions2Handler(webapp.RequestHandler):
# 	def get(self):
# 		doRender(self, 'instructions2.htm')

# class InstructionHandler(webapp.RequestHandler):
# 	def get(self):
# 		session = get_current_session()
# 		scenario = session.get('scenario')
# 		if scenario==0: #Instructions before trial scenario
# 			doRender(self, 'instruction.htm')
# 		else:
# 			doRender(self, 'instructions.htm')

########### FOR EVELYN

class EvelynHandler(webapp.RequestHandler): # Handler for the whole page
	def get(self): # what happens with a Get request
		self.session=get_current_session()
		doRender(self, 'evelynspage.htm') # this displays the page
	def post(self): #what happens when i want to get stuff out of the page
		self.session=get_current_session()
		Gender = int(self.request.get('gender')) # converts from string in form to int to store in DB
		MOOCBefore = int(self.request.get('moocBefore'))
		BrowserLanguage = str(self.request.get('language'))
		# DetectIP = str(self.request.get('getip'))

		newInput = SurveyData(Gender=Gender, #I'm equating database name with variable (list all here!)
			MOOCBefore = MOOCBefore,
			BrowserLanguage = BrowserLanguage);
			# DetectIP = DetectIP),
		newInput.put() #this takes all of the above data and puts it in a single line


	
################################################################################
############################ DemographicsHandler ###############################
################################################################################
# This handler is a bit confusing - it has all this code to calculate the
# correct race number

# class DemographicsHandler(webapp.RequestHandler):
#   def get(self):
# 	doRender(self, 'demographics.htm')
	
#   def post(self):
# 	self.session=get_current_session()
	
# 	sex=int(self.request.get('sex'))
# 	ethnicity=int(self.request.get('ethnicity'))
# 	racel=map(int,self.request.get_all('race')) #race list
# 	logging.info("race list")   
# 	logging.info(racel)

# 	rl1=int(1 in racel)
# 	rl2=int(2 in racel)
# 	rl3=int(3 in racel)
# 	rl4=int(4 in racel)
# 	rl5=int(5 in racel)
# 	rl6=int(6 in racel)
# 	rl7=int(7 in racel)
	
# #Amer Indian, Asian, Native Hawaiian, Black, White, More than one, No Report
# #race_num is a number corresponding to a single race AmerInd (1) - White(5)
# 	race_num=rl1*1+rl2*2+rl3*3+rl4*4+rl5*5
	
# 	morethanonerace=0
# 	for i in [rl1,rl2,rl3,rl4,rl5]:
# 		if i==1:
# 			morethanonerace+=1
# 	if rl6==1:
# 		morethanonerace+=2
		
# 	if rl7==1:  #dont want to report
# 		race=7
# 	elif morethanonerace>1:
# 		race=6
# 	elif morethanonerace==1:
# 		race=race_num
	
# 	logging.info("race")
# 	logging.info(race)
	
	
	
# 	Completion_Code=random.randint(10000000,99999999)
	
	
# 	obj = User.get(self.session['userkey'])
# 	obj.Completion_Code = Completion_Code
# 	#obj.BonusList = self.session['BonusList']
# 	obj.sex = sex
# 	obj.ethnicity = ethnicity
# 	obj.race = race
# 	obj.put()
	
	
# 	self.session.__delitem__('usernum')
# 	self.session.__delitem__('username')
# 	self.session.__delitem__('userkey')
# 	self.session.__delitem__('scenario')
# 	self.session.__delitem__('browser')
# 	self.session.__delitem__('conditionWithin')
	
# 	doRender(self, 'logout.htm', {'Completion_Code': Completion_Code, })
	
	
# ################################################################################
# ############################### MturkIDHandler #################################
# ################################################################################
	  
# class MturkIDHandler(webapp.RequestHandler):
# 	def get(self):
# 		doRender(self, 'mturkid.htm')

# 	def post(self):
# 		ID=self.request.get('ID')
# 		acct=ID ##no reason

# 		form_fields = {
# 			"ID": ID,
# 			"ClassOfStudies": 200,
# 			"StudyNumber": 1
# 			}
# 		form_data = urllib.urlencode(form_fields)
# 		url="http://www.mturk-qualify.appspot.com"
# 		result = urlfetch.fetch(url=url,
# 								payload=form_data,
# 								method=urlfetch.POST,
# 								headers={'Content-Type': 'application/x-www-form-urlencoded'})

# 		if result.content=="0":
# 			#self.response.out.write("ID is in global database.")
# 			doRender(self, 'do_not_qualify.htm')

# 		elif result.content=="1":
# 			# Check if the user already exists
# 			que = db.Query(User).filter('account =',ID)
# 			results = que.fetch(limit=1)

# 			# Allows username 'ben' to pass. You can't just allow other names to pass - it needs to be changed in http://www.mturk-qualify.appspot.com too
# 			if (len(results) > 0) & (ID!='ben'):   
# 				doRender(self, 'do_not_qualify.htm')

# 			# If user is qualified (http://www.mturk-qualify.appspot.com returns 1)
# 			else:
# 				#Create the User object and log the user in.
# 				usernum = create_or_increment_NumOfUsers()

# 			##############################################################################
# 			######## Condition randomizer and stimulus selection based on usernum ########
# 			##############################################################################
			
# 			# Within-subjects randomization, demo scenario is always [2] = covariation of 0
			
# 				conditionWithin = [0] + random.sample([1,2,3,4,5,6,7],NumScenarios)

# 			##############################################################################
# 			######## Get browser #########################################################      
# 			##############################################################################

# 				browser=self.request.get('browser')

# 			##############################################################################
# 			##############################################################################      
			
# 				newuser = User(account=acct, 
# 							usernum=usernum,
# 							browser=browser);
			
# 				# dataframe modeling, but I'm not sure what exactly
# 				userkey = newuser.put()
# 				# this stores the new user in the datastore
# 				newuser.put()

# 				# store these variables in the session
# 				self.session=get_current_session() #initialize sessions
# 				self.session['usernum']			= usernum
# 				self.session['username']		= acct
# 				self.session['browser']			= browser
# 				self.session['userkey']			= userkey
# 				#self.session['conditionBetween']= conditionBetween
# 				self.session['conditionWithin']	= conditionWithin
# 				self.session['scenario']		= 0
# 				doRender(self, 'qualify.htm')

# 		# If got no response back from http://www.mturk-qualify.appspot.com
# 		else:
# 			error="The server is going slowly. Please reload and try again."
# 			self.response.out.write(result.content)

	  
################################################################################
############################### MainAppLoop ####################################
################################################################################ 

application = webapp.WSGIApplication([
	# ('/scenario', ScenarioHandler),
	# ('/logout', LogoutHandler),
	# ('/data', DataHandler),
	# ('/qualify', QualifyHandler),
	# ('/do_not_qualify', DNQHandler),
	# ('/instructions1', Instructions1Handler),
	# ('/instructions2', Instructions2Handler),
	# ('/instruction', InstructionHandler),
	# ('/demographics', DemographicsHandler),
	# ('/mturkid', MturkIDHandler),   #this goes to the same default page
	('/evelyn', EvelynHandler),
	('/.*', EvelynHandler)],  #default page
	# ('/.*',      MturkIDHandler)],  #default page
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
