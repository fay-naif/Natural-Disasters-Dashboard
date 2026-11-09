-- Natural disasters analysis queries
-- Table: disasters (one row per event, loaded from data/Natural_Disasters_Clean_AR.zip)
-- Written for SQLite. python/load_to_sqlite.py builds disasters.db and runs these queries.

-- 1. Headline KPIs
SELECT COUNT(*)                            AS disasters,
       SUM(Deaths)                         AS deaths,
       SUM(People_Affected)                AS people_affected,
       SUM(Economic_Loss_USD)              AS economic_loss_usd,
       COUNT(DISTINCT Country)             AS countries_affected
FROM disasters;

-- 2. Disasters, deaths and losses by type
SELECT Disaster_Type,
       COUNT(*)                            AS disasters,
       SUM(Deaths)                         AS deaths,
       ROUND(SUM(Economic_Loss_USD) / 1e9, 1) AS economic_loss_bn_usd,
       ROUND(1.0 * SUM(Deaths) / COUNT(*), 1) AS deaths_per_event
FROM disasters
GROUP BY Disaster_Type
ORDER BY disasters DESC;

-- 3. Disasters by continent
SELECT Continent,
       COUNT(*)                            AS disasters,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM disasters), 1) AS share_pct,
       SUM(Deaths)                         AS deaths
FROM disasters
GROUP BY Continent
ORDER BY disasters DESC;

-- 4. Top 10 countries by deaths
SELECT Country, Continent,
       COUNT(*)                            AS disasters,
       SUM(Deaths)                         AS deaths
FROM disasters
GROUP BY Country, Continent
ORDER BY deaths DESC
LIMIT 10;

-- 5. Trend by year
SELECT Year,
       COUNT(*)                            AS disasters,
       SUM(Deaths)                         AS deaths,
       ROUND(SUM(Economic_Loss_USD) / 1e9, 1) AS economic_loss_bn_usd
FROM disasters
GROUP BY Year
ORDER BY Year;

-- 6. Most frequent disaster type in each continent
WITH counts AS (
    SELECT Continent, Disaster_Type, COUNT(*) AS disasters,
           RANK() OVER (PARTITION BY Continent ORDER BY COUNT(*) DESC) AS rnk
    FROM disasters
    GROUP BY Continent, Disaster_Type
)
SELECT Continent, Disaster_Type, disasters
FROM counts
WHERE rnk = 1
ORDER BY disasters DESC;

-- 7. Busiest months
SELECT Month, Month_AR,
       COUNT(*)                            AS disasters
FROM disasters
GROUP BY Month, Month_AR
ORDER BY Month;
