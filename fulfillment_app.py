import streamlit as st
import pandas as pd
import numpy as np
import base64
import sys, os, re
sys.path.append(os.getcwd()+"/scripts/")
from gb_lib import rename_box_type, process_day, get_table_download_link_csv
#sys.path.append(".")
#import process_orders
#import importlib
#importlib.reload(process_orders)
#from ut_methods import *
#from compare_files.py import process_day

### settings
st.sidebar.markdown('#### Select week, year and day')
week = int(st.sidebar.number_input('Week number (e.g.: 16):', format='%.0f'))
year = st.sidebar.number_input('Year (e.g.: 2021):', 2021, format='%.0f')
day = st.sidebar.selectbox('Select a day', ['TUE','WED','THU', 'FRI'])
ignore = st.sidebar.multiselect('Which box type to not consider this week', ['NP', 'LF', 'GF'])
st.sidebar.markdown('---')


upcoming = st.sidebar.file_uploader("Select \"upcoming_"+day+"_CW"+str(week)+".csv\" file")
processed = st.sidebar.file_uploader("Select \"processed_"+day+"_CW"+str(week)+".csv\" file")

if not (str(day)=="TUE"):
    days_eng =np.array(["MON", "TUE", "WED", "THU", "FRI"])
    yesterday = np.where(days_eng==day)
    st.sidebar.markdown('\* The `collected_processed_until` file needs to be the one you downloaded yesterday')
    coll_proc_until = st.sidebar.file_uploader("Select \"collected_processed_until"+days_eng[yesterday[0]-1][0]+"_CW"+str(week)+".csv\" file")
elif day=="TUE":
    coll_proc_until = []

if (upcoming is not None) and (processed is not None) and (coll_proc_until is not None):
    #df = pd.read_csv(upl)
    #st.dataframe(df)

    df, df_dup, df_min, df_extra, df_extra_min, df_expected, df_till = process_day(day, week, year, method="streamlit", ignore=ignore,  new_raw=processed, recurr_raw=upcoming, df_prev=coll_proc_until)

    ## PRINT summary of a given day (optimoroute_summarized)
    print("DAY: "+day)
    # total counts
    majtypes = ["VEGAN", "VG", "OMNI"]

    # counts including specials
    df_min["TYPE"] = df_min["TYPE"].str.replace(re.escape(" (1st box)"),"")
    df_min["TYPE"] = df_min["TYPE"].str.split("+").str[0].str.rstrip(" ")
    df_min["Number"] = df_min["Email"]
    sdf = df_min.groupby(by=["TYPE"]).count()["Number"]
    total_boxes = sdf.sum()
    for tp in majtypes:
        sdf = sdf.append(pd.Series(df_min["TYPE"].str.contains(tp).sum(), index=[tp+" TOTAL"]))
        #st.markdown(tp +" boxes: "+str(df_min["TYPE"].str.contains(tp).sum()))
    sdf =sdf.append(pd.Series(total_boxes, index=["TOTAL"]))

    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(["Box Type (WK "+ str(week) + ", "+ day +")", "Number"]),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[sdf.index, sdf],
                   fill_color='lavender',
                   align='left'))
    ])
    st.plotly_chart(fig)

    st.markdown('**Duplicate entries**')
    st.dataframe(df_dup)

#dwnld = st.button('Download optimoroute')
#if (dwnld):
    st.markdown(get_table_download_link_csv(df_min, 'optimoroute_'+day+'_CW'+str(week)), unsafe_allow_html=True)
    st.markdown(get_table_download_link_csv(df_extra_min, 'extra_items_PRINTABLE_'+day+'_CW'+str(week)), unsafe_allow_html=True)
    st.markdown(get_table_download_link_csv(df_till, 'collected_processed_until'+day+'_CW'+str(week)), unsafe_allow_html=True)
