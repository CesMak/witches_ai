## Rules:
*	60 	   Cards(4xJoker, 1-14 in Yellow, Green, Red, Blue)
*	Red    Cards give -1 Point (except Red 11)
*	Blue   Cards do nothing    (except Blue 11 if you have it in your offhand deletes all Green -Points)
*	Green  Cards			   (except Green 11 -5 and Green 12 -10 Points)
* 	Yellow Cards do nothing    (except Yellow 11 +5)
*	A joker can be placed anytime otherwise you have to give the same color as the first player
*	Aim:	Have a minimum of minus Points!
* 	Note: Number 15 is a Joker

## Run code:
* necessary is >=python3.5
* Train the agent: 'python Agent.py'
* Play random    : 'python play_random.py'

## DQN Representation
### Inputs:
As binary (a vector of 180 bool)
* 60 card x is currently on the table
* 60 card x is in the ai hand
* 60 card x is already been played

### Outputs:
*    If the ai is the first player of a round it can play any card
*    If the ai is not first player it has to respect the first played card (or play a wizzard)
This means there is actually a list of available options. I then sort this list and have 60 Output bools which I set to 1 if this option is possible. Among these options the ai should then decide what the correct option is.

## TODO:
* respect: [evaluating the value of the state after the action with your neural network instead of the value of a action](https://ai.stackexchange.com/questions/16999/dqn-card-game-how-to-represent-the-actions)
* Have a look into: [github_rlcards](https://github.com/datamllab/rlcard) [and this paper](https://arxiv.org/abs/1910.04376)

## Stats for AI
* Currently the train_long_memory does not work at all nevertheless, the ai player seems to learn something:
* ![Ai (orange) a little bit better as the other players](imgs/ai_.png)


## Stats (random playing):
* For 4 Players, played 50.000 Rounds
* If Player 0 has to start and plays a random card he will have a minus of -6.025 for each game
* Not Player 0  random	-5.85 each game
* Not Player 0  mini	    -5.80 each game
