# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben
# Bibliotheken
from math import pi, sqrt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events
import numpy as np


# HTML Einstellungen
st.set_page_config(layout="wide")
st.markdown("""<style>
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;margin-left: -500px;}
footer:after{
    content:"Berliner Hochschule für Technik (BHT) | Konstruktiver Hoch- und Ingenieurbau (M.Eng.) | \
    Ingenieurholzbau | Prof. Dr. Jens Kickler | Cal Mense 914553";
    display:block;
    position:relative;
    color:grey;
}
</style>""",unsafe_allow_html=True)

#__________main page__________

# Text
#st.image('image_header_vg.png')
original_title = '<p style="font-family:Times; color:rgb(230, 40, 30); font-size: 60px;">P-Delta Analysis</p>'
st.markdown(original_title, unsafe_allow_html=True)

st.header('Non-linear Stability Check')
st.write("Especially in columns, practically unavoidable imperfections and pre-deformations in construction can lead to instability in the structure, \
        making the consideration of equilibrium in the deformed system crucial. As an alternative to design using the equivalent member method, the load-bearing \
        capacity is demonstrated according to the second-order theory by establishing the equilibrium system with a pre-deformation. However, for the sake of simplification, \
        the linear-elastic material behavior is still utilized as an idealization in the analysis of nonlinear internal forces.\
        The design process now proceeds with the assessment of a rectangular wooden column supported on both sides with hinges.")

st.image('Capture.PNG')
st.subheader('Input Parameters')

# class load_duration_class:
#    def __innit__(self, kled, kmod)

L_kled = ['permanent', 'long-term', 'medium-term', 'short-term', 'instantaneous']
L_material = ['Timber', 'Steel', 'Concrete']
L_service_class = [1, 2, 3]
L_kmod = [[0.6, 0.7, 0.8, 0.9, 1.1], [0.6, 0.7, 0.8, 0.9, 1.1], [0.5, 0.55, 0.65, 0.7, 0.9]]
L_rho_k = [380, 350, 410, 380, 430, 410, 450, 430]
L_holzart = ['GL24h', 'GL24c', 'GL28h',
             'GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c']

d = {'permanent': [0.6, 0.6, 0.5], 'long-term': [0.7, 0.7, 0.55], 'medium-term': [0.8, 0.8, 0.65], 'short-term': [0.9, 0.9, 0.7], 'instantaneous': [1.1, 1.1, 0.9]}
pd.DataFrame(data=d, index=[1, 2, 3])

#def xlookup(lookup_value, lookup_array, return_array, if_not_found:str = ''):
#    match_value = return_array.loc[lookup_array == lookup_value]
#    if match_value.empty:
#        return f'"{lookup_value}" not found!' if if_not_found == '' else

col1, col2, col3, col4, col5 = st.columns(5, gap="small")
with col1:
    st.write('System')
    bearing = st.selectbox('Bearing', ('pinned', 'fixed'))
    material = st.selectbox('Material', L_material)
    grade = st.selectbox('Grade', L_holzart)
    if bearing == "pinned":
        beta = 1.0
    elif bearing == "fixed":
        beta = 0.5

with col2:
    st.write('Geometry')
    L = float(st.text_input('Length [m]', 3))
    b = float(st.text_input('Width [m]', 0.5))
    h = float(st.text_input('Height [m]', 0.4))
        
with col3:
    st.write('Design Forces')
    N_ed = int(st.text_input('Ned [kN]', 2000))
    M_yd = int(st.text_input('Myd [kNm]', 30))
    M_zd = int(st.text_input('Mzd [kNm]', 40))
    
with col4:
    st.write('Material Values')
    f_c0k = int(st.text_input('f_c0k [N/mm2]', 28))
    f_mk = int(st.text_input('f_myk [N/mm2]', 28))
    E_0mean = int(st.text_input('E_0mean [N/mm2]', 12500))
    f_mzk = f_myk = f_mk
    E_0mean = E_0mean
    
with col5:
    st.write('Resistance Values')
    k_mod = float(st.text_input('k_mod', 0.8))
    gamma = float(st.text_input('gamma', 1.3))
  
