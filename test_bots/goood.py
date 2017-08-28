import random

def make_choice(x,y,field):

	x_size = len(field)
	y_size = len(field[0])
	
	coin_left = x_size
	coin_right = x_size
	coin_up = y_size
	coin_down = y_size
	stena = 0

	for i in range(1, x):
		if field[x-i][y]==-1:
			stena = 1
		if coin_left == x_size and field[x-i][y] == 1 and stena == 0:
			coin_left = i
		if field[x-i][y]!=0 and field[x-i][y]!=1 and field[x-i][y]!=-1 and stena ==0:
			return "fire_left"
			
	stena = 0
	
	for i in range(x+1, x_size):
		if field[i][y]==-1:
			stena = 1
		if coin_right == x_size and field[i][y] == 1 and stena == 0:
			coin_left = i - x 
		if field[i][y]!=0 and field[i][y]!=1 and field[i][y]!=-1 and stena==0:
			return "fire_right"

	stena = 0
	
	for i in range(1, y):
		if field[x][y-i]==-1:
			stena = 1
		if coin_up == y_size and field[x][y-i] == 1 and stena == 0:
			coin_up = i
		if field[x][y-i]!=0 and field[x][y-i]!=1 and field[x][y-i]!=-1 and stena==0:
			return "fire_up"
			
	stena = 0
	
	for i in range(y + 1, y_size):
		if field[x][i]==-1:
			stena = 1
		if coin_down == y_size and field[x][i] == 1 and stena == 0:
			coin_down = i - y
		if field[x][i]!=0 and field[x][i]!=1 and field[x][i]!=-1 and stena == 0:
			return "fire_down"

			
	if coin_up <= coin_down and coin_up <= coin_left and coin_up <= coin_right  and coin_up != y_size:
		return "go_up"

	if coin_down <= coin_up and coin_down <= coin_left and coin_down <= coin_right  and coin_down != y_size:
		return "go_down"

	if coin_left <= coin_down and coin_left <= coin_up and coin_left <= coin_right  and coin_left != x_size:
		return "go_left"

	if coin_right <= coin_down and coin_right <= coin_left and coin_right <= coin_up  and coin_right != x_size:
		return "go_right"
		
			
	return random.choice(["go_up","go_down","go_left","go_right"])
