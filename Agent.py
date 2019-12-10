import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from network import Linear_QNet2
import random
import os
import pygame
import numpy as np
from operator import add
from collections import deque
from witches_game import game
import matplotlib.pyplot as plt
import matplotlib.animation as animation

random.seed(9001) # always same case !

class DQNAgent_train(object):

	def __init__(self):
		self.gamma = 0.9
		self.epsilon = 0
		self.counter_games = 0
		self.memory = deque()
		self.lr = 1e-4
		self.model = Linear_QNet2(180, 256, 60) #input_size, hidden_size, output_size
		self.model.train()
		self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
		self.loss_fn = nn.MSELoss()

		fig = plt.figure()
		self.ax1 = fig.add_subplot(1,1,1)

	def get_state(self, game):
		return np.asarray(game.getState())

	def remember(self, state, action, reward, next_state, done):
		self.memory.append([state, action, reward, next_state, done])
		if len(self.memory) > 100000:
			self.memory.popleft()

	def train_long_memory(self, memory):
		self.counter_games += 1
		if len(memory) > 1000:
			minibatch = random.sample(memory, 1000)
		else:
			minibatch = memory

		state, action, reward, next_state, done = zip(*minibatch)
		state = torch.tensor(state, dtype=torch.float) #[1, ... , 0]
		action = torch.tensor(action, dtype=torch.long) # [1, 0, 0]
		reward = torch.tensor(reward, dtype=torch.float) # int
		next_state = torch.tensor(next_state, dtype=torch.float) #[True, ... , False]
		target = reward
		# Loss function?!:
		target = reward + self.gamma * torch.max(self.model(next_state))
		print("Target:", target)
		location = torch.argmax(action)
		print("Location:", location)
		# location = [[x] for x in torch.argmax(action).numpy()]
		# location = torch.tensor(location)
		pred = self.model(state)#.gather(1, location)#[action]
		pred = pred.squeeze(1)
		loss = self.loss_fn(target, pred)
		loss.backward()
		self.optimizer.step()

	def train_short_memory(self, state, action, reward, next_state, done):
		state = torch.tensor(state, dtype=torch.float)
		next_state = torch.tensor(next_state, dtype=torch.float)
		action = torch.tensor(action, dtype=torch.long)
		reward = torch.tensor(reward, dtype=torch.float)
		target = reward

		if not done:
			target = reward + self.gamma * torch.max(self.model(next_state))
		pred = self.model(state)
		target_f = pred.clone()
		target_f[torch.argmax(action).item()] = target
		loss = self.loss_fn(target_f, pred)
		self.optimizer.zero_grad()
		loss.backward()
		self.optimizer.step()

	def animate(self, i):
		print(i)
		self.ax1.clear()
		self.ax1.plot([1,1],[2,3])

	def getSummedList(self, inputlist):
		summed_list = []
		for j, i in enumerate(inputlist):
			if j >0:
				summed_list.append(i + summed_list[j-1])
			else:
				summed_list.append(i)
		return summed_list

	def plot(self, score, other_players):
		# from IPython import display
		# display.clear_output(wait=True)
		# display.display(plt.gcf())
		plt.clf()
		plt.title('Training...')
		plt.xlabel('Number of Games')
		plt.ylabel('Score')
		j = 0

		plt.plot(score, label="ai")
		plt.plot(self.getSummedList(score), label="ai_s")

		tim  = []
		anja = []
		lena = []
		for i in other_players:
			tim.append(i[0])
			anja.append(i[1])
			lena.append(i[2])
		plt.plot(tim, label="tim")
		plt.plot(self.getSummedList(tim), label="tim_s")
		plt.plot(anja, label="anja")
		plt.plot(self.getSummedList(anja), label="anja_s")
		plt.plot(lena, label="lena")
		plt.plot(self.getSummedList(lena), label="lena_s")
		plt.legend()
		plt.draw()

	def getActionsIndex(self, options_list, tmp):
		p = 0
		for i, item in enumerate((options_list)):
			if item:
				p+=1
			if item and p==tmp:
				return i
		return 0

	def get_action(self, state, game):
		self.epsilon = 80 - self.counter_games
		result = 0
		my_color = game.first_played_card
		if my_color is  not None:
			my_color  = my_color.color

		options       = game.players[game.ai_player_idx].getOptions(my_color, orderOptions=1)
		trans_options = game.translateOptions(options)
		print("options of ai player (sorted:) ", options)
		print("translated options:", trans_options)
		rand_opt = random.randint(0, len(options))

		# sometimes play a random card for testing
		if random.randint(0, 200) < self.epsilon:
			# play a random possible option!
			print("AI random option:", rand_opt)
			result = self.getActionsIndex(trans_options, rand_opt)
		else:
			state0     = torch.tensor(state, dtype=torch.float)
			prediction = self.model(state0)
			new_action = torch.argmax(prediction).item()
			print("argmax:", torch.argmax(prediction), new_action)
			print(game.action2Card(new_action))
			if trans_options[new_action]:  #check if this action is possible!
				result = new_action
			else:
				result = self.getActionsIndex(trans_options, rand_opt)
		print("Result:", result, "Ai plays: ", game.action2Card(result))
		return result


