from flask import Flask, render_template, flash
from flask import request, redirect
from flask import Markup
from db_connector.db_connector import connect_to_database, execute_query

app = Flask(__name__)
app.secret_key = "westcoastdevs"

@app.route('/')
def home():
	return render_template("index.html")


@app.route('/movies', methods=['POST', 'GET'])
def searchMovie():	
	db_connection = connect_to_database()
	if request.method== 'GET':
    		
		# This will pull movie times from db to the dropdown selection
		pullTime= "SELECT DISTINCT start_time FROM showtimes ORDER BY start_time ASC"
		allTimes = execute_query(db_connection, pullTime).fetchall()				   			 

		dropdown2 = request.args.get('timeVal', None)
		query2 = "SELECT showtimes.showtimeID, showtimes.movieTitle2, showtimes.movie_day, \
				theaters.screenName, movieGenre, movieRating, \
				IF (showtimes.seats_available, 'Yes', 'No'), movies.movieID \
				FROM movies \
				INNER JOIN showtimes ON movies.movieID = showtimes.movieID \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID \
				WHERE start_time ='{}'"
		queryVariable2 = query2.format(dropdown2)
		cursor2 = execute_query(db_connection, queryVariable2).fetchall()	
		timeData = [dict(showtimeID=row[0], movieTitle2=row[1], day=row[2], theaterName=row[3], \
				genreName=row[4], ratingType=row[5], soldOut=row[6], movieID=row[7]) for row in cursor2]

		# This will pull in movie titles from db to the dropdown selection
		pullMovie= "SELECT DISTINCT movieTitle FROM movies ORDER BY movieTitle ASC"
		allMovies = execute_query(db_connection, pullMovie).fetchall()		   			 
		
		dropdown = request.args.get('moviesVal', None)
		query = "SELECT showtimes.showtimeID, showtimes.start_time, showtimes.movie_day, theaters.screenName, movieGenre, movieRating, \
				IF (showtimes.seats_available, 'Yes', 'No'), movies.movieID \
				FROM movies \
				INNER JOIN showtimes ON movies.movieID = showtimes.movieID \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID \
				WHERE movieTitle ='{}'"
		queryVariable = query.format(dropdown)
		cursor = execute_query(db_connection, queryVariable).fetchall()		
		movieData = [dict(showtimeID=row[0], showTime=row[1], day=row[2], theaterName=row[3], \
				genreName=row[4], ratingType=row[5], soldOut=row[6], movieID=row[7]) for row in cursor]

		return render_template('search_Page.html', movieData = movieData, movieTitle = dropdown, allMovies = allMovies, \
								timeData = timeData, timeTitle=dropdown2, allTimes = allTimes)

	# If a selection is made on soldout movie - notify user to search again. 
	if request.method== 'POST':
		if request.form['showtimeID']:
			showtimeID = request.form['showtimeID']
			soldOut = request.form['soldOut']
			if soldOut == "No":		
				query3 = "INSERT INTO reservations (showtimeID) VALUES ('{0}')".format(showtimeID) 
				execute_query(db_connection, query3)
				return redirect('/reservations')

			elif soldOut =="Yes":
				flash("THAT MOVIE IS SOLD OUT - PLEASE SEARCH AGAIN!")
				return redirect('/movies')		
		else:
			return('No Queries Here')
	else:
		print("Something is wrong or it's not reading the post")

# Deletes reservation (Ticket reserve page)
@app.route('/deleteReserveTicket', methods=['POST'])
def	delete():
	db_connection = connect_to_database()		
	reservationID = request.form['reservationID']
	query = ("delete from reservations where reservationID= '{}'").format(reservationID)
	cursor=execute_query(db_connection, query).fetchall()

	return redirect('/movies')

@app.route('/reservations', methods=['POST', 'GET'])
def reservations():
	db_connection = connect_to_database()
	if request.method=='GET': 

		# Latest reservation query
		query = "SELECT reservations.reservationID, showtimes.movieTitle2, reservations.num_of_adults, \
				reservations.num_of_children, reservations.num_of_seniors \
				FROM showtimes \
				INNER JOIN reservations WHERE showtimes.showtimeID = reservations.showtimeID \
				ORDER BY reservations.reservationID DESC LIMIT 1;"

		# Get the latest movie from the latest reservation to display
		query2 = "SELECT showtimes.movieTitle2, showtimes.start_time, showtimes.movie_day \
				FROM showtimes \
				INNER JOIN reservations WHERE showtimes.showtimeID = reservations.showtimeID \
				ORDER BY reservations.reservationID DESC LIMIT 1;"
	
		result = execute_query(db_connection, query).fetchall()
		result2 = execute_query(db_connection, query2).fetchall()

		print('Reservation Part1 Added!')
		newNums=request.args.get('button3')
	
		return render_template("sale_Page.html", reserve=result, reserveMOV=result2)

	# Update the Reservation
	elif request.method =='POST':
		print("Updating Reservation!")
		reservationID = request.form['reservationID']
		movieTitle = request.form['movieTitle']
		num_of_adults = request.form['num_of_adults']
		num_of_children = request.form['num_of_children']
		num_of_seniors = request.form['num_of_seniors']

		query = "UPDATE reservations SET num_of_adults= '{0}', num_of_children= '{1}', num_of_seniors='{2}' \
				WHERE reservationID = '{3}'".format(num_of_adults, num_of_children, num_of_seniors, reservationID)
		execute_query(db_connection, query)
		return redirect('/checkout')	
	else:
		print('something went wrong')
		return render_template("sale_Page.html")

