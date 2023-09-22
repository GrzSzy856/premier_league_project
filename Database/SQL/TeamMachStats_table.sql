CREATE TABLE TeamMatchStats(
	match_id int NOT NULL,
	club_id int NOT NULL,
	is_home bit NOT NULL CHECK(is_home IN (0,1)),
	shots_on_goal tinyint CHECK(shots_on_goal >= 0),
	total_shots tinyint CHECK(total_shots >= 0),
	fouls tinyint CHECK(fouls >= 0),
	corner_kicks tinyint CHECK(corner_kicks >= 0),
	ball_possession tinyint CHECK(ball_possession BETWEEN 0 AND 100),
	yellow_cards tinyint,
	red_cards tinyint,
	expected_goals float

)