Semae Altinkaynak
Cédric Bevilacqua

# Pretty-Printer

Le pretty-printer prend en entrée un Json et la traduit en une syntaxe JavaScript.

Les éléments suivants ont été implémentés : 
- Les expressions
- Déclarations et manipulations de variables
- Les conditions
- Les boucles while/for
- Les instructions break, continue ainsi que la fonction print

Le pretty-printer s'exécute correctement sur les exemples 1 à 7 fournis ainsi que sur des tests tels que des boucles ou conditions imbriquées. Néanmoins, ni les fonctions ni les objets n'ont été implémentés ici.

Le fonctionnement repose sur une méthode principale parcours_program qui va en fonction des éléments rencontrés orienter la ligne à exécuter vers des fonctions de plus en plus spécifiques jusqu'à arriver sur une fonction en capacité de traiter l'opération. A la fin, on retourne irrémédiablement sur la fonction principale jusqu'à ce qu'il n'y ait plus de lignes dans le Json.

# Interprète

L'interprète prend en entrée un Json et l'interprête à la manière d'une console JavaScript.

Les éléments suivants ont été implémentés : 
- Les expressions
- Déclarations et manipulations de variables
- Les conditions
- Les boucles while/for
- Les instructions break, continue ainsi que la fonction print
- Les fonctions

L'interprète s'exécute correctement sur les exemples 1 à 6 ainsi que sur l'exemple 11 de fonction. Les exécutions sont possibles sur des enchainements de fonction et on distingue correctement les variables qui se trouvent dans une fonction que en dehors. Néanmoins, cela ne fonctionne pas dans des conditions particulières comme des fonctions dans des fonctions. Les objets n'ont pas pu être implémenté jusqu'au bout, toutefois des traces de tentatives d'implémentations existent dans le code et les classes peuvent être correctement chargées en mémoire.

La structure du fonctionnement reprend celle du pretty-printer mais a été largement modifiée afin de correspondre aux contraintes d'une interprétation. Une des grandes différences a été la gestion de la mémoire. En effet, il a fallu créer une mémoire afin de gérer toutes les variables et autres, c'est une partie importante du travail qui a dû être réalisé. 

Pour gérer la mémoire, on retrouve énormément de dictionnaires ou de tableaux globaux. Certains éléments sontd es flags comme pour les break, continue ou return. Les méthodes concernées peuvent donc agir différemment quand elles sont sous le coup d'une de ces instructions, cela évite de rajouter à toute la chaine de fonctions des paramètres inutiles.

De même, de nombreux dictionnaires permettent de gérer les variables en associant leur nom à leur valeur ainsi que des dictionnaire distincts permettant de gérer la mémoire d'une fonction en contenant un dictionnaire propre à chaque fonction ou encore ses arguments de manière séparée des autres mémoires. Lorsqu'on utilise une variable, on cherche d'abord si elle existe dans la mémoire de la fonction, sinon, on va rechercher dans la mémoire principale. Une pile d'exécution permet de savoir dans quelle fonction on se trouve.

Cette pile d'exécution aurait également dû servir pour des fonctions imbriquées afin de pouvoir gérer plusieurs niveaux de fonction. Malheureusement, d'autres contraintes ont empêché cette imbrication d'être possible. De même, une mémoire particulière existe pour stocker les classes d'objet et donc les charger en mémoire pour une exécution future.

Le code est organisé en plusieurs fonction. La fonction principale est la fonction parcours_main qui parcours toutes les instructions présente dans le json. Les expressions arithmétiques et les affectations, incrémentations et décrementation sont réalisé dans la fonction decoder_expression, cette fonction s'occupe des sous expressions ou encore des plus petite expression comme les appels à des variables. Les variables sont gèrée par la fonction decoder_declaration qui va affecter à plusieurs variables globals :
- le type des variables
- le contenu des variables si elles sont initialisés
- le nom des variables
La fonction decoder_whileif s'occupera du cas des expressions tel que while, if et else. Elle executera le corps de instructions en faisant appel à parcours_main et en testant les conditions requise pour executer le corps de l'instruction. 
La fonction decoder_call est une fonction qui gère les print mais aussi les appels de fonctions. Elle initie donc des variables permettant de récuperer les variables locales des fonctions lors de l'execution d'une fonction par exemple.
La fonction decoder_for est une fonction ressemblant fortement à decoder_whileif, elle execute le corps de la boucle en incrèmentant la variable local et en testant la condition de boucle, elle fait appel à decoder_expression pour les tests et parcours_main pour executer le corps de la boucle.

# Compilateur

Le compilateur prend en entrée un JSON AST d'un script JavaScript pour en générer le code assembleur associé.

Les éléments suivants ont été implémentées : 
    - Déclarations de variables
    - Opérations arithmétiques
    - Incrémentation / décrémentation
    - Conditions if
    - Boucles conditionnelles while
    - Fonctions simples (sans arguments ni retour)

L'interprète d'exécute correctement sur les exemples 1 à 4 ainsi que sur l'exemple personnalisé "exemple_func".

Concernant la structure du programme, nous nous sommes appuyés sur la structure utilisée lors des TP précédents afin cette fois de générer le code C. Nous retrouvons donc la plupart des méthodes que nous avons vues précédemment, notamment les méthodes de point d'entrée parcours_main, puis parcours_program qui va parcourir chaque instruction du JSON ainsi que toutes les fonctions de compilation qui sont appelées à l'intérieur de parcours_program afin de traiter toutes les instructions supportées.

Concernant les fonctions, nous mettons en mémoire un dictionnaire contenant un numéro d'étiquette associé à un nom de fonction dans le dictionnaire functionNumberEtiquette. Un autre dictionnaire functionMemory contient le body de chaque fonction en JSON.

Ainsi, chaque appel de fonction amène à un code compilé de la fonction au travers d'un goto et des étiquettes qui à la fin revient à l'étiquette de retour se trouvant juste après le goto du code principal. C'est pour pouvoir toujours revenir à l'endroit où nous étions qu'on crée une nouvelle étiquette à chaque appel de la fonction.
