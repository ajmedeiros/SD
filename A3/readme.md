SD - A3

1 Fila para nós vizinhos (entrada main)
1 Fila de acks (ack count = numero de vizinhos)
	pode ser ack ou msg de resposta (com o maior candidato ex: H|17)
1 candidato pai = ID ou SOURCE

Thread transmissao msg para: iniciar nova eleição
Thread para ack count: Se ack_count = numero vizinhos, responde ao pai (se for source, broadcast do novo lider)

Ao transmitir msg:
	Tipo de msg (broadcast ou unicast)
	Se tipo = 0, então broadcast
		broadcast gambiarra, varre a lista de vizinhos e envia msg para cada um
	Se não, unicast = tipo (que será a porta)

Ao receber msg:
	Se tiver eleicao aberta:
		Se for ack (o outro ja tinha um pai), entao ack_count++
		Se for resposta, compara com o atual maior e guarda, ack_count++
		Se for pedido de eleicao:
				Se id do pedido for maior que atual, descarta eleição atual (zera os acks etc) e passa a atender eleição do pedido
				Se não, descarta o pedido e prossegue

	Se não tiver eleicao aberta:
		Se for pedido de eleicao:
			Guarda o transmissor como nó pai
			Transmite em broadcast (exceto para o pai) a eleicao

Source da eleição:
	Se ack_count == numero vizinhos
		Broadcast: ID|Carga do líder
