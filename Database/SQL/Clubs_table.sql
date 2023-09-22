CREATE TABLE Clubs(
	club_id int PRIMARY KEY,
	stadium_id int  NULL,
	manager_id int  NULL,
	club_name varchar(50) NOT NULL,
	name_abbreviation char(3) --3 letters match name for the club


)