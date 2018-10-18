#==============================================#
#   SISTEMAS DISTRIBUIDOS - ATIVIDADE 1  
#   MULTICAST TOTALMENTE ORDENADO
#         
#   Antonio Jorge Medeiros     620521      
#   Bruno Morii Borges         726500      
#==============================================#

import socket
import sys
import thread
import time
import random

#-------CONFIGURACOES DO GRUPO MULTICAST-------#
#IP de multicast (classe D) de 224.0.0.0 a 239.255.255.255
grupo = '225.225.225.225'
#IP local, o '0.0.0.0' faz com que o SO tente todas as interfaces disponiveis
localhost = '0.0.0.0'
#porta do grupo de multicast
porta = 11111
#TTL = 1 para que os pacotes nao sejam enviados para fora da rede local
ttl = 1


#------ARGUMENTOS DA MAIN -------#
#Seta a quantidade de acks esperados por cada processo (numero de processos no grupo)
#Se numero de processos abertos < ack_count = ERRO! (pq nao desinfilera)
ack_count = 0
#ID do processo
pid = 0
#Relogio logico
relogio = 0


#Inicializa fila de acks (hash map)
fila_ack = dict()
#Inicializa fila de msgs
fila_msg = []


#----------FUNCAO(THREAD) PARA TRATAR O RECEBIMENTO DE MSGS E SIMULAR ATRASO NA REDE-----------#
def recebe_msg(msg, transmissor, s):
    global relogio, pid, fila_msg, fila_ack, ack_count

    #Atraso da mensagem 
    atraso = random.randint (100, 300)
    time.sleep (atraso/100.0)

    #Guarda o PID e o Relogio Logico do transmissor, assim como a msg
    msg_pid, msg_relogio, msg_data = msg.split('|')

    #Relogio = max (relogio local, relogio transmissor + 1)
    relogio = max (relogio, int(msg_relogio))

    #Incrementa o relogio, pois receber msg e um evento
    relogio += 1

    #Se a msg conter um ACK, i.e., for um ACK
    if '_ACK_' in msg_data:
        #Remove o ack da string e acrescenta um ACK a fila de ACK, com identificador Relogio+PID
        if msg_data.replace('_ACK_', '') in fila_ack:
            #fila_ack[RELOGIO+PID] += 1
            fila_ack[msg_data.replace('_ACK_', '')] += 1
        else:
            #fila_ack[RELOGIO+PID] = 1
            fila_ack[msg_data.replace('_ACK_', '')] = 1

    #Se a msg nao conter um ACK, i.e., for uma msg normal
    else:
        #Envia um ACK com identificador msg_relogio + msg_pid
        s.sendto(str(pid) + '|' + str(relogio) + '|' + '_ACK_' + msg_relogio + msg_pid, (grupo, porta))
        #Atrasa para enfileirar a msg
        #time.sleep (3)

        #Enfileira a msg
        fila_msg.append(str(msg_relogio) + str(msg_pid))
        #Ordena a fila de msgs
        fila_msg.sort();


    #Printa o socket, PID, relogio e msg do transmissor
    #Printa a fila de ack, fila de msg e relogio local
    print ('----------------------------MENSAGEM RECEBIDA-----------------------------')
    print str(transmissor) + '\nPID: ' + msg_pid + '  _  Relogio: ' + msg_relogio + '  _  Msg: ' + msg_data
    print 'Fila de ACKS: ', fila_ack
    print 'Fila de mensagens: ', fila_msg
    print 'Relogio Logico: ' + str(relogio)
    print ('--------------------------------------------------------------------------')

    return 0
#--------------------------------------------------------------------------------------#

def envia_para_aplicacao():
    global fila_msg, fila_ack, pid, relogio

    while True:
        time.sleep(0.3)
        lista_ack = sorted(list(fila_ack))

        #Se a fila de ack nao estiver vazia
        while fila_ack:
            #Se a primeira msg ja tiver sido reconhecida por todos os outros processos
            if fila_msg and fila_msg[0] in fila_ack and fila_msg[0] == lista_ack[0] and fila_ack[fila_msg[0]] >= ack_count:
                #Guarda a msg que foi enviada a aplicacao
                msg_aux = fila_msg[0]
                #Manda a msg para a aplicacao e remove da fila de msg e de ack
                fila_ack.pop(fila_msg.pop(0), None)
                #Incrementa o relogio logico, pois enviar para a aplicacao e um evento
                relogio += 1
                #Imprime a fila de acks, msgs e relogio apos enviar para a aplicacao
                print ('#################----------ENVIADO A APLICACAO----------##################')
                print 'Mensagem enviada: ' + msg_aux
                print 'Fila de ACKS: ', fila_ack
                print 'Fila de mensagens: ', fila_msg
                print 'Relogio Logico: ' + str(relogio)
                print ('##########################################################################')
            else:
                break
    return 0

def transmissor(grupo):
    global relogio, pid
    #Cria um socket
    s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)

    #Seta TTL
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    while True:
        #Entrar com qualquer coisa apenas para enviar uma msg
        raw_input()
        #Para cada msg enviada, incrementa o relogio
        relogio += 1
        #PID + RELOGIO + MSG, com o delimitador '|'
        s.sendto(str(pid) + '|' + str(relogio) + '|' + '_MSG_' + str(relogio) + str(pid), (grupo, porta))
    return 0


def receptor(grupo):
    global relogio, pid, fila_ack, fila_msg

    #Cria um socket
    s = socket.socket(socket.TIPC_ADDR_NAME, socket.SOCK_DGRAM)

    #Permite mais de uma execucao na mesma maquina
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Conecta o socket ao grupo e a porta
    s.bind((grupo, porta))

    #Concatena os ips binarios do grupo e local
    requisicao = socket.inet_aton(grupo) + socket.inet_aton(localhost)

    #Faz a requisicao do socket ao grupo
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, requisicao)

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
        print('PID + Relogio Logico + Total de processos')
        sys.exit(0)
    pid = int(sys.argv[1])
    relogio = int(sys.argv[2])
    ack_count = int(sys.argv[3])

    #Thread para o transmissor funcionar concorrentemente ao receptor
    thread.start_new_thread (transmissor, (grupo, ))
    thread.start_new_thread (envia_para_aplicacao, ())
    receptor(grupo)
    sys.exit(0)