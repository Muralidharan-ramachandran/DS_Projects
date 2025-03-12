import streamlit as slt
import pandas as pd
import sqlalchemy as sa

# Sidebar for navigation
slt.sidebar.title("Navigation")
page = slt.sidebar.selectbox("Go to:", ["Home", "Search and Filter","Player Details","Country-wise-performance"])



engine = sa.create_engine("mysql+pymysql://root:8098388128%40Murali@localhost:3306/Sports_Analytics")
compt_df = pd.read_sql_table('competitors_table',engine)
total_comp,columns = compt_df.shape
country_rep = pd.read_sql_query('select count(distinct country) as cr from competitors_table where country != "Neutral";',engine)

compt_rank_df = pd.read_sql_table('competitors_ranking_table',engine)



query = """
SELECT crt.rank, crt.points, cpt.name
FROM competitors_ranking_table crt
JOIN competitors_table cpt
ON crt.competitor_id = cpt.competitor_id
WHERE crt.points = (
    SELECT MAX(points) FROM competitors_ranking_table
);
"""
qr="""select crt.rank,crt.movement,crt.points,crt.competitions_played,cpt.name,cpt.country,cpt.country_code
FROM competitors_ranking_table crt
JOIN competitors_table cpt
ON crt.competitor_id = cpt.competitor_id;"""

pl_maxp = pd.read_sql_query(query,engine)
pl_maxp_points= pl_maxp['points'][0]
pl_maxp_name=pl_maxp['name'][0]

#for filtering players with points threshold
pl_pointf=pd.read_sql_query(qr,engine)

# Home Page
if page == "Home":
 slt.header('World of Tennis')
 slt.markdown('###### Presented by SPORTSRADAR')

 col1 , col2 , col3 = slt.columns(3)
 col1.metric("Total Competitors",f"{total_comp}")
 col2.metric("No.of Countries represented",f"{country_rep['cr'][0]}")
 col3.metric("Highest point scored by a competitor",f"{pl_maxp_points}")
 col3.markdown(f"{pl_maxp_name}")
 
 slt.header('Leaderboard')
 qry1='''SELECT 
    c.name, 
    c.country, 
    r.rank, 
    r.points 
 FROM 
    competitors_table c
 JOIN 
    competitors_ranking_table r
 ON 
    c.competitor_id = r.competitor_id
 WHERE 
    r.rank <= 10
 ORDER BY 
    r.rank ASC;'''
 
 qry2= '''SELECT 
    c.name, 
    c.country, 
    r.rank, 
    r.points 
 FROM 
    competitors_table c
 JOIN 
    competitors_ranking_table r
 ON 
    c.competitor_id = r.competitor_id
 ORDER BY 
    r.points DESC
 LIMIT 10;'''
 
 top_10R=pd.read_sql_query(qry1,engine)
 top_10P=pd.read_sql_query(qry2,engine)

 colm1 ,colm2 = slt.columns(2)
 with colm1:
    slt.title('Top 10 Ranks:')
    slt.write(top_10R)

 with colm2:
   slt.title('Top 10 points')
   slt.write(top_10P)
    
   

# Search and Filter Page
elif page == "Search and Filter":
 

 # Search by name
 search_name = slt.text_input("Search by competitor name:")
 filtered_df = compt_df[compt_df["name"].str.contains(search_name, case=False, na=False)] 
 if search_name: 
  slt.write(filtered_df)
 # Filter by rank range
 rank_min, rank_max = slt.slider(
    "Select rank range:",
    min_value=int(compt_rank_df["rank"].min()),
    max_value=int(compt_rank_df["rank"].max()),
    value=(int(compt_rank_df["rank"].min()), int(compt_rank_df["rank"].max()))
)
  # Filter data based on rank threshold
 filtered_data = pl_pointf[(pl_pointf["rank"] >= rank_min) & (pl_pointf["rank"] <= rank_max)]

 # Display the filtered data
 slt.write(f"Competitors in the specified rank range:")
 slt.dataframe(filtered_data)



 # Filter by country
 country_filter = slt.selectbox("Filter by country:", options=["All"] + compt_df["country"].unique().tolist())
 if country_filter != "All":
     filtered_df1 = compt_df[compt_df["country"] == country_filter]
 else:
    filtered_df1=compt_df
 if country_filter: 
  slt.write(filtered_df1)

 # Input slider for points threshold
 points_threshold = slt.slider(
    "Filter competitors with points greater than or equal to:", 
    min_value=int(pl_pointf["points"].min()), 
    max_value=int(pl_pointf["points"].max()), 
    value=int(pl_pointf["points"].min())
)

 # Filter data based on points threshold
 filtered_data = pl_pointf[pl_pointf["points"] >= points_threshold]

 # Display the filtered data
 slt.write(f"Competitors with points ≥ {points_threshold}:")
 slt.dataframe(filtered_data)

#player details
elif page == "Player Details":
    slt.title("Competitor Details Viewer")

  # Layout: Sidebar for selection, Main area for preview
    left_column, right_column = slt.columns(2)

  # Left column: Competitor selection
    with left_column:
     selected_name = slt.selectbox("Select a Competitor", pl_pointf['name'])

   # Right column: Detailed Preview
    with right_column:
     slt.write("### Competitor Details")
     competitor_details = pl_pointf[pl_pointf['name'] == selected_name]  # Filter data for selected competitor
    
     if not competitor_details.empty:
        slt.write(f"**Rank:** {competitor_details.iloc[0]['rank']}")
        slt.write(f"**Movement:** {competitor_details.iloc[0]['movement']}")
        slt.write(f"**Competitions Played:** {competitor_details.iloc[0]['competitions_played']}")
        slt.write(f"**Country:** {competitor_details.iloc[0]['country']}")
     else:
        slt.write("No competitor selected.")

#country wise performance
elif page == "Country-wise-performance":
   qry='''SELECT 
    c.country,
    COUNT(c.competitor_id) AS total_competitors,
    AVG(r.points) AS average_points
 FROM 
    competitors_table c
 JOIN 
    competitors_ranking_table r
 ON 
    c.competitor_id = r.competitor_id
 GROUP BY 
    c.country
 ORDER BY 
    c.country;'''
   
   country_df=pd.read_sql_query(qry,engine)
   slt.header('Country-Wise-Performance')
   slt.write(country_df)
   