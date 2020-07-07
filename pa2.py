import threading
import time
import socket
import sys
import ast
import numpy as np
import pickle
import sched

def update_distances(matrix, received, neighbor, name):
	original = matrix.copy()

	#matrix is 5x5, received is 1x5
	temp = get_node_num(neighbor)
	own = get_node_num(name)
	#update row of neighbor in own matrix
	for i in range(0,5):
		matrix[temp,i] = received[i]
		matrix[i,temp] = received[i]
		
	#update rest of matrix
		for i in range(0,5):
			for j in range(0,5):
				matrix[j,i] = min(matrix[j,i], matrix[j,temp] + received[i])		
				

	
	
	if np.array_equal(matrix,original)== False:
		print(name," DV has updated\n\n")
		return "updated",name
	
	return "same",name
	

def tcp_listen(host,port,name,distances,matrix,queue,round):
	try:
		while True:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.bind((host,port))
				s.listen()
				s.settimeout(3)
				conn, addr = s.accept()
				with conn:
					while True:
						data = conn.recv(1024)
						if not data:
							break
						data=pickle.loads(data)
						#update matrix
						node = data[1]
						flag = data[2]
						queue = data[3]
						round = data[4]
						data = data[0]
						if flag == "no go":
							print(name," received DV from ", node)
							response = update_distances(matrix,data,node,name)
							#tell node if it updated
							conn.send(pickle.dumps(response))
							#print("response is", response)
						else:
							return "go"
					conn.close()
						
							
				
	except socket.timeout:
		return "timeout"
	finally:
		s.close()
	
		
		

def tcp_send(host,port,dst_ip,dst_port,name,matrix,flag,queue,round):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((dst_ip,dst_port))
		#send row matrix
		s.send(pickle.dumps((matrix[get_node_num(name)],name,flag,queue,round)))
		#get response back
		data = s.recv(1024)
		if not data:
			return None
		s.close();
		data = pickle.loads(data)
		return data
	
def node_name(num):
	if num==0:
		return 'a'
	if num==1:
		return 'b'
	if num==2:
		return 'c'
	if num==3:
		return 'd'
	if num==4:
		return 'e'

def get_port_num(node):
#return the corresponding port number
	if node=='a':
		return a_port
	if node=='b':
		return b_port
	if node=='c':
		return c_port
	if node=='d':
		return d_port
	if node=='e':
		return e_port

def get_node_num(node):
	if node=='a':
		return 0
	if node=='b':
		return 1
	if node=='c':
		return 2
	if node=='d':
		return 3
	if node=='e':
		return 4

def next_node(queue,node):
	x = get_node_num(node)
	queue[x] =0
	#print("queue = ",queue)
	for i in range(x,5):
		if queue[i] == 1:
			return node_name(i)
	
	for i in range(0,5):
		if queue[i] == 1:
			return node_name(i)
	
	print("no next node")
	return 'z'
		
def add_to_queue(queue,node):
	queue[get_node_num(node)] =1

def connect(neighbors, port, mode, name, matrix, last_matrix,queue,round):
	loop = True
	while loop:
		if mode ==0:
			flag = tcp_listen('localhost',port,name,neighbors,matrix,queue,round)
			if flag == "go":
				mode=1
			if flag == "timeout":
				loop = False
				print("Final DV for", name, ":",matrix[get_node_num(name)],"\n" )
		
		elif mode==1:
			round = round +1
			#determine the neighbors port number and make a tcp connection
			print("Round ",round, ": " ,name)
			print("Current DV Matrix: \n",matrix)
			print("Last DV Matrix: \n",last_matrix)
			print("Updated from last DV matrix or the same?")
			if round==1 or not np.array_equal(matrix, last_matrix):
				print("updated")
				responses = []
				for x in neighbors:
					node = x[0]
					#establish tcp connection with neighbor
					responses.append(tcp_send('localhost',port,'localhost',get_port_num(node),name,matrix,"no go",queue,round))
					
				for x in responses:
					if x[0] =="updated":
						add_to_queue(queue,x[1])
						loop = True
			
				if loop == True:
					#tell next in line to send
					mode =0
					node = next_node(queue,name)
					last_matrix = matrix.copy()
					if not node=='z':
						#print("telling ",node, " to go next")
						tcp_send('localhost',port,'localhost',get_port_num(node),name,matrix,"go",queue,round)
			
			else:
				print("same")
				node = next_node(queue,name)
				mode =0 
				last_matrix = matrix.copy()
				if not node=='z':
					#print("telling ",node, " to go next")
					tcp_send('localhost',port,'localhost',get_port_num(node),name,matrix,"go",queue,round+1)
			
			
			
	
