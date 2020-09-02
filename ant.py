#V1 - thesis release version
import pygame,random
from pygame.locals import *

#Global functions
def cell_conversion(x,y,xoffset,yoffset):
	newx = (x*5) + xoffset
	newy = (y*5) + yoffset
	return newy,newx

def map_generator(dimension,evap):
	output = []
	row = []
	for i in range(0,dimension):
		for j in range(0,dimension):
			if i == 0 or i == dimension-1 or j == 0 or j == dimension-1:
				row.append(-1)
			else:
				row.append(1*(1-evap))
		output.append(row)
		row = []
	return output

def event_handler(currentflag):
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE: #spacebar pauses app
				if currentflag == 1: #if app is running
					return 0 #pause value
				else:
					return 1 #unpause value
		elif event.type == QUIT:
			pygame.quit()
			quit()
	return currentflag

#Map class
class Map():
	def __init__(self,marray,vx,vy,cx,cy,fx,fy,stats,evap):
		self.marray = marray
		self.len = len(marray)
		self.vx = vx #visualizer x
		self.vy = vy #visualizer y
		self.marray[cx][cy] = -2 #colony coordenates
		self.marray[fx][fy] = -3 #food coordenates
		self.antlist = [] #ant array
		self.statlist = [] #statistic collector list
		self.show_stats = stats
		self.evap = evap
	#Draw map - Main visualization tool
	def draw_map(self):
		for i in range(0,self.len):
			for j in range(0,self.len):
				(x,y) = cell_conversion(i,j,self.vx,self.vy)
				if self.marray[i][j] == -1:
					color = [0,0,0]
				elif self.marray[i][j] == -2:
					color = [0,150,0]
				elif self.marray[i][j] == -3:
					color = [150,0,0]
				else:
					value = self.marray[i][j]*5
					if value > 255:
						value = 255
					color = [255-value,255-value,255]
				pygame.draw.rect(appdisplay,color,[x,y,5,5])
	#Evaporate
	def evaporate(self):
		for i in range(0,self.len):
			for j in range(0,self.len):
				if self.marray[i][j] >= 0:
					self.marray[i][j] = (1-self.evap)*self.marray[i][j]
	#Statistic Collection - Prints captured data
	def print_stats(self):
		#id,x,y,objetive,goals,distance,pheromone
		for row in self.statlist: #expecting [[x,...]...] 7 elementos
			print("\t",row[0],"\t",row[1],"\t",row[2],"\t",row[3],"\t",row[4],"\t",row[5],"\t\t",row[6])
		self.statlist = []
	#Main Loop - Execute all ants
	def run_ants(self):
		self.statlist = []
		flag = 0
		for ant in self.antlist:
			ant.draw_ant(self.vx,self.vy)
			ant.pheromone_charge(self.marray)
			flag = ant.ant_movement(self.marray)
			self.statlist.append(ant.get_stats())
		if self.show_stats == 1:
			self.print_stats()
		if flag == 1:
				self.evaporate()
