from gameClasses import game
import numpy as np
import random
import math
from multiprocessing import Process, Pipe

#now create a vectorized environment
def worker(remote, parent_remote):
	parent_remote.close()
	my_game = game(["Tim", "Bob", "Lena", "Anja"])
	while True:
		cmd, data = remote.recv()
		if cmd == 'step':
			reward, done, info = my_game.step(data)
			remote.send((reward, done, info))
		elif cmd == 'reset':
			print("inside reset!! This is never entered????!!!!!")
			my_game.reset()
			pGo, cState, availAcs = my_game.getState()
			remote.send((pGo, cState))
		elif cmd == 'getCurrState':
			pGo, cState, availAcs = my_game.getState() # in here!
			#print("in getCurrState:", availAcs, cState)
			remote.send((pGo, cState, availAcs))
		elif cmd == 'close':
			remote.close()
			break
		else:
			print("Invalid command sent by remote")
			break


class vectorizedBig2Games(object):
	def __init__(self, nGames):

		self.waiting = False
		self.closed = False
		self.remotes, self.work_remotes = zip(*[Pipe() for _ in range(nGames)])
		self.ps = [Process(target=worker, args=(work_remote, remote)) for (work_remote, remote) in zip(self.work_remotes, self.remotes)]

		for p in self.ps:
			p.daemon = True
			p.start()
		for remote in self.work_remotes:
			remote.close()

	def step_async(self, actions):
		for remote, action in zip(self.remotes, actions):
			remote.send(('step', action))
		self.waiting = True

	def step_wait(self):
		results = [remote.recv() for remote in self.remotes]
		self.waiting = False
		rewards, dones, infos = zip(*results)
		return rewards, dones, infos

	def step(self, actions):
		self.step_async(actions)
		return self.step_wait()

	def currStates_async(self):
		for remote in self.remotes:
			remote.send(('getCurrState', None))
		self.waiting = True

	def currStates_wait(self):
		results = [remote.recv() for remote in self.remotes]
		self.waiting = False
		pGos, currStates, currAvailAcs = zip(*results)
		return np.stack(pGos), np.stack(currStates), np.stack(currAvailAcs)

	def getCurrStates(self):
		self.currStates_async()
		return self.currStates_wait()

	def close(self):
		if self.closed:
			return
		if self.waiting:
			for remote in self.remotes:
				remote.recv()
		for remote in self.remotes:
			remote.send(('close', None))
		for p in self.ps:
			p.join()
		self.closed = True
