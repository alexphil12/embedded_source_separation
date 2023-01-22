# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 11:00:30 2022

@author: alexa
"""

import librosa
import os
import numpy as np
import random as rd
import pandas as pd
import copy as cp
import scipy
import soundfile as sf
from scipy.stats import bernoulli
import matplotlib.pyplot as plt
from scipy import signal
import scipy.io.wavfile as siow
#%%
# chemin du dossier contenant les files de licture(format wav)
path = "C:/Users/alexa/OneDrive/Bureau/Dossier_source_audio"
  
# Change the directory
os.chdir(path)

  
# Read text File
  
  
freq=[]
signal1=[]
debut=[]  
nom=[]

# itère sur tous les fichiers
for file in os.listdir():
    # vérifie que le fichier est .wav
    if file.endswith(".wav"):
        file_path = f"{path}/{file}"
        hasard=rd.uniform(2,10)#on sélectionne 15 secondes n'importe où entre 2 et 10 secondes d'enregistrement
        y, sr = librosa.load(file_path,duration=15,offset=hasard,sr=44100)
        u=np.max(y)
        o=np.min(y)
        signal1.append((((y-o)/(u-o))-1/2)*2)#normalisation -1,1
        freq.append(sr)
        debut.append(hasard)
        nom.append(file)
        print(file)
tab=np.float32(np.empty((len(nom)*3,44100*5)))
#on découpe les extraits de 15 secondes en 3 extraits de 5.
for j in range(len(nom)*3):
    u=signal1[j//3]
    tab[j,:]=u[5*(j%3)*44100:5*(44100)*(j%3 +1)]
    
tab1=cp.deepcopy(tab)
tab2=cp.deepcopy(tab)
tab3=cp.deepcopy(tab)
tab4=cp.deepcopy(tab)
tab5=cp.deepcopy(tab)
tab6=np.empty_like(tab)

index=[]
nom_fichier=[]



for j in range(len(nom)):
    nom_fichier.append([nom[j]]*3)
nom_fichier=np.ndarray.flatten(np.array(nom_fichier)).astype(str).tolist()


data_sig_original=pd.DataFrame(tab)   
#on applique des effet sur les 96 fichiers originaux(6 effets + aucun=7*96 voix indépendantes)
for j in range(96):
    b, a = scipy.signal.butter(10, 1000, 'low',fs=44100)
    tab1[j,:] = np.float32(scipy.signal.filtfilt(b, a, tab[j,:]))
for j in range(96):
    b, a = scipy.signal.butter(10, 700, 'high',fs=44100)
    tab2[j,:] = np.float32(scipy.signal.filtfilt(b, a, tab[j,:]))
for j in range(96):
    n_steps = 8
    tab3[j,:] = np.float32(librosa.effects.pitch_shift(tab3[j,:], 44100, n_steps=n_steps))
for j in range(96):
    n_steps = -7
    tab4[j,:] = np.float32(librosa.effects.pitch_shift(tab4[j,:], 44100, n_steps=n_steps))
for j in range(96):
    n_steps = 12
    tab5[j,:] = np.float32(librosa.effects.pitch_shift(tab5[j,:], 44100, n_steps=n_steps))
#%%

#C'est une modulation en fréquence par une sinusoide
def Vibrato(entree,f_ech,f,A):
    out=np.empty_like(entree)
    for i in range(len(entree)):
        m=round(A*((1+np.cos(2*np.pi*(f/f_ech)*i))/2))
        if i<=m:
            out[i]=entree[i]
        else:
            out[i]=entree[i-m]
    return(out)
for j in range(96):
    A=300
    freq=5
    tab6[j,:] = np.float32(Vibrato(tab[j,:],44100,freq,A))


big_tab=np.float32(np.empty((8000,11025*3)).astype(float))



#pour écouter les effets audio en question, spécifié le chemin désiré
# à la place du mien.
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test1.wav", tab1[35,:], 44100)
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test2.wav", tab2[35,:], 44100)
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test3.wav", tab3[35,:], 44100)
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test4.wav", tab4[35,:], 44100)
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test5.wav", tab5[35,:], 44100)
sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/test6.wav", tab6[35,:], 44100)

#%%
big_tab[0:96]=tab[:,0:44100*3:4]
big_tab[96:96*2]=tab1[:,0:44100*3:4]
big_tab[96*2:96*3]=tab2[:,0:44100*3:4]
big_tab[96*3:96*4]=tab3[:,0:44100*3:4]
big_tab[96*4:96*5]=tab4[:,0:44100*3:4]
big_tab[96*5:96*6]=tab5[:,0:44100*3:4]
big_tab[96*6:96*7]=tab6[:,0:44100*3:4]
nom_fichier_big_tab=[]
freq_ech_big_tab=[]
Amplitude_des_sigs_big_tab=[]
nbr_voix_big_tab=[]
presence_bruit_big_tab=[]
effet_sonore_big_tab=[]
index_voix_big_tab=[]
for j in range(96*7):
    index_voix_big_tab.append([j])
    nom_fichier_big_tab.append(nom_fichier[j%96])
    freq_ech_big_tab.append(11025)
    Amplitude_des_sigs_big_tab.append([1])
    nbr_voix_big_tab.append(1)
    presence_bruit_big_tab.append("Faux")
    if j>=0 and j<96:
        effet_sonore_big_tab.append("aucun")
    if j>=96 and j<96*2:
        effet_sonore_big_tab.append("Filtre_passe_bas")
    if j>=96*2 and j<96*3:
        effet_sonore_big_tab.append("Filtre_passe_haut")
    if j>=96*3 and j<96*4:
        effet_sonore_big_tab.append("Pitch_shift_8/2")
    if j>=96*4 and j<96*5:
        effet_sonore_big_tab.append("Pitch_shift_-7/2")
    if j>=96*5 and j<96*6:
        effet_sonore_big_tab.append("Pitch_shift_12/2")
    if j>=96*6 and j<96*7:
        effet_sonore_big_tab.append("Vibrato")
     
        
        
        
    
#%%
sig=big_tab[96,:]+big_tab[250,:]+big_tab[500,:]
bruit=np.random.normal(0,0.003,3*11025)
sig=sig+bruit
sig=(((sig-min(sig))/(max(sig)-min(sig)))-1/2)*2

sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/Audio_test.wav", sig, 11025)
#%%
Amplitude_des_sigs=[]
effet_sonore=[]
#data_frame contenant le signal
df_sig=pd.DataFrame(big_tab)
#data_frame contenant les information du signal au même index
df_y=pd.DataFrame(index=range(0,8000),columns=["Nom_fichier","Fréquence_échantillonnage","Nbr_voix","Amplitude_relative_des_voix","Présence_bruit","Effet_sonores","Index_des_voix"])

df_y.loc[0:96*7-1,"Nom_fichier"]=nom_fichier_big_tab
df_y.loc[0:96*7-1,"Fréquence_échantillonnage"]=freq_ech_big_tab
df_y.loc[0:96*7-1,"Amplitude_relative_des_voix"]= Amplitude_des_sigs_big_tab
df_y.loc[0:96*7-1,"Nbr_voix"]=nbr_voix_big_tab
df_y.loc[0:96*7-1,"Présence_bruit"]= presence_bruit_big_tab
df_y.loc[0:96*7-1,"Effet_sonores"]=effet_sonore_big_tab
df_y.loc[0:96*7-1,"Index_des_voix"]=index_voix_big_tab



for j in range(96*7,8001):
    h=bernoulli(4/9)
    nb_voi=h.rvs(1)+1#le nombre de voix est décidé par une variable aléatoire de Bernoulli 
    index_voix=[0]*nb_voi#on peut choisir également de le fixer à deux pour créer les fichier mix.wav
    bruit_pas=bernoulli(0.6)
    result=bruit_pas.rvs(1)#environ deux tiers des fichier seront bruité
    if(result==1):
        sigma=rd.uniform(0.001,0.02)
        bruit=np.float32(np.random.normal(0,sigma,3*11025))
        bruit_vrai="Vrai"
    else:
        bruit=np.zeros((1,3*11025))
        bruit_vrai="Faux"
    for u in range(nb_voi):#on choisit au hasard parmis les signaux 'originaux'
        index_voix[u]=rd.randint(1 ,96*7-1)#pour créer les mélanges
    effet_sonore=[]
    for u in index_voix:
        effet_sonore.append(df_y.loc[u,"Effet_sonores"])
    coef=np.random.uniform(1,5,(nb_voi)).tolist()
    r=sum(coef)
    coef=np.multiply(coef,(1/r))
    if(bruit_vrai=="Vrai"):
        sigma2=np.array(sigma)
        coef=np.append(coef,sigma2)
    sigu=np.float32(np.zeros((3*11025)))
    for l in range(nb_voi):
        u=big_tab[index_voix[l],:]
        sigu=np.add(sigu,coef[l]*u)#on additionne et multiplie les signaux par leurs coef
    if(nb_voi==1):                 #pour créer les mix
        h=np.random.randint(-3,3)#cas où nb_voix=1, pour éviter la redondance avec les 
        if(h==0):               #signaux originaux, on pitch-shift le signal entre -3 et 3/12
            h=-1
        sig=librosa.effects.pitch_shift(sig,11025, n_steps=h)
        effet_sonore.append("Pitch_shift_"+str(h)+"/2")
    sigu=sigu+bruit
    u=np.max(sigu)
    o=np.min(sigu)
    sig=(((sigu-o)/(u-o))-1/2)*2#on copie le signal ainsi que ces information à
    df_sig.loc[j,:]=cp.deepcopy(np.float32(sigu))#leurs places dans les dataframes respectifs
    df_y.loc[j,"Nom_fichier"]="Mélange_audio_"+str(j-671)
    df_y.loc[j,"Fréquence_échantillonnage"]=11025
    df_y.loc[j,"Nbr_voix"]=nb_voi
    df_y.loc[j,"Amplitude_relative_des_voix"]=coef
    df_y.loc[j,"Présence_bruit"]=bruit_vrai
    df_y.loc[j,"Effet_sonores"]=effet_sonore
    df_y.loc[j,"Index_des_voix"]=index_voix
    if(j%100==0):
        print(j)
#%%

col=columns=["Nom_fichier","Fréquence_échantillonnage","Nbr_voix","Amplitude_relative_des_voix","Présence_bruit","Effet_sonores","Index_des_voix"]
#pour écrire les dataframes sous formes de csv
df_y.to_csv("C:/Users/alexa/OneDrive/Bureau/Dossier_source_audio/df_info.csv",columns=col,index=True)       
print("ok1") 
df_sig.to_csv("C:/Users/alexa/OneDrive/Bureau/Dossier_source_audio/df_signal.csv",index=True)
print("ok2")


