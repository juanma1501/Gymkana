#!/usr/bin/python3
# -*- coding: utf-8 -*-
"Usage: %s [<'respuestas'>]"

							#############################################################################
							##          GYMKANA JUAN MANUEL PORRERO ALMANSA 2ºA CURSO 2019/2020	   ##
							#############################################################################



#############################################################################
##                 CÓMO UTILIZAR ESTE PROGRAMA	                           ##
#############################################################################
'''
Este programa en Python 3 consiste en superar una gymkana, una serie de retos consecutivos. No podremos pasar al siguient
si no hemos superado antes el anterior con éxito. Este programa está diseñado por JUAN MANUEL PORRERO ALMANSA.

Al ejecutar este programa, tendremos dos opciones, que se activarán dependiendo de si hemos introducido la palabra "respuestas" o no.
Si la hemos introducido, quedando el comando para ejecutarlo, de la siguiente forma: "python3 solucion-yinkana.py respuestas" el programa generará 
un fichero llamado "respuestas_JuanManuelPorrero" en el directorio desde el cual lo estamos ejecutando y se escribirán en él las respuestas sobre retos posteriores
que el servidor nos manda cuando superamos uno correctamente.
Por el contrario, si no la incluimos, el fichero jamás será creado, y estas respuestas no serán almacenadas. Únicamente visualizaremos por pantalla 
el funcionamiento del programa al ejecutarlo.
'''




#############################################################################
##                       USO DE LIBRERÍAS                                  ##
#############################################################################
'''
*** SOCKET *** Librería necesaria para crear Sockets, los cuales son necesarios para establecer comunicación entre el cliente y servidor (leer y enviar datos)
*** THREADING *** Creado para poder threads, puesto que la solución deber un único archivo .py, esto nos permite ejecutar nuestro servidor en este único archivo
*** ARGV *** Para poder manejar las opciones del programa, concretamente la opcion "respuestas"
*** SLEEP *** Utilizado a modo de espera para que el servidor del reto 1 reciba las instrucciones
*** _EXIT *** Para poder finalizar el programa de manera adecuada cuando hayamos hecho todos los retos
*** RANDINT *** La utilizamos para poder crear un número aleatorio entre un determinado intervalo haciendo uso de la función randint()
*** STRUCT *** Para poder empaquetar en el reto 5 WYP
*** BASE64 *** Para cifrar el payload del reto 5 WYP
*** HASHLIB *** Con ella podemos calcular el MD5 del archivo en el reto 4
*** URLLIB *** Para realizar peticiones a página y poder descargar el archivo en el reto 6
'''

from socket import *
from urllib import request
import threading
import hashlib
import sys
from sys import argv
from time import sleep
from os import _exit
from random import randint
import struct
import base64





#############################################################################
##                       VARIABLE GLOBALES                                 ##
#############################################################################

''' Lista de cada una de las variables globales utilizadas y su descripción '''

SERVER='node1' #------------------------------------->Nombre del servidor de la gymkana
RECV_UDP=65507 #------------------------------------->Maximo nº de bytes que puede recibir UDP
RECV_TCP=65535 #------------------------------------->Máximo nº de bytes que puede recibir TCP
PORT_FASE0=2000 #------------------------------------>Puerto al que nos conectamos en la fase 0
PORT_SERVER1=3000 #---------------------------------->Puerto al que nos conectamos en la fase 1
PORT_SERVER2=4001 #---------------------------------->Puerto al que nos conectamos en la fase 2
PORT_SERVER3=5001 #---------------------------------->Puerto al que nos conectamos en la fase 3
PORT_SERVER4=10000 #---------------------------------->Puerto al que nos conectamos en la fase 4
PORT_SERVER5=7001 #---------------------------------->Puerto al que nos conectamos en la fase 5
PORT_SERVER6=8003 #---------------------------------->Puerto al que nos conectamos en la fase 6
PORT_SERVER7=33333 #---------------------------------->Puerto al que nos conectamos en la fase 7
PORT_PROXY=randint(1000,8000) #Puerto elegido aleatoriamente para nuestro servidor proxy
Fase1end=False #------------------------------------->Para saber si el servidor de la fase 1 ha recibido las instrucciones
respuestas=None #------------------------------------>Variable para saber si la opción "respuestas" ha sido activada
FASE=0 #--------------------------------------------->Funciona como un contador para saber en qué fase nos encontramos. Solo la utilizaremos a la hora de escribir en el fichero cuando hayamos escrito "respuestas"
fichero='respuestas_JuanManuelPorrero' #-------------->Nombre del fichero que se creará en caso de que hayamos escrito "respuestas"
instrucciones = "" #---------------------------------->Es una variable global utilizada para almacenar las instrucciones del reto 7, que estas las recibimos a través de un hilo del servidor proxy