#Ant class
class Ant():
	def __init__(self,id,x,y,qconstant,antdistance):
		self.id = id
		self.x = x
		self.y = y
		self.objective = -3 #Inital objective: Food source cell
		self.distance = 0
		self.distance_value = antdistance
		self.qconstant = qconstant# Adjustable pheromone constant
		self.goals = 0
		self.barray = [1,1,1,1,0,1,1,1,1] # 0 unavailable movement / 1 available ...
		self.statarray = [self.id,0,0,0,0,0,0] #id,x,y,objetive,goals,distance,pheromone
		self.visited = []
	#Get stats
	def get_stats(self):
		#stat array 0 ID / array 5 pheromone charge on function pheromone charge
		self.statarray[1] = self.x
		self.statarray[2] = self.y
		self.statarray[3] = self.objective
		self.statarray[4] = self.goals
		self.statarray[5] = self.distance
		return self.statarray
	#Ant x,y position
	def get_ant_position(self):
		return self.x,self.y
	#Update x,y
	def update_position(self,x,y):
		self.x = x
		self.y = y
	#Draw ant
	def draw_ant(self,mapx,mapy):
		(x,y) = cell_conversion(self.x,self.y,mapx,mapy)
		pygame.draw.rect(appdisplay,[0,0,0],[x,y,5,5])
	#Pheromone
	def pheromone_charge(self,marray):
		self.distance = self.distance + self.distance_value
		if [self.x,self.y] not in self.visited:
			if  marray[self.x][self.y] >= 0:
				self.visited.append([self.x,self.y])
				value = marray[self.x][self.y] + (self.qconstant/self.distance)
				marray[self.x][self.y] = value
				self.statarray[6] = value
		else:
			# marray[self.x][self.y] = marray[self.x][self.y]
			self.statarray[6] = 0
	#Block movement
	def update_block(self,newx,newy):
		if newx == -1: #up
			if newy == -1:#left
				self.barray = [1,1,0,1,0,0,0,0,0]
				# self.barray = [1,1,1,1,0,0,1,0,0]
			elif newy == 0:#UP
				self.barray = [1,1,1,0,0,0,0,0,0]
				# self.barray = [1,1,1,1,0,1,0,0,0]
			elif newy == 1:#right
				self.barray = [0,1,1,0,0,1,0,0,0]
				# self.barray = [1,1,1,0,0,1,0,0,1]
		elif newx == 0: #middle
			if newy == -1:#left
				self.barray = [1,0,0,1,0,0,1,0,0]
				# self.barray = [1,1,0,1,0,0,1,1,0]
			elif newy == 1:#right
				self.barray = [0,0,1,0,0,1,0,0,1]
				# self.barray = [0,1,1,0,0,1,0,1,1]
		elif newx == 1: #down
			if newy == -1:#left
				self.barray = [0,0,0,1,0,0,1,1,0]
				# self.barray = [1,0,0,1,0,0,1,1,1]
			elif newy == 0:#DOWN
				self.barray = [0,0,0,0,0,0,1,1,1]
				# self.barray = [0,0,0,1,0,1,1,1,1]
			elif newy == 1:#right
				self.barray = [0,0,0,0,0,1,0,1,1]
				# self.barray = [0,0,1,0,0,1,1,1,1]
	#Change objective
	def change_objective(self):
		# self.visited = []
		self.distance = 0
		self.barray = [1,1,1,1,0,1,1,1,1]
		self.goals = self.goals + 1
		if self.objective == -2:
			self.objective = -3
			self.visited = []
			return 1# 1: Full cicle
		else:
			self.objective = -2
			return 0# 0: Mid cicle
	#main function - movement
	def ant_movement(self,marray):
		blist = []
		alist = []
		aux = 0
		sumation = 0
		for i in range(self.x-1,self.x+2):
			for j in range(self.y-1,self.y+2):
				if marray[i][j] == self.objective: #objective found
					self.update_position(i,j)
					return self.change_objective()
				elif marray[i][j] >= 0:
					# print("ITEM",i,j,marray[i][j])
					alist.append([i,j]) #available moves
					if self.barray[aux] == 1: # available moves acording to barray
						sumation = sumation + marray[i][j]
						blist.append([i,j,marray[i][j]])
				aux = aux + 1
		# print("alist",alist)
		# print("blist",blist)
		# print("len(blist)",len(blist))
		if len(blist) == 0:
			# print("blist vacia")
			newmove = random.choice(alist)
			x,y = newmove[0],newmove[1]
		else:
			for item in blist:
				item[2] = item[2] / sumation #item = [i,j,Probability]
			# print("blist, prob",blist)
			blist.sort(key= lambda x : x[2])#sorting for Probability value
			# print("blist, prob, sorted",blist)
			sumation = 0
			r = random.random() #r = [0,1)
			# print("r",r)
			for item in blist:
				sumation = sumation + item[2]
				if r <= sumation:
					x,y = item[0],item[1]
					# print(x,y)
					break
		self.update_block(x - self.x, y - self.y)
		self.update_position(x,y)
		return 0

#Variable configuration
show_stats = 1
antdistance = 0.2
evaporation_rate = 0.5
qconstant = 100
clock_speed = 300
antnum = 15
colx = 2
coly = 2
foodx = 58
foody = 58
map_dimension = 62


#Pygame setup
pygame.init()
pygame.display.set_caption('ACO V.1')
appres = [410,410]
appdisplay = pygame.display.set_mode(appres)
clock = pygame.time.Clock()
#map generation
array = map_generator(map_dimension,evaporation_rate)
map0 = Map(array,53,53,colx,coly,foodx,foody,show_stats,evaporation_rate)
#ant array
for i in range(0,antnum):
	map0.antlist.append(Ant(i,colx,coly,qconstant,antdistance))

#Main code
appdisplay.fill([255,255,255])
map0.draw_map()
flag = 0
iter = 0
while True:
	clock.tick(clock_speed)
	flag = event_handler(flag)
	if flag == 0:
		pygame.draw.rect(appdisplay,[255,0,0],[10,10,20,20])
	elif flag == 1:
		appdisplay.fill([255,255,255])
		map0.draw_map()
		if show_stats == 1:
			print("Iteration:",iter,"\n\tID\tX\tY\tObj\tGoals\td\t\t\tPheromone")
		map0.run_ants()
		iter = iter + 1
	pygame.display.update()
