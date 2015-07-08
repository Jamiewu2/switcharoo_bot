import praw
import re
import time
#import signal
import json
import sys
class Roo():
	#static visited set here probably
	match_urls = re.compile(ur'(https?:\/\/)?([\da-z\.-]+)?reddit\.com([\/\w \.-]*)?comments([\/\w \.-?]*)*\/?', re.UNICODE)
	r = praw.Reddit(user_agent = "test script by someone")
	def __init__(self, url, author):
		self.url = self.getURLfromString(url, 0, len(url)) #passed in url
		self.author = author
		self.submission = r.get_submission(self.getTruncURL(url))
		self.next = None
		self.actualURL = None #where the Roo actually is
		self.commentAuthor = None #author of the comment, for reasons
		self.notRightAuthor = False
		self.notRightComment = False
		self.noContext = False 
		self.nextNoContext = False
		self.nextNotRightComment = False
		self.nextNotRightPost = False
		tmp = self.getNext()
		if tmp:
			self.commentAuthor, self.actualURL, self.next = tmp #url
			if not self.commentAuthor == self.author:
				print self.author
				print self.commentAuthor
				self.notRightAuthor = True
		else:
			self.actualURL = self.url
			self.next = None
		self.nextsubmission = None
		if self.next:
			self.nextsubmission = r.get_submission(self.getTruncURL(self.next))

		#self.setFlags()
	def getNext(self):
		if self.next is None:
			comment = None
			if not len(self.submission.comments) == 0:
				comment = self.submission.comments[0]
			result = self.checkComment(comment)
			if result:
				return result
			else: #TODO store all valid posts and return the best one rather than the first valid post
				self.notRightComment = True
				if comment:
					result = self.checkParent(comment)
				# print "parent result"
				# print result
				if result:
					return result
				result = self.checkSubmission()
				# print "submission result"
				# print result
				if result:
					return result
				comments = praw.helpers.flatten_tree(self.submission.comments)
				for comment in comments:
					if type(comment) == praw.objects.MoreComments:
						print "moreComments Object: this is not good"
						print sys.stderr, "moreComments Object: this is not good"
						continue
					result = self.checkComment(comment)
					if result:
						return result
						#next comment text
				return None
		else:
			return self.next
	
	def getURL(self):
		if self.getTruncURL(self.url) == self.getTruncURL(self.actualURL):
			return self.url
		else:
			return self.actualURL
			
	def setFlags(self, nextRoo):
		try:
			self.url.index("?")
		except ValueError:
			self.noContext = True
		if not (self.getTruncURL(self.next) == nextRoo.getTruncURL(nextRoo.actualURL) or self.getTruncURL(self.next) == nextRoo.getTruncURL(nextRoo.url)):
			self.nextNotRightPost = True
		if self.next:
			try:
				self.next.index("?")
			except ValueError:
				self.nextNoContext = True
			#next author checking to be implemented here
			if len(self.nextsubmission.comments) == 0 or not self.checkComment(self.nextsubmission.comments[0], nextRoo.author):
				self.nextNotRightComment = True
			if self.nextsubmission.author == nextRoo.author:
				self.nextNotRightComment = False
		else:
			print "no next RIP"
			
	def checkComment(self, comment, author=None):
		if not author:
			author = self.author
		if not comment:
			return None
		result = self.searchURL(comment.body)
		# print "checkComment Result"
		# print result
		
		#it seems that checking a comment's author calls reddit? This makes this extremely slow
		if result and comment.author == author:
			return comment.author, comment.permalink, result
		elif comment.author == author: #needs to be changed to search for all comments first before this
			return comment.author, comment.permalink, None
		elif result: #if valid link based on sanity checks. This if statement needs some work.
			return comment.author, comment.permalink, result
		return None
			
	def searchURL(self, str):
		result = Roo.match_urls.search(str)

		if result:
			return self.getURLfromString(str, result.start(), result.end() )
		return None
	
	def getURLfromString(self, str, start, end):
		beginning = 0
		url = str[start:end]
		try:
			beginning = url.index("reddit.com") + 10
		except ValueError:
			pass
			#print "NoContextError: 'reddit.com' not found in "+ url
		return "https://www.reddit.com"+url[beginning:]
		
	def getTruncURL(self, url):
		if not url:
			return None
		start = 0
		try:
			start = url.index("reddit.com") + 10
		except ValueError:
			print "IndexError: 'reddit.com' not found in "+ url
		try:
			url = url[:url.index("?")]
		except ValueError:
			pass
			#print "NoContextError: '?' not found in "+ url
		return "https://www.reddit.com"+url[start:]
			
	def checkParent(self, comment):
		parent = r.get_info(thing_id = comment.parent_id)
		if type(parent) == praw.objects.Comment:
			return self.checkComment(parent)
		return None
		
	def checkSubmission(self):
		result = self.searchURL(self.submission.selftext)
		if result and self.submission.author == self.author:
			return self.submission.author, self.submission.url, self.searchURL(self.submission.selftext)
		return None

