# Movie Theater Web App
A simple movie theater database that keeps track of movies and movie theater capacity per each movie. The user is able to
add/remove movies, add/remove reservations, add/remove theaters and add/remove movie showtimes. The database is a MariaDB and 
is maintained through phpmyadmin. The app was developed with python/flask and html/css. 

## OUTLINE:
### Theaters: Records the details of available movie theaters showing a particular movie
- theaterID: int(11), auto_increment, not Null, PK
- screenName: VARCHAR(255), Not Null
- Relationship: A M:M relationship between entity Theater and Movies. There are
many movies and there are many theater screens that can play the movies.
### Movies: Records the details of available movies
- movieID: int(11), auto_increment, not NULL, PK
- theaterID: int(11), FK
- movieTitle: varchar(255), Not Null
- movieRating: varchar(255), Not Null
- movieGenre: varchar(255), Not Null
- Relationship: A M:M relationship with Movies and Showtimes. There are many
movies and each movie as 2 show times.
### Showtimes: Records the details of movie show times for available theatres
- showtimeID: int(11), auto_increment, not Null, PK
- movieID: int(11), Not Null, FK
- movieTitle2: varchar(255), Not Null, FK
- start_time: varchar(255), Not Null
- movie_day: varchar(255), not Null, FK
- seats_available: Boolean, Not Null, Default 0 ---(ie, yes)
- movieTitle2: varchar(255), Not Null
- Relationship: 1:M - A relationship between Reservations and Showtimes is 1:M
because a reservation can only be for one showtime. However, a showtime can have
many reservations.
### Reservations: Records the data about a ticket reservation for a particular movie.
- reservationID: int(11), auto_increment, Not Null, PK
- showtimeID: int(11), Not Null, FK
- num_of_adults: int(11)
- num_of_children: int(11)
- num_of_seniors: int(11)
- cust_Name: varchar(255)
- cust_Email: varchar(255)
- Relationship: 1:M – A relationship between Reservations and Showtimes is 1:M
because a reservation can only be for one showtime. However, a showtime can have
many reservations.