# Calculation
## System
st.subheader('System')
col11, col22, col33, col44 = st.columns(4, gap="small")
with col11:
    st.latex("Effective Length")
    l_ef = L*beta
    st.latex(r"L_{ef}=L*\beta=" + str(l_ef) + r"m")
    A = b*h    # $m^2$ - Querschnitt
    
with col22:
    st.latex("Reduction Factor")
    chi = k_mod/gamma    # Abminderungsbeiwert
    st.latex(r"\chi=\frac{k_{mod}}{\gamma}=" + str("{:+.2f}".format(chi)))
    
with col33:
    st.latex("Predeformation")
    theta = 1/400    # Predeformation
    st.latex(r"\theta=" + str(theta))
    

# Cross-sectional Parameters
st.subheader('Cross-sectional Parameters') 
col111, col222, col333, col444 = st.columns(4, gap="small")
with col111:
    st.latex("y-Axis")
    I_y = (b*h**3)/12    # $m^4$ - FTM
    w_y = (b*h**2)/6    # $m^3$ - Widerstandsmoment
    i_y = h/sqrt(12)    # $m$ - polares Trägheitsmoment
    
    st.latex(r"I_{y}=\frac{b*h^3}{12}=" + str("{:.4f}".format(I_y)) + r" m^4")
    st.latex(r"w_{y}=\frac{b*h^2}{6}=" + str("{:.4f}".format(w_y)) + r" m^3")
    st.latex(r"i_{y}=\frac{h}{\sqrt{12}}=" + str("{:.4f}".format(i_y)) + r" m^4")
    
with col222:
    st.latex("z-Axis")
    I_z = (h*b**3)/12    # $m^4$ - FTM
    w_z = (h*b**2)/6    # $m^3$ - Widerstandsmoment
    i_z = b/sqrt(12)    # $m$ - polares Trägheitsmoment
    
    st.latex(r"I_{z}=\frac{h*b^3}{12}=" + str("{:.4f}".format(I_z)) + r" m^4")
    st.latex(r"w_{z}=\frac{h*b^2}{6}=" + str("{:.4f}".format(w_z)) + r" m^3")
    st.latex(r"i_{z}=\frac{b}{\sqrt{12}}=" + str("{:.4f}".format(i_z)) + r" m^4")

with col333:
    st.latex("Strengths")
    f_c0d = f_c0k*chi    # $N/mm^2$ - Bemessungswert der Druckfestigkeit
    f_myd = f_myk*chi    # $N/mm^2$ - Bemessungswert der Biegefestigkeit
    f_mzd = f_mzk*chi    # $N/mm^2$ - Bemessungswert der Biegefestigkeit
    E_0meand =E_0mean/gamma    # $N/mm^2$ - Bemessungswert der Biegefestigkeit
    
    st.latex(r"f_{c0d}=f_{c0k}*\chi=" + str("{:.1f}".format(f_c0d)) + r" N/mm^2")
    st.latex(r"f_{myd}=f_{mzd}=f_{myk}*\chi=" + str("{:.1f}".format(f_myd)) + r" N/mm^2")
    st.latex(r"E_{0meand}=E_{0mean}*\chi=" + str("{:.1f}".format(E_0meand)) + r" N/mm^2")

# First Order Theory
st.subheader('First Order Theory') 
st.write("DIN EN 1995-1-1 Abs- 5.4.3")
col1111, col2222, col3333, col4444 = st.columns(4, gap="small")
with col1111:
    e_0 = l_ef*theta    # m   
    st.latex(r"e_{0}=L_{ef}*\theta=" + str("{:+.4f}".format(e_0)) + r" m")
  
with col2222:
    M_0 = e_0*N_ed    # kNm
    st.latex(r"M_{0}=e_{0}*N_{ed}=" + str("{:+.1f}".format(M_0)) + r" kNm")

# Beiwert k_m
if M_yd == 0 or M_zd == 0:
    L_km = [[1,1],[1,1]]
else:
    L_km = [[1,0.7],[0.7,1]]
    
