import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import datetime
import os

file_path = os.path.join(os.path.dirname(__file__), 'Silly_Fragrance_excel.xlsx')

from wears import WearsFunctions

# streamlit run app.py
# tutorial https://medium.com/@vishaltyagi.dev098/excel-sheet-interactive-dashboard-python-streamlit-114f7c240fc8

df=pd.read_excel(
    io=file_path,
    engine='openpyxl',
    sheet_name='Insane Persons Sheet'
)
df=df.dropna(how='all')

df = df.dropna(subset=[df.columns[0], df.columns[1]], how='any')
df["Retail $/mL"]=df["$"]/df["mL"]

wears_df=WearsFunctions.read_wears()

# PANDAS DATABASE CREATION
st.set_page_config(
  page_title="Insane Fragrance Dashboard",
  page_icon=":lipstick:",
  layout="wide"                 
)


# SIDEBAR

#fragrance= st.sidebar.multiselect(
#  "Select Fragrance:",
#  options=df["Fragrance"].unique(),
#  default=df["Fragrance"].unique()
#)
#select from all fragrances

# TO DO: NEED TO FIX FILTERS. This is simplest filter

# st.sidebar.header("Filter by House, Perfumer, or Select from All Fragrances:")
# selected_filter = st.sidebar.selectbox('Select Filter:', options=['House','Perfumer','All Fragrances'])
# filtered_fragrances_house = df[df['House'] == selected_house]['Fragrance'].unique()
# # selected_fragrance_house = st.sidebar.selectbox('Select Fragrance:', options=filtered_fragrances_house)

# # filter for all fragrances
# fragrance = st.sidebar.selectbox('Select Fragrance:',
#                                  options=df['Fragrance'].astype(str).dropna().unique(),
#                                  key="all_fragrances")
# df_selection=df.query(
#  "Fragrance== @fragrance"
# )

df_sort_score = df.dropna(subset=["Score out of 100"]).sort_values(by='Score out of 100',ascending=False)

df['First_Word_Type'] = df['Type'].str.split().str[0]
unique_first_words = df['First_Word_Type'].dropna().unique()

# Sidebar filter selection
filter_choice = st.sidebar.selectbox('Filter by House, Perfumer, Type, or See All:', options=['House', 'Perfumer', 'Type','All Fragrances'])

# Filter based on the first choice
if filter_choice == 'House':
    selected_house = st.sidebar.selectbox('Select House:', options=df['House'].dropna().unique())
    filtered_fragrances_house = df[df['House'] == selected_house]['Fragrance'].unique()
    fragrance = st.sidebar.selectbox('Select Fragrance:', options=filtered_fragrances_house)
    

    
elif filter_choice == 'Perfumer':
    selected_house = st.sidebar.selectbox('Select Perfumer:', options=df['Perfumer'].dropna().unique())
    filtered_fragrances_house = df[df['Perfumer'] == selected_house]['Fragrance'].unique()
    fragrance = st.sidebar.selectbox('Select Fragrance:', options=filtered_fragrances_house)


elif filter_choice == 'Type':
    selected_house = st.sidebar.selectbox('Select Type:', options=unique_first_words)
    filtered_fragrances_house = df[df['First_Word_Type'] == selected_house]['Fragrance'].unique()
    fragrance = st.sidebar.selectbox('Select Fragrance:', options=filtered_fragrances_house)
    
elif filter_choice == 'All Fragrances':
    fragrance = st.sidebar.selectbox('Select Fragrance, ordered best to worst:', options=df_sort_score["Fragrance"].unique())


    
df_selection=df.query(
 "Fragrance== @fragrance"
)

st.header(fragrance)

c1,c2,c3=st.columns(3)
with c1:
    st.subheader("House")
    st.subheader(df_selection["House"].iloc[0])


with c2:
    st.subheader("Perfumer")
    st.subheader(df_selection["Perfumer"].iloc[0])

with c3: 
    st.subheader("Type")
    st.subheader(df_selection["Type"].iloc[0])



# review text
for note in df_selection["My notes"]:
    st.markdown(note)


if pd.notna(df_selection["Score out of 100"]).any():

    score=int(df_selection["Score out of 100"])
else:
    score="NA"
if pd.notna(df_selection["Performance (1-10)"]).any():
    perfo=int(df_selection["Performance (1-10)"])
else:
    perfo="NA"
scent_value=df_selection["Scent (1-10)*"]
if pd.notna(scent_value).any():
    # Round the value to 4 decimal places
    scent = round(float(scent_value), 4)
else:
    scent="NA"
    
# Custom CSS style for smaller text
small_text_style = "font-size: small;"

# TO DO: 1st review is n=1. Afterwards, don't show scoring system
# n=1