# def sliceURL(url):
	# start = 0
	# error = None
	# try:
		# start = url.index("reddit.com") + 10
	# except ValueError:
		# print "IndexError: 'reddit.com' not found in "+ url
	# try:
		# url = url[:url.index("?")]
	# except ValueError:
		# print "IndexError: '?' not found in "+ url
		# error = "No Context"
	# return "https://www.reddit.com"+url[start:], error

# def getURL(str, start, end):
	# url = str[start:end]
	# url = sliceURL(url)
	# return url		
def createURLinNew(prev_prev_sub):
	msg = "https://www.reddit.com/r/switcharoo/new"
	if prev_prev_sub:
		msg+="?&after=t3_"+prev_prev_sub.id
	return msg

def createMessage(msg, msg_exists):
	tmp = ""
	if msg_exists:
		tmp+= """  
Also, """
	else:
		tmp+= "Hello! "
	tmp += msg.replace("\t", "")
	return tmp
	


	
f = open('already_done.json')
data = json.load(f)
already_done = data
f2 = open('userpass.json')
user_pass = json.load(f2)
username = user_pass["user"]
password = user_pass["pass"]

try:
	#match_urls = re.compile(ur'(https?:\/\/)?([\da-z\.-]+)?reddit\.com([\/\w \.-]*)?comments([\/\w \.-?]*)*\/?', re.UNICODE)
	user_agent= "Switcharoo Bot by Jamie Wu"
	r = praw.Reddit(user_agent = user_agent)
	r.login(username, password)
	s = r.get_subreddit("switcharoo")
	#sub_new = s.get_new(limit=None)
	limit = 25
	prev_start_submission = None
	while 1:
		sub_new = s.get_new(limit=limit)
		#sub_new = s.get_new(limit=limit, params={"after" : "t3_3b136w"})
		# print s
		# print sub_new
		prev_roo = None #the one thats processed, sorry about the var names
		curr_roo = None #the one after
		prev_sub = None
		prev_prev_sub = None
	#	already_done = set()
		last_msg_time = None
		process_list = list(sub_new) #sorta defeats the purpose of a generator
		if not prev_start_submission:
			prev_start_submission = process_list[0]
		elif prev_start_submission == process_list[0]:
			time.sleep(300)
			print "Same start"
			continue
		else:
			prev_start_submission = process_list[0]
		for submission in process_list:

			msg = ""
			msg_exists = False
			if not submission.link_flair_text: #non meta post
				#print submission.author
				curr_roo = None
				try:
					curr_roo = Roo(submission.url, submission.author)
				except praw.errors.Forbidden as e:
					print e
					print "'"+ str(submission)+ "' is Forbidden: skipping"
					prev_roo = None
					continue
				if prev_roo:
					prev_roo.setFlags(curr_roo) #set flags of current
					print prev_sub #current submission being processed
					if prev_roo.notRightComment:
						tmp = """It seems that your Roo link is not correct. Most of the time (almost all of the time) this occurs because you linked to the parent comment (the comment above the Roo) instead of your post directly.  
						Your Roo link is actually [Here](%s).  
						Please include context instead of directly linking to the parent by appending "?context=x" to the link where x is the number of parent comments needed to understand the context of the Roo. 
						""" % (prev_roo.actualURL)
						msg += createMessage(tmp, msg_exists)
						#print "not right comment"
						msg_exists = True
					elif prev_roo.noContext:
						#print "no Context"
						tmp = """It seems that your Roo does not contain context.  
						Please include context by appending "?context=x" to the link where x is the number of parent comments needed to understand the context of the Roo.
						"""
						msg += createMessage(tmp, msg_exists)
						msg_exists = True
						
					if prev_roo.nextNotRightPost:
						#print "Not Correct: '%s' instead of '%s'" % (prev_roo.next, curr_roo.url) 
						#print str(prev_sub) +' --> ' + str(submission)
						print prev_roo.next
						print curr_roo.url
						tmp = """It seems that your link to the next Roo in the chain is not the correct post.  
						It should be linked [Here](%s). Please add the appropriate context if it is doesn't exist.  
						""" % (curr_roo.getURL())
						msg += createMessage(tmp, msg_exists)
						msg_exists = True

						#r.send_message("switcharoo_bot", "test", msg)
						#time.sleep(1800)
						#print time.clock()
						#prev_sub.add_comment('')

					elif prev_roo.nextNotRightComment:
						tmp = """It seems that that your link to the next Roo in the chain is not pointing to the correct location. Most of the time (almost all of the time) this occurs because your Roo links to their Roo's parent comment (the comment above the Roo) instead of the Roo directly.  
						It should be pointing [Here](%s). Please include context by appending "?context=x" to the link where x is the number of parent comments needed to understand the context of the Roo.
						""" % (curr_roo.getURL()) #think this works, might not
						msg += createMessage(tmp, msg_exists)
						msg_exists = True
					elif prev_roo.nextNoContext:
						tmp = """It seems that that your link to the next Roo in the chain is correct. However, it does not contain context.  
						Please include context by appending "?context=x" to the link where x is the number of parent comments needed to understand the context of the Roo.
						"""
						if not curr_roo.noContext and not curr_roo.notRightComment:
							tmp += "It should look something like [This](%s)." % curr_roo.getURL()
						msg += createMessage(tmp, msg_exists)
						msg_exists = True
					if not prev_roo.next:
						msg = """Hello! It seems that your Roo has been deleted or your link does not point to a comment.  
						I'm not exactly sure what you can do but the next link in the chain is [Here](%s).  
						""" % (curr_roo.getURL()) #override message
						msg_exists = True
					if prev_roo.getTruncURL(prev_roo.url) == curr_roo.getTruncURL(curr_roo.url):
						msg = """Hello! It seems that your Roo is the same as the next Roo.  
						I'm not exactly sure how that happened but it probably means your Roo got deleted.  
						""" #override message
						msg_exists = True
					if not curr_roo.next: #if next is not a Roo, don't print a message
						msg_exists = False
						#continue
						
					if prev_roo.notRightAuthor:
						msg += """\n\nIt seems you are not the Roo poster. If the problem is something that you cannot change yourself, please refer the poster to this thread.
						"""
						print "Not Right Author"
					if msg_exists:
						msg += """  
Check [This](%s) link to see the ordering of your Roo.  
						  
						*I am an unofficial bot. I might be wrong. Reddit Formatting is Hard* """ % createURLinNew(prev_prev_sub)
						if not prev_sub.id in already_done:
							#already_done.append(prev_sub.id)
							print msg
							# response = raw_input("Is this correct? (Y/N) ")
							# if response.lower() == 'y':
							save_post = True
							try:
								prev_sub.add_comment(msg)
							except praw.errors.APIException as e:
								print e
								save_post = False
							if save_post:
								time.sleep(600)
								already_done.append(prev_sub.id)
		#					process_list.append((prev_sub, msg))
		
							#r.send_message("switcharoo_bot","test2", msg )
							#time.sleep(700)
					print '\n'
				prev_prev_sub = prev_sub
				prev_roo = curr_roo
				prev_sub = submission
		with open("already_done.json", "w") as outfile:
			json.dump(already_done, outfile)
		time.sleep(300)
#		limit += 10
except:
	e = sys.exc_info()[0]
	print e
	raise
finally:
	with open("already_done.json", "w") as outfile:
		json.dump(already_done, outfile)
		
		