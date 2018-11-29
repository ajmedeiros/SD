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
#Socket UDP
localhost = '127.0.0.1'
ttl = 0

#Dicionario de portas (apenas para facilitar, mas os nós só se comunicam com vizinhos imediatos)
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

#Topologia de testes (vizinhos = em uso)
vizinhos_teste = {
	'A': ['B', 'C', 'E'],
	'B': ['A', 'D'],
	'C': ['A', 'D', 'E'],
	'D': ['B', 'C'],
	'E': ['A', 'C'],	
}

#Dicionario dos vizinhos (mesma topologia da imagem topo2.png)
vizinhos_off = {
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

vizinhos = {
	'A': ['D'],
	'B': ['D', 'E', 'G'],
	'C': ['E', 'I'],
	'D': ['A', 'B', 'F', 'H'],
	'E': ['B', 'C', 'G', 'L'],
	'F': ['D'],
	'G': ['B', 'E', 'H'],
	'H': ['D', 'J', 'K'],
	'I': ['C', 'L'],
	'J': ['H'],
	'K': ['H'],
	'L': ['E', 'I'],
}


#-- LÓGICA DO ALGORÍTMO --# (necessario zerar todos apos cada eleicao terminar)
ack_count = 0
pai = 0 #Se pai = 0, entao não há eleição ativa, caso contrario, há
eleicao = 0 #Se eleicao = 0, então não há eleição ativa, caso contrário, há
maiorNo = 0
maiorNoPeso = 0
novoLider = 0

#Transmissor
solicitarEleicao = 'placeholder'

#-- ARGUMENTOS DA MAIN --#
porta = 0
nid = 0
peso = 0

#-- VERIFICA ACKS --#
def contador ():
	global pai, eleicao, ack_count, maiorNo, maiorNoPeso, novoLider

	#Transmissor
	sock_transmissor = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	sock_transmissor.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		time.sleep (.3)

		#Verifica se já recebeu todos os ACKS e responde ao nó pai
		#Se for source, então ack count = número de vizinhos
		if pai == nid:
			if nid in vizinhos and ack_count >= len (vizinhos[nid]):
				print txt.OKGREEN + txt.BOLD + 'Novo líder eleito: ' + maiorNo + txt.ENDC
				print txt.OKGREEN + txt.BOLD + 'Eleição: ' + eleicao + txt.ENDC
				print txt.OKGREEN + txt.BOLD + 'Capacidade: ' + maiorNoPeso + txt.ENDC

				novoLider = 1
				for no in vizinhos[nid]:
					sock_transmissor.sendto('NOVOLIDER|' + eleicao + '_' + maiorNo + '_' + maiorNoPeso + '|' + nid, (localhost, int (portaNo [no])))
				#Reseta a eleição
				pai = 0
				eleicao = 0
				ack_count = 0
				maiorNo = nid
				maiorNoPeso = peso

		#Se não for source, então ack count = número de vizinhos - 1
		else:
			if nid in vizinhos and pai in portaNo and ack_count >= len (vizinhos[nid]) - 1:
				sock_transmissor.sendto('RESPOSTA|' + eleicao + '_' + maiorNo + '_' + maiorNoPeso + '|' + nid, (localhost, int (portaNo [pai])))
				#Reseta a eleição
				pai = 0
				eleicao = 0
				ack_count = 0
				maiorNo = nid
				maiorNoPeso = peso
	return 0

#-- RECEPTOR UDP --#
def receptor():
	global localhost, porta, ack_count, pai, eleicao, maiorNo, maiorNoPeso, novoLider

	#Receptor
	sock_receptor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_receptor.bind((localhost, int (porta)))

	#Transmissor
	sock_transmissor = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	sock_transmissor.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		#Guarda a msg e quem a transimitiu
		msg, transmissor = sock_receptor.recvfrom(1500)

		#Se houver alguma mensagem
		if msg:
			time.sleep(1)
			#Recebe os campos da msg
			msg_type, msg_data, msg_nid = msg.split ('|')

			if 'ELEICAO' in msg_type:
				print txt.OKBLUE + msg + txt.ENDC
				#Não há nenhuma eleição ativa
				if eleicao == 0:
					novoLider = 0
					pai = msg_nid
					eleicao = msg_data
					#Transmite a solicitação da eleição em broadcast
					for no in vizinhos[nid]:
						#Não transmite para o pai
						if no == pai:
							continue
						sock_transmissor.sendto('ELEICAO|' + msg_data + '|' + nid, (localhost, int (portaNo [no])))

				#Se já estiver participando de uma eleição
				else:
					#Compara os IDs das eleições e descarta o menor
					if int (msg_data) > int (eleicao):
						print txt.WARNING + 'Eleição atual ' + eleicao + ' descartada'
						#Descarta a eleição anterior
						pai = msg_nid
						eleicao = msg_data
						ack_count = 0
						maiorNo = nid
						maiorNoPeso = peso

						#Transmite a nova solicitação da eleição em broadcast
						for no in vizinhos[nid]:
							#Não transmite para o pai
							if no == pai:
								continue
							sock_transmissor.sendto('ELEICAO|' + msg_data + '|' + nid, (localhost, int (portaNo [no])))

					#Se for a mesma eleição que já participa, apenas devolve um ACK
					elif int (msg_data) == int (eleicao):
						sock_transmissor.sendto('ACK|' + msg_data + '|' + nid, (localhost, int (portaNo [msg_nid])))

					#Se o ID for menor, então descarta e não faz nada
					else:
						print txt.WARNING + 'Solicitação de eleição ' + msg_data + ' do nó ' + msg_nid + ' descartada'

			elif 'RESPOSTA' in msg_type:
				print txt.OKGREEN + msg + txt.ENDC
				msg_eleicao, msg_maiorNo, msg_maiorPeso = msg_data.split ('_')

				#Verifica se a resposta é da atual eleição, se não descarta (eleição já está 'obsoleta') 
				if msg_eleicao == eleicao:
					#Incrementa os acks
					ack_count += 1
					#Verifica se o peso é maior que o atual maior
					if int (msg_maiorPeso) > int (maiorNoPeso):
						maiorNo = msg_maiorNo
						maiorNoPeso = msg_maiorPeso

				else:
					print txt.WARNING + 'Resposta de eleição ' + msg_data + ' do nó ' + msg_nid + ' descartada'

			elif 'ACK' in msg_type:
				print txt.HEADER + msg + txt.ENDC
				#Verifica se o ack é da atual eleição, se não descarta
				if msg_data == eleicao:
					ack_count += 1
				else:
					print txt.WARNING + 'ACK de eleição ' + msg_data + ' do nó ' + msg_nid + ' descartado'

			elif 'NOVOLIDER' in msg_type:
				print txt.HEADER + msg + txt.ENDC
				msg_eleicao, msg_maiorNo, msg_maiorNoPeso = msg_data.split ('_')
				if eleicao != 0 and msg_eleicao != eleicao:
					continue
				if novoLider == 0:
					print txt.OKGREEN + txt.BOLD + 'Novo líder eleito: ' + msg_maiorNo + txt.ENDC
					print txt.OKGREEN + txt.BOLD + 'Eleição: ' + msg_eleicao + txt.ENDC
					print txt.OKGREEN + txt.BOLD + 'Capacidade: ' + msg_maiorNoPeso + txt.ENDC
					for no in vizinhos[nid]:
						sock_transmissor.sendto('NOVOLIDER|' + msg_data + '|' + nid, (localhost, int (portaNo[no])))
				novoLider = 1
			else:
				print txt.FAIL + txt.BOLD + 'Erro: mensagem não reconhecida.' + txt.ENDC
	return 0

#-- TRANSMISSOR UDP --#
def transmissor ():
	global solicitarEleicao, eleicao, nid, pai, peso, maiorNoPeso, novoLider
	#Cria um socket
	s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	#Seta TTL
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		#Identificador do recurso solicitado
		solicitarEleicao = raw_input ()

		if (solicitarEleicao == 'exit'):
			break

		if eleicao == 0:
			if 'eleicao' in solicitarEleicao:	
				novoLider = 0
				aux, eleicao = solicitarEleicao.split(' ')
				pai = nid
				#Broadcast simulado
				for no in vizinhos[nid]:
					s.sendto('ELEICAO|' + eleicao + '|' + nid, (localhost, int (portaNo [no])))

			if 'peso' in solicitarEleicao:
				aux, peso = solicitarEleicao.split (' ')
				maiorNoPeso = peso
		else:
			print txt.WARNING + 'Existe uma eleição em andamento' + txt.ENDC

	return 0


if __name__ == '__main__':
	if (len(sys.argv) != 3):
		print txt.FAIL + txt.BOLD + "ERRO: Entre com ID + PESO" + txt.ENDC
		sys.exit(0)

	nid = sys.argv[1]
	peso = sys.argv[2]
	porta = portaNo[nid]

	maiorNo = nid
	maiorNoPeso = peso

	#Thread para o transmissor funcionar concorrentemente ao receptor
	thread.start_new_thread (transmissor, ())
	thread.start_new_thread (receptor, ())
	thread.start_new_thread (contador, ())

	while (True):
		time.sleep(.5)
		if (solicitarEleicao == 'exit'):
			sys.exit(0)
	sys.exit(0)
