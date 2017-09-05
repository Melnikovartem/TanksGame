# TanksGame
New game that i want to make for programmers

So in this game you have a tank and need to get the heightest score by your tank, but just by python script. 

_Ssry i am really bad at writing docs. I will improve my skills_
## Some words about Structure of the project:

There are 2 modules. They works separately. They are connected by database(I am using sqlite)
About the modules:
### __Game_module__
   Module that generate several games and than wright them to database. Wore information about the game read below
### Server module__
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
      Using ```python import tornado``` library as web framework
      
## Docs for the game
This is game were you need to get score.
Final score is calculated by formula:
```python score = coins*50 + hittings*20+lifetime-crashes*5
```
Where:
* Coins - number of coins that you's bot got in continuation of the game
* Hittings - How many times your's bot hitted
* Lifetime - how may ticks you's bot was alive
* Crashes - how may ticks you's bot crashed











_It is not such important to make good readme for this project. I wan't spend much time doing it._
