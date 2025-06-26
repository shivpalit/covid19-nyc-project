# COVID-19 Impact Analysis on New York City

## Project Overview
This project, developed as part of the Data Visualization course in the M.S. in Data Science program at Johns Hopkins University, analyzes the economic and societal impact of COVID-19 on New York City. The analysis focuses on three key areas:

1. COVID-19 case tracking and spread across NYC boroughs
2. Economic impact through unemployment rates and rental market changes
3. Social impact with a focus on homelessness trends

## Key Findings
The analysis revealed that New York City experienced severe initial impact during the first months of the pandemic, though its economic recovery generally followed global trends toward improvement. However, the research uncovered that short-term protective policies, such as eviction moratoriums, while well-intentioned, appeared to delay rather than prevent negative outcomes. This became evident in the post-policy period, which showed significant increases in the homeless population. Additionally, the economic impact varied considerably by borough, with some areas demonstrating greater resilience than others in terms of employment rates and rental market stability.

*For the complete analysis and methodology, please refer to the full project report: `covid19_nyc_project_report.pdf`*

## Interactive Dashboard
The project features an interactive Streamlit dashboard with three main sections:

1. **Overview of COVID-19**
   - Borough-level case tracking
   - Interactive choropleth maps
   - Time series analysis of cases, hospitalizations, and deaths

2. **Economic Impact**
   - Unemployment rates by borough
   - Rental market trends
   - Combined COVID-19 and economic indicator analysis

3. **Homelessness Impact**
   - Shelter population trends
   - Correlation with economic indicators
   - Adult vs. child homeless population tracking

## Technical Stack
- **Python** - Primary programming language
- **Streamlit** - Web application framework
- **Plotly** - Interactive visualization library
- **Pandas** - Data manipulation and analysis
- **GeoPandas** - Geospatial data handling
- **NumPy** - Numerical computing
- **Matplotlib** - Additional plotting capabilities

## Data Sources
- NYC Department of Health COVID-19 data
- Bureau of Labor Statistics employment data
- NYC Department of Homeless Services daily reports
- NYC rental market data

## Requirements
```
streamlit
numpy
pandas
plotly
geopandas
matplotlib
```

## Running the Dashboard
1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run covid_dashboard.py
```

## Author
Shiv Palit
M.S. Data Science
Johns Hopkins University
