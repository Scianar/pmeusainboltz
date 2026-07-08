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


- Finir la formalisation.
(Entamé, dernière preuve à construire, peut-être complété autres preuves, peut-être rajouter un exemple)

- Rajout de MSET, PSET, UCYCLE
(PSET fait non testé, MSET fait par Martin non testé, UCYCLE à moitié testé)

- Mise en place de MSETCP et UCYCLECP non étiqueté pour la grammaire.
(fait pour la grammaire et insertion de la grammaire dans le générateur,
MSETCP et UCYCLECP non borné, non testé)

- Rédaction du rapport de stage.
(Entamé, 11 pages, un peu brouillon changer la definition de labelled et unlabelled pour le début, besoin d'exemples).

- Implémenter dérivation par rapport à une rulename.