# Listen
L_bh = [[b,h],[h,b],[b,h],[h,b]]
L_e = [[e_0*1000],[0],[0],[e_0*1000]]
L_M = [[M_yd+M_0],[M_zd],[M_yd],[M_zd+M_0]]
L_e_total = [[e_0*1000],[0],[0],[e_0*1000]]
L_M_total = [[M_yd+M_0],[M_zd],[M_yd],[M_zd+M_0]]
L_sigma_mIId = []
L_Mi = [M_yd+M_0, M_zd, M_yd, M_zd+M_0]

# Schleife 1: Schnittgrößenermittlung nach Theorie II. Ordnung
for n in range(4):

    ## Querschnittsparameter
    A = b*h    # $m^2$ 
    I = (L_bh[n][0]*L_bh[n][1]**3)/12    # $m^4$ - FTM
    w = (L_bh[n][0]*L_bh[n][1]**2)/6    # $m^3$ - Widerstandsmoment
    i = L_bh[n][1]/sqrt(12)    # $m$ - polares Trägheitsmoment

    ## Theorie II. Ordnung
    # Schleife 2
    for i in range(5):  

        ## Ermittlung der Werte
        e_i = (L_M[n][i]*l_ef**2)/(E_0meand*1000*I*pi**2)
        M_i = e_i * N_ed

        ## Anhängen der Werte in Listen
        L_e[n].append(round(e_i*1000,2))
        L_M[n].append(round(M_i,2)) 
        e_total = sum(L_e[n])
        M_total = sum(L_M[n])
        L_e_total[n].append(round(e_total,2))
        L_M_total[n].append(round(M_total,2))

    # Spannungen
    sigma_mIId = L_M_total[n][-1]/w #$kN/m^2$
    L_sigma_mIId.append(round(sigma_mIId,0))

# Ergebnisse in Listen
## Verformungen und Momente
L_e_res = [[L_e[0][-1], L_e[1][-1]], [L_e[2][-1], L_e[3][-1]]]
L_M_res = [[L_M[0][-1], L_M[1][-1]], [L_M[2][-1], L_M[3][-1]]]
L_e_total_res = [[L_e_total[0][-1], L_e_total[1][-1]], [L_e_total[2][-1], L_e_total[3][-1]]]
L_M_total_res = [[L_M_total[0][-1], L_M_total[1][-1]], [L_M_total[2][-1], L_M_total[3][-1]]]

## Spannungen nach Theorie II. Ordnung
sigma_cd = N_ed/A
sigma_myIId_imp = L_sigma_mIId[0]
sigma_mzIId = L_sigma_mIId[1]
sigma_myIId = L_sigma_mIId[2]
sigma_mzIId_imp = L_sigma_mIId[3]
L_sigma_mIId = [[sigma_myIId_imp, sigma_mzIId], [sigma_myIId, sigma_mzIId_imp]]

# Tables
## Erstellen eines Dictionaries
st.subheader('Second Order Theory') 

# Erstellen der Tabelle
# red = '#ff4b4b'
# dark_grey = 'lightslategrey'
# dict_y = {'values': ["Δey [mm]",  "ΔMy [kNm]", "∑ey [mm]", "∑My [kNm]"], \
#              'align': 'center', 'font': {'size': 15, 'color': 'black'}, 'fill_color': dark_grey, 'line_color': 'white'}
# df_y = {'values': [L_e[0],  L_M[0], L_e_total[0], L_M_total[0]], 'height': 30, 'font': {'size': 15, 'color': 'black'}}
# dict_z = {'values': ["Δey [mm]",  "ΔMy [kNm]", "∑ey [mm]", "∑My [kNm]"], \
#               'align': 'center', 'font': {'size': 15, 'color': 'black'}, 'fill_color': dark_grey, 'line_color': 'white'}
# df_z = {'values': [L_e[1],  L_M[1], L_e_total[1], L_M_total[1]], 'height': 30, 'font': {'size': 15, 'color': 'black'}}

