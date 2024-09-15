# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben
# Bibliotheken
from math import pi, sqrt, cos, sin, atan
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from itertools import product
from collections import defaultdict

# Function to get modification factor
def get_kmod(serviceClass, loadDurationCLass):

    # Define service class, load duration class, and modification factor
    df_dict = {'permanent': [0.6, 0.6, 0.5], 
               'long-term': [0.7, 0.7, 0.55], 
               'medium-term': [0.8, 0.8, 0.65], 
               'short-term': [0.9, 0.9, 0.7], 
               'instantaneous': [1.1, 1.1, 0.9]}
    df = pd.DataFrame(data=df_dict, index=[1, 2, 3])
    
    # Look up the modification factor
    k_mod = float(df.at[serviceClass, loadDurationCLass])
    
    # Calculate gamma and chi
    gamma = 1.3
    chi = k_mod/gamma
    
    return k_mod, gamma, chi

# Timber properties
L_glulam_classes = []

# Define lists for timber properties
# DIN EN 14080
L_grades = ["GL20c", "GL22c", "GL24c", "GL26c", "GL28c", "GL30c", "GL32c", "GL20h", "GL22h", "GL24h", "GL26h", "GL28h", "GL30h", "GL32h"]
L_rhok = [355, 355, 365, 385, 390, 390, 400, 340, 370, 385, 405, 425, 430, 440]
L_fmk = [20, 22, 24, 26, 28, 30, 32, 20, 22, 24, 26, 28, 30, 32]
L_t0k = [15, 16, 17, 19, 19.5, 19.5, 19.5, 16, 17.6, 19.2, 20.8, 22.3, 24, 25.6]
L_t90k = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
L_fc0k = [18.5, 20, 21.5, 23.5, 24, 24.5, 24.5, 20, 22, 24, 26, 28, 30, 32]
L_c90k = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
L_fvk = [3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
L_E0mean = [10400, 10400, 11000, 12000, 12500, 13000, 13500, 8400, 10500, 11500, 12100, 12600, 13600, 14200]
L_E05 = [8600, 8600, 9100, 10000, 10400, 10800, 11200, 7000, 8800, 9860, 10100, 10500, 11300, 11800]
L_G05 = [540, 540, 540, 540, 540, 540, 540, 540, 540, 540, 540, 540, 540, 540]

# Class for glulam properties
class Glulam:
    def __init__(self, name, rho_k, f_mk, f_c0k, f_t0k, f_t90k, f_c90k, f_vk, E0mean, E05, G05):
        self.name = name
        self.rho_k = rho_k
        self.f_mk = f_mk
        self.f_t0k = f_t0k
        self.f_t90k = f_t90k
        self.f_c0k = f_c0k
        self.f_c90k = f_c90k
        self.f_vk = f_vk
        self.E0mean = E0mean
        self.E05 = E05
        self.G05 = G05

# Instantiate objects using a loop
for i in range(len(L_grades)):
    L_glulam_classes.append(Glulam(L_grades[i], L_rhok[i], L_fmk[i], L_t0k[i], L_t90k[i], L_fc0k[i], L_c90k[i], L_fvk[i], L_E0mean[i], L_E05[i], L_G05[i]))

# Function to get glulam properties
def get_glulam_properties(grade):
    # Find index of the grade
    timber_index = L_grades.index(grade)
    
    # Retrieve glulam class
    glulam_class = L_glulam_classes[timber_index]
    
    # Retrieve timber properties
    name = L_glulam_classes[timber_index].name 
    rho_k = L_glulam_classes[timber_index].rho_k 
    f_myk = L_glulam_classes[timber_index].f_mk 
    f_t0k = L_glulam_classes[timber_index].f_t0k    
    f_t90k = L_glulam_classes[timber_index].f_t90k    
    f_c0k = L_glulam_classes[timber_index].f_c0k    
    f_c90k = L_glulam_classes[timber_index].f_c90k  
    f_vk = L_glulam_classes[timber_index].f_vk   
    E_0mean = L_glulam_classes[timber_index].E0mean    
    E_05 = L_glulam_classes[timber_index].E05   
    G_05 = L_glulam_classes[timber_index].G05 
    
    return glulam_class, name, rho_k, f_myk, f_t0k, f_t90k, f_c0k, f_c90k, f_vk, E_0mean, E_05, G_05

# Retrieve glulam properties for a specific grade
glulam_class, name, rho_k, f_myk, f_t0k, f_t90k, f_c0k, f_c90k, f_vk, E_0mean, E_05, G_05 = get_glulam_properties("GL24h")

def ec5_63_esv(support, length, width, height, N_ed, M_yd, M_zd, f_c0k, f_myk, f_mzk, E, G_05, k_mod, gamma):

    # Vorbereitung
    # Listen
    L_M = [M_yd, M_zd]
    L_bh = [[width, height], [height, width]]
    L_fmk = [f_myk, f_mzk]
    L_k_crit = [1, 1]
    L_lamb = []
    L_lamb_rel = []
    L_ky = []
    L_kc = []
    L_sigma_md = []
    L_eta = []
    L_nw = []
    L_w = []
    L_I = []

    # Beiwert km
    if M_yd == 0 or M_zd == 0:
        L_km = [[1, 1], [1, 1]]
    else:
        L_km = [[1, 0.7], [0.7, 1]]

    # if-Abfrage zur Bestimmung von beta
    if support == 'pinned':
        beta = 1
    elif support == 'cantilever':
        beta = 2
    elif support in ['fixed (top)', 'fixed (bottom)']:
        beta = 0.7
    else:
        beta = 0.5

    # Berechnung
    # Knicklänge
    l_ef = length*beta
    e_0 = 0

    # Bemessungswerte der Festigkeit
    xi = k_mod/gamma
    f_c0d = f_c0k*xi  # $N/mm^2$ - Bemessungswert der Druckfestigkeit
    f_myd = f_myk*xi  # $N/mm^2$ - Bemessungswert der Biegefestigkeit
    f_mzd = f_mzk*xi  # $N/mm^2$ - Bemessungswert der Biegefestigkeit

    

    # Schleife für Momente um y- und z-Achse
    for n, M in enumerate(L_M):

        # Querschnittsparameter
        A = width*height  # $m^2$
        I = (L_bh[n][0]*L_bh[n][1]**3)/12  # $m^4$ - FTM
        w = (L_bh[n][0]*L_bh[n][1]**2)/6  # $m^3$ - Widerstandsmoment
        i = L_bh[n][1]/sqrt(12)  # $m$ - polares Trägheitsmoment
        L_w.append(w)
        L_I.append(I)

        # Knicken
        lamb = (beta*l_ef)/i  # Schlankheitsgrad
        lamb_rel = lamb/pi*sqrt(f_c0k/E)  # bezogene Schlankheit
        k_y = 0.5*(1+0.1*(lamb_rel-0.3)+lamb_rel**2)  # Beiwert
        k_c = 1/(k_y+sqrt(k_y**2-lamb_rel**2))  # Knickbeiwert

        # Spannungen
        sigma_cd = N_ed/A/1000 # $N/mm^2$ - Druckspannung
        sigma_md = M/w/1000  # $N/mm^2$ - Biegespannung

        # Anhängen an Listen
        L_lamb.append(round(lamb, 2))
        L_lamb_rel.append(round(lamb_rel, 2))
        L_ky.append(round(k_y, 2))
        L_kc.append(round(k_c, 2))
        L_sigma_md.append(round(sigma_md, 2))

    # Kippen um starke Achse
    # Ermittlung des maßgebenden Widerstandsmoments
    index = L_w.index(max(L_w))
    w = L_w[index]
    width = L_bh[index][0]
    height = L_bh[index][1]
    f_mk = L_fmk[index]

    lamb_relm = sqrt(l_ef/(pi*width**2)) * \
        sqrt(f_mk/sqrt(E*G_05))  # bez. Schlankheitsgrad

    # Kippbeiwert
    if lamb_relm <= 0.75:
        k_crit = 1
    elif lamb_relm > 0.75 and lamb_relm < 1.4:
        k_crit = 1.56-0.75*lamb_relm
    elif lamb_relm > 1.4:
        k_crit = 1/lamb_relm**2

    if index == 0:
        L_k_crit[0] = k_crit
        L_k_crit[1] = 1

    elif index == 1:
        L_k_crit[0] = 1
        L_k_crit[1] = k_crit

    # Listen für Nachweise
    L_Md = [M_yd, M_zd]
    lamb_rel = min(L_lamb_rel)
    L_pot = [[1, 2], [2, 1]]
    k_crit_index = L_w.index(max(L_w))

    # Schleife für Nachweise
    for n, M in enumerate(L_Md):
        # EC5 Abs. 6.2.4: Biegung m/o Druck ohne Knicken ohne Kippen
        if k_crit == 1 and lamb_rel < 0.3:
            eta = (sigma_cd/f_c0d)**2 + \
                L_km[n][0]*L_sigma_md[0]/f_myd + L_km[n][1]*L_sigma_md[1]/f_mzd
            L_eta.append(round(eta, 2))
            nw = ('Sp')

        # EC5 Abs. 6.3.2: Biegung m/o Druck mit Knicken ohne Kippen
        elif k_crit == 1 and lamb_rel > 0.3:
            eta = (sigma_cd)/(f_c0d*L_kc[n]) + L_km[n][0] * \
                L_sigma_md[0]/f_myd + L_km[n][1]*L_sigma_md[1]/f_mzd
            L_eta.append(round(eta, 2))
            nw = ('Kn')

        # EC5 Abs. 6.3.3: Biegung m/o Druck mit Knicken und Kippen
        elif k_crit < 1 and lamb_rel < 0.3:
            eta = (sigma_cd)/(f_c0d*L_kc[n]) + (L_sigma_md[0]/(f_myd*L_k_crit[0])
                                                )**L_pot[n][0] + (L_sigma_md[1]/(f_mzd*L_k_crit[1]))**L_pot[n][1]
            L_eta.append(round(eta, 2))
            nw = ('Kn/Ki')

        else:
            eta = 0
            L_eta.append(round(eta, 2))
            nw = ('N/A')

    return e_0, L_lamb, L_lamb_rel, L_ky, L_kc, k_crit, sigma_cd, L_sigma_md, L_eta, nw

def addColumn(fig, xCoordinates, yCoordinates, diameter):
    for i in range(len(xCoordinates)):
        x = xCoordinates[i] 
        y = yCoordinates[i] 
        x1 = x + diameter
        y1 = y + diameter
        fig.add_shape(dict(type="circle", x0 = x, y0 = y, x1 = x1, y1 = y1), line_color='black', fillcolor = "black")

def add_text(fig, text, xPosition, yPosition, textSize, color):
    fig.add_annotation(dict(font=dict(size=textSize, color = color),
                                            x = xPosition,
                                            y = yPosition,
                                            showarrow=False,
                                            text=text,
                                            textangle=0,
                                            xanchor='left',
                                            xref="x",
                                            yref="y"))