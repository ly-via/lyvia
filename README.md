# Greater Sydney Analysis
This project focuses on analyzing the 350+ Statistical Area Level 2 (SA2) regions within the Greater Sydney area to develop a "bustling" metric. This metric quantifies how busy each district is, considering Sydney's unique blend of urban life and natural beauty.

# Project Overview
Australia is divided into over 2000 SA2 regions, each representing communities that interact socially and economically. For this analysis, the focus is on the Greater Sydney area, known for its combination of bustling city life and proximity to natural attractions like beaches and national parks.

# Objectives
## Data Integration: Spatially integrate multiple datasets of various formats to evaluate the activity levels across different regions.
## Metric Development: Develop a "bustling" metric to quantify the busyness of each SA2 region within Greater Sydney.
## Data Processing: Clean and preprocess data using Python, followed by SQL for merging datasets and generating the final scores.

# Approach
## Data Loading and Cleaning: Python was used to load and clean the initial datasets. This involved handling various data formats and ensuring consistency across the datasets.
## Spatial Integration: Utilizing PostGIS, the spatial extension of PostgreSQL, to integrate spatial data, including SA2 digital boundaries obtained from the ABS website.
## Scoring: SQL queries were employed to merge the datasets and calculate the bustling metric for each SA2 region, which was then visualized to highlight the busiest areas within Greater Sydney.

# Tools and Technologies
## Python: For data cleaning and preprocessing.
## PostgreSQL with PostGIS: For managing spatial data and calculating metrics.
## Jupyter Notebook: To collate and present the analysis in a clear, concise format.

# Results
The project successfully quantified the bustling nature of each SA2 region, offering insights into how activity levels vary across Greater Sydney. These results can be utilized for urban planning, resource allocation, and further research into the dynamics of city life in Sydney.