# Successfully added a reseration html page
@app.route('/addReservationSuccess')
def reservationSuccess():
	return render_template("addReservationSuccess.html")

# Checkout page
@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
	db_connection = connect_to_database()
	if request.method == 'GET':
		query = "SELECT reservations.reservationID, showtimes.movieTitle2, reservations.num_of_adults, \
				reservations.num_of_children,reservations.num_of_seniors, showtimes.start_time, showtimes.movie_day, theaters.screenName \
				FROM showtimes \
				INNER JOIN reservations ON showtimes.showtimeID = reservations.showtimeID \
				INNER JOIN movies ON showtimes.movieID = movies.movieID \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID \
				ORDER BY reservations.reservationID DESC LIMIT 1;"
		result = execute_query(db_connection, query).fetchall()
		return render_template("transaction_Page.html", checkout=result)
	
	# Update/Complete/Add to the reservation information
	if request.method == 'POST':
		print('FINISHING RESERVATION')
		reservationID = request.form['reservationID']
		cust_name = request.form['cust_name']
		cust_email = request.form['cust_email']

		query = "UPDATE reservations SET cust_name= '{0}', cust_email= '{1}' \
				WHERE reservationID = '{2}'".format(cust_name, cust_email, reservationID)
		execute_query(db_connection, query)
		return render_template("transaction_PageSuccess.html")

@app.route('/transaction_PageSuccess.html')
def transactionsSuccess():
	return render_template("transaction_PageSuccess.html")

# Deletes a movie (Admin page)
@app.route('/deleteMovieAdmin', methods=['POST'])
def	deleteMovieAdmin():
	db_connection = connect_to_database()	
	movieID = request.form['movieID']	
	query = ( "DELETE FROM movies WHERE movies.movieID='{}'").format(movieID)
	cursor=execute_query(db_connection, query).fetchall()
	
	if cursor == ():
		flash("Delete Successful!")	
	else:
		flash("Delete NOT Successful")		
		
	return redirect('/admin')

# Deletes a reservation (Admin page)
@app.route('/deleteReserveAdmin', methods=['POST'])
def	deleteReserveAdmin():
	db_connection = connect_to_database()	
	reservationID = request.form['reservationID']
	query = ("DELETE FROM reservations WHERE reservationID='{}'").format(reservationID)
	cursor=execute_query(db_connection, query).fetchall()

	if cursor == ():
		flash("Delete Successful!")	
	else:
		flash("Delete NOT Successful")	
	
	return redirect('/admin')

# Deletes a showtime (Admin page)
@app.route('/deleteShowtimeAdmin', methods=['POST'])
def	deleteShowtimeAdmin():
	db_connection = connect_to_database()		
	showtimeID = request.form['showtimeID']
	query = ("DELETE FROM showtimes WHERE showtimeID='{}'").format(showtimeID)
	cursor=execute_query(db_connection, query).fetchall()

	if cursor == ():
		flash("Delete Successful!")	
	else:
		flash("Delete NOT Successful")	
	return redirect('/admin')

# Deletes a theater (Admin page)
@app.route('/deleteTheaterAdmin', methods=['POST'])
def	deleteTheaterAdmin():
	db_connection = connect_to_database()		
	theaterID = request.form['theaterID']
	query = ("DELETE FROM theaters WHERE theaterID='{}'").format(theaterID)
	cursor=execute_query(db_connection, query).fetchall()

	if cursor == ():
		flash("Delete Successful!")	
	else:
		flash("Delete NOT Successful")	
	return redirect('/admin')

