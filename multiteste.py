#==============================================#
#   SISTEMAS DISTRIBUIDOS - ATIVIDADE 2  
#   EXCLUSAO MUTUA
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

#-------CONFIGURACOES DO GRUPO MULTICAST-------#
#IP de multicast (classe D) de 224.0.0.0 a 239.255.255.255
grupo = '225.225.225.225'
#Interface local, o '0.0.0.0' faz com que o SO tente todas as interfaces disponiveis
interface_local = '0.0.0.0'
#porta do grupo de multicast
porta = 11111
#TTL = 1 para que os pacotes nao sejam enviados para fora da rede local
ttl = 1
#IP local
localhost = '127.0.0.1'

#------ARGUMENTOS DA MAIN -------#
#Seta a quantidade de acks esperados por cada processo (numero de processos no grupo)
#Se numero de processos abertos < ack_count = ERRO! (pq nao desinfilera)
ack_count = 0
#ID do processo
pid = 0
#Relogio logico
relogio = 0
#SOLICITAR RECURSO
recurso = '?'
#porta que o processo estara ouvindo
porta_udp = 7777

#Inicializa fila de acks (hashmap de lista)
fila_ack = defaultdict(list)
#Inicializa fila de recursos solicitados
fila_solicitado = dict()
#Inicializa fila de recursos na aplicacao
fila_aplicacao = []
#Inicializa fila de processos que solicitaram o recurso (hashmap de lista)
fila_proximos = defaultdict(list)

#----------FUNCAO(THREAD) PARA TRATAR O RECEBIMENTO DE MSGS E SIMULAR ATRASO NA REDE-----------#
def recebe_msg(msg, transmissor, s):
	global relogio, pid, fila_msg, fila_ack, ack_count

	#Atraso da mensagem 
	atraso = random.randint (100, 300)
	time.sleep (atraso/100.0)

	#Guarda o PID e o Relogio Logico do transmissor, assim como a msg
	msg_pid, msg_relogio, msg_porta, msg_data = msg.split('|')

	#Relogio = max (relogio local, relogio transmissor + 1)
	relogio = max (relogio, int(msg_relogio))

	#Incrementa o relogio, pois receber msg e um evento
	relogio += 1

	#Se a msg conter um ACK, i.e., for um ACK
	if '_ACK_' in msg_data:
		msg_recurso = msg_data.replace('_ACK_', '')
		#Remove o ack da string e acrescenta um ACK a fila de ACK, com identificador Relogio+PID
		fila_ack[msg_recurso].append (str (msg_pid))

	#Se a msg for um NAK
	elif '_NAK_' in msg_data:
		msg_recurso = msg_data.replace('_NAK_', '')

	#Se a msg nao conter um ACK ou NAK, i.e., for uma msg normal
	else:
		msg_recurso = msg_data

		#Se o recurso estiver sendo utilizado pelo processo
		if msg_recurso in fila_aplicacao:
			#Envia um NAK e enfilera a requisicao
			s.sendto(str(pid) + '|' + str(relogio) + '|' + str(porta_udp) + '|'  + '_NAK_' + str(msg_recurso), (localhost, int(msg_porta)))
			fila_proximos[msg_recurso].append (msg_porta)

		elif msg_recurso in fila_solicitado:
			#Se identificador do processo for menor que o solicitante
			if (str(msg_pid) != str(pid) and (str(msg_pid) in fila_ack[msg_recurso] or (fila_solicitado[msg_recurso] < msg_relogio + msg_pid))):
				#Envia um NAK e enfilera a requisicao
				s.sendto(str(pid) + '|' + str(relogio) + '|' + str(porta_udp) + '|'  + '_NAK_' + str(msg_recurso), (localhost, int(msg_porta)))
				fila_proximos[msg_recurso].append (msg_porta)
			else:
				#Envia um ACK
				s.sendto(str(pid) + '|' + str(relogio) + '|' + str(porta_udp) + '|'  + '_ACK_' + str(msg_recurso), (localhost, int(msg_porta)))
		else:
			#Se nao estou utilizando o recurso, nem o solicitei,
			#envia um ACK com identificador msg_relogio + msg_pid
			s.sendto(str(pid) + '|' + str(relogio) + '|' + str(porta_udp) + '|'  + '_ACK_' + str(msg_recurso), (localhost, int(msg_porta)))

	#Printa o socket, PID, relogio e msg do transmissor
	#Printa a fila de ack, fila de msg e relogio local
	print ('----------------------------MENSAGEM RECEBIDA-----------------------------')
	print str(transmissor) + '\nPID: ' + msg_pid + '  _  Relogio: ' + msg_relogio + '  _  Msg: ' + msg_data
	print 'Fila de ACKS: ', dict.__repr__(fila_ack)
	print 'Fila de aplicacao: ', fila_aplicacao
	print 'Fila de proximos: ', dict.__repr__(fila_proximos)
	print 'Fila de solicitacoes: ', fila_solicitado
	print 'Relogio Logico: ' + str(relogio)
	print ('--------------------------------------------------------------------------')

	return 0
#--------------------------------------------------------------------------------------#

