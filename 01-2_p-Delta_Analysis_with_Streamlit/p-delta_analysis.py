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
    content:"Python for Structural Engineers | Konstruktiver Hoch- und Ingenieurbau (M.Eng.) | \
    | Cal Mense";
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

# Lists
L_ldc = ['permanent', 'long-term', 'medium-term', 'short-term', 'instantaneous']    # load duration classes
L_material = ['Timber', 'Steel', 'Concrete']
L_service_class = [1, 2, 3]
L_kmod = [[0.6, 0.7, 0.8, 0.9, 1.1], [0.6, 0.7, 0.8, 0.9, 1.1], [0.5, 0.55, 0.65, 0.7, 0.9]]
L_holzart = ['GL24h', 'GL24c', 'GL28h','GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c']
holzarten = ['GL24h', 'GL24c', 'GL28h','GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c']
L_rhok = [380, 350, 410, 380, 430, 410, 450, 430]
L_fmk = [28, 29, 30, 31, 32, 33, 34, 35]
L_fc0k = [38, 39, 40, 41, 42, 43, 44, 45]
L_E0mean = [8500, 8500, 8500, 41, 42, 43, 44, 45]

# Input Parameters
col1, col2, col3, col4, col5 = st.columns(5, gap="small")
with col1:
    st.write('System')
    bearing = st.selectbox('Bearing', ('pinned', 'fixed'))
    material = st.selectbox('Material', L_material)
    grade = st.selectbox('Grade', holzarten)

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
    st.write('Resistance Values')
    service_c = float(st.selectbox('Service Class', L_service_class))
    load_duration_c = str(st.selectbox('Load Duration Class', L_ldc))
  
# Classes
## Class for glulam properties
class glulam:
    def __init__(self, name, rho_k, f_mk, f_c0k, E0mean):
        self.name = name
        self.rho = rho_k
        self.f_mk = f_mk
        self.f_c0k = f_c0k
        self.E0mean = E0mean
        
## Class for cross-section
class section_yz:
    def __init__(self, direction, width, height, moment):
        self.direction = direction
        self.width = width
        self.height = height
        self.moment = moment
        
    def moment_of_inertia(self):
        return (self.width*self.height**3)/12    # $m^4$ - moment of inertia
    
    def section_modulus(self):
        return (self.width*self.height**2)/6    # $m^3$ - section modulus
    
    def polar_moment_of_inertia(self):
        return self.height/sqrt(12)    # $m$ - polar moment of inertia

# Functions
## Function to get beta
def get_beta(bearing):
    if bearing == "pinned":
        beta = 1.0
        return beta
    elif bearing == "fixed":
        beta = 0.5
        return 
    
## Function to create a list with km-values
def create_km(Moment_y, Moment_z):
    if M_yd == 0 or M_zd == 0:
        L_km = [[1,1],[1,1]]
        return L_km
    else:
        L_km = [[1,0.7],[0.7,1]]
        return L_km

## Function for p-Delta iteration
def p_delta_iteration(no_iteration, L_M, N_ed, l_ef, E_0meand):
    
    # Schleife 1: Schnittgrößenermittlung nach Theorie II. Ordnung
    for n in range(4):
        
        ## Querschnittsparameter
        I = L_I[n]
        w = L_w[n]
        i = L_i[n]

        ## Theorie II. Ordnung
        # Schleife 2
        for i in range(no_iteration):  

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
            
            ## x-values
            x = L_x.append(i)

        # Spannungen
        sigma_mIId = L_M_total[n][-1]/w #$kN/m^2$
        L_sigma_mIId.append(round(sigma_mIId,0))
        
    return x, L_e, L_M, e_total, M_total, L_e_total, L_M_total, L_sigma_mIId

