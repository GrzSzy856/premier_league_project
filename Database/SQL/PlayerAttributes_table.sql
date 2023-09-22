CREATE TABLE PlayerAttributes(
	player_id integer,
	pace tinyint CHECK(pace BETWEEN 1 and 99),
	shooting tinyint CHECK(shooting BETWEEN 1 and 99),
	passing tinyint CHECK(passing BETWEEN 1 and 99),
	dribbling tinyint CHECK(dribbling BETWEEN 1 and 99),
	defending tinyint CHECK(defending BETWEEN 1 and 99),
	physicality tinyint CHECK(physicality BETWEEN 1 and 99)

	CONSTRAINT FK_PlayerAttributesPlayer FOREIGN KEY (player_id) REFERENCES Players(player_id)

)