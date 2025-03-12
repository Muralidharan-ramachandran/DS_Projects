use sports_analytics;
-- for competitions and category tables
-- 1.List all competitions along with their category name
select c.competition_name,ca.category_name 
from competitions_table as c join categories_table as ca
on c.category_id = ca.category_id;
-- 2.Count the number of competitions in each category
 select count(competition_id) as numberofCompetions,ca.category_name 
 from competitions_table as c join categories_table as ca 
 on c.category_id = ca.category_id group by ca.category_id;
-- 3.Find all competitions of type 'doubles'
select * from competitions_table where type ='doubles'; 
-- 4.Get competitions that belong to a specific category (e.g., ITF Men)
select * from competitions_table as c join categories_table as ca on c.category_id = ca.category_id
where ca.category_name = 'ITF Men';   
-- 5.Identify parent competitions and their sub-competitions
SELECT 
    c.competition_name AS subcompetition,
    c.parent_id,
    dense_rank() over(PARTITION BY parent_id ORDER BY competition_name) AS `rank`
FROM 
    competitions_table as c where parent_id is not null;
-- 6.Analyze the distribution of competition types by category
SELECT 
    c.category_id,
    c.type,
    COUNT(*) AS competition_count,
    (select ca.category_name from categories_table ca where ca.category_id = c.category_id) as categoryname
FROM 
    competitions_table c
GROUP BY 
    category_id, type
ORDER BY 
    category_id, competition_count DESC;
-- 7.List all competitions with no parent (top-level competitions)
select * from competitions_table where parent_id is null;

-- for complexes and venues tables
-- 1.List all venues along with their associated complex name
select v.venue_name,v.city_name,v.country_name,c.complex_name from venues_table v join complexes_table c where v.complex_id = c.complex_id;
-- 2.Count the number of venues in each complex
select complex_id,count(venue_id) as Number_of_venues from venues_table group by complex_id;
-- 3.Get details of venues in a specific country (e.g., Chile)
select * from venues_table where country_name = 'Chile';
-- 4.Identify all venues and their timezones
select venue_name,country_name,timezone from venues_table;
-- 5.Find complexes that have more than one venue
SELECT c.complex_id,c.complex_name,
COUNT(v.venue_id) AS num_venues
FROM complexes_table c JOIN venues_table v 
ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1;
-- 6.List venues grouped by country
SELECT 
  country_name,
  GROUP_CONCAT(venue_name ORDER BY venue_name SEPARATOR ', ') AS venue_list
FROM venues_table
GROUP BY country_name
ORDER BY country_name;
-- 7.Find all venues for a specific complex (e.g., Nacional)
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_name
FROM venues_table v JOIN complexes_table c 
ON v.complex_id = c.complex_id
WHERE c.complex_name = 'Nacional';

-- for competitors and ranks table
-- 1.Get all competitors with their rank and points.
SELECT 
    c.competitor_id,
    c.name AS competitor_name,
    r.rank,
    r.points
FROM competitors_table c
LEFT JOIN competitors_ranking_table r
ON c.competitor_id = r.competitor_id
ORDER BY r.rank;
-- 2.Find competitors ranked in the top 5
SELECT 
    c.competitor_id,
    c.name AS competitor_name,
    r.rank,
    r.points
FROM competitors_ranking_table r
JOIN competitors_table c 
ON r.competitor_id = c.competitor_id
WHERE r.rank <= 5
ORDER BY r.rank;
-- 3.List competitors with no rank movement (stable rank)
SELECT 
    c.competitor_id,
    c.name AS competitor_name,
    r.rank,
    r.points,
    r.competitions_played,
    r.movement
FROM competitors_table c
JOIN competitors_ranking_table r
ON c.competitor_id = r.competitor_id
WHERE r.movement = 0
ORDER BY r.rank;
-- 4.Get the total points of competitors from a specific country (e.g., Croatia)
SELECT
    c.country, 
    SUM(r.points) AS total_points
FROM competitors_ranking_table r
JOIN competitors_table c 
ON r.competitor_id = c.competitor_id
WHERE c.country = 'Croatia';
-- 5.Count the number of competitors per country
SELECT 
    country,
    COUNT(*) AS competitor_count
FROM competitors_table
GROUP BY country;
-- 6.Find competitors with the highest points in the current week
SELECT 
    c.competitor_id,
    c.name AS competitor_name,
    r.points
FROM competitors_table c
JOIN 
competitors_ranking_table r 
ON c.competitor_id = r.competitor_id
WHERE r.points = (SELECT MAX(r2.points) FROM competitors_ranking_table r2);