def create_st_table(direction, L_e, L_M, L_e_total, L_M_total, n):
    st.latex(direction)
    
    # plotly tables
    dict_header = {'values': [('Δei', '[mm]'),  ('ΔMi', '[kNm]'), ('∑ei', '[mm]'), ('∑Mi', '[kNm]')],
                   'align': 'center', 
                   'font': {'size': 15, 'color': 'white'}, 
                   'fill_color': "#262730"}
    
    dict_cells = {'values': [L_e[n],  L_M[n], L_e_total[n], L_M_total[n]], 
                  'height': 30, 
                  'font': {'size': 15, 'color': 'white'},
                  'fill_color': ["#0E1117", "#0E1117", "#0E1117"]}
    
    tabelle = go.Figure(data=[go.Table(header=dict_header, 
                                       cells=dict_cells, 
                                       columnwidth=[40])])
    
    st.plotly_chart(tabelle)

def create_st_line_chart(direction, x, L_M_total, color, n):

    # plotly line chart
    fig = go.Figure(data=go.Scatter(x=x, 
                                    y=L_M_total[n], 
                                    mode='lines', 
                                    name='Line Chart', 
                                    line=dict(color=color, width=2)))      
    ## Customize layout
    fig.update_layout(
        title=direction,
        xaxis_title='Iteration i',
        yaxis_title='Moment')
    
    ## Display the chart using Streamlit
    st.plotly_chart(fig)
    
    
### Instantiation of objects
section_y = section_yz("y", b, h, M_yd)
I_y = section_y.moment_of_inertia()    # moment of intertia
w_y = section_y.section_modulus()     # section modulus
i_y = section_y.polar_moment_of_inertia()    # polar moment of intertia

section_z = section_yz("z", h, b, M_zd)
I_z = section_z.moment_of_inertia()    # moment of intertia
w_z = section_z.section_modulus()     # section modulus
i_z = section_z.polar_moment_of_inertia()    # polar moment of intertia

# Service class, load duration class and modification factor
## Creating a dataframe
df_dict = {'permanent': [0.6, 0.6, 0.5], 
           'long-term': [0.7, 0.7, 0.55], 
           'medium-term': [0.8, 0.8, 0.65], 
           'short-term': [0.9, 0.9, 0.7], 
           'instantaneous': [1.1, 1.1, 0.9]}
df = pd.DataFrame(data=df_dict, index=[1, 2, 3])

## lookup function to get k_mod
k_mod = float(df.at[service_c, load_duration_c])

# Calculation
## System
beta = get_beta(bearing)    # 
l_ef = L*beta    # m - effective length
A = b*h    # $m^2$ - cross-section
theta = 1/400    # predeformation
e_0 = l_ef*theta    # m - eccentricity
M_0 = e_0*N_ed    # kNm - initial moment

## Resistance Values
gamma = 1.3    # partial factor for material properties
chi = k_mod/gamma    # reduction factor

## Cross-sectional parameters
## Getting the index of the glulam type
timber_index = holzarten.index(grade)

## Instantiation of objects with a loop
for i in range(len(L_holzart)):
    L_holzart[i] = glulam(L_holzart[i], L_rhok[i], L_fmk[i], L_fc0k[i], L_E0mean[i])

# Strength
## Characteristic values from glulam class
f_c0k = L_holzart[timber_index].f_c0k    # $N/mm^2$ - characteristic compressive strength along the grain
f_mzk = f_myk = L_holzart[timber_index].f_mk    # $N/mm^2$ - characteristic bending strengths about y-axis
E_0mean = L_holzart[timber_index].E0mean    # $N/mm^2$ - characteristic E-modulus
    
## Design values
f_c0d = f_c0k*chi    # $N/mm^2$ - design compressive strength along the grain
f_myd = f_myk*chi    # $N/mm^2$ - design bending strengths about y-axis
f_mzd = f_mzk*chi    # $N/mm^2$ - design bending strengths about z-axis
E_0meand =E_0mean/gamma    # $N/mm^2$ - design E-modulus

# Factor k_m
L_km = create_km(M_yd, M_zd)    # lists with factors
   
# Lists
L_bh = [[b,h],[h,b],[b,h],[h,b]]
L_I = [I_y, I_z, I_y, I_z,]
L_w = [w_y, w_z, w_y, w_z,]
L_i = [i_y, i_z, i_y, i_z,]
L_e = [[e_0*1000],[0],[0],[e_0*1000]]
L_M = [[M_yd+M_0],[M_zd],[M_yd],[M_zd+M_0]]
L_e_total = [[e_0*1000],[0],[0],[e_0*1000]]
L_M_total = [[M_yd+M_0],[M_zd],[M_yd],[M_zd+M_0]]
L_Mi = [M_yd+M_0, M_zd, M_yd, M_zd+M_0]
L_sigma_mIId = []
L_x = []

