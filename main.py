# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben

# Standard Libraries
from math import pi, sqrt, cos, sin, atan, isnan
from itertools import product
from collections import defaultdict

# External Libraries
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# Custom Functions
from utils import *

# HTML Einstellungen
st.set_page_config(page_title="Timber Column Designer", layout="wide")
st.markdown("""<style>
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;margin-left: -500px;}
footer:after{
    content:"Cal Mense M.Eng. | Timber Column Designer | Version 1";
    display:block;
    position:relative;
    color:grey;}
    </style>""",unsafe_allow_html=True)

st.markdown('''
<style>
.katex-html {
    text-align: left;
}
</style>''',
unsafe_allow_html=True
)


L_loadDurationClass = ['permanent', 'long-term', 'medium-term', 'short-term', 'instantaneous']    # load duration classes
L_timber_type = ['Glulam', 'Softwood', 'Hardwood']
L_serviceClass = [1, 2, 3]
L_kmod = [[0.6, 0.7, 0.8, 0.9, 1.1], [0.6, 0.7, 0.8, 0.9, 1.1], [0.5, 0.55, 0.65, 0.7, 0.9]]
L_grades = ['GL24h', 'GL24c', 'GL28h','GL28c', 'GL32h', 'GL32c']
L_lamella = []

st.header("Timber Column Designer")
st.write("This application visualizes rectangular cross-sections of concrete beams.")

with st.sidebar:
    st.header("Parameter")

    grade = st.selectbox("Grade", L_grades)
    serviceClass = float(st.selectbox('Service Class', L_serviceClass))
    loadDurationClass = str(st.selectbox('Load Duration Class', L_loadDurationClass))
    support = st.selectbox("Support", ["pinned", "fixed", 'fixed (top), fixed (bottom)'], 0)

    st.write("Slab")
    with st.expander("Coordinates"):
        # input editable table
                
        df = pd.DataFrame(
            [
                {"xCord": 0, "yCord": 0},
                {"xCord": 40, "yCord": 0},
                {"xCord": 40, "yCord": 40},
                {"xCord": 0, "yCord": 40},
                {"xCord": 0, "yCord": 0},
        ])


        edited_df_slab = st.data_editor(df, hide_index=True, num_rows="dynamic", width=400) 
        xSlab = edited_df_slab["xCord"]
        ySlab = edited_df_slab["yCord"]




# _______________________main_______________________________________
# __________________________________________________________________
        
st.subheader("Table")
st.write("The table below is interactive and editable. You can easily paste data from applications like Excel. Utilize the **Select** buttons to display your desired column.")
# input editable table
        
df = pd.DataFrame(
    [
        {"Select": True, "Title": "S-201", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 1000, "Myd": 30, "Mzd": 10, "xCord": 3, "yCord": 3},
        {"Select": False, "Title": "S-202", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 1200, "Myd": 60, "Mzd": 80, "xCord": 17, "yCord": 3},
        {"Select": False, "Title": "S-203", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 1400, "Myd": 5, "Mzd": 25, "xCord": 17, "yCord": 37},
        {"Select": False, "Title": "S-204", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 800, "Myd": 5, "Mzd": 25, "xCord": 3, "yCord": 37},
        {"Select": False, "Title": "S-205", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 400, "Myd": 5, "Mzd": 25, "xCord": 3, "yCord": 20},
        {"Select": False, "Title": "S-206", "Length": 4, "Width": 0.5, "Height": 0.4, "Ned": 500, "Myd": 5, "Mzd": 25, "xCord": 17, "yCord": 20},
   ])


edited_df = st.data_editor(df, hide_index=True, num_rows="dynamic", width=1200, height=300) 

# get index of the selected table
ListIndex = [x for x in edited_df["Select"]]
ListIndexFiltered = [n for n,bool in enumerate(ListIndex) if bool == True]
index = 0 if not ListIndexFiltered else ListIndexFiltered[0]

# support, length, width, height, N_ed, M_yd, M_zd, f_c0k, f_myk, f_mzk, E_0mean, G_05, k_mod, gamma  
# Sytem und Geometrie
L_title = [x for x in edited_df["Title"]]
L_length = [y for y in edited_df["Length"]]
L_width = [y for y in edited_df["Width"]]
L_height = [y for y in edited_df["Height"]]
L_N_ed = [y for y in edited_df["Ned"]]
L_M_yd = [y for y in edited_df["Myd"]]
L_M_zd = [y for y in edited_df["Mzd"]]

title = L_title[index]
length = L_length[index]
width = L_width[index]
height = L_height[index]
N_ed = L_N_ed[index]
M_yd = L_M_yd[index]
M_zd = L_M_zd[index]

titles = edited_df["Title"]
xCols = edited_df["xCord"]
yCols = edited_df["yCord"]

# ____________________calculation___________________________________
# __________________________________________________________________

# load duration
k_mod, gamma, chi = get_kmod(serviceClass, loadDurationClass)

# timber properties
glulam_class, name, rho_k, f_myk, f_t0k, f_t90k, f_c0k, f_c90k, f_vk, E_0mean, E_05, G_05 = get_glulam_properties(grade)

# column design 
e_0, L_lamb, L_lamb_rel, L_ky, L_kc, k_crit, sigma_cd, L_sigma_md, L_eta, nw = ec5_63_esv(support, length, width, height, N_ed, M_yd, M_zd, f_c0k, f_myk, f_myk, E_05, G_05, k_mod, gamma)



# ____________________Graph_________________________________________
# __________________________________________________________________

# Create the line chart
fig = go.Figure(data=go.Scatter(x=xSlab, y=ySlab, mode='lines'))

# column markers
for i in range(len(xCols)):
    addColumn(fig, xCols, yCols, 0.5)
# update layout
fig.update_layout(
    autosize=False,
    width = 800,
    height = 600,
    uirevision='static',
    xaxis=dict(scaleanchor="y", scaleratio=1, fixedrange=True, visible=False),
    yaxis=dict(scaleanchor="x", scaleratio=1, fixedrange=True, visible=False),
    showlegend=False)

# add text
for i, x in enumerate(xCols):
    e_0, L_lamb, L_lamb_rel, L_ky, L_kc, k_crit, sigma_cd, L_sigma_md, L_eta, nw = ec5_63_esv(support, L_length[i], L_width[i], L_height[i], L_N_ed[i], L_M_yd[i], L_M_zd[i], f_c0k, f_myk, f_myk, E_05, G_05, k_mod, gamma)
    add_text(fig, L_title[i], x+1, yCols[i]+1, 20, "black")
    color = "green" if L_eta[0] < 1 else "red"
    add_text(fig, str(int(L_eta[0] * 100))+"%", x+1, yCols[i]-0.5, 20, color)


# Hide the axis
fig.update_xaxes(showline=False, showgrid=False, zeroline=False)
fig.update_yaxes(showline=False, showgrid=False, zeroline=False)

# Show the figure
st.write(fig)



# ____________________Report________________________________________
# __________________________________________________________________

# Create the line chart

with st.expander("Expand"):
    st.write("Hi")