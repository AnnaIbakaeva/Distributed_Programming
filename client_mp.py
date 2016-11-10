import rpyc


class Client(object):
    def __init__(self):
	    self.current_my_value = 0
		self.my_data = []
		self.iteration_size = 0
		self.iterations_count = 0
		
		self.update_data(infList, port)
		
		self.calculate(1000000 / 4, 10)
		
	def calculate(self, count, iterations):
	    iterCount = iterations
        iterSize = count / iterCount

        self.update_data(iterCount, iterSize)
		
		self.user.mass_start()
		
		
	def mass_start(self):
	    self.main()
		
	def main(self):
	    result = self.get_result()		
		
	def get_result(self):
	    wait = 0
	    iterationsCount = (Informations.Count + 1) * IterationsCount; # сколько всего вычислений
	    alreadyCalc = self.is_all_over() # сколько уже сделано
		
		while alreadyCalc < iterationsCount:
		    aviable = self.get_active_clients_count() # сколько активных учатсникв
            clients = self.get_clients_count() # сколько всего должно быть
            doing = alreadyCalc + Informations.Count(x => x.WaitMe && x.HasConnection); # сколько сделано на данный момент задач + сколько делаются в данный момент
            if doing < iterationsCount: #// ??? // Если ктото упал  // и при этом есть свободные итерации
                self.next_step()  # берем итерацию и делаем
            alreadyCalc = self.is_all_over() # обновляем общее значение сделанных итераций
			
					
		# считаем число пи
        count = self.MyData.Count
        result = 0
        for value in self.MyData:
		    result += value;
			
		for information in self.Informations: 
            for value in information.RecievedData:
                result += value
            dataCount = len(information.RecievedData)
            count += dataCount
			
	    return (float)((float)result * 4) / (float)count

    def is_all_over(self):
        dataCount = len(self.my_data)
	    Informations.ForEach(x => dataCount += x.RecievedData.Count);
		
	def get_active_clients_count(self):
	    return Informations.Count(x => x.HasConnection == true)
		
	def get_clients_count(self):
	    return len(Informations)
		
	def next_step(self):
	    # Сообщаем каждому, с кем есть связь, что мы считаем
		for other in Informations:
		    if other.HasConnection:
			    self.user.wait(true)
		
		self.make_iteration() #// Считаем один блок
		
		# рассылаем всем посчитаный блок
		for other in Informations:
		    if other.HasConnection:
			    self.user.UpdateInformation()
				self.user.wait(false)
				
				
	def wait(self, isWait):
	    self.get_information().WaitMe = isWait
		
		
	def make_iteration(self):
	    self.current_my_value = 0
		for i in range(0, self.iteration_size):
		    self.current_my_value += self.is_enter()
		self.my_data.append((float)self.current_my_value / self.iteration_size)
	
	
	def is_enter(self):
	    """// Берет произвольную точку в квадрате с ребром 1 и считает её удаленность от левого нижнего угла
	    // Возвращает 1, если точка находится в окружности
	    // Возвращает 0, если точка за пределами окружности"""
	    x = rand()
	    y = rand()
		z = sqrt(x*x + y*y)
		
		if z <= 1:
		    return 1
		return 0
		
	def update_data(self, count, size):
	    Informations.ForEach(i => i.RecievedData = new List<double>());
		
		self.my_data = []
		self.iterations_count = count
		self.iteration_size = size
		
		print("I got some task! Iteraions: " + count + " with size of: " + size)
		
	def update_information(self, value):
	    GetInformation(address).RecievedData.Add(value);
		
#public Information GetInformation(string address)
 #           {
  #              return Informations.First(x => x.Address == address);
   #         }
		
	
		
		
		
		
	
		
	    
		
	