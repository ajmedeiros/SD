# Mutex - Ricart e Agrawala

## Pedido de recurso: 
* Se receber todos ACKS, consome o recurso (o envia para a thread de recursos)
* Se não receber todos ACKS, aguarda a liberação do recurso (ou seja, alguém o está consumindo e enviará ACK dps de terminar)
* Se dois processos pedirem o mesmo recurso, no mesmo tempo (relógio lógico igual), aquele com o menor PID utilizará o recurso primeiro
	* Ou seja, se p1 < p2, p1 receberá todos os acks e consumirá o recurso
	* p2 deve esperar, pois receberá n - 1 acks (receberá seu próprio ACK, mas não receberá o ACK de p1)
	* Quando p1 terminar de utilizar o recurso, enviará um ACK, então p2 pode consumir o recurso

	* Se, ainda nesse caso, um terceiro processo p3 pedir o recurso, ele será enfileirado tanto por p1 quanto por p2
		* o recurso então passará de p1 .. p2 .. p3
			* p3 receberá n - 2 acks, daí receberá o ack de p1 e ficará com n - 1 acks
			* quando p2 terminar de utilizar o recurso, enviará um ack para quem está na sua fila (isto é, p3)
			* então p3 receberá n acks e poderá utilizar o recurso
			* isso deve ser verdade para qualquer número N de solicitações de um mesmo recurso em uso



## Para cada processo:
* Uma fila de recurso que está utilizando
	* Se algum outro processo pedir um recurso que está utilizando, o coloca na fila e só após terminar de consumir o recurso, envia um ACK

* Uma fila de acks para um recurso solicitado
	* Só irá consumir o recurso quando receber todos os N acks

* Se receber uma solicitação de recurso:
	* Verifica se está utilizando o recurso (ou se já fez uma solicitação antes e a enfilera), caso contrário, envia um ACK
		* Se estiver utilizando o recurso, enfilera o PID do processo solicitante, ao terminar de utilizar o recurso, envia um ACK
		* Se o próprio processo também enviou uma solicitação, compara os relógios+PIDs
			* Se 'perder', envia um ACK
			* Se 'ganhar', consome o recurso e enfilera o processo que também está pedindo o recurso
