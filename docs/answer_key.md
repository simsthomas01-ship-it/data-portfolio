# Answer Key (spoilers!)


## Series A: Getting to know the environment

**A001**: What is the table with the fewest rows?

Answer: `coverage_group`

```sql
SELECT 'policy' t, COUNT(*) n FROM policy UNION ALL SELECT 'vehicle',COUNT(*) FROM vehicle UNION ALL SELECT 'coverage_group',COUNT(*) FROM coverage_group UNION ALL SELECT 'coverage_description',COUNT(*) FROM coverage_description UNION ALL SELECT 'coverage',COUNT(*) FROM coverage UNION ALL SELECT 'claim',COUNT(*) FROM claim ORDER BY n ASC LIMIT 1
```

**A002**: What is the table with the most rows?

Answer: `coverage`

```sql
SELECT 'policy' t, COUNT(*) n FROM policy UNION ALL SELECT 'vehicle',COUNT(*) FROM vehicle UNION ALL SELECT 'coverage_group',COUNT(*) FROM coverage_group UNION ALL SELECT 'coverage_description',COUNT(*) FROM coverage_description UNION ALL SELECT 'coverage',COUNT(*) FROM coverage UNION ALL SELECT 'claim',COUNT(*) FROM claim ORDER BY n DESC LIMIT 1
```

**A003**: What is the earliest policy effective date?

Answer: `2016-03-01`

```sql
SELECT MIN(effective_date) FROM policy
```

**A004**: What is the latest policy expiry date?

Answer: `2025-09-06`

```sql
SELECT MAX(expiry_date) FROM policy
```

**A005**: What is the oldest car year?

Answer: `1999`

```sql
SELECT MIN(car_year) FROM vehicle
```

**A006**: How many different provinces are there?

Answer: `5`

```sql
SELECT COUNT(DISTINCT province) FROM policy
```

**A007**: How many coverage descriptions belong to the largest coverage group?

Answer: `4`

```sql
SELECT COUNT(*) FROM coverage_description GROUP BY coverage_group_id ORDER BY 1 DESC LIMIT 1
```

**A008**: What province has the most insured cars?

Answer: `ON`

```sql
SELECT province FROM policy JOIN vehicle USING(policy_number) GROUP BY province ORDER BY COUNT(*) DESC LIMIT 1
```

**A009**: What is the sum of all coverage premiums?

Answer: `$191,614.37`

```sql
SELECT ROUND(SUM(premium),2) FROM coverage
```

**A010**: What is the sum of all reported losses?

Answer: `$219,581.13`

```sql
SELECT ROUND(SUM(reported_loss),2) FROM claim
```

**A011**: Which table(s) have the most foreign keys?

Answer: `coverage and claim`

```sql
SELECT 'coverage and claim (tie: 2 each), see schema'
```


## Series B: Simple SELECT

**B001**: What is the expiry date for policy number 0C0H10518?

Answer: `2020-09-01`

```sql
SELECT expiry_date FROM policy WHERE policy_number='0C0H10518'
```

**B002**: What is the make and model of the vehicle with VIN 52DNR9IS25HBPKT9A?

Answer: `Chevrolet Equinox`

```sql
SELECT make||' '||model FROM vehicle WHERE vin='52DNR9IS25HBPKT9A'
```

**B003**: What is the VIN that has the character "U" at the 5th position? (If more than one, give the first alphabetically.)

Answer: `9C3FUQUHZ6A830DM7`

```sql
SELECT vin FROM vehicle WHERE substr(vin,5,1)='U' ORDER BY vin LIMIT 1
```

**B004**: How many claims were reported for VIN R9A7MFP059P452BFS?

Answer: `6`

```sql
SELECT COUNT(*) FROM claim WHERE vin='R9A7MFP059P452BFS'
```

**B005**: What is the largest single reported loss? Give the claim number.

Answer: `EVCC4678669`

```sql
SELECT claim_number FROM claim ORDER BY reported_loss DESC LIMIT 1
```


## Series C: More SELECT

**C001**: Among policies without claims, what is the first policy number if you sort the list alphabetically?

Answer: `1H3C50983`

```sql
SELECT policy_number FROM policy WHERE policy_number NOT IN (SELECT v.policy_number FROM vehicle v JOIN claim c ON c.vin=v.vin) ORDER BY policy_number LIMIT 1
```

**C002**: What is the VIN of the vehicle with no coverages?

Answer: `MPYO0CU4YYJ5CI6VG`

```sql
SELECT vin FROM vehicle WHERE vin NOT IN (SELECT vin FROM coverage)
```

**C003**: How many policies have ever been written in March or September?

Answer: `5`

```sql
SELECT COUNT(*) FROM policy WHERE strftime('%m',effective_date) IN ('03','09')
```

**C004**: How many policies have never had a claim?

Answer: `3`

```sql
SELECT COUNT(*) FROM policy WHERE policy_number NOT IN (SELECT v.policy_number FROM vehicle v JOIN claim c ON c.vin=v.vin)
```


## Series D: Simple aggregations

**D001**: How many policies expired in 2021?

Answer: `5`

```sql
SELECT COUNT(*) FROM policy WHERE strftime('%Y',expiry_date)='2021'
```

**D002**: How many policies had at least 1 day of exposure in 2019?

Answer: `10`

```sql
SELECT COUNT(*) FROM policy WHERE effective_date<='2019-12-31' AND expiry_date>'2019-01-01'
```

**D003**: How many policies were in force as of 2021-06-30?

Answer: `9`

```sql
SELECT COUNT(*) FROM policy WHERE effective_date<='2021-06-30' AND expiry_date>'2021-06-30'
```

