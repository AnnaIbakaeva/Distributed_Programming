# coding: utf8
import rpyc
from random import random
from math import sqrt, ceil
import threading


class Client(object):
	def __init__(self):
		self.current_my_value = 0
		self.my_data = []
		self.received_data = []
		self.iteration_size = 0
		self.iterations_count = 0
		self.name = "Ann"
		self.other = None
		self.conn = None
		self.wait_me = False

		self.on_connect()

		self.calculate(1000000 / self.other.get_clients_count(), 10)

	def calculate(self, count, iterations):
		iterCount = iterations
		iterSize = count / iterCount

		self.other.update_data(iterCount, iterSize)

		self.other.mass_start()
		# thread = threading.Thread(target=self.other.mass_start)
		# thread.start()

	def mass_start(self):
		self.main()

	def main(self):
		result = self.get_result()
		print("Result pi = ", result)

	def get_result(self):
		iterationsCount = self.iterations_count * self.other.get_clients_count() # сколько всего вычислений
		alreadyCalc = self.is_all_over() # сколько уже сделано

		print("Before while, iterationsCount = ", iterationsCount, " alreadyCalc = ", alreadyCalc)
		while alreadyCalc < iterationsCount:
			# aviable = self.other.get_active_clients_count() # сколько активных учатсникв
			# clients = self.other.get_clients_count() # сколько всего должно быть
			doing = alreadyCalc + self.other.get_wait_me_clients_count() # сколько сделано на данный момент задач + сколько делаются в данный момент
			print("doing ", doing)
			if doing < iterationsCount: #// ??? // Если ктото упал  // и при этом есть свободные итерации
				self.next_step()  # берем итерацию и делаем
			alreadyCalc = self.is_all_over() # обновляем общее значение сделанных итераций
			print("alreadyCalc ", alreadyCalc)

		count = len(self.my_data)
		result = 0
		for value in self.my_data:
			result += value

		for rec_result in self.received_data:
			result += rec_result

		count += len(self.received_data)

		return float((result * 4) / count)

	def is_all_over(self):
		dataCount = len(self.my_data)
		dataCount += self.other.get_received_data_count()
		return dataCount

	def get_received_data_count(self):
		print("len(self.received_data) ", len(self.received_data))
		return len(self.received_data)

	# def get_my_data_count(self):
	# 	return len(self.my_data)

	def next_step(self):
		print("\nnext_step\n")
		# Сообщаем каждому, с кем есть связь, что мы считаем
		self.wait_me = True

		self.make_iteration() #// Считаем один блок
		# рассылаем всем посчитаный блок
		print("self.other.update_information ", self.my_data[len(self.my_data) - 1])
		self.other.update_information(self.my_data[len(self.my_data) - 1])
		self.wait_me = False

	def get_wait(self):
		print("self.wait_me ", self.wait_me)
		return self.wait_me

	def make_iteration(self):
		print("make_iteration")
		self.current_my_value = 0
		print("self.iteration_size = ", int(self.iteration_size))
		for i in range(0, int(self.iteration_size)):
			self.current_my_value += self.is_enter()
		data = float(self.current_my_value/self.iteration_size)
		print("data= ", data)
		self.my_data.append(data)


	def is_enter(self):
		"""// Берет произвольную точку в квадрате с ребром 1 и считает её удаленность от левого нижнего угла
	    // Возвращает 1, если точка находится в окружности
	    // Возвращает 0, если точка за пределами окружности"""
		x = random()
		y = random()
		z = sqrt(x*x + y*y)

		if z <= 1:
			return 1
		return 0

	def update_data(self, count, size):
		# Informations.ForEach(i => i.RecievedData = new List<double>());

		self.my_data = []
		self.iterations_count = count
		self.iteration_size = size

		print("I got some task! Iteraions: " + count + " with size of: " + size)

	def update_information(self, value):
		self.received_data.append(value)

	# Пересчитать нагрузку, которую будем считать
	# def update_iterations(self, unsolved):
	# 	current_active_clients = self.other.get_active_clients_count()
	# 	delta = ceil(float(unsolved / current_active_clients))
	# 	self.iterations_count += int(delta)

	# def update_status(self, name):
	# 	try:
	# 		client = self.other_clients.index(name)
	# 		client.has_connection = False
	#
	# 		unsolved = self.iterations_count - inf.RecievedData.Count;
	# 		self.update_iterations(unsolved)
	# 	except:
	# 		print ("No client ", name)

	def disconnect(self):
		if self.conn:
			try:
				self.other.logout()
			except:
				print("Logout except")
			self.conn.close()
			self.other = None
			self.conn = None

	def on_close(self):
		print("I closed!")
		self.disconnect()

	def on_connect(self):
		try:
			self.conn = rpyc.connect("localhost", 19912)
		except Exception:
			print("")
			print("EXCEPTION!!!")
			print("")
			self.conn = None
			return
		try:
			self.other = self.conn.root.login(self.name, self.update_data, self.mass_start,
											  self.get_wait, self.update_information, self.get_received_data_count)
		except ValueError:
			self.conn.close()
			self.conn = None

if __name__ == "__main__":
	cc = Client()