col1111, col2222 = st.columns(2, gap="medium")
with col1111:
    st.latex("y-Axis")
    # tabelle = go.Figure(data=[go.Table(header=dict_y, cells=df_y, columnwidth=[20])])
    # st.write(tabelle)
    
    dict_y_table = {"Δey [mm]": L_e[0], "ΔMy [kNm]": L_M[0], "∑ey [mm]": L_e_total[0], "∑My [kNm]": L_M_total[0]}
    df = pd.DataFrame(dict_y_table)
    st.table(df)
    
    dict_y_chart = {"ΔMy [kNm]": L_M[0]}
    chart_data = pd.DataFrame(dict_y_chart)
    st.line_chart(chart_data)
    
with col2222:
    st.latex("z-Axis")
    dict_z_table = {"Δez [mm]": L_e[1], "ΔMz [kNm]": L_M[1], "∑ez [mm]": L_e_total[1], "∑Mz [kNm]": L_M_total[1]}
    df = pd.DataFrame(dict_z_table)
    st.table(df)
    
    dict_z_chart = {"ΔMz [kNm]": L_M[1]}
    chart_data = pd.DataFrame(dict_z_chart)
    st.line_chart(chart_data)
    
k_m1 = L_km[0][0]
k_m2 = L_km[0][1]
sigma_my2d_imp = L_sigma_mIId[0][0]
sigma_mz2d = L_sigma_mIId[0][1]

k_m3 = L_km[1][0]
k_m4 = L_km[1][1]
sigma_y2d = L_sigma_mIId[1][0]
sigma_mz2d_imp = L_sigma_mIId[1][1]

eta_y = (sigma_cd/(f_c0d*1000))**2 + k_m1*sigma_my2d_imp/(f_myd*1000) + k_m2*sigma_mz2d/(f_mzd*1000)
eta_z = (sigma_cd/(f_c0d*1000))**2 + k_m3*sigma_y2d/(f_myd*1000)  + k_m4*sigma_mz2d_imp/(f_mzd*1000)

# Results
st.subheader('Results') 
st.latex(r"\sigma_{cd}=\frac{N_{ed}}{A}=" + str("{:.2f}".format(sigma_cd/1000)) + r" N/mm^2")
col11111, col22222 = st.columns(2, gap="medium")
with col11111:
    st.latex(r"e_{toty}=" + str("{:.2f}".format(L_e_total[0][-1])) + r" mm")
    st.latex(r"M_{toty}=" + str("{:.2f}".format(L_M_total[0][-1])) + r" kNm")
    st.latex(r"\sigma_{m2ydimp}=\frac{M_{totyd}}{w_y}=" + str("{:.2f}".format(sigma_myIId_imp/1000)) + r" N/mm^2")
    st.latex(r"\sigma_{m2zd}=\frac{M_{2zd}}{w_z}=" + str("{:.2f}".format(sigma_mz2d/1000)) + r" N/mm^2")
    st.latex(r"k_{m1}=" + str(k_m1))
    st.latex(r"k_{m2}=" + str(k_m2))
    st.latex(r"\eta_{y}=(\frac{\sigma_{cd}}{f_{cd0}})^2+k_{m1}*\frac{\sigma_{m2ydimp}}{f_{myd}}+k_{m2}*\frac{\sigma_{m2zd}}{f_{mzd}} = " + str("{:.2f}".format(eta_y)))

   
with col22222:
    st.latex(r"e_{totz}=" + str("{:.2f}".format(L_e_total[1][-1])) + r" mm")
    st.latex(r"M_{totz}=" + str("{:.2f}".format(L_M_total[1][-1])) + r" kNm")
    st.latex(r"\sigma_{my2d}=\frac{M_{2yd}}{w_y}=" + str("{:.2f}".format(sigma_y2d/1000)) + r" N/mm^2")
    st.latex(r"\sigma_{mz2dimp}=\frac{M_{totzd}}{w_z}=" + str("{:.2f}".format(sigma_mz2d_imp/1000)) + r" N/mm^2")
    st.latex(r"k_{m1}=" + str(k_m3))
    st.latex(r"k_{m2}=" + str(k_m4))
    st.latex(r"\eta_{z}=(\frac{\sigma_{cd}}{f_{cd0}})^2+k_{m1}*\frac{\sigma_{mzd}}{f_{mzd}}+k_{m2}*\frac{\sigma_{m2zdimp}}{f_{mzd}} = " + str("{:.2f}".format(eta_z)))

