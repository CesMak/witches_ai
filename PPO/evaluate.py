import joblib
import numpy as np

infos = joblib.load("epInfos.pkl")
infos = [t for t in infos if t] # delete all empty entrys
print("games played", len(infos), "  games in parralell:", len(infos[0]))

def getSummedResults(infos, input_name):
	for game in infos:
		summed_results = 0
		for parallel in game:
			summed_results+=(parallel[input_name])
	return summed_results

def check_nan(input_name):
	print("\n")
	loaded_model = joblib.load(input_name)
	for i in loaded_model: print(i.size, type(i), i.shape, "NANS:", np.sum(np.isnan(i, where=True)))

anja_last_game = getSummedResults(infos, "A_tr")
lena_last_game = getSummedResults(infos, "L_tr")
bob_last_game = getSummedResults(infos, "B_tr")
tim_last_game = getSummedResults(infos, "T_tr")
print("Anja", anja_last_game, anja_last_game/len(infos[0]), "Lena", lena_last_game, lena_last_game/len(infos[0]))
print("Bob ", bob_last_game, bob_last_game/len(infos[0]), "Tim ", tim_last_game, tim_last_game/len(infos[0]))

#Check NAN:
check_nan("modelParameters450")
