from flask import (Flask, session, flash, get_flashed_messages, jsonify, render_template, redirect, request)
from flask_session import Session
from tempfile import mkdtemp
import twitter
import tweepy
import os

#http://docs.tweepy.org/en/v3.5.0/auth_tutorial.html

# Configure application
app = Flask(__name__)
app.secret_key="SECRET_KEY"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_FILE_DIR']=mkdtemp()
app.config['SESSION_TYPE']='filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

print(str(os.environ.get("consumer_key")))
print(str(os.environ.get("consumer_secret")))
print(str(os.environ.get("access_token_key")))
print(str(os.environ.get("access_token_secret")))

consumer_key= str(os.environ.get("consumer_key"))
consumer_secret=str(os.environ.get("consumer_secret"))
api = twitter.Api(consumer_key = consumer_key,
					consumer_secret= consumer_secret,
					access_token_key=str(os.environ.get("access_token_key")),
					access_token_secret=str(os.environ.get("access_token_secret")))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback="https://twittertapi.herokuapp.com/twitter_login/twitter/authorized")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/twitter_login/twitter/authorized")
def call_back():
	if session.get("username"):
		session.clear()
	
	access = auth.get_access_token(request.args.get("oauth_verifier"))
	
	auth.set_access_token(access[0],access[1])
	tweepy_api = tweepy.API(auth)
	user = tweepy_api.verify_credentials()
	session['username'] = user.screen_name
	
	# session.set('request_token', auth.request_token)
	
	return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
	session.clear()

	return redirect("/")

@app.route("/login",methods=["GET"])
def login():
	
	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError:
		print("ERROR - Failed to get Token")
		return apology("AUTHENTICATION FAILED, REGENERATE KEYS",400)	
	
	return redirect(redirect_url)

@app.route("/", methods=["GET"])
def index():
	if session.get("username"):
		tweepy_api = tweepy.API(auth)
		statuses = tweepy_api.home_timeline()
		return render_template("index.html", statuses=statuses)

	return render_template("index.html")

@app.route("/search", methods=["GET","POST"])
def search():
	if request.method == "GET":
		return render_template("search.html")
	else:
		if not request.form.get("user"):
			return apology("No Username given", 400)
		name = request.form.get("user")
		
		statuses = api.GetUserTimeline(screen_name = name)
		return render_template("search.html", tweets = statuses)
	return redirect("/search")

def apology(message:str, code = 400):

	return render_template("apology.html", err_code = code, message = message)



if __name__ == "__main__":
	import os
	port = int(os.environ.get("PORT",80))

	app.run(host="0.0.0.0",port=port)