# chart of metrics

c1,c2,c3=st.columns(3)
with c3:
    st.subheader("Score")
    st.subheader(f"{score}")
    st.write('<div style="{}">(1-100) Final score. </div>'.format(small_text_style), unsafe_allow_html=True)

with c2:
    st.subheader("Performance")
    st.subheader(f"{perfo}")
    st.write('<div style="{}">(1-10) A 10 has all day/all night longevity and a noticeable sillage.</div>'.format(small_text_style), unsafe_allow_html=True)

with c1: 
    st.subheader("Scent")
    st.subheader(f"{scent}")    
    st.write('<div style="{}">(1-10) A 10 smells of beauty, perfection. Some fragrances will be alotted an extra 0.25. This floating point is awarded to personal favorites that I am drawn to emotionally, with reckless abandon.</div>'.format(small_text_style), unsafe_allow_html=True)




    
st.markdown("---")
# WEARS PER YEAR and predicted end year

total_wear_frags=len(wears_df["Fragrance"].unique())

if wears_df["Fragrance"].isin([fragrance]).any():
    st.subheader("Wears Tracker")


    wears, ranking, ml_left, plot_df,ml_start=WearsFunctions.sum_wears(wears_df,fragrance)
    plot, slope=WearsFunctions.plot_wears(plot_df, ml_start)
    
    st.plotly_chart(WearsFunctions.all_wears_plot(fragrance,wears_df))

    
    st.plotly_chart(plot)

    bottle_size=plot_df["mL"].values[0]
    #show total wears and all time ranking and year to run out
    w1,w2,w3=st.columns(3)
    with w1:
        st.subheader("Starting mL")
        st.subheader(f"{ml_start}")
        st.plotly_chart(WearsFunctions.plot_bottles(1,bottle_size) )

        for i in range(0,plot_df["Backups"].values[0] ):
            st.plotly_chart(WearsFunctions.plot_bottles(1,bottle_size) )
    #with w2:
    #    st.subheader("Total Wears")
    #    st.subheader(f"{wears}")
    
    with w2:
        st.subheader("Remaining mL")
        st.subheader(f"{round(ml_left)}")
        
        
        if plot_df["Backups"].values[0]>0:
            pct_list=WearsFunctions.list_mult_bottles(ml_left,ml_start,plot_df)

            for i in pct_list:
                st.plotly_chart(WearsFunctions.plot_bottles(i,bottle_size) )
        else:
            st.plotly_chart(WearsFunctions.plot_bottles(ml_left/ml_start,bottle_size) )


    year_empty=round( datetime.datetime.now().year +(ml_left *3 /slope ) )
    with w3:
        st.subheader("Year to Run out")
        st.subheader(f"{year_empty}")
        if pd.isna(df_selection["Retail $/mL"]).any()==False:
            st.subheader("💸💸💸")
            moolah = df_selection["Retail $/mL"].values[0] / 3
            formatted_moolah = "${:.2f}".format(moolah)
            #styled_text = f'<p style="color: #d4b2f1; font-size: xx-large;">{formatted_moolah}/Wear</p>'
            #st.markdown(styled_text, unsafe_allow_html=True)
            st.subheader(f"{formatted_moolah} per Wear")


else:
    st.subheader("Wears not tracked yet.")
    if pd.isna(df_selection["Retail $/mL"]).any()==False:
        st.subheader("💸💸💸")
        moolah = df_selection["Retail $/mL"].values[0] / 3
        formatted_moolah = "${:.2f}".format(moolah)
        #styled_text = f'<p style="color: #d4b2f1; font-size: xx-large;">{formatted_moolah}/Wear</p>'
        #st.markdown(styled_text, unsafe_allow_html=True)
        st.subheader(f"{formatted_moolah} per Wear")

    
st.write('<div style="{}">Data from Anonymous Man, to whom I am grateful :)<br> By CLUBSMELL</div>'.format(small_text_style), unsafe_allow_html=True)
st.markdown('<a href="http://www.clubsmell.com" style="color: #602ec9;">CLUBSMELL.COM</a>', unsafe_allow_html=True)

st.markdown('---')

st.write('<div style="{}"> Details and Assumptions<br> 1. Wears visualized for 2021-2022 were tracked together since July 2021. For the line graph, I halved the total for 2021-2022 and assigned the rounded down value to 2021, and rounded up for 2022.<br>2. I assumed 12 sprays per 1 mL, 4 sprays for 1 wear, so that is 3 wears per 1 mL! This is a gross approximation and changes based on atomizer size and type.<br>3. Last updated 3 February 2024. </div>'.format(small_text_style), unsafe_allow_html=True)