#############################################################################
##               FUNCIONES DE GRAN AYUDA EN LA RESOLUCIÓN	           ##
#############################################################################

''' Para explicar el funcionamiento de cada función auxiliar utilizada, habrá un comentario encima de cada una '''


'''
Función para ver si el usuario ha incluido la opción "repuestas" o no. Se modificará la variable globar respuestas dependiendo de ello.
'''
def ficheroSiNo():
	global respuestas
	if len(argv) == 1:
		respuestas=False	

	elif len(argv)==2 and argv[1]=="respuestas":
		respuestas=True




'''
Función que alberga el servidor UDP creado por nosotros mismos necesario para el correcto desarrollo de la fase 1. En él recibimos las instrucciones de esta fase. Este
servidor estará abierto mediante un bucle hasta que el programa finalice, a la espera de recibirlas.
'''
def Fase1server(portServer1,msg1):
	sockServer1=socket(AF_INET, SOCK_DGRAM)
	sockServer1.bind(('',portServer1))
	global Fase1end
	
	print("[FASE 1 Servidor Local] Esperando instrucciones de",SERVER,":",PORT_SERVER1)
	while 1:
		msg1[0],client=sockServer1.recvfrom(RECV_UDP)
		print("[FASE 1 Servidor Local] Instrucciones recibidas")
		Fase1end=True

	sockServer1.close()



'''
Función para escribir el mensaje que se le pasa por parámetro en el fichero que crearemos en caso de "respuestas". 
'''
def escribe(msg):
	fase_actual=("\n----------------FASE %d--------------------\n"% FASE)

	if FASE==0:
		with open(fichero,"w") as f:
			f.write(fase_actual)
			f.write(msg)
			f.close()
	else:
		with open(fichero,"a") as f:
			f.write(fase_actual)
			f.write(msg)
			f.close()



'''
Función para obtener el código de fase del primer reto
'''
def obtenerCodigo(msg,line=0):
	id=(msg.splitlines())[line]
	return id




'''
Función para obtener el código de fase de los demás retos, varía un poco respecto a la anterior, puesto que ahora se incluye la los caracteres
code: delante del código de fase.
'''
def obtenerCodigoCode(msg,line=0):
	id=(msg.splitlines())[line] 
	id_final=id[5:]
	return id_final



'''
Función para contar los carácteres que hay antes de uno determinado (en este caso es '0'). Lo primero que hacemos es transformar el mensaje en una lista
para así poder acceder a cada elemento de forma más fácil haciendo uso de un bucle y la función split() y isdigit(). Devolvemos la cuenta de esos carácteres.
'''
def cuentaCaracteres(msg2):
	lista=[int(Numero) for Numero in msg2.split() if Numero.isdigit()]
	count=0
	for q in lista:
		if(q==0):
			break
		else:
			count+=1
	return count



'''
Esta función nos servirá para detectar si en el mensaje que se le pasa como argumento hay un 0, devuelve True en caso afirmativo y False en caso negativo. Hacemos uso de una lista creada de igual
forma que en la función anterior.
'''
def detectarCero(msg2):
	lista=[int(Numero) for Numero in msg2.split() if Numero.isdigit()]
	existe=False
	for q in lista:
		if(q==0):
			existe=True
	return existe



'''
Función para transformar un mensaje en una lista, en la que cada palabra o número separado por un espacio ocupa una posición
'''
def mensajeLista(msg3):
	lista=[palabra for palabra in msg3.split()]
	return lista




'''
Función para sumar todos los números de una lista que también contiene palabras.
'''
def sumaNumeros(msg3):
	total=0
	lista=[numero for numero in msg3.split() if numero.isdigit()]
	for numero in lista:
		total+=int(numero)
	return total



'''
A esta función le pasamos de parámetro un mensaje, que se transformará en una lista en la que cada elemento ocupará una posición mediante la función mensajeLista().
El algoritmo que usa es: vamos recorriendo la lista y, si un elemento es un número ( isdigit() ) lo sumamos a cuenta total, y en caso de ser superior a 1300 nos saldremos del bucle.
A la misma vez, si ese elemento no es un número, lo iremos almacenando en la variable palabra, de modo que cuando la suma sea superior a 1300 la función retornará el último valor que ha
adquirido la variable palabra, siendo este la última palabra encontrada antes de que la suma de los números rebasara 1300.
'''
def solucionFase3(msg):
	lista = mensajeLista(msg)
	suma = 0
	palabra =" "
	for item in lista:
		if (item.isdigit()==True):
			suma = suma + int(item)
			if suma > 1300:
					break;
		else:
			palabra=item
	return palabra