**D004**: How many vehicles are not from Toyota?

Answer: `31`

```sql
SELECT COUNT(*) FROM vehicle WHERE make<>'Toyota'
```

**D005**: How many claims in 2020 exceeded $10,000?

Answer: `2`

```sql
SELECT COUNT(*) FROM claim WHERE strftime('%Y',loss_date)='2020' AND reported_loss>10000
```

**D006**: What is the largest average reported loss per claim, by vehicle make?

Answer: `$4,352.80`

```sql
SELECT ROUND(AVG(reported_loss),2) FROM claim JOIN vehicle USING(vin) GROUP BY make ORDER BY 1 DESC LIMIT 1
```

**D007**: Which policy has the most claims?

Answer: `0D5Z43039`

```sql
SELECT policy_number FROM vehicle JOIN claim USING(vin) GROUP BY policy_number ORDER BY COUNT(*) DESC LIMIT 1
```


## Series E: More aggregations

**E001**: What is the maximum number of coverages a single vehicle can have?

Answer: `5`

```sql
SELECT MAX(n) FROM (SELECT COUNT(*) n FROM coverage GROUP BY vin)
```

**E002**: What is the sum of 2021 reported losses for vehicles with a car year of 2005 or newer?

Answer: `$13,578.28`

```sql
SELECT ROUND(SUM(reported_loss),2) FROM claim JOIN vehicle USING(vin) WHERE strftime('%Y',loss_date)='2021' AND car_year>=2005
```

**E003**: What is the average number of claims in 2020 per vehicle, across ALL vehicles (including those with none)?

Answer: `0.457`

```sql
SELECT ROUND(1.0*(SELECT COUNT(*) FROM claim WHERE strftime('%Y',loss_date)='2020')/(SELECT COUNT(*) FROM vehicle),3)
```

**E004**: What is the average number of claims in 2020 per vehicle, only counting vehicles that had at least 1 claim in 2020?

Answer: `1.333`

```sql
SELECT ROUND(AVG(n),3) FROM (SELECT COUNT(*) n FROM claim WHERE strftime('%Y',loss_date)='2020' GROUP BY vin)
```

**E005**: What is the average reported loss for claims under Liability coverages?

Answer: `$3,377.32`

```sql
SELECT ROUND(AVG(reported_loss),2) FROM claim c JOIN coverage_description d USING(coverage_description_id) JOIN coverage_group g USING(coverage_group_id) WHERE g.group_name='Liability'
```

**E006**: What is the excess of total premiums over total reported losses for vehicles insured under Ontario policies?

Answer: `$-3,261.98`

```sql
SELECT ROUND((SELECT SUM(premium) FROM coverage JOIN vehicle USING(vin) JOIN policy USING(policy_number) WHERE province='ON')-(SELECT SUM(reported_loss) FROM claim JOIN vehicle USING(vin) JOIN policy USING(policy_number) WHERE province='ON'),2)
```

**E007**: How many policies have at least one insured car manufactured before 2005 and one manufactured after 2015?

Answer: `2`

```sql
SELECT COUNT(*) FROM policy p WHERE EXISTS(SELECT 1 FROM vehicle v WHERE v.policy_number=p.policy_number AND car_year<2005) AND EXISTS(SELECT 1 FROM vehicle v WHERE v.policy_number=p.policy_number AND car_year>2015)
```


## Series F (stretch): Joins, CTEs and window functions

**F001**: What is the loss ratio (total reported losses / total premiums) for each province? Which province has the highest ratio, and what is it (2 decimals)?

Answer: `BC 3.59`

```sql
SELECT province||' '||ROUND(l/pr,2) FROM (SELECT p.province, (SELECT SUM(reported_loss) FROM claim c JOIN vehicle v2 ON v2.vin=c.vin JOIN policy p2 ON p2.policy_number=v2.policy_number WHERE p2.province=p.province) l, (SELECT SUM(premium) FROM coverage co JOIN vehicle v3 ON v3.vin=co.vin JOIN policy p3 ON p3.policy_number=v3.policy_number WHERE p3.province=p.province) pr FROM policy p GROUP BY p.province) ORDER BY l/pr DESC LIMIT 1
```

**F002**: Using a CTE, list the number of policies whose total reported losses exceed their total premiums.

Answer: `10`

```sql
WITH pl AS (SELECT v.policy_number, SUM(c.reported_loss) loss FROM vehicle v JOIN claim c USING(vin) GROUP BY v.policy_number), pp AS (SELECT v.policy_number, SUM(co.premium) prem FROM vehicle v JOIN coverage co USING(vin) GROUP BY v.policy_number) SELECT COUNT(*) FROM pl JOIN pp USING(policy_number) WHERE loss>prem
```

**F003**: Using a window function, what is the claim number of the second-largest reported loss for each coverage group? Give the answer for the "Physical Damage" group.

Answer: `MNEY5881537`

```sql
SELECT claim_number FROM (SELECT c.claim_number, g.group_name, ROW_NUMBER() OVER (PARTITION BY g.group_name ORDER BY c.reported_loss DESC) rn FROM claim c JOIN coverage_description d USING(coverage_description_id) JOIN coverage_group g USING(coverage_group_id)) WHERE group_name='Physical Damage' AND rn=2
```

**F004**: What is the running total of reported losses in 2020 after the last claim of that year (i.e. total 2020 losses), computed with a window function?

Answer: `$51,601.41`

```sql
SELECT ROUND(MAX(rt),2) FROM (SELECT SUM(reported_loss) OVER (ORDER BY loss_date, claim_number) rt FROM claim WHERE strftime('%Y',loss_date)='2020')
```
