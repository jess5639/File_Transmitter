# -*- coding: UTF-8 -*-
# Code produit par Jessy MARTIN - 2014
import os
import ftplib
import time
from datetime import datetime
import signal
import sys
import glob
import shutil
import logging
import logging.handlers
from logging.handlers import *
from lxml import etree
import smtplib
import sqlite3

from asyncore import dispatcher
import sys, time, socket


#Initialisation de la boucle
running = True

#Lecture du fichier XML
try:
	nf = sys.argv[0]
	nfcourt = (os.path.basename(nf)).split(".")
	nfparam = nfcourt[0] + ".xml"
	dir_path = os.path.dirname(os.path.abspath(sys.argv[0])) + "\\" + nfparam

	tree = etree.parse(dir_path)

	for parametre in tree.xpath("/config/connection/host"):
		host = parametre.text
	print host

	for parametre in tree.xpath("/config/connection/user"):
		user = parametre.text
	print user

	for parametre in tree.xpath("/config/connection/password"):
		password = parametre.text
	print password

	for parametre in tree.xpath("/config/action/backup"):
		if parametre.text == "True":
			backup = True
		else:
			backup = False
	print backup

	for parametre in tree.xpath("/config/action/repbackup"):
		dest_backup = parametre.text
	print dest_backup

	for parametre in tree.xpath("/config/general/rep_courant"):
		if (str(parametre.text) == 'oui'):
			current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
		else:
			for parametre1 in tree.xpath("/config/general/custom_rep"):
				current_dir = parametre1.text
	print current_dir

	for parametre in tree.xpath("/config/general/extension"):
		extension = "\*" + parametre.text
	print extension

	for parametre in tree.xpath("/config/logs/replog"):
		rep_log = parametre.text

	for parametre in tree.xpath("/config/logs/nom"):
		if rep_log != None:
			nom_log = rep_log + "\\" + parametre.text
		else:
			nom_log = parametre.text
	print nom_log
	for parametre in tree.xpath("/config/logs/tag"):
		tag = parametre.text

	for parametre in tree.xpath("/config/logs/full_log"):
		if parametre.text == "oui":
			full_log = True
		else:
			full_log = False
	print "full_log: " + str(full_log)
	email = []
	for parametre in tree.xpath("/config/logs/listmail/email"):
		email.append(str(parametre.text))
	print email

except Exception, e:
	print "Lecture du fichier xml Impossible, vérifiez que le nom du fichier xml correspond au même nom que le programme python " + str(e)

try:
	logger = logging.getLogger(tag)
	hdlr = RotatingFileHandler(nom_log, 'a', 5000000, 3)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	hdlr.setFormatter(formatter)

	if full_log == True:
		hdlr.setLevel(logging.INFO)
		logger.setLevel(logging.INFO)
		print "info"
	else:
		hdlr.setLevel(logging.WARNING)
		logger.setLevel(logging.WARNING)
		print "warning"


	hdlr2 = SMTPHandler(
    # Host et port
    ('avmail'),
    # From
    "no-reply@example.com",
    # To (liste)
	email,
    # Sujet du message
    "Erreur critique dans File Transmitter"
	)

	hdlr2.setLevel(logging.ERROR)
	hdlr2.setFormatter(formatter)
	logger.addHandler(hdlr2)
	logger.addHandler(hdlr)
	logger.setLevel(logging.INFO)
	#logger.setLevel(logging.INFO)
	logger.info('')
	logger.info('///////////////////////////////////////////////////////////')
	logger.info('=============== debut execution log message ===============')
	logger.info('///////////////////////////////////////////////////////////')
	logger.info('-----------------------------------------------------------')
	logger.info('Paramètres xml: -- Hôte: ' + str(host) + ' -- Utilisateur: ' + str(user) + ' -- Mot de passe: ' + str(password) + " -- Backup_On: " + str(backup) + " -- Rep_backup :" + str(dest_backup) + " -- Repertoire contenant fichiers a envoyé: " + str(current_dir) + " -- extension: " + str(extension) + " -- Répertoire du log: " + str(rep_log))
	logger.info('-----------------------------------------------------------')

except Exception, e:
	print "impossible de créer le fichier log: " + str(e)



