# Claims & Insurance SQL Practice: Questions

Load `claims_practice_setup.sql` into SQLite (or adapt the date functions for MySQL/Postgres). Answers are in `answer_key.md`.

Tables: `policy`, `vehicle`, `coverage_group`, `coverage_description`, `coverage`, `claim`. Dates are stored as ISO text (YYYY-MM-DD). A policy is in force from `effective_date` up to (not including) `expiry_date`.


## Series A: Getting to know the environment

- **A001**: What is the table with the fewest rows?
- **A002**: What is the table with the most rows?
- **A003**: What is the earliest policy effective date?
- **A004**: What is the latest policy expiry date?
- **A005**: What is the oldest car year?
- **A006**: How many different provinces are there?
- **A007**: How many coverage descriptions belong to the largest coverage group?
- **A008**: What province has the most insured cars?
- **A009**: What is the sum of all coverage premiums?
- **A010**: What is the sum of all reported losses?
- **A011**: Which table(s) have the most foreign keys?

## Series B: Simple SELECT

- **B001**: What is the expiry date for policy number 0C0H10518?
- **B002**: What is the make and model of the vehicle with VIN 52DNR9IS25HBPKT9A?
- **B003**: What is the VIN that has the character "U" at the 5th position? (If more than one, give the first alphabetically.)
- **B004**: How many claims were reported for VIN R9A7MFP059P452BFS?
- **B005**: What is the largest single reported loss? Give the claim number.

## Series C: More SELECT

- **C001**: Among policies without claims, what is the first policy number if you sort the list alphabetically?
- **C002**: What is the VIN of the vehicle with no coverages?
- **C003**: How many policies have ever been written in March or September?
- **C004**: How many policies have never had a claim?

## Series D: Simple aggregations

- **D001**: How many policies expired in 2021?
- **D002**: How many policies had at least 1 day of exposure in 2019?
- **D003**: How many policies were in force as of 2021-06-30?
- **D004**: How many vehicles are not from Toyota?
- **D005**: How many claims in 2020 exceeded $10,000?
- **D006**: What is the largest average reported loss per claim, by vehicle make?
- **D007**: Which policy has the most claims?

## Series E: More aggregations

- **E001**: What is the maximum number of coverages a single vehicle can have?
- **E002**: What is the sum of 2021 reported losses for vehicles with a car year of 2005 or newer?
- **E003**: What is the average number of claims in 2020 per vehicle, across ALL vehicles (including those with none)?
- **E004**: What is the average number of claims in 2020 per vehicle, only counting vehicles that had at least 1 claim in 2020?
- **E005**: What is the average reported loss for claims under Liability coverages?
- **E006**: What is the excess of total premiums over total reported losses for vehicles insured under Ontario policies?
- **E007**: How many policies have at least one insured car manufactured before 2005 and one manufactured after 2015?

## Series F (stretch): Joins, CTEs and window functions

- **F001**: What is the loss ratio (total reported losses / total premiums) for each province? Which province has the highest ratio, and what is it (2 decimals)?
- **F002**: Using a CTE, list the number of policies whose total reported losses exceed their total premiums.
- **F003**: Using a window function, what is the claim number of the second-largest reported loss for each coverage group? Give the answer for the "Physical Damage" group.
- **F004**: What is the running total of reported losses in 2020 after the last claim of that year (i.e. total 2020 losses), computed with a window function?
