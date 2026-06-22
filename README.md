# pmeusainboltz
Implementation de la méthode de pointage pour Boltzmann dans usainboltz.
),

# feuille de route 
À peu près dans l'ordre de priorité:

#-----------------------------------------------------------Phase: début du stage
- Gérer les rulenames se pointant vers un ensemble vide.
(Fait)

- Gérer les arguments du générateur pour la construction de l'oracle.
(Fait)

- Retravailler les builders pour réaliser moins d'opérations à l'exécution des builders.
(Fait)

- Rajout des sets et cycles étiquetés.
(Fait, il y aura besoin d'aide pour les tests de cycle)

- Imaginer et implémenter des tests.
(Pas l'intention d'en rajouter pour l'instant.)

- Construire la théorie derrière la conversion des tuples.
(Entamé)

- Ajout de la gestion des arguments pour certaines constructions de classes.
(Fait)

- Intégration de la méthode de pointage dans la bibliothèque UsainBoltz.
(Git sur gitlab)
#----------------------------------------------------------- Phase close.

#----------------------------------------------------------- Mise au propre de ce qui a été fait.

- Finir la formalisation.
(Entamé, dernière preuve à construire, peut-être complété autres preuves et rajouté règles d'inférences)
	- Rajout du pointage de contexte.
	(Fait)

- Trouver quelques exemples pour le pointage.
(Trouver solution pour oracle et À mettre au propre)

- Tout relire.
(Fait pour grammar.py)

#---------------------------
- Mise en place de MSET et cycle non étiqueté.