def run_program():
	while running == True:
		montemps=time.time()
		#On récupère la liste des fichiers présent dans le dossier trié par date de modification
		tab_txt = sorted(glob.glob(current_dir + str(extension)), key=os.path.getmtime)

		nbficht = True

		for elem in tab_txt:
			tps1 = time.clock()
			con = sqlite3.connect('ftdb.sql')
			cur = con.cursor()
			if nbficht == True:
				logger.info(".........Fichiers trouvés: " + str(len(tab_txt)) + ".........")
				logger.info('-----------------------------------------------------------')
				nbficht = False

			if os.path.isfile(elem) == True:
				# On se connecte au serveur ftp
				try:
					ftp = ftplib.FTP(host)
					ftp.login(user, password)
					print "Connexion au serveur ftp réussie"
					logger.info("Connexion au serveur ftp réussie")
					logger.info('-----------------------------------------------------------')

				except Exception, e:
					print 'Erreur connexion ftp :' + str(e)
					logger.error('Erreur connexion ftp :' + str(e))
					logger.warning('-----------------------------------------------------------')
					time.sleep(600)
				#On envois le fichier 'elem' récupéré dans la boucle
				try:
					fic_open = open(str(elem), 'rb+')
					ftp.storbinary('STOR ' + str(os.path.basename(elem)), fic_open)
					fic_open.close()
					success = True

					print "Transfert de " + str(os.path.basename(elem)) + " effectué"
					logger.info("Transfert de " + str(os.path.basename(elem)) + " effectué")
					logger.info('-----------------------------------------------------------')

				except Exception, e:
					print 'Erreur lors du transfert du fichier: ' + str(e)
					logger.error('Erreur lors du transfert du fichier: ' + str(e))
					logger.warning('-----------------------------------------------------------')
					success = False

				#On vérifie si le fichier est bien présent sur le serveur distant uniquement si le transfert c'est bien passé
				try:
					if success == True:
						ftp_dist = ftp.nlst() #Instruction permettant de lister le répertoire courant du ftp
						if os.path.basename(elem) in ftp_dist:
							ftp_success = True
							elemtabmin = os.path.basename(elem).split('.')
							elemOKmin = elemtabmin[0] + '.OK'
							print elemOKmin

							elemtabs = elem.split('.')
							OKdir = str(elemtabs[0]) + '.OK'
							print OKdir

							elemOK = open(OKdir, "w")
							elemOK.close()
							time.sleep(0.1)

							ftp.storbinary('STOR ' + elemOKmin, open(OKdir))

							print "Le fichier " + str(os.path.basename(elem)) + " a bien été transféré sur le ftp distant."
							logger.info("Le fichier " + str(os.path.basename(elem)) + " a bien été transféré sur le ftp distant.")
							logger.info('-----------------------------------------------------------')
						else:
							ftp_success = False
					else:
						print "Impossible de tester si le fichier existe sur le serveur ftp"
						logger.error("Impossible de tester si le fichier existe sur le serveur ftp")
						logger.warning('-----------------------------------------------------------')
				except Exception, e:
					print "Impossible de récupérer la liste des fichiers distant: " + str(e)
					logger.error("Impossible de récupérer la liste des fichiers distant: " + str(e))
					logger.warning('-----------------------------------------------------------')
				#On vérifie que le fichier a bien été envoyé, et si c'est le cas, sois on le backup, sois un le supprime du répertoire local
				try:
					if ftp_success == True:
						maintenant = datetime.now()
						a = maintenant.date()
						b = maintenant.hour
						cur.execute("SELECT nbfichier FROM donnees_transmises WHERE date = '" + str(a) + "' AND num_heure = " + str(b) )
						all1 = cur.fetchall()

						if all1 != []:
							print all1[0][0]

							all2 = int(all1[0][0]) + 1
							print all2
							print "liste pas vide donc update"
							cur.execute("UPDATE donnees_transmises SET nbfichier =" + str(all2) + " WHERE date ='" + str(a) + "' AND num_heure =" + str(b))
							con.commit()
						else:
							print "liste vide"
							cur.execute("""INSERT INTO donnees_transmises (date, num_heure, nbfichier) VALUES(?,?,?)""", (a, b, "1"))
							con.commit()
						cur.close()
						con.close()
				except Exception, e:
					print "Erreur lors du remplissage de la base de données sqlite3: " + str(e)

				try:
					if ftp_success == True:
						if backup == True:
							shutil.copy(elem, dest_backup)
							os.remove(elem)
							os.remove(OKdir)
							print "Déplacement du fichier vers: " + dest_backup
							logger.info("Déplacement du fichier vers: " + dest_backup)
							logger.info('-----------------------------------------------------------')
						else:
							os.remove(elem)
							print "Fichier " + str(os.path.basename(elem)) + " effacé du répertoire courant."
							logger.info("Fichier " + str(os.path.basename(elem)) + " effacé du répertoire courant.")
							logger.info('-----------------------------------------------------------')
				except Exception, e:
					if backup == True:
						print "Erreur lors du déplacement du fichier: " + str(e)
						logger.error("Erreur lors du déplacement du fichier: " + str(e))
						logger.warning('-----------------------------------------------------------')
					else:
						print "Erreur lors de l'effacement du fichier: " + str(e)
						logger.error("Erreur lors de l'effacement du fichier: " + str(e))
						logger.warning('-----------------------------------------------------------')
				#Une fois qu'on a fini, on se déconnecte.
				try:
					ftp.close()
					print "Déconnexion du serveur ftp réussie."
					logger.info("Déconnexion du serveur ftp réussie.")
				except:
					print "Impossible de fermer la connexion ftp"
					logger.error("Impossible de fermer la connexion ftp")
				#On met un timer pour éviter que la boucle s'exécute trop vite
				tps2 = time.clock()
				temps_instruc = tps2 - tps1
				print "Exécuté en :" + str(temps_instruc) + " sec"
				time.sleep(0.2)
				print datetime.now()

				logger.info('/////////////////////////////FIN/////////////////////////////')
		time.sleep(0.2)

class Server( dispatcher ):
	def __init__(self):
		dispatcher.__init__(self)
		self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
		self.bind( ( '', 50000 ) )
		self.listen(1)


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)


    print("Programme quitté !")
    sys.exit(0)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

if __name__ == '__main__':
    # store the original SIGINT handler
	try:
		Server()
	except:
		print 'Déjà en service !'
		sys.exit()

	original_sigint = signal.getsignal(signal.SIGINT)

	signal.signal(signal.SIGINT, exit_gracefully)
	run_program()