def envia_para_aplicacao():
	global fila_solicitado, fila_ack, pid, relogio

	while True:
		time.sleep(0.1)

		#Percorro a lista de recursos solicitados
		for k in list(fila_solicitado):
			#Se algum recurso ja recebeu todos ACKS
			if len(fila_ack[k]) >= ack_count:
				#Guarda o recurso que foi enviado para a aplicacao
				recurso = k
				#Remove o recurso da fila de solicitados e da fila de ACK
				fila_ack.pop (recurso)
				fila_solicitado.pop (recurso)
				#Envia o recurso para a aplicacao
				fila_aplicacao.append (recurso)
				#incrementa o relogio logico, pois enviar para a aplicacao e um evento
				relogio += 1

				#Imprime a fila de acks, msgs e relogio apos enviar para a aplicacao
				print ('#################----------ENVIADO A APLICACAO----------##################')
				print 'Recurso enviado: ' + recurso
				print 'Fila de ACKS: ', dict.__repr__(fila_ack)
				print 'Fila de solicitacao', fila_solicitado
				print 'Fila de aplicacao: ', fila_aplicacao
				print 'Relogio Logico: ' + str(relogio)
				print ('##########################################################################')
	return 0

def consome_recurso():
	global relogio
	#Cria um socket
	s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	#Seta TTL
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		time.sleep(.5)

		for k in fila_aplicacao:
			time.sleep (3)
			relogio += 1
			recurso = k
			fila_aplicacao.remove (k)

			for x in fila_proximos[recurso]:
				#Envia um ACK
				s.sendto(str(pid) + '|' + str(relogio) + '|' + str(porta_udp) + '|'  + '_ACK_' + str(recurso), (localhost, int(x)))

			fila_proximos.pop (recurso)

			#Imprime a fila de acks, msgs e relogio apos enviar para a aplicacao
			print ('*****************------APLICACAO CONSUMIU RECURSO-------******************')
			print 'Recurso consumido: ' + recurso
			print 'Fila de aplicacao: ', fila_aplicacao
			print 'Fila de proximos: ', dict.__repr__(fila_proximos)
			print 'Relogio Logico: ' + str(relogio)
			print ('**************************************************************************')
	return 0

def transmissor():
	global relogio, pid, recurso, grupo, porta
	#Cria um socket
	s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	#Seta TTL
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	while True:
		#Identificador do recurso solicitado
		recurso = raw_input()

		if (recurso == 'exit'):
			break

		if (recurso in fila_solicitado or recurso in fila_aplicacao):
			print 'Recurso ja solicitado ou em uso'
		else:
			#Enfilera o recurso com a sua ordenacao
			fila_solicitado[recurso] = str(relogio) + str(pid)

			#Para cada msg enviada, incrementa o relogio
			relogio += 1

			#PID + RELOGIO + MSG, com o delimitador '|'
			s.sendto(str(pid) + '|' + str(relogio) + '|' + str (porta_udp) + '|' + recurso, (grupo, porta))
	return 0

def receptor():
	global grupo, porta

	#------------- MULTICAST ------------#
	#Cria um socket
	s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)
	#Permite mais de uma execucao na mesma maquina
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#Conecta o socket ao grupo e a porta
	s.bind((grupo, porta))
	#Concatena os ips binarios do grupo e local
	requisicao = socket.inet_aton(grupo) + socket.inet_aton(interface_local)
	#Faz a requisicao do socket ao grupo
	s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, requisicao)
	#------------- MULTICAST ------------#

	while True:
		#Guarda a msg e quem a transimitiu
		msg, transmissor = s.recvfrom(1500)

		#Se houver alguma mensagem
		if msg:
			#Cria uma nova thread para receber a mensagem, simulando um atraso de rede, 
			#sem interromper o resto do programa
			thread.start_new_thread (recebe_msg, (msg, transmissor, s))
	return 0

def receptor_UDP():
	global localhost, porta_udp

	#------------- UNICAST --------------#
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((localhost, porta_udp))
	#------------- UNICAST --------------#

	while True:
		#Guarda a msg e quem a transimitiu
		msg, transmissor = s.recvfrom(1500)

		#Se houver alguma mensagem
		if msg:
			#Cria uma nova thread para receber a mensagem, simulando um atraso de rede, 
			#sem interromper o resto do programa
			thread.start_new_thread (recebe_msg, (msg, transmissor, s))
	return 0

if __name__ == '__main__':
	if (len(sys.argv) != 4):
		print('PID + Porta + Total de processos')
		sys.exit(0)
	pid = int(sys.argv[1])
	porta_udp = int(sys.argv[2])
	ack_count = int(sys.argv[3])
	relogio = random.randint (10000, 50000)

	if (str(porta_udp) == str(porta)):
		print('A porta deve ser diferente de 11111')
		sys.exit(0)

	#Thread para o transmissor funcionar concorrentemente ao receptor
	thread.start_new_thread (transmissor, ())
	thread.start_new_thread (consome_recurso, ())
	thread.start_new_thread (envia_para_aplicacao, ())
	thread.start_new_thread (receptor, ())
	thread.start_new_thread (receptor_UDP, ())

	while (True):
		time.sleep(.5)
		if (recurso == 'exit'):
			sys.exit(0)
	sys.exit(0)