def network_init():
	#read from file
	f = open("network.txt","r")
	a = f.readline()
	b = f.readline()
	c = f.readline()
	d = f.readline()
	e = f.readline()
	
	#split into 5 arrays
	a = [int(n) for n in a.split(',')]
	b = [int(n) for n in b.split(',')]
	c = [int(n) for n in c.split(',')]
	d = [int(n) for n in d.split(',')]
	e = [int(n) for n in e.split(',')]
	
	a_neighbors = []
	b_neighbors = []
	c_neighbors = []
	d_neighbors = []
	e_neighbors = []
	
	a_matrix = np.full((5,5),999)
	b_matrix = np.full((5,5),999)
	c_matrix = np.full((5,5),999)
	d_matrix = np.full((5,5),999)
	e_matrix = np.full((5,5),999)
	
	#determine neighbors
	for i in range(0,5):
		if a[i]>0:
			a_matrix[0,i] =a[i]
			#add to neighbor list:
			pair = node_name(i),a[i]
			a_neighbors.append(pair)
	#print("A neighbors are:", a_neighbors)
	
	for i in range(0,5):
		if b[i]>0:
			b_matrix[1,i] =b[i]
			#add to neighbor list:
			pair = node_name(i),b[i]
			b_neighbors.append(pair)
	#print("B neighbors are:", b_neighbors)
	
	for i in range(0,5):
		if c[i]>0:
			c_matrix[2,i] =c[i]
			#add to neighbor list:
			pair = node_name(i),c[i]
			c_neighbors.append(pair)
	#print("C neighbors are:", c_neighbors)
	
	for i in range(0,5):
		if d[i]>0:
			d_matrix[3,i] =d[i]
			#add to neighbor list:
			pair = node_name(i),d[i]
			d_neighbors.append(pair)
	#print("D neighbors are:", d_neighbors)
	
	for i in range(0,5):
		if e[i]>0:
			e_matrix[4,i] =e[i]
			#add to neighbor list:
			pair = node_name(i),e[i]
			e_neighbors.append(pair)
	#print("E neighbors are:", e_neighbors)
	
	
	#compute initial matrices for each node
	for i in range(0,5):
		a_matrix[i,i]=0
		b_matrix[i,i]=0
		c_matrix[i,i]=0
		d_matrix[i,i]=0
		e_matrix[i,i]=0
		
	queue = np.array([1,1,1,1,1])
	
	#create n threads, pass them neighbors with distances
	thread1 = threading.Thread(target = connect, args = (a_neighbors,a_port,1,'a',a_matrix,a_matrix.copy(),queue,0))# 1 sending
	thread2 = threading.Thread(target = connect, args = (b_neighbors,b_port,0,'b',b_matrix,b_matrix.copy(),queue,0))# 2 listening
	thread3 = threading.Thread(target = connect, args = (c_neighbors,c_port,0,'c',c_matrix,c_matrix.copy(),queue,0))# 3 listening
	thread4 = threading.Thread(target = connect, args = (d_neighbors,d_port,0,'d',d_matrix,d_matrix.copy(),queue,0))# 4 listening
	thread5 = threading.Thread(target = connect, args = (e_neighbors,e_port,0,'e',e_matrix,e_matrix.copy(),queue,0))# 5 listening
	
	thread1.start() #a
	thread2.start() #b
	thread3.start() #c
	thread4.start() #d
	thread5.start() #e

#call the function: network_init
a_port = 10000
b_port = 20000
c_port = 30000
d_port = 40000
e_port = 50000
host = 'localhost'
network_init()






