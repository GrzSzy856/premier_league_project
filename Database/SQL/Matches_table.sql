CREATE TABLE Matches (
	match_id int PRIMARY KEY,
	match_date date,
	match_time time,
	home_team_id int NOT NULL,
	away_team_id int NOT NULL,
	home_team_goals tinyint CHECK (home_team_goals >= 0),
	away_team_goals tinyint CHECK (away_team_goals >= 0),
	referee_id int NOT NULL,
	matchday_number tinyint CHECK (matchday_number BETWEEN 0 and 38)

	CONSTRAINT FK_Matches_Referees FOREIGN KEY (referee_id) REFERENCES Referees(referee_id)



)