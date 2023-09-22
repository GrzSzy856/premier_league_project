CREATE TABLE Stadiums(
	stadium_id int PRIMARY KEY,
	stadium_name varchar(60),
	city varchar(50),
	capacity smallint CHECK(capacity > 0)

)
