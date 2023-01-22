Pour utiliser l'implémentation suivante:
Assurer d'avoir l'environement adéquat etun GPU à disposition (cuda) faisant l'affaire.
Lire le requirement dans Tasnet.
Vous devez à partir du moment où vous avez les fichier wav constituant la base de votre base de donnée:
-executer le code, create data. celui ci vas alors au emplacement que vous aurez choisi, crée les dossiers contenant vos fichier wav mix,s1,s2 du train,test,valid
-ensuite executer le code preprocess-12.py dans Tasnet en spécifiant les chemins vers les dossier précédent pour créer les fichier json.
-vous pouvez ensuite lancer le train.py de Tasnet pour entrainer le réseau, separate pour qu'il sépare à partir du meilleurs model en validation les données
-ou evaluate pour connaitre ses performances sur le test set.
ps:extract-data-construct permis de sauvegarder le  dataframe de signal et celui des information sous format csv pouvant alors être utilisé sur colab par exemple ou jupyter notebook.4
pss:une fois le model entrainer et sauvegarder, vous pouvez utilisez lancer le code record and separate pour enregistrer une extrait audio de votre choix et tester sur celui ci la séparation.