class DQNAgent_play(object):
	def __init__(self, path):
		self.counter_games = 0
		self.model = Linear_QNet2(11, 256, 3)
		self.model.load_state_dict(torch.load(path))
		self.model.eval()

	def get_state(self, snake):
		state = [
			# Snake location
			(snake.x_change == 20 and snake.y_change == 0 and ((list(map(add, snake.snakeSegments[0], [20, 0])) in snake.snakeSegments) or snake.snakeSegments[0][0] + 20 >= (snake.display_width - 20))) or
			(snake.x_change == -20 and snake.y_change == 0 and ((list(map(add, snake.snakeSegments[0], [-20, 0])) in snake.snakeSegments) or snake.snakeSegments[0][0] - 20 < 20)) or
			(snake.x_change == 0 and snake.y_change == -20 and ((list(map(add, snake.snakeSegments[0], [0, -20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] - 20 < 20)) or
			(snake.x_change == 0 and snake.y_change == 20 and ((list(map(add, snake.snakeSegments[0], [0, 20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] + 20 >= (snake.display_height-20))),

			(snake.x_change == 0 and snake.y_change == -20 and ((list(map(add,snake.snakeSegments[0],[20, 0])) in snake.snakeSegments) or snake.snakeSegments[0][0] + 20 > (snake.display_width-20))) or
			(snake.x_change == 0 and snake.y_change == 20 and ((list(map(add,snake.snakeSegments[0],[-20,0])) in snake.snakeSegments) or snake.snakeSegments[0][0] - 20 < 20)) or
			(snake.x_change == -20 and snake.y_change == 0 and ((list(map(add,snake.snakeSegments[0],[0,-20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] - 20 < 20)) or
			(snake.x_change == 20 and snake.y_change == 0 and ((list(map(add,snake.snakeSegments[0],[0,20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] + 20 >= (snake.display_height-20))),

			(snake.x_change == 0 and snake.y_change == 20 and ((list(map(add,snake.snakeSegments[0],[20,0])) in snake.snakeSegments) or snake.snakeSegments[0][0] + 20 > (snake.display_width-20))) or
			(snake.x_change == 0 and snake.y_change == -20 and ((list(map(add, snake.snakeSegments[0],[-20,0])) in snake.snakeSegments) or snake.snakeSegments[0][0] - 20 < 20)) or
			(snake.x_change == 20 and snake.y_change == 0 and ((list(map(add,snake.snakeSegments[0],[0,-20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] - 20 < 20)) or
			(snake.x_change == -20 and snake.y_change == 0 and ((list(map(add,snake.snakeSegments[0],[0,20])) in snake.snakeSegments) or snake.snakeSegments[0][-1] + 20 >= (snake.display_height-20))),

			# Move direction
			snake.x_change == -20,
			snake.x_change == 20,
			snake.y_change == -20,
			snake.y_change == 20,
			# Raspberry location
			snake.raspberryPosition[0] < snake.snakePosition[0],  # food left
			snake.raspberryPosition[0] > snake.snakePosition[0],  # food right
			snake.raspberryPosition[1] < snake.snakePosition[1],  # food up
			snake.raspberryPosition[1] > snake.snakePosition[1]  # food down
			]
		for i in range(len(state)):
			if state[i]:
				state[i]=1
			else:
				state[i]=0

		return np.asarray(state)

	def plot(self, score, mean_per_game):
		from IPython import display
		display.clear_output(wait=True)
		display.display(plt.gcf())
		plt.clf()
		plt.title('Training...')
		plt.xlabel('Number of Games')
		plt.ylabel('Score')
		plt.plot(score)
		plt.plot(mean_per_game)
		plt.ylim(ymin=0)
		plt.text(len(score)-1, score[-1], str(score[-1]))
		plt.text(len(mean_per_game)-1, mean_per_game[-1], str(mean_per_game[-1]))

	def get_action(self, state):
		final_move = [0, 0, 0]
		state0 = torch.tensor(state, dtype=torch.float)
		prediction = self.model(state0)
		move = torch.argmax(prediction).item()
		final_move[move] += 1
		return final_move

def train():

	model_folder_path = './model'
	if not os.path.exists(model_folder_path):
		os.makedirs(model_folder_path)

	score_plot = []
	others_score_list = []
	total_score = 0
	mean_plot =[]
	record = -150
	agent = DQNAgent_train()
	my_game = game(["Tim", "Bob", "Lena", "Anja"])
	nu_games  = 0
	while True:
		#1. Play unti AI has to move:
		my_game.play_round_until_ai()

		#2. Get old state:
		state_old = agent.get_state(my_game)

		#3. Get the action the AI should perform
		action_ = agent.get_action(state_old, my_game)

		#4. perform new Action and get new state
		#reward rates how good the current action was
		#score is the actual score of this game!
		reward, done, score, others_score = my_game.finishRound(action_)

		# 5: Calculate new state
		state_new = agent.get_state(my_game)

		#6. train short memory base on the new action and state
		agent.train_short_memory(state_old, action_, reward, state_new, done)

		#7. store the new data into a long term memory
		agent.remember(state_old, action_, reward, state_new, done)

		if done == True:
			# One game is over, train on the memory and plot the result.
			my_game.reset_ai_game()
			total_score += score
			#TODO:
			#agent.train_long_memory(agent.memory)
			print('Game', agent.counter_games, '      Score:', score)
			if score > record:
				record = score
				name = 'best_model.pth'.format(score)
				dir = os.path.join(model_folder_path, name)
				torch.save(agent.model.state_dict(), dir)
			print('record: ', record)
			score_plot.append(score)
			others_score_list.append(others_score)
			#mean = total_score / agent.counter_games
			#mean_plot.append(mean)

			nu_games +=1
			if nu_games == 50:
				print(total_score)
				agent.plot(score_plot, others_score_list)
				plt.show()
				return

	plt.ioff()
	plt.show()

def play():
	pygame.display.set_caption('AI play!')
	# Load image and set icon
	image = pygame.image.load('joystick.ico')
	pygame.display.set_icon(image)

	model_folder_path = './model/best_model.pth'
	plt.ion()
	pygame.init()
	score_plot = []
	total_score = 0
	mean_plot =[]
	record = 0
	agent = DQNAgent_play(model_folder_path)
	game = game_ai()
	while True:
		state = agent.get_state(game)
		final_move = agent.get_action(state)
		reward, done, score = game.frameStep(final_move)

		if done == True:
			sc = game.reset()
			total_score += sc
			print('Game', agent.counter_games, '      Score:', sc)
			if sc > record:
				record = sc
			print('record: ', record)
			score_plot.append(sc)
			mean = total_score / agent.counter_games
			mean_plot.append(mean)
			agent.plot(score_plot, mean_plot)

	plt.ioff()
	plt.show()

if __name__ == '__main__':
	#agent.plot(50)
	#plot()
	train()
	#play()
