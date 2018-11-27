# -*- coding: utf-8 -*-
#==============================================#
#   SISTEMAS DISTRIBUIDOS - ATIVIDADE 3 [P1]  
#   ELEICAO DE LIDER EM AMBIENTE SEM FIO
#		 
#   Antonio Jorge Medeiros	 620521	  
#   Bruno Morii Borges		 726500	  
#==============================================#

import socket
import sys
import thread
import time
import random
from collections import defaultdict

#-- Para facilitar a visualizacao --#
class txt:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    GRAY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#-- Inicializacao estatica --#
#Socket
localhost = '127.0.0.1'
ttl = 0

#Dicionario de portas
portaNo = {
    'A': '10000',
    'B': '10001',
    'C': '10002',
    'D': '10003',
    'E': '10004',
    'F': '10005',
    'G': '10006',
    'H': '10007',
    'I': '10008',
    'J': '10009',
    'K': '10010',
    'L': '10011',
    'M': '10012',
    'N': '10013',
}

#Dicionario dos vizinhos
vizinhos = {
    'A': ['B', 'E'],
    'B': ['A', 'C', 'F', 'I'],
    'C': ['B', 'F', 'D', 'G', 'J'],
    'D': ['C', 'G', 'K'],
    'E': ['A', 'H', 'I'],
    'F': ['B', 'C', 'I', 'J', 'M'],
    'G': ['C', 'D', 'J', 'K', 'N'],
    'H': ['E', 'I', 'L'],
    'I': ['B', 'E', 'F', 'H', 'L', 'M'],
    'J': ['C', 'F', 'G', 'M', 'N'],
    'K': ['D', 'G', 'N'],
    'L': ['H', 'I'],
    'M': ['F', 'I', 'J'],
    'N': ['G', 'J', 'K'],
}

#Logica do algoritmo
ack_count = 0
pai = 0
solEleicao = 'placeholder'

#-- ARGUMENTOS DA MAIN --#
porta = 0
nid = 0
peso = 0

#-- RECEPTOR UDP --#
def receptor():
	global localhost, porta

	#------------- UNICAST --------------#
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((localhost, int (porta)))
	#------------- UNICAST --------------#

	while True:
		#Guarda a msg e quem a transimitiu
		msg, transmissor = s.recvfrom(1500)

		#Se houver alguma mensagem
		if msg:
			print str (transmissor) + '\n' + str (msg)
	return 0

#-- TRANSMISSOR UDP --#
def transmissor ():
	global solEleicao
	#Cria um socket
	s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	#Seta TTL
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		#Identificador do recurso solicitado
		solEleicao = raw_input (txt.HEADER + txt.BOLD + "Iniciar eleicao com ID: " + txt.ENDC)

		if (solEleicao == 'exit'):
			break

		#Broadcast simulado
		for no in vizinhos[nid]:
			s.sendto('ELEICAO|' + solEleicao + '|' + nid, (localhost, int (portaNo [no])))
	return 0


if __name__ == '__main__':
	if (len(sys.argv) != 3):
		print txt.FAIL + txt.BOLD + "ERRO: Entre com ID + PESO" + txt.ENDC
		sys.exit(0)

	nid = sys.argv[1]
	peso = sys.argv[2]
	porta = portaNo[nid]

	#Thread para o transmissor funcionar concorrentemente ao receptor
	thread.start_new_thread (transmissor, ())
	thread.start_new_thread (receptor, ())

	while (True):
		time.sleep(.5)
		if (solEleicao == 'exit'):
			sys.exit(0)
	sys.exit(0)
