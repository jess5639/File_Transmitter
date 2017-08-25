File Transmitter
===================


Bienvenue sur la page de présentation de ce mini projet de stage.

File transmitter est un petit projet réalisé en python durant mon stage de première année en BTS. Je disposais à l'époque de maigre connaissances en programmation, et encore moins en python, donc le code n'est pas franchement propre. Zero découpage, tout d'une traite ou rien :D
 Je trouvais rigolo l'idée de le mettre sur un github! Qui sais, ça peut servir! Mon tuteur m'avais même proposé de le faire.

C'est un batch qui permet d'envoyer des fichiers d'un point A à un point B via FTP. Le but était de pouvoir faire communiquer deux applications - une produisant des fichiers - une autre les parsant pour agrémenter sa BDD. 

Le batch archive (de mémoire) les transferts OK dans un dossier nommé OK (coïncidence?) et les transferts KO dans un dossier KO.

Il scrute le répertoire configuré dans le fichier file_transmitter.xml, et dès qu'il trouve un fichier avec l'extension donnée il l'envoi.

Beaucoup de courage à ceux qui voudraient s'en servir.