@app.route('/admin', methods=['POST', 'GET'])
def admin():
	print("Fetching and rendering people web page")
	db_connection = connect_to_database()
	if request.method =='GET':
    	# Get all of the reservation information for the various reservation ID's
		query = "SELECT reservations.reservationID, reservations.cust_Name, reservations.cust_Email, \
				showtimes.movieTitle2, showtimes.movie_day, showtimes.start_time, theaters.screenName, \
				reservations.num_of_adults, reservations.num_of_children, reservations.num_of_seniors, \
				IF (showtimes.seats_available, 'Yes', 'No') \
				FROM reservations \
				INNER JOIN showtimes ON reservations.showtimeID = showtimes.showtimeID \
				INNER JOIN movies ON showtimes.movieID = movies.movieID \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID \
				ORDER BY reservations.reservationID ASC;"
		result = execute_query(db_connection, query).fetchall()

		# Get all of the movie information from the database
		query2 = "SELECT movies.movieID, movies.movieTitle, movies.movieRating, movies.movieGenre, theaters.screenName \
				FROM movies \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID;" 
		result2 = execute_query(db_connection, query2).fetchall()
	
		# Get all of the showtime information from the database
		query3 = "SELECT showtimes.showtimeID, showtimes.movieTitle2, showtimes.start_time, showtimes.movie_day, \
				IF (showtimes.seats_available, 'No', 'Yes'), theaters.screenName \
				FROM showtimes \
				INNER JOIN movies ON showtimes.movieID = movies.movieID \
				INNER JOIN theaters ON movies.theaterID = theaters.theaterID;"
		result3 = execute_query(db_connection, query3).fetchall()
		
		# Get all of the the theaters from the database
		query4 = "SELECT * FROM theaters;"
		result4 = execute_query(db_connection, query4).fetchall()

		return render_template("adminPage.html", people=result, movies=result2, showtimes=result3, theaters=result4)

	else:
		print('goodbye, its not here')

	return render_template("adminPage.html")

### The following are the methods to add/delete entries by way of the Admin page ###

@app.route('/addTheater', methods=['POST', 'GET'])
def addTheater():
	db_connection = connect_to_database()
	if request.method =='POST': 
		screenName = request.form['screenName']

		query = "INSERT INTO theaters (screenName) VALUES ('%s')" % screenName
		data = screenName
		execute_query(db_connection, query)
		return render_template("addTheaterSuccess.html")

	else:
		return render_template("addTheater.html")

@app.route('/addTheaterSuccess')
def theaterSuccess():
	return render_template("addTheaterSuccess.html")

@app.route('/addMovie', methods=['POST', 'GET'])
def addMovie():
	db_connection = connect_to_database()
	if request.method == 'GET':
		query1 = 'SELECT screenName FROM theaters'
		result1 = execute_query(db_connection, query1).fetchall()

		return render_template('addMovie.html', screens=result1)

	# Add a new movie
	elif request.method =='POST': 
		movieTitle = request.form['movieTitle']
		movieGenre = request.form['movieGenre']
		movieRating = request.form['movieRating']
		screenName = request.form['screenName']
		# Insert movie info into database
		query = "INSERT INTO movies (movieTitle, movieGenre, movieRating, theaterID) VALUES ('{0}','{1}','{2}',\
				(SELECT theaterID FROM theaters WHERE screenName = ('{3}')))".format(movieTitle, movieGenre, movieRating, screenName)
		execute_query(db_connection, query)	
		print('Movie added!')

		return render_template("addMovieSuccess.html")
		
	return render_template("addMovie.html")

@app.route('/addMovieSuccess')
def movieSuccess():
	return render_template("addMovieSuccess.html")

@app.route('/addShowtime', methods=['POST', 'GET'])
def addShowtime():
	db_connection = connect_to_database()
	
	if request.method == 'GET':
		query1 = 'SELECT movieTitle FROM movies'
		result1 = execute_query(db_connection, query1).fetchall()
		return render_template('addShowtime.html', movies=result1)

	# Add a new showtime
	elif request.method =='POST': 
		movieTitle2 = request.form['movieTitle2']
		start_time = request.form['start_time']
		movie_day = request.form['movie_day']
		seats_available = request.form['seats_available']
		
		query = "INSERT INTO showtimes (movieID, movieTitle2, seats_available, start_time, movie_day) \
				VALUES ((SELECT movieID FROM movies WHERE movieTitle = '{0}'), '{1}', '{2}', '{3}', '{4}')".format(movieTitle2, \
				movieTitle2, seats_available, start_time, movie_day)
		data = (movieTitle2, movieTitle2, seats_available, start_time, movie_day)
		execute_query(db_connection, query)

		print('Movie added!')
		return render_template("addShowtimeSuccess.html")

	return render_template("addShowtime.html")

if __name__ == '__main__':
	# app.run(host='0.0.0.0')
	app.run(debug=True)