# p-Delta iteration
no_iteration = 5
x, L_e, L_M, e_total, M_total, L_e_total, L_M_total, L_sigma_mIId = p_delta_iteration(no_iteration, 
                                                                                      L_M, 
                                                                                      N_ed, 
                                                                                      l_ef, 
                                                                                      E_0meand)

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


## System
st.subheader('System')
col11, col22, col33, col44 = st.columns(4, gap="small")
with col11:
    st.latex("Effective Length")
    st.latex(r"L_{ef}=L*\beta=" + str(l_ef) + r"m")
    
with col22:
    st.latex("Reduction Factor")
    st.latex(r"\chi=\frac{k_{mod}}{\gamma}=" + str("{:.2f}".format(chi)))
    
with col33:
    st.latex("Predeformation")
    st.latex(r"\theta=" + str(theta))
    
# Cross-sectional Parameters
st.subheader('Cross-sectional Parameters') 
col111, col222, col333, col444 = st.columns(4, gap="small")
with col111:
    st.latex("y-Axis")
    st.latex(r"I_{y}=\frac{b*h^3}{12}=" + str("{:.4f}".format(I_y)) + r" m^4")
    st.latex(r"w_{y}=\frac{b*h^2}{6}=" + str("{:.4f}".format(w_y)) + r" m^3")
    st.latex(r"i_{y}=\frac{h}{\sqrt{12}}=" + str("{:.4f}".format(i_y)) + r" m^4")
    
with col222:
    st.latex("z-Axis")
    st.latex(r"I_{z}=\frac{h*b^3}{12}=" + str("{:.4f}".format(I_z)) + r" m^4")
    st.latex(r"w_{z}=\frac{h*b^2}{6}=" + str("{:.4f}".format(w_z)) + r" m^3")
    st.latex(r"i_{z}=\frac{b}{\sqrt{12}}=" + str("{:.4f}".format(i_z)) + r" m^4")

with col333:
    st.latex("Strengths")
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
 

# Tables
## Erstellen eines Dictionaries
st.subheader('Second Order Theory') 

col1111, col2222 = st.columns(2, gap="medium")
with col1111:
    
    direction = 'y-Axis'
    n = 0
    color = "yellow"
    
    # plotly table
    table = create_st_table(direction, L_e, L_M, L_e_total, L_M_total, 0)

    # plotly line chart
    create_st_line_chart(direction, x, L_M_total, color, n)
    
with col2222:
    st.latex("z-Axis")
    
    # plotly tables
    dict_header = {'values': [('Δez', '[mm]'),  ('ΔMz', '[kNm]'), ('∑ez', '[mm]'), ('∑Mz', '[kNm]')],
                   'align': 'center', 
                   'font': {'size': 15, 'color': 'white'}, 
                   'fill_color': "#262730"}
    
    dict_cells = {'values': [L_e[1],  L_M[1], L_e_total[1], L_M_total[1]], 
                  'height': 30, 
                  'font': {'size': 15, 'color': 'white'},
                  'fill_color': ["#0E1117", "#0E1117", "#0E1117"]}
    
    tabelle = go.Figure(data=[go.Table(header=dict_header, 
                                       cells=dict_cells, 
                                       columnwidth=[40])])
    
    st.plotly_chart(tabelle)

    # plotly line chart
    fig = go.Figure(data=go.Scatter(x=x, 
                                    y=L_M_total[1], 
                                    mode='lines', 
                                    name='Line Chart', 
                                    line=dict(color='blue', width=2)))
    
    ## Customize layout
    fig.update_layout(
        title='z-Axis',
        xaxis_title='Iteration i',
        yaxis_title='Moment')
    
    ## Display the chart using Streamlit
    st.plotly_chart(fig)
    
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
