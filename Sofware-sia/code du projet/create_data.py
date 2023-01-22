"""

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
#Fonctionne sensiblement comme extract_data_construct
path = "C:/Users/alexa/OneDrive/Bureau/Dossier_source_audio"
  
os.chdir(path)
  

  
  
freq=[]
signal1=[]
debut=[]  
nom=[]


for file in os.listdir():
    if file.endswith(".wav"):
        file_path = f"{path}/{file}"
        hasard=rd.uniform(2,10)
        y, sr = librosa.load(file_path,duration=15,offset=hasard,sr=44100)
        u=np.max(y)
        o=np.min(y)
        signal1.append((((y-o)/(u-o))-1/2)*2)
        freq.append(sr)
        debut.append(hasard)
        nom.append(file)
        print(file)
tab=np.float32(np.empty((len(nom)*3,44100*5)))

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

for j in range(len(nom_fichier)):
    b, a = scipy.signal.butter(10, 1000, 'low',fs=44100)
    tab1[j,:] = np.float32(scipy.signal.filtfilt(b, a, tab[j,:]))
for j in range(len(nom_fichier)):
    b, a = scipy.signal.butter(10, 700, 'high',fs=44100)
    tab2[j,:] = np.float32(scipy.signal.filtfilt(b, a, tab[j,:]))
for j in range(len(nom_fichier)):
    n_steps = 8
    tab3[j,:] = np.float32(librosa.effects.pitch_shift(tab3[j,:], 44100, n_steps=n_steps))
for j in range(len(nom_fichier)):
    n_steps = -7
    tab4[j,:] = np.float32(librosa.effects.pitch_shift(tab4[j,:], 44100, n_steps=n_steps))
for j in range(len(nom_fichier)):
    n_steps = 12
    tab5[j,:] = np.float32(librosa.effects.pitch_shift(tab5[j,:], 44100, n_steps=n_steps))
#%%
def Vibrato(entree,f_ech,f,A):
    out=np.empty_like(entree)
    for i in range(len(entree)):
        m=round(A*((1+np.cos(2*np.pi*(f/f_ech)*i))/2))
        if i<=m:
            out[i]=entree[i]
        else:
            out[i]=entree[i-m]
    return(out)
for j in range(len(nom_fichier)):
    A=300
    freq=5
    tab6[j,:] = np.float32(Vibrato(tab[j,:],44100,freq,A))



big_tab=np.float32(np.empty((9000,11025*5)).astype(float))


#%%
big_tab[0:96]=tab[:,0:44100*5:4]
big_tab[96:96*2]=tab1[:,0:44100*5:4]
big_tab[96*2:96*3]=tab2[:,0:44100*5:4]
big_tab[96*3:96*4]=tab3[:,0:44100*5:4]
big_tab[96*4:96*5]=tab4[:,0:44100*5:4]
big_tab[96*5:96*6]=tab5[:,0:44100*5:4]
big_tab[96*6:96*7]=tab6[:,0:44100*5:4]
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
bruit=np.random.normal(0,0.003,5*11025)
sig=sig+bruit
sig=(((sig-min(sig))/(max(sig)-min(sig)))-1/2)*2

sf.write("C:/Users/alexa/OneDrive/Bureau/Dossier_test_audio/Audio_test.wav", sig, 11025)
#%%
Amplitude_des_sigs=[]
effet_sonore=[]

df_sig=pd.DataFrame(big_tab)
df_y=pd.DataFrame(index=range(0,9000),columns=["Nom_fichier","Fréquence_échantillonnage","Nbr_voix","Amplitude_relative_des_voix","Présence_bruit","Effet_sonores","Index_des_voix"])

df_y.loc[0:96*7-1,"Nom_fichier"]=nom_fichier_big_tab
df_y.loc[0:96*7-1,"Fréquence_échantillonnage"]=freq_ech_big_tab
df_y.loc[0:96*7-1,"Amplitude_relative_des_voix"]= Amplitude_des_sigs_big_tab
df_y.loc[0:96*7-1,"Nbr_voix"]=nbr_voix_big_tab
df_y.loc[0:96*7-1,"Présence_bruit"]= presence_bruit_big_tab
df_y.loc[0:96*7-1,"Effet_sonores"]=effet_sonore_big_tab
df_y.loc[0:96*7-1,"Index_des_voix"]=index_voix_big_tab



for j in range(96*7,8001+96*7):
    h=bernoulli(4/9)
    nb_voi=2   #on fixe nb=2 car on veut créer un dataframe ne contenant que des mix
    index_voix=[0]*nb_voi # de 2 voix
    bruit_pas=bernoulli(0.6)
    result=bruit_pas.rvs(1)
    if(result==1):
        sigma=rd.uniform(0.001,0.02)
        bruit=np.float32(np.random.normal(0,sigma,5*11025))
        bruit_vrai="Vrai"
    else:
        bruit=np.zeros((1,5*11025))
        bruit_vrai="Faux"
    for u in range(nb_voi):
        index_voix[u]=rd.randint(1 ,96*7-1)
    effet_sonore=[]
    for u in index_voix:
        effet_sonore.append(df_y.loc[u,"Effet_sonores"])
    coef=np.random.uniform(1,5,(nb_voi)).tolist()
    r=sum(coef)
    coef=np.multiply(coef,(1/r))
    if(bruit_vrai=="Vrai"):
        sigma2=np.array(sigma)
        coef=np.append(coef,sigma2)
    sigu=np.float32(np.zeros((5*11025)))
    for l in range(nb_voi):
        u=big_tab[index_voix[l],:]
        sigu=np.add(sigu,coef[l]*u)
    if(nb_voi==1):
        h=np.random.randint(-3,3)
        if(h==0):
            h=-1
        sig=librosa.effects.pitch_shift(sig,11025, n_steps=h)
        effet_sonore.append("Pitch_shift_"+str(h)+"/2")
    sigu=sigu+bruit
    u=np.max(sigu)
    o=np.min(sigu)
    sig=(((sigu-o)/(u-o))-1/2)*2
    df_sig.loc[j,:]=cp.deepcopy(np.float32(sigu))
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

#Cette partie écrit les signaux mixée ainsi que les signaux s1 et s2 allant avec dans
N=8000# des dossier train/mix ... valid/s2 qui seront ensuite parcourue pendant le preprocess
prop_test=0.2
prop_val=0.1
N1=round(0.7*7001)+7*96;
N2=round(0.2*7001)
N3=round(0.1*7001)
for j in range(7*96,N1):
    de=np.random.randint(0,11025*2)#on choisit pour chacun des fichier mix,s1,s2 d'un set(train,valid,tes) une longueur aléatoire entre 1 et 5 secondes
    fin=np.random.randint(11025*3,11025*5-1)
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/train/mix/mix"+str(j)+".wav",11025,df_sig.loc[j,de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/train/s1/s1-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][0],de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/train/s2/s2-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][1],de:fin])
    if(j%100==0):
        print(str(j)+" Avancement train")
for j in range(N1,N1+N2):
    de=np.random.randint(0,11025*2)
    fin=np.random.randint(11025*3,11025*5-1)
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/test/mix/mix"+str(j)+".wav",11025,df_sig.loc[j,de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/test/s1/s1-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][0],de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/test/s2/s2-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][1],de:fin])   
    if(j%100==0):
        print(str(j)+" Avancement test")
for j in range(N1+N2,N1+N2+N3):
    de=np.random.randint(0,11025*2)
    fin=np.random.randint(11025*3,11025*5-1)
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/valid/mix/mix"+str(j)+".wav",11025,df_sig.loc[j,de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/valid/s1/s1-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][0],de:fin])
    siow.write("C:/Users/alexa/OneDrive/Bureau/Source-audio-SIA/valid/s2/s2-"+str(j)+".wav",11025,df_sig.loc[df_y.loc[j,"Index_des_voix"][1],de:fin])
    if(j%100==0):
        print(str(j)+" Avancement valid")





   