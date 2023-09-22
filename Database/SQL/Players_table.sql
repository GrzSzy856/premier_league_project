CREATE TABLE Players(
	player_id int PRIMARY KEY,
	club_id int NOT NULL,
	player_name varchar(50),
	player_surname varchar(50),
	nationality varchar(50),
	position varchar(3),
	birth_date date,
	contract_expiration date,
	height tinyint, --height in cm
	better_foot varchar(5) CHECK(better_foot IN ('Left','Right','Both')),
	market_value_in_m_eur float

	CONSTRAINT FK_Players_Clubs FOREIGN KEY (club_id) REFERENCES Clubs(club_id)
)