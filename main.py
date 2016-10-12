# import flask stuff
from flask import Flask,render_template,redirect,request,session,jsonify
from flaskext.mysql import MySQL
import bcrypt



# set up mysql connection here later
mysql=MySQL()
app=Flask(__name__)
# Add to the app (Flask Object) some config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
# the name of the database we want to connect to at the db server
app.config['MYSQL_DATABASE_DB'] = 'bawk'
# Where the mysql server is at
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
# use the mysql objects method "init_app" and pass it the flask object 
mysql.init_app(app)


app.secret_key='HSDG(#*&@(#&(JDKWJDWJJ89729837&*@&#*(jkhkja@*&'
conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def homepage():

	if 'username' in session:
		
		homepage_profile_pic="SELECT profile_pic FROM user WHERE username='%s'" % session['username']
		print homepage_profile_pic
		cursor.execute(homepage_profile_pic)
		homepage_profile_pic=cursor.fetchone()
		

		homepage_page_query="SELECT user.id,username,profile_pic,post_content,current_vote,date,posts.id FROM user INNER JOIN  posts ON user.id=posts.user_id WHERE username='%s' ORDER BY date DESC"%session['username']
		cursor.execute(homepage_page_query)
		homepage_page_query=cursor.fetchall()

		comment_page_query="SELECT user.id,username,profile_pic,post_content,current_vote,date FROM user INNER JOIN  comments ON user.id=comments.user_id "
		cursor.execute(comment_page_query)
		comment_page_query=cursor.fetchall()

		return render_template('homepage.html',
			homepage_profile_pic=homepage_profile_pic,
			comment_page_query=comment_page_query,
			homepage_page_query=homepage_page_query)
	else:
		return redirect('/?message=YouMustLogIn')
			


@app.route('/login')
def login():
	if request.args.get('message'):
		return render_template('login.html',
			message="Login failed")
	elif request.args.get('logout-message'):
		return render_template('login.html',
			message="You are now logged out")
	else:
		
		return render_template('login.html')

@app.route('/login_submit',methods=["POST"])
def login_submit():
	username=request.form['username']
	password=request.form['password'].encode('utf-8')
	user_sql="SELECT username,password,id FROM user WHERE username = '%s'" % request.form['username']
	cursor.execute(user_sql)
	
	result=cursor.fetchone()

	mysql_pass=result[1].encode('utf-8')
	mysql_id=result[2]
	# print mysql_id
	print mysql_pass
	print password
	print cursor
	if bcrypt.checkpw(password,mysql_pass):
   		session['username']=username
   		session['id']=mysql_id
   		print session['id']

		return redirect('/')
	else:
		return redirect('/login?message=failed')
	 
	# to check a hash against english

		
		


@app.route('/logout')
def logout(): 
	#nuke their session vars. this will end session which is what we use to let them into the portal
	session.clear()
	return redirect('/login?logout-message=LoggedOut')




@app.route('/register')
def register():
	if request.args.get('username'):
		return render_template('register.html',
		message="That username is already taken")
	elif request.args.get('password'):
		return render_template('register.html',
		message="Passwords do not match")

	else:

		return render_template('register.html')

@app.route('/register_submit',methods=['POST'])
def register_submit():
	# First check to see if username is already taken
	# this means a select statement
	check_username_query="SELECT * FROM user WHERE username = '%s'"%request.form['username']
	# print check_username_query
	cursor.execute(check_username_query)
	check_username_result=cursor.fetchone()
	if check_username_result is None:
		#no match. Insert
		email=request.form['email']
		username=request.form['username']
		password=request.form['password'].encode('utf-8')
		confirm_password=request.form['confirm-password'].encode('utf-8')
		hashed_password=bcrypt.hashpw(password,bcrypt.gensalt())
		profile_pic = request.files['profile_pic']
		# image.save passes where we want to save it which is image.filename
		profile_pic.save('static/images/'+profile_pic.filename)
		profile_pic_path=profile_pic.filename
		bio= request.form['bio']
		print password
		print confirm_password
		if (password==confirm_password):
			user_insert_query="INSERT INTO user VALUES(DEFAULT,'"+email+"','"+username+"','"+hashed_password+"','"+profile_pic_path+"','"+bio+"')"
			cursor.execute(user_insert_query)
			conn.commit()
			user_sql="SELECT username,password,id FROM user WHERE username='"+username+"'"
			result=cursor.execute(user_sql)
			session['username']=username
			session['id']=user_sql[2]
			print session['id']
   			
			return redirect('/')
		else:
			
			return redirect('/register?password=nomatch')


	else:
		return redirect('/register?username=taken')
		print check_username_result
		return "done"

	# Second if it is talen send them back to the registration page with a message
	# Second B, if its not taken then insert user into mysql

# Route for posting off of the homepage



@app.route('/home_post_submit',methods=["POST"])
def post_submit():
	post_content=request.form['post_content']
	get_user_id_query="SELECT id FROM user WHERE username='%s'"%session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result=cursor.fetchone()
	user_id=get_user_id_result[0]

	insert_post_query="INSERT INTO posts (post_content,user_id,current_vote) VALUES ('"+post_content+"',"+str(user_id)+",0)"
	cursor.execute(insert_post_query)
	conn.commit()

	return redirect('/')

@app.route('/dashboard')
def dashboard():
	if 'username' in session:
		dashboard_page_query="SELECT user.id,username,profile_pic,post_content,current_vote,date FROM user INNER JOIN  posts ON user.id=posts.user_id ORDER BY date DESC"
		cursor.execute(dashboard_page_query)
		dashboard_page_query=cursor.fetchall()

		return render_template('dashboard.html',
			dashboard_page_query=dashboard_page_query)
	else:
		return redirect('/admin?message=YouMustLogIn')
	return render_template('dashboard.html')


@app.route('/dashboard_post_submit',methods=["POST"])
def dashboard_submit():
	post_content=request.form['post_content']
	get_user_id_query="SELECT id FROM user WHERE username='%s'"%session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result=cursor.fetchone()
	user_id=get_user_id_result[0]

	insert_post_query="INSERT INTO posts (post_content,user_id,current_vote) VALUES ('"+post_content+"',"+str(user_id)+",0)"
	cursor.execute(insert_post_query)
	conn.commit()
	return redirect('/dashboard')

@app.route('/post_comment',methods=["POST"])
def post_comment():
	post_content=request.form['post_content']
	get_user_id_query="SELECT id FROM user WHERE username='%s'"%session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result=cursor.fetchone()
	user_id=get_user_id_result[0]

	insert_post_query="INSERT INTO comments (post_content,user_id,current_vote) VALUES ('"+post_content+"',"+str(user_id)+",0)"
	cursor.execute(insert_post_query)
	conn.commit()
	return redirect('/')

@app.route('/process_vote', methods=['POST'])
def process_vote():
	# check to see, has th euser voted on this particular item
	post_id = request.form['vid'] # the post they voted on. This came from jquery $.ajax
	vote_type = request.form['voteType']
	check_user_votes_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.user_id WHERE user.username = '%s' AND votes.post_id = '%s'" % (session['username'], post_id)
	# print check_user_votes_query
	cursor.execute(check_user_votes_query)
	check_user_votes_result = cursor.fetchone()

	# It's possible we get None back, becaues the user hsn't voted on this post
	if check_user_votes_result is None:
		# User hasn't voted. Insert.

		insert_user_vote_query = "INSERT INTO votes (post_id, user_id, vote_type) VALUES ('"+str(post_id)+"', '"+str(session['id'])+"', '"+str(vote_type)+"')"
		# print insert_user_vote_query
		cursor.execute(insert_user_vote_query)
		conn.commit()
		return jsonify("voteCounted")
	else:
		check_user_vote_direction_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.user_id WHERE user.username = '%s' AND votes.post_id = '%s' AND votes.vote_type = %s" % (session['username'], post_id, vote_type)
		cursor.execute(check_user_vote_direction_query)
		check_user_vote_direction_result = cursor.fetchone()
		if check_user_vote_direction_result is None:
			# User has voted, but not this direction. Update
			update_user_vote_query = "UPDATE votes SET vote_type = %s WHERE user_id = '%s' AND post_id = '%s'" % (vote_type, session['id'], post_id)
			cursor.execute(update_user_vote_query)
			conn.commit()
			return "voteChanged"
		else:
			# User has already voted this directino on this post. No dice.
			return "alreadyVoted"


@app.route('/profile/<username>')
def profile(username):
	
		
		profile_page_pic="SELECT profile_pic FROM user WHERE username='%s'"%username
		cursor.execute(profile_page_pic)
		profile_page_pic=cursor.fetchone()
		
		
		profile_page_name="SELECT username FROM user WHERE username='%s'"%username
		cursor.execute(profile_page_name)
		profile_page_name=cursor.fetchone()

		profile_page_id="SELECT id FROM user WHERE username='%s'"%username
		cursor.execute(profile_page_id)
		profile_page_id=cursor.fetchone()
		followed=profile_page_id[0]
		print followed
		
		

		profile_page_query="SELECT user.id,username,profile_pic,post_content,current_vote,date,posts.id FROM user INNER JOIN  posts ON user.id=posts.user_id WHERE username='%s' ORDER BY date DESC"%username
		cursor.execute(profile_page_query)
		profile_page_query=cursor.fetchall()

		
		followed_already="SELECT f.follower_id FROM friends f WHERE f.followee_id='%s'"%session['id']
		cursor.execute(followed_already)
		followed_already=cursor.fetchone()

		profile_comment_query="SELECT user.id,username,profile_pic,post_content,current_vote,date FROM user INNER JOIN  comments ON user.id=comments.user_id "
		cursor.execute(profile_comment_query)
		profile_comment_query=cursor.fetchall()

		return render_template('profile.html',
			profile_page_name=profile_page_name,
			profile_page_pic=profile_page_pic,
			profile_comment_query=profile_comment_query,
			profile_page_query=profile_page_query,
			followed_already=followed_already)
	
	
			
	


@app.route('/follow_requests/<username>',methods=['GET','POST'])
def follow_requests(username):

	if 'username' in session:
		followed="SELECT id FROM user WHERE username='%s'"%username
		cursor.execute(followed)
		followed=cursor.fetchone()
		followed_id=followed[0]
		print followed_id
		followers= "INSERT INTO friends VALUES (DEFAULT,'%s','%s')"%(followed_id,session['id'])
		cursor.execute(followers)
		conn.commit()
		return redirect('/profile/%s'%username)
	else:
		return redirect('/profile/%s'%username)


@app.route('/delete_follower/<username>',methods=['POST'])
def delete_follower(username):
	if 'username' in session:
		followed="SELECT id FROM user WHERE username='%s'"%username
		cursor.execute(followed)
		followed=cursor.fetchone()
		followed_id=followed[0]
		unfollow="DELETE FROM friends WHERE follower_id='%s'"%followed_id
		cursor.execute(unfollow)
		conn.commit()
		return redirect('/profile/%s'%username)
	else:
		return redirect('/profile/%s'%username)

@app.route('/search',methods=["POST"])
def search():
	searched_name = request.form['searched-name']

	print searched_name
	return redirect('/profile/%s'%searched_name)


if __name__=="__main__":
	app.run(debug=True)






