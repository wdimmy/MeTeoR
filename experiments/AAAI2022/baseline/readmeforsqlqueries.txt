This directory contains the sql files we used as baseline for Experiment 2, as well as a representative dataset. 

LUBMProgramOne.sql, LUBMProgramTwo.sql, LUBMProgramThree.sql correspond to programs \Pi^1_L, \Pi^2_L, and \Pi^3_L, respectively.


WeatherProgramOne.sql and WeatherProgramTwo.sql correspond to programs \Pi^1_W and \Pi^2_W, respectively.


LUBMD200.dump is a PostgreSQL data dump corresponding to the dataset D^200_L used in Experiment 2c. 

To restore the PostgreSQL database using the dump file, please first create a database by running:

createdb foobar

Once the database is created, issue the following command to write the dump into the database:

psql foobar < LUBMD200.dump


Finally, assuming that your password is 111111, you can use the following command to measure the time taken by PostgreSQL to run an SQL script and record the result in result.log. 

{ time PGPASSWORD=111111 psql foobar -a -f ./LUBMProgramOne.sql; } &> ./result.log


The size of the Weather datasets exceeds the limit of supplementary files so we do not include them. We will make all our datasets publicly available after the review period.

