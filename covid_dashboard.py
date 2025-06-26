import time
import streamlit as st
import numpy as np 
import pandas as pd
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import calendar
from dateutil import relativedelta
import itertools
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from time import strptime
from datetime import datetime,date
# from st_aggrid import AgGrid, GridOptionsBuilder,GridUpdateMode,DataReturnMode,ColumnsAutoSizeMode


def main():
    st.set_page_config(layout='wide',page_title="Palit - Final Project",) #set the page view configs
    main_container = st.container() #container
    f1,f2,f3 = main_container.columns((1,2,1))
    
    st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True) 
    f2.markdown(f"<h1 style='text-align: center;'>A COVID-19 New York</h1>", unsafe_allow_html=True) #title
    pages = st.sidebar.selectbox("Choose a Page", ['Overview of COVID-19','Economic Impact of COVID-19','Homelessness Impact of COVID-19']) #selectbox for all the tools on the dashboard

    if pages == 'Overview of COVID-19':
        main_container.markdown(f"<h3 style='text-align: center;'>Overview of COVID-19</h3>", unsafe_allow_html=True) #title
        col1,col2,col3 = main_container.columns((3,1,1))
        main_container.markdown(f"<br>", unsafe_allow_html=True)
        
        polygons = json.load(open('data/new-york-city-boroughs.geojson'))
        df_covid_orig = pd.read_csv('data/covid_data_by_day.csv')
        df_covid_orig['date_of_interest'] = pd.to_datetime(df_covid_orig['date_of_interest'])

        date_slider = col1.slider('Select Date Range',min_value=df_covid_orig['date_of_interest'].min().date(),
                                                                max_value=df_covid_orig['date_of_interest'].max().date(),
                                                                value=(df_covid_orig['date_of_interest'].min().date(),df_covid_orig['date_of_interest'].max().date()))
        start_date = date_slider[0]
        end_date = date_slider[1]
        c_var = col2.selectbox('Map Color Variable',['Cases','Hospitalizations','Deaths', 'Hosp. Rate','Death Rate'])
        l_var = col3.selectbox('Charting Variable',['Cases','Hospitalizations','Deaths'])

        df_covid = df_covid_orig[(df_covid_orig['date_of_interest']>=pd.to_datetime(start_date)) & (df_covid_orig['date_of_interest']<=pd.to_datetime(end_date))].copy()
        df_covid.sort_values('date_of_interest',inplace=True)
        #### VIZ ####

        df_covid_map_cc = df_covid[['BK_CASE_COUNT','SI_CASE_COUNT',
                        'BX_CASE_COUNT','QN_CASE_COUNT',
                        'MN_CASE_COUNT']]
        df_covid_map_cc.columns = [c[:2] for c in df_covid_map_cc.columns]

        df_covid_map_dc = df_covid[['BK_DEATH_COUNT','SI_DEATH_COUNT',
                                'BX_DEATH_COUNT','QN_DEATH_COUNT',
                                'MN_DEATH_COUNT']]
        df_covid_map_dc.columns = [c[:2] for c in df_covid_map_dc.columns]

        df_covid_map_hc = df_covid[['BK_HOSPITALIZED_COUNT','SI_HOSPITALIZED_COUNT',
                                'BX_HOSPITALIZED_COUNT','QN_HOSPITALIZED_COUNT',
                                'MN_HOSPITALIZED_COUNT']]
        df_covid_map_hc.columns = [c[:2] for c in df_covid_map_hc.columns]

        df_covid_map = pd.concat([df_covid_map_cc.sum(),df_covid_map_hc.sum(),df_covid_map_dc.sum()],axis=1)
        df_covid_map.columns = ['Cases','Hospitalizations','Deaths']
        df_covid_map.rename({'BK':'Brooklyn','SI':'Staten Island','BX':'Bronx','QN':'Queens','MN':'Manhattan'},inplace=True)
        df_covid_map.reset_index(inplace=True)
        df_covid_map.rename({'index':'Borough'},axis=1,inplace=True)
        df_covid_map['Hosp. Rate'] = (df_covid_map['Hospitalizations']/df_covid_map['Cases']).round(3)
        df_covid_map['Death Rate'] = (df_covid_map['Deaths']/df_covid_map['Cases']).round(3)
        df_covid_map['Death %'] = df_covid_map['Deaths']/df_covid_map['Deaths'].sum()
        df_covid_map['Case %'] = df_covid_map['Cases']/df_covid_map['Cases'].sum()
        df_covid_map['Hosp. %'] = df_covid_map['Hospitalizations']/df_covid_map['Hospitalizations'].sum()

        fig1 = px.choropleth_mapbox(df_covid_map, geojson=polygons, featureidkey='properties.name',locations='Borough', color=c_var,
                                color_continuous_scale="Peach",
                                mapbox_style="carto-positron",
                                zoom=9, 
                                center = {"lat": 40.7128, "lon": -74.0060},
                                opacity=0.5,
                                hover_data=['Cases','Hospitalizations','Deaths','Hosp. Rate','Death Rate'],
                                title=f'Map of NYC Boroughs (Color by {c_var})'
                                )
        fig1.update_layout(margin={"r":0,"t":25,"l":0,"b":0})


        l_var_dict = {'Cases':['BK_CASE_COUNT_7DAY_AVG','SI_CASE_COUNT_7DAY_AVG',
                                'BX_CASE_COUNT_7DAY_AVG','QN_CASE_COUNT_7DAY_AVG',
                                'MN_CASE_COUNT_7DAY_AVG'],
                      'Hospitalizations':['BK_HOSPITALIZED_COUNT_7DAY_AVG','SI_HOSPITALIZED_COUNT_7DAY_AVG',
                                'BX_HOSPITALIZED_COUNT_7DAY_AVG','QN_HOSPITALIZED_COUNT_7DAY_AVG',
                                'MN_HOSPITALIZED_COUNT_7DAY_AVG'],
                      'Deaths':['BK_DEATH_COUNT_7DAY_AVG','SI_DEATH_COUNT_7DAY_AVG',
                                'BX_DEATH_COUNT_7DAY_AVG','QN_DEATH_COUNT_7DAY_AVG',
                                'MN_DEATH_COUNT_7DAY_AVG']}
                 
        lines = l_var_dict[l_var]
        fig2 = px.line(df_covid,x='date_of_interest',y=lines,
                        labels={'value':l_var,
                                'date_of_interest':'Date'},
                        height=400,
                        title=f'7D Avg. {l_var} over Time')
        newnames = {lines[0]:'Brooklyn',
                    lines[1]:'Staten Island',
                    lines[2]:'Bronx',
                    lines[3]:'Queens',
                    lines[4]:'Manhattan'}
        fig2.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                               legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
        fig2.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))
        
        p_var_dict = {"Cases": "Case %",'Deaths':'Death %','Hospitalizations':'Hosp. %'}

        fig3 = px.bar(df_covid_map,x='Borough',y=l_var, title=f'Total {l_var}')
        fig4 = px.pie(df_covid_map,names='Borough',values=p_var_dict[l_var], title=f'Portion of {l_var}',
                        color = 'Borough',
                        color_discrete_map={'Brooklyn':'#2a68c2',
                                            'Staten Island':'#93c8fa',
                                            'Bronx':'#eb4343',
                                            'Queens':'#f3afad',
                                            'Manhattan':'#57ad9d'})

        main_container.plotly_chart(fig1,use_container_width=True)
        main_container.plotly_chart(fig2,use_container_width=True)
        v_col1,v_col2 = main_container.columns((1,1))
        v_col1.plotly_chart(fig3,use_container_width=True)
        v_col2.plotly_chart(fig4,use_container_width=True)

    if pages == 'Economic Impact of COVID-19':
        main_container.markdown(f"<h3 style='text-align: center;'>Economic Impact of COVID-19</h3>", unsafe_allow_html=True) #title
        col1,col2,col3 = main_container.columns((3,1,1))
        main_container.markdown(f"<br>", unsafe_allow_html=True)

        polygons = json.load(open('data/new-york-city-boroughs.geojson'))
        df_covid_orig = pd.read_csv('data/covid_data_by_day.csv')
        df_covid_orig['date_of_interest'] = pd.to_datetime(df_covid_orig['date_of_interest'])

        df_unemp_orig_l = []

        for b in ['Brooklyn','Bronx','Manhattan','Queens','Staten Island']:
            df_unemp = pd.read_excel('data/revised-2018-2022-borough-labor-force.xlsx',skiprows=2,sheet_name=b)
            df_unemp.dropna(subset=['Area'],inplace=True)
            df_unemp.columns = ['Borough', 'Year','Month','Labor Force','Employed','Unemployed','Unemp. Rate']
            df_unemp['Borough'] = b
            df_unemp_orig_l.append(df_unemp)

        df_unemp_orig = pd.concat(df_unemp_orig_l,ignore_index=True)
        df_unemp_orig = df_unemp_orig.pivot(index=['Year','Month'],columns='Borough',values='Unemp. Rate').reset_index()
        df_unemp_orig = df_unemp_orig[df_unemp_orig['Month']!='Avg']
        df_unemp_orig['month_n'] = df_unemp_orig['Month'].apply(lambda x : strptime(x,'%b').tm_mon)
        df_unemp_orig['Date'] = df_unemp_orig.apply(lambda x: datetime(int(x['Year']),x['month_n'],1),axis=1)
        df_unemp_orig.drop(['Year','Month','month_n'],axis=1,inplace=True)

        date_slider = col1.slider('Select Date Range',min_value=datetime(2019,6,1).date(),
                                                                max_value=df_unemp_orig['Date'].max().date(),
                                                                value=(datetime(2019,6,1).date(),df_unemp_orig['Date'].max().date()))
        start_date = date_slider[0]
        end_date = date_slider[1]
        c_var = col2.selectbox('Map Color Variable',['Cases','Avg. Unemp. Rate'])

        df_covid = df_covid_orig[(df_covid_orig['date_of_interest']>=pd.to_datetime(start_date)) & (df_covid_orig['date_of_interest']<=pd.to_datetime(end_date))].copy()
        df_unemp = df_unemp_orig[(df_unemp_orig['Date']>=pd.to_datetime(start_date)) & (df_unemp_orig['Date']<=pd.to_datetime(end_date))].copy()
        df_unemp.sort_values('Date',inplace=True)

        df_date_new = pd.DataFrame(df_unemp[df_unemp['Date']<df_covid['date_of_interest'].min()]['Date']).rename({'Date':'date_of_interest'},axis=1)
        df_covid = (pd.concat([df_covid, df_date_new], ignore_index=True)
                    .reindex(columns=df_covid.columns)
                    .fillna(0, downcast='infer'))
        df_covid.sort_values('date_of_interest',inplace=True)

        df_rent_orig = pd.read_csv('data/medianAskingRent_All.csv')
        df_rent_orig.drop(['areaName','areaType'],axis=1,inplace=True)
        df_rent = df_rent_orig.groupby('Borough').mean().reset_index().copy()
        df_rent = df_rent.melt(id_vars=['Borough'],var_name='Date', value_name='Avg. Rent')
        df_rent['Date'] = pd.to_datetime(df_rent['Date'])
        df_rent = df_rent[(df_rent['Date']>=pd.to_datetime(start_date)) & (df_rent['Date']<=pd.to_datetime(end_date))].copy()
        df_rent_piv = df_rent.pivot(index='Date',columns='Borough',values='Avg. Rent').round(2).reset_index()
        df_rent_piv.sort_values('Date',inplace=True)
        for b in ['Brooklyn','Bronx','Manhattan','Queens','Staten Island']:
            df_rent_piv[b+' Change'] = ((df_rent_piv[b]/df_rent_piv[b][0])-1)*100

        #### VIZ ####

        df_covid_map_cc = df_covid[['BK_CASE_COUNT','SI_CASE_COUNT',
                        'BX_CASE_COUNT','QN_CASE_COUNT',
                        'MN_CASE_COUNT']]
        df_covid_map_cc.columns = [c[:2] for c in df_covid_map_cc.columns]

        df_covid_map = pd.concat([df_covid_map_cc.sum()],axis=1)
        df_covid_map.rename({'BK':'Brooklyn','SI':'Staten Island','BX':'Bronx','QN':'Queens','MN':'Manhattan'},inplace=True)
        df_covid_map = df_covid_map.merge(df_unemp.drop(['Date'],axis=1).mean().round(1).rename('Unemp'),left_index=True,right_index=True)
        df_covid_map.columns = ['Cases','Avg. Unemp. Rate']
        df_covid_map.reset_index(inplace=True)
        df_covid_map.rename({'index':'Borough'},axis=1,inplace=True)

        fig1 = px.choropleth_mapbox(df_covid_map, geojson=polygons, featureidkey='properties.name',locations='Borough', color=c_var,
                                color_continuous_scale="Peach",
                                mapbox_style="carto-positron",
                                zoom=9, 
                                center = {"lat": 40.7128, "lon": -74.0060},
                                opacity=0.5,
                                hover_data=['Cases','Avg. Unemp. Rate'],
                                title=f'Map of NYC Boroughs (Color by {c_var})'
                                )
        fig1.update_layout(margin={"r":0,"t":25,"l":0,"b":0})
        
        lines = ['BK_CASE_COUNT_7DAY_AVG','SI_CASE_COUNT_7DAY_AVG',
                    'BX_CASE_COUNT_7DAY_AVG','QN_CASE_COUNT_7DAY_AVG',
                    'MN_CASE_COUNT_7DAY_AVG']
        fig2 = px.line(df_covid,x='date_of_interest',y=lines,
                        labels={'value':'Cases',
                                'date_of_interest':'Date'},
                        height=400,
                        title=f'7D Avg. Cases over Time')
        newnames = {lines[0]:'Brooklyn',
                    lines[1]:'Staten Island',
                    lines[2]:'Bronx',
                    lines[3]:'Queens',
                    lines[4]:'Manhattan'}
        fig2.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                               legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
        fig2.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))
        
        fig3 = px.line(df_unemp,x='Date',y=['Brooklyn','Staten Island','Bronx','Queens','Manhattan'],
                        labels={'value':'Unemp. Rate',
                                'Date':'Date'},
                        height=400,
                        title=f'Unemploymemt Rate over Time')
        
        fig3.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))

        fig4 = px.line(df_rent_piv,x='Date',y=['Brooklyn','Staten Island','Bronx','Queens','Manhattan'],
                        labels={'value':'Avg. Rent',
                                'Date':'Date'},
                        height=400,
                        title=f'Avg. Rent over Time')
        
        fig4.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))

        fig5 = px.line(df_rent_piv,x='Date',y=['Brooklyn Change','Staten Island Change','Bronx Change','Queens Change','Manhattan Change'],
                        labels={'value':'Avg. Rent Change',
                                'Date':'Date'},
                        height=400,
                        title=f'% Change in Avg. Rent vs Start of Time Period')
        newnames = {'Brooklyn Change':'Brooklyn',
                    'Staten Island Change':'Staten Island',
                    'Bronx Change':'Bronx',
                    'Queens Change':'Queens',
                    'Manhattan Change':'Manhattan'}
        fig5.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                               legendgroup = newnames[t.name],
                                                hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
        
        fig5.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))


        main_container.plotly_chart(fig1,use_container_width=True)
        main_container.plotly_chart(fig2,use_container_width=True)
        main_container.plotly_chart(fig3,use_container_width=True)
        main_container.plotly_chart(fig4,use_container_width=True)
        # main_container.plotly_chart(fig5,use_container_width=True)

    if pages == 'Homelessness Impact of COVID-19':
        main_container.markdown(f"<h3 style='text-align: center;'>Homelessness Impact of COVID-19</h3>", unsafe_allow_html=True) #title
        col1,col2,col3 = main_container.columns((3,1,1))
        main_container.markdown(f"<br>", unsafe_allow_html=True)

        polygons = json.load(open('data/new-york-city-boroughs.geojson'))
        df_covid_orig = pd.read_csv('data/covid_data_by_day.csv')
        df_covid_orig['date_of_interest'] = pd.to_datetime(df_covid_orig['date_of_interest'])

        df_unemp_orig_l = []

        for b in ['Brooklyn','Bronx','Manhattan','Queens','Staten Island']:
            df_unemp = pd.read_excel('data/revised-2018-2022-borough-labor-force.xlsx',skiprows=2,sheet_name=b)
            df_unemp.dropna(subset=['Area'],inplace=True)
            df_unemp.columns = ['Borough', 'Year','Month','Labor Force','Employed','Unemployed','Unemp. Rate']
            df_unemp['Borough'] = b
            df_unemp_orig_l.append(df_unemp)

        df_unemp_orig = pd.concat(df_unemp_orig_l,ignore_index=True)
        df_unemp_orig = df_unemp_orig.pivot(index=['Year','Month'],columns='Borough',values='Unemp. Rate').reset_index()
        df_unemp_orig = df_unemp_orig[df_unemp_orig['Month']!='Avg']
        df_unemp_orig['month_n'] = df_unemp_orig['Month'].apply(lambda x : strptime(x,'%b').tm_mon)
        df_unemp_orig['Date'] = df_unemp_orig.apply(lambda x: datetime(int(x['Year']),x['month_n'],1),axis=1)
        df_unemp_orig.drop(['Year','Month','month_n'],axis=1,inplace=True)

        df_unemp_full = pd.read_excel('data/nyclfsa.xlsx',skiprows=3,sheet_name='Data',usecols="A,B,F")
        df_unemp_full.columns = ['Date','Labor Force','Unemp. Rate']
        df_unemp_full['Labor Force'] = df_unemp_full['Labor Force']*1000
        df_unemp_full['Date'] = pd.to_datetime(df_unemp_full['Date'])

        df_homeless_orig = pd.read_csv('data/DHS_Daily_Report.csv')
        df_homeless_orig['Date of Census'] = pd.to_datetime(df_homeless_orig['Date of Census'])
        df_homeless_orig.rename({'Date of Census':'Date'},axis=1,inplace=True)
        df_homeless_orig.sort_values('Date',inplace=True)

        date_slider = col1.slider('Select Date Range',min_value=datetime(2019,6,1).date(),
                                                                max_value=df_homeless_orig['Date'].max().date(),
                                                                value=(datetime(2019,6,1).date(),df_homeless_orig['Date'].max().date()))
        start_date = date_slider[0]
        end_date = date_slider[1]

        df_covid = df_covid_orig[(df_covid_orig['date_of_interest']>=pd.to_datetime(start_date)) & (df_covid_orig['date_of_interest']<=pd.to_datetime(end_date))].copy()
        df_unemp = df_unemp_full[(df_unemp_full['Date']>=pd.to_datetime(start_date)) & (df_unemp_full['Date']<=pd.to_datetime(end_date))].copy()
        df_unemp.sort_values('Date',inplace=True)

        df_date_new = pd.DataFrame(df_unemp[df_unemp['Date']<df_covid['date_of_interest'].min()]['Date']).rename({'Date':'date_of_interest'},axis=1)
        df_covid = (pd.concat([df_covid, df_date_new], ignore_index=True)
                    .reindex(columns=df_covid.columns)
                    .fillna(0, downcast='infer'))
        df_covid.sort_values('date_of_interest',inplace=True)

        df_rent_orig = pd.read_csv('data/medianAskingRent_All.csv')
        df_rent_orig.drop(['areaName','areaType'],axis=1,inplace=True)
        df_rent = df_rent_orig.groupby('Borough').mean().reset_index().copy()
        df_rent = df_rent.melt(id_vars=['Borough'],var_name='Date', value_name='Avg. Rent')
        df_rent['Date'] = pd.to_datetime(df_rent['Date'])
        df_rent.drop(['Borough'],axis=1,inplace=True)
        df_rent = df_rent.groupby('Date').mean().reset_index()
        df_rent = df_rent[(df_rent['Date']>=pd.to_datetime(start_date)) & (df_rent['Date']<=pd.to_datetime(end_date))].copy()

        df_homeless = df_homeless_orig[(df_homeless_orig['Date']>=pd.to_datetime(start_date)) & (df_homeless_orig['Date']<=pd.to_datetime(end_date))].copy()
        df_homeless = df_homeless[['Date','Total Adults in Shelter','Total Children in Shelter']]
        df_homeless = df_homeless.melt(id_vars='Date',var_name='Type',value_name='Population')

        #### VIZ ####
        
        fig2 = px.line(df_unemp,x='Date',y='Unemp. Rate',
                        labels={'value':'Unemp. Rate',
                                'Date':'Date'},
                        height=400,
                        title=f'Overall Unemploymemt Rate over Time')
        
        fig2.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))

        fig3 = px.line(df_rent,x='Date',y='Avg. Rent',
                        labels={'value':'Avg. Rent',
                                'Date':'Date'},
                        height=400,
                        title=f'Overall Avg. Rent over Time')
        
        fig3.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))
        
        fig4 = px.area(df_homeless, x="Date", y="Population", color="Type", line_group="Type",
                        height=500,
                        title=f'Population in Shelter over Time')
        
        fig4.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))

        fig5 = make_subplots(specs=[[{"secondary_y": True}]])
        fig5.add_trace(
            go.Scatter(x=df_unemp['Date'], y=df_unemp['Labor Force'], name="Labor Force"),
            secondary_y=False,
        )
        fig5.add_trace(
            go.Scatter(x=df_unemp['Date'], y=df_unemp['Unemp. Rate'], name="Unemp. Rate"),
            secondary_y=True,
        )
        fig5.update_layout(
            title_text="Overall Unemployment Rate"
        )
        fig5.update_xaxes(title_text="xaxis title")
        fig5.update_yaxes(title_text="Labor Force", secondary_y=False)
        fig5.update_yaxes(title_text="Unemp. Rate", secondary_y=True, showgrid=False)
        fig5.update_layout(legend=dict(
                            orientation='h',
                            yanchor="top",
                            y=-0.3,
                            xanchor="center",
                            x=0.5,
                            title = {'text':None}
                        ))

        
        main_container.plotly_chart(fig5,use_container_width=True)
        main_container.plotly_chart(fig3,use_container_width=True)
        main_container.plotly_chart(fig4,use_container_width=True)
        # main_container.plotly_chart(fig5,use_container_width=True)
        # main_container.table(df_unemp)
        


if __name__ == '__main__': 
    main()  #execute main when this script is run - run dashboard 