'''
A esta función se le pasa de parametro el mensaje recibido en el reto 4 y elimina la parte en la que se nos indica el tamaño del archivo.
'''
def eliminar_n_bytes(msg):
	index=0
	for i in msg:
		if (chr(i)==':'):
			break
		else:
			index+=1
	return msg[index+1:]



'''
Función para obtener el número de bytes que ocupa el archivo a recibir en la fase 4
'''
def obtenerBytes(msg):
	index=0
	for i in msg:
		if (i ==':'):
			break
		else:
			index+=1
	tamano=msg[:index]
	return int(tamano)


'''
Esta función y la siguiente sirven para calcular en checksum de un payload que será enviado en la fase 5, WYP
'''
#https://bitbucket.org/DavidVilla/inet-checksum/src/master/inet_checksum.py
def sum16(data):
	if len(data) % 2:
		data = b'\0' + data

	return sum(struct.unpack('!%sH' % (len(data) // 2), data))

#https://bitbucket.org/DavidVilla/inet-checksum/src/master/inet_checksum.py
def cksum(data):
	sum_as_16b_words  = sum16(data)
	sum_1s_complement = sum16(struct.pack('!L', sum_as_16b_words))
	_1s_complement    = ~sum_1s_complement & 0xffff
	return _1s_complement



'''
Esta función actúa para recibir la petición de cada cliente, descargar el RFC que solicita y enviarlo al cliente.
'''
#https://rico-schmidt.name/pymotw-3/urllib.request/
def gestor_peticiones(sock,client,n):
	print("[FASE 6 Servidor Proxy] Cliente conectado",n,client)
	peticionHTTP=sock.recv(RECV_TCP).decode()
	if(peticionHTTP.find('POST') == -1):  #Si la petición no es POST entonces no es el último cliente

		rfc = peticionHTTP.splitlines()[0].split(' ')[1]

		print("[FASE 6 Servidor Proxy] Petición Cliente ",n,"recibida")

		get = request.Request('https://uclm-arco.github.io/ietf-clone/rfc' + rfc) #Realizamos la petición para descargar el archivo y contestamos al cliente con su contenido
		respuestaHTTP = request.urlopen(get)
		data = respuestaHTTP.read()
		sock.sendall('HTTP/1.1 200 OK\n\n'.encode() + data)
		sock.close()
	
		print("[FASE 6 Servidor Proxy] Petición cliente",n,"descargada y reedirigida")
		#print("[FASE 6 Servidor Proxy] Respuesta Cliente ",n," :",data)


		
	else: #El último cliente sí contiene POST
		print("[FASE 6 Servidor Proxy] El cliente número ",n,"contenía la petición POST")
		global instrucciones
		instrucciones = peticionHTTP #Almacenamos el mensaje en la variable global instrucciones para poder utilizarla en la función que resuelve el reto 6 y recuperar el código para la fase 7
		sock.sendall(('HTTP/1.1 200 OK\n\n').encode())
		sock.close()

		if respuestas:
			escribe(peticionHTTP)
			global FASE
			FASE+=1
		


'''
Es el servidor al que se conecta cada cliente, de esta forma podemos atender concurrentemente a todos ellos. Cuando ya no quedan clientes, el servidor se cierra.
'''
def servidorProxy(socketProxy):
	socketProxy.bind(('',PORT_PROXY))
	socketProxy.listen()

	n=0

	while 1:
		child_sock,client=socketProxy.accept()
		n=n+1
		peticion = threading.Thread(target=gestor_peticiones, args=(child_sock,client,n))
		peticion.daemon = True
		peticion.start()
		if threading.active_count() > 15: #Cuando hay más de este número de hilos ejecutándose concurrentemente, nos da problemas y por eso lo limitamos
			peticion.join() #Cuando hay más del límite, el siguiente tendrá que esperar a que uno de ellos termine para conectarse.


	print("[FASE 6 Servidor Proxy Cerrado]")	
	socketProxy.close()


			









#############################################################################
##                   FUNCIONES PARA RESOLVER FASES                         ##
#############################################################################



'''
Esta función resuelve la fase 0 de la Gymkana. Consiste en conectarnos al servidor y recibir las primeras instrucciones
de la Gymkana.
'''
def fase0():

	
	#Recibimos las instrucciones y enviamos los datos necesarios
	print("\n------------------ FASE 0 ------------------\n")
	print("[Fase 0] RECIBIENDO LAS PRIMERAS INSTRUCCIONES DEL SERVIDOR DE LA GYMKANA\n")
	sock0=socket(AF_INET, SOCK_STREAM)
	sock0.connect((SERVER,PORT_FASE0))
	msg0=sock0.recv(RECV_UDP).decode()
	print("[Fase 0] ENVIANDO LOS DATOS REQUERIDOS POR EL SERVIDOR\n") 
	sock0.send('juanmanuel.porrero'.encode(),PORT_FASE0)

	
	print("[Fase 0] CÓDIGO PARA COMPLETAR LA SIGUIENTE FASE:")
	msg1=sock0.recv(RECV_UDP).decode()
	cod=obtenerCodigo(msg1)
	print(cod,"\n")
	sock0.close()

	#Solo se escribirá en el fichero si hemos introducido la opción respuestas
	if respuestas:
		escribe(msg1)
		global FASE
		FASE+=1
	
	return cod

	

'''
Función para pasar el reto 1. Consiste en crear un servidor UDP. Utilizaremos threads para poder crear el servidor en este mismo archivo y debido a que un servidor no debe iniciar la conexión.
El servidor recibirá las instrucciones y podremos continuar al siguiente reto.
'''
def fase1(cod1):

	print("\n------------------ FASE 1 ------------------\n")

	#Utilizaremos un puerto aleatorio entre esos dos valores
	PORT_FASE1=randint(3000,7000)
	msg1=[""] 
	
	#Creamos el hilo del servidor local
	hilo1 = threading.Thread(target=Fase1server, args=(PORT_FASE1,msg1))
	hilo1.start()

	#Eviamos la petición
	peticion="%s %s" % (PORT_FASE1,cod1)
	sock1=socket(AF_INET, SOCK_DGRAM)
	sock1.sendto(peticion.encode(),(SERVER,PORT_SERVER1))
	print("[FASE 1 Cliente] Petición:",repr(peticion)," enviada a",SERVER,":",PORT_SERVER1) 

	#Esperamos al servidor
	global Fase1end
	while not(Fase1end):
		sleep(2)
	
	#Obtenemos el código
	cod2= obtenerCodigoCode(msg1[0].decode())
	print("[Fase 1] Código necesario para la siguiente fase:")
	print(cod2,"\n")

	sock1.close()
	

	if respuestas:
		escribe(msg1[0].decode())
		global FASE
		FASE+=1

	return cod2


'''
Fase 2 de la Gymkana. El reto consiste en contar cuantos numeros aparecen antes del 0. El 0 puede estar en el primer paquete recibido o no. Para asegurarnos de que nos llega el 0
utilizamos un bucle de recepción que para cuando detecta el 0 (haciendo uso de la función detectarCero). Después, pasamos el mensaje con el 0 a la función cuentaCaracteres para que nos
devuelva la cantidad de números antes del 0.
'''
def fase2(cod2):

	print("\n------------------ FASE 2 ------------------\n")

	#Creamos el socket TCP y la variable counter para almacenar la cuenta
	sock2=socket(AF_INET, SOCK_STREAM)
	sock2.connect((SERVER,PORT_SERVER2))
	counter=0

	#Recibimos el mensaje hasta detectar el 0
	msg2=sock2.recv(RECV_TCP).decode()
	while (detectarCero(msg2)==False):
		msg2 += sock2.recv(RECV_TCP).decode()

	#Sacamos la cuenta, después enviamos la petición
	counter=cuentaCaracteres(msg2)
	print("Resultado de la cuenta de números: ",counter)
	peticion="%s %s" % (cod2,counter)
	print("[FASE 2 Cliente] Petición:",repr(peticion)," enviada a",SERVER,":",PORT_SERVER2) 
	sock2.sendall(peticion.encode())

	#Este tipo de bucle lo veremos en todos los retos, se realiza para eliminar texto residual
	#mediante la función find() ya que todos las instrucciones contienen el caracter '>'
	msg2=sock2.recv(RECV_TCP).decode()
	while (msg2.find('>')==-1):
		msg2=sock2.recv(RECV_TCP).decode()
		
	cod3= obtenerCodigoCode(msg2)
	sock2.close()
	print("[Fase 2] Código necesario para la siguiente fase:")
	print(cod3,"\n")

	if respuestas:
		escribe(msg2)
		global FASE
		FASE+=1

	return cod3




'''
Reto 3. La estructura del reto es parecida a la del 2, pero más complicado. Esta vez recibiremos números y palabras juntos, y tendremos
que sumar esos números hasta sobrepasar 1300 y devolver la palabra inmediatamente anterior al número que ha hecho que la suma rebase 1300.
'''
def fase3(cod3):

	print("\n------------------ FASE 3 ------------------\n")

	#Creamos el socket TCP
	sock3=socket(AF_INET, SOCK_STREAM)
	sock3.connect((SERVER,PORT_SERVER3))

	#Recibimos el mensaje las veces que haga falta hasta que nos aseguramos que la suma de los números que hay en él es mayor que 1300, haciendo uso de la funcion sumaNumeros()
	msg3=sock3.recv(RECV_TCP).decode()
	while sumaNumeros(msg3) < 1301:
		msg3+=sock3.recv(RECV_TCP).decode()
	
	#Recibimos la última palabra antes de superar 1300 mediante solucionFase3() y la enviamos
	ultima_palabra=solucionFase3(msg3)
	print("[FASE 3 Cliente] La última palabra es: ",ultima_palabra)
	peticion="%s %s" % (ultima_palabra,cod3)
	sock3.sendall(peticion.encode())
	print("[FASE 3 Cliente] Petición:",repr(peticion)," enviada a",SERVER,":",PORT_SERVER3)

	#Recibimos las instrucciones del siguiente reto
	msg3=0 
	msg3=sock3.recv(RECV_TCP).decode()
	while(msg3.find(":") == -1):
		msg3=sock3.recv(1024).decode()

	indice=msg3.find(":")
	msg3 = msg3[indice-4:] #Algunas veces el mensaje code: viene pegado a una palabra en latín (ipsemcode:) por lo que buscamos : y nos retrasamos 4 posiciones para quedarnos con el msg verdadero
		
	#Obtenemos el código
	cod4= obtenerCodigoCode(msg3)
	sock3.close()
	print("[FASE 3 Cliente] Código necesario para la siguiente fase:")
	print(cod4,"\n")
	

	if respuestas:
		escribe(msg3)
		global FASE
		FASE+=1

	return cod4


'''
Esta función resuelve el reto 4, que consiste en recibir un archivo y calcular su MD5.
'''
def fase4(cod4):
	
	print("\n------------------ FASE 4 ------------------\n")

	#Creamos el socket y enviamos el código
	sock4=socket(AF_INET, SOCK_STREAM)
	sock4.connect((SERVER,PORT_SERVER4))
	sock4.sendall(cod4.encode())
	print("[FASE 4 Cliente] Petición:",repr(cod4)," enviada a",SERVER,":",PORT_SERVER4)

	#Recibimos una parte del archivo
	msg4=sock4.recv(RECV_TCP)
	tamano = obtenerBytes(msg4.decode('utf-8','ignore')) #Obtenemos su tamaño
	msg4=eliminar_n_bytes(msg4) #Eliminamos esa parte
	
	print('[FASE 4 Cliente] El tamaño del archivo son: ',tamano, 'bytes')
	
	#Recibimos hasta que el fichero está completo
	while(len(msg4) < tamano):
		msg4+=sock4.recv(tamano - len(msg4))
		if(len(msg4) >= tamano ):
			break

	print('[FASE 4 Cliente] Archivo recibido con éxito')
	
	#Calculamos su MD5 y lo enviamos para pasar el reto
	h = hashlib.md5(msg4).digest()
	print('[FASE 4 Cliente] El MD5 del archivo recibido es: ',h)
	sock4.sendall(h)
	print("[FASE 4 Cliente] Petición:",repr(h)," enviada a",SERVER,":",PORT_SERVER4)
	
	#Recibimos las instrucciones del siguiente
	msg4=sock4.recv(RECV_TCP).decode()
	while(msg4.find(">") == -1):
		msg4=sock4.recv(RECV_TCP).decode()

	cod5=obtenerCodigoCode(msg4)
	print('[FASE 4 Cliente] El código necesario para la siguiente fase es:')
	print(cod5,"\n")
	
	sock4.close()

	if respuestas:
		escribe(msg4)
		global FASE
		FASE+=1

	return cod5



'''

'''
def fase5(cod5):

	print("\n------------------ FASE 5 ------------------\n")

	sock5=socket(AF_INET, SOCK_DGRAM)

	#Preparamos el contenido
	msg_type=0
	code=0
	payload = base64.b64encode(cod5.encode())
	data = ('WYP'.encode() + bytes([msg_type]) + bytes(code) + payload)
	checksum = cksum(data)
	print("El tamaño de la cabecera es: {}.".format(struct.calcsize('3sBHH')))

	#Creamos el paquete
	paquete = struct.pack('!3sBHH'+str(len(payload))+'s','WYP'.encode(), msg_type, code, checksum, payload)
	
	print('[FASE 5 Cliente] Paquete WYP creado con las siguientes características:')
	print('  | HEADER | ')
	print('\t Type  -> 0 (request)')
	print('\t Code  -> 0 (request)')
	print('\t Checksum  -> ', checksum )
	print('  | DATA | ')
	print('\t Payload  ->', payload)

	#Lo enviamos
	sock5.sendto(paquete, (SERVER,PORT_SERVER5))

	#Recibimos y desempaquetamos
	msg5=sock5.recv(RECV_UDP)
	msg5 = struct.unpack('3sBHH'+str(len(msg5)-8)+'s', msg5[0:struct.calcsize('3sBHH'+str(len(msg5))+'s')])  #Restamos 8 porque la cabecera son 8 bytes y el resto será el mensaje de respuesta
	msg5=base64.b64decode(msg5[4]).decode()
	cod6=obtenerCodigoCode(msg5)
	print('[FASE 5 Cliente] El código necesario para la siguiente fase es:')
	print(cod6,"\n")

	if respuestas:
		escribe(msg5)
		global FASE
		FASE+=1

	return cod6




'''
En la fase tendremos que atender peticiones de muchos clientes que se conectaran a un servidor proxy que hemos creado. Tendremos que atender concurrentemente todas sus peticiones y dentro del tiempo límite
ya que si no tendremos problemas de Time Out. El último cliente nos enviará la información del siguiente reto mediante una petició POST. El servidor Proxy estará activo hasta que se ha respondido a todos los clientes.
'''
def fase6(cod6):

	print("\n------------------ FASE 6 ------------------\n")

	#Socked para comunicarnos con runway
	peticion="%s %s"% (cod6, PORT_PROXY)
	sock6=socket(AF_INET,SOCK_STREAM)
	sock6.connect((SERVER,PORT_SERVER6))
	sock6.send(peticion.encode())
	print("[FASE 6 Cliente] Petición:",repr(peticion),"enviada a",SERVER,":",PORT_SERVER6)

	#Servidor proxy al que se conectarán los diferentes clientes
	socketProxy=socket(AF_INET, SOCK_STREAM)
	proxy = threading.Thread(target=servidorProxy, args=(socketProxy,))
	proxy.start()

	msg6=sock6.recv(1024).decode()
	
	print("[FASE 6 Cliente MENSAJE FINAL] ",msg6)
	
	sock6.close()
	socketProxy.close()
	print("[FASE 6] Socket del Servidor Proxy cerrado")
	cod7=obtenerCodigoCode(instrucciones,8)
	print('[FASE 6 Cliente] El código necesario para la siguiente fase es:')
	print(cod7,"\n")

	return cod7





'''
Simplemente tendremos que enviar el código recibido en la fase anterior para confirmar que hemos superado la gymkana.
'''
def fase7(cod7):
	print("\n------------------ FASE 7 ------------------\n")
	sock7=socket(AF_INET,SOCK_STREAM)
	sock7.connect((SERVER,PORT_SERVER7))
	sock7.sendall(cod7.encode())
	msg7=sock7.recv(RECV_TCP).decode()
	print("[FASE 7] ",msg7)

	if respuestas:
		escribe(msg7)
		global FASE
		FASE+=1








#############################################################################
##                               MAIN                                      ##
#############################################################################

print('\n\t\t\t#############################################################################\n','\t\t\t##          GYMKANA JUAN MANUEL PORRERO ALMANSA 2ºA CURSO 2019/2020	   ##\n','\t\t\t#############################################################################')

ficheroSiNo() #Evaluamos si hay que escribir en el fichero o no
cod1=fase0()
cod2=fase1(cod1)
cod3=fase2(cod2)
cod4=fase3(cod3)
cod5=fase4(cod4)
cod6=fase5(cod5)
cod7=fase6(cod6)
fase7(cod7)
_exit(0)
