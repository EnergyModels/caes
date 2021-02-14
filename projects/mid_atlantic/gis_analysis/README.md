# To visualize the results in ArcMap

0) Run study
- caes/projects/mid_atlantic/run_mid_atlantic_study.sh

1) Copy results
    1) copy the following files from mid_atlantic/study to mid_atlantic/gis_analysis
        - LK1_analysis.csv
        - LK1_analysis
        - LK1_analysis

2) Get supporting data for visualization
    1) BOEM
       - https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data
       - Download BOEM_Renewable_Energy_Areas_Shapefile_4_13_2020.zip
       - This study used data accessed 2020/04/26
    2) tl_2019_us_state.
       - www2.census.gov/geo/tiger/TIGER2019/STATE/tl_2019_us_state.zip
       - Download tl_2019_us_state.zip
       - This study used data accessed 2020/07/19
    3) UIA_World_Countries_Boundaries-shp 
        - https://hub.arcgis.com/datasets/UIA::uia-world-countries-boundaries
        - Download Full Dataset (UIA_World_Countries_Boundaries-shp)
        - This study used data accessed 2021/02/01
    4) These datasets need to be unzipped and then stored in the gis_analysis directory

3) Open ArcMap 10.8 and run plot_in_arcmap.py script

4) Open study_results.mxd using ArcMap 10.8 to visualize results
    - You may need to redirect map to find the supporting visualization data