# TanksGame
New game that i want to make for programmers

So in this game you have a tank and need to get the heightest score by your tank, but just by python script. 

_Ssry i am really bad at writing docs. I will improve my skills_
## Some words about Structure of the project:

There are 2 modules. They works separately. They are connected by database(I am using sqlite)
About the modules:
### Game module
   Module that generate several games and than wright them to database. Wore information about the game read below
### Server module
  All stuff that you can view on the web site. Like: 
    * Regestration
      Of course you can wake your own accont(rigth now it is very bad-released)
    * Sing in
      You need to sing in to download your bot. Alsow you can coose your own style.
    * Leader Board
      You can get to the top by having heightest average score
    * Spectate games
      Alsow you can spectate games in different rooms
      We start different games on our server(each with 6 or less random bots) you can see their statistic and graphical interface.
      Using `import tornado` library as web framework
      
## Docs for the game
This is game were you need to get heightest score.

###### Score
Final score is calculated by formula:
```python score = coins*50 + hittings*20+lifetime-crashes*5```
Where:
* Coins - number of coins that you's bot got in continuation of the game
* Hittings - How many times your's bot hitted
* Lifetime - how may ticks you's bot was alive
* Crashes - how may ticks you's bot crashed

###### Your script
So your bot(tank) __must__ have function __make_choice__ that gets 3 arguments:
    1. X coordinate of your bot 
    2. Y coordinate of your bot
    3. Field - special type of field that contains all information about game
example:
```python
from random import choice

def make_choice(x,y,field):
    return choice(["fire_right", "fire_down", "fire_left", "fire_up", "go_right", "go_down", "go_left", "go_up"])
```

###### And you need to choose between this commands:
*Commands to move:
	1. "go_right"
	2. "go_down"
	3. "go_left"
	4. "go_left"
*Commands to fire:
	1. "fire_right"
	2. "fire_down"
	3. "fire_left"
	4. "fire_up"

First all players move and just then fire.

###### Before map about game objects: (all images from "Рост" style. It is my friend(or i just think so))
    * __BackGround__ = Just BG.
        ![BG](/server_module/styles/roctbb/grass.jpg)
    * __Tanks__ = Different players bots.
        ![Tans](/server_module/styles/roctbb/player.png)
    * __Wals__ = Tanks can't step _on_ walls and fire through them.
        ![Walls](/server_module/styles/roctbb/brick.png)
    * __Coins__ = You need to step on a coin to get some score points.
        ![Coins](/server_module/styles/roctbb/coin.png)
    * __Lasers__ = show shots of users.
        ![Lasers](/server_module/styles/roctbb/vertical.png)
        ![Lasers](/server_module/styles/roctbb/horizontal.png)
    
######Field Map:
	* I will write it later

Have Fun :)

-
-
-
-
-
-
-
-
-
-
-
_It is not such important to make good readme for this project. I wan't spend much time doing it._
