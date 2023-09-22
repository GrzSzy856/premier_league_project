Select * INTO Matches_Errors From Matches Where 1 = 2;

Select * INTO TeamMatchStats_Errors From TeamMatchStats Where 1 = 2;

ALTER TABLE Matches_Errors
ADD Error_code int,
    Error_column varchar(150);

ALTER TABLE TeamMatchStats_Errors
ADD Error_code int,
    Error_column varchar(150);
