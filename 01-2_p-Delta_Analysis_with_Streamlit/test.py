# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben
# Bibliotheken
from math import pi, sqrt
import pandas as pd
import numpy as np


L_kled = ['permanent', 'long-term', 'medium-term', 'short-term', 'instantaneous']
L_material = ['Timber', 'Steel', 'Concrete']
L_service_class = [1, 2, 3]
L_kmod = [[0.6, 0.7, 0.8, 0.9, 1.1], [0.6, 0.7, 0.8, 0.9, 1.1], [0.5, 0.55, 0.65, 0.7, 0.9]]
L_rho_k = [380, 350, 410, 380, 430, 410, 450, 430]
L_holzart = ['GL24h', 'GL24c', 'GL28h', 'GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c']

# dictionary
## lookup funktion
df_dict = {'permanent': [0.6, 0.6, 0.5], 'long-term': [0.7, 0.7, 0.55], 'medium-term': [0.8, 0.8, 0.65], 'short-term': [0.9, 0.9, 0.7], 'instantaneous': [1.1, 1.1, 0.9]}
df = pd.DataFrame(data=df_dict, index=[1, 2, 3])

# Query, um den Wert basierend auf Zeilen- und Spaltenindices zu erhalten
result = df.at[1,"permanent"]
print(result)

# classes
class glulam:
    def __init__(self, name, rho):
        self.name = name
        self.rho = rho

## dictionary - list of dictionary
dict1 = {"name": "GL24h", "rho_k": 380}
print(dict1["name"])

glulam_dict = [{"name": "GL24h", "rho": 380},
               {"name": "GL28h", "rho": 420}]
print(glulam_dict[0]["name"])

## inserting elements into the dictionary
gl1 = glulam("GL24h", 380)
print(gl1.name)
        
a = [glulam(daten["name"], daten["rho"]) for daten in glulam_dict]

# klasse glulam
glulam_dict = [{"name": "GL24h", "rho": 380, "fmk": 28,"fck": 38,"E0mean": 8500,},
               {"name": "GL24c", "rho": 390, "fmk": 29,"fck": 38,"E0mean": 8500,},
               {"name": "GL28h", "rho": 400, "fmk": 30,"fck": 38,"E0mean": 8500,},
               {"name": "GL28c", "rho": 410, "fmk": 31,"fck": 38,"E0mean": 8500,},
               {"name": "GL32h", "rho": 420, "fmk": 32,"fck": 38,"E0mean": 8500,},
               {"name": "GL32c", "rho": 430, "fmk": 33,"fck": 38,"E0mean": 8500,},
               {"name": "GL36h", "rho": 440, "fmk": 34,"fck": 38,"E0mean": 8500,},
               {"name": "GL36c", "rho": 450, "fmk": 35,"fck": 38,"E0mean": 8500,}]

L_holzart = ['GL24h', 'GL24c', 'GL28h','GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c']
L_rho_k = [380, 350, 410, 380, 430, 410, 450, 430]
L_fmk = [28, 29, 30, 31, 32, 33, 34, 35]
L_fc0k = [38, 39, 40, 41, 42, 43, 44, 45]
L_E0mean = [8500, 8500, 8500, 41, 42, 43, 44, 45]

# classes
class glulam:
    def __init__(self, name, rho, f_mk, f_c0k, E0mean):
        self.name = name
        self.rho = rho
        self.f_mk = f_mk
        self.f_c0k = f_c0k
        self.E0mean = E0mean

for i in range(len(L_holzart)):
    L_holzart[i] = glulam(L_holzart[i], L_rho_k[i], L_fmk[i], L_fc0k[i], L_E0mean[i])


# Überprüfe die erstellten Glulam-Objekte
for glulam_obj in L_holzart:
    print(f"{glulam_obj.name}: rho={glulam_obj.rho}, f_mk={glulam_obj.f_mk}, f_c0k={glulam_obj.f_c0k}, E0mean={glulam_obj.E0mean}")

a = L_holzart

print(a)