from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from random import randint

cities = []
cities_count = 0
distance_matrix = []

# Логические флаги
is_already_started = False

class Algorithm:
    def __init__(self, name):
        self.name = name

algorithms = [Algorithm('Brute-force'), Algorithm('Genetic')]

class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class BruteForceStrategy():
    def __init__(self, cities: list, distance_matrix: list, canvas: Canvas):
        self.cities = cities
        self.distance_matrix = distance_matrix
        self.canvas = canvas
        self.cur_path = []
        self.min_len = 100000000
        self.min_path = []
        self.iteration = 0
    def start(self):
        cities_without_first = cities.copy()
        cities_without_first.pop(0)
        self.find_path(cities[0], cities_without_first)
    def draw_path(self, path: list):
        self.canvas.delete(ALL)
        for i in range(len(path) - 1):
            draw_city(path[i], is_first=i==0)
            self.canvas.create_line(path[i].x, path[i].y, path[i+1].x, path[i+1].y)


    def find_path(self, c: City, rest: list):
        if is_already_started:
            self.cur_path.append(c)
            if len(rest) == 0:
                self.iteration += 1
                lbl_iteration.configure(text="Итерация: " + str(self.iteration))
                cur_len = 0
                self.cur_path.append(cities[0])
                for i in range(len(self.cur_path)):
                    cur_len += distance_matrix[self.cur_path[i].id][self.cur_path[i-1].id]
                if cur_len < self.min_len or self.min_len == None:
                    self.min_len = cur_len
                    self.min_path = self.cur_path.copy()
                    lbl_length_1.configure(text='Длина: ' + str(self.min_len))
                    self.draw_path(self.min_path)
                self.cur_path.pop(len(self.cur_path) - 1)
                window.update()
            else:
                for r in rest:
                    r_copy = rest.copy()
                    r_copy.remove(r)
                    self.find_path(r, r_copy)
            self.cur_path.pop(len(self.cur_path) - 1)

class GeneticStrategy():
    def __init__(self, cities: list, distance_matrix: list, canvas: Canvas):
        self.cities = cities
        self.distance_matrix = distance_matrix
        self.canvas = canvas
        self.population = []
        self.min_len = 1000000000000
        self.min_path = []
        self.cur_gen = 0
        self.max_gen = int(ent_max_gen.get())

    def path_length(self, path):
        res = 0
        path.append(0)
        for i in range(len(path) - 1):
            res += distance_matrix[path[i]][path[i+1]]
        path.pop(len(path) - 1)
        return round(res, 2)

    def start(self):
        # генерируем популяцию
        self.population.append(list(range(cities_count)))
        for i in range(int(ent_population.get()) - 1):
            h = self.population[i].copy()
            d1, d2 = randint(1, cities_count - 1), randint(1, cities_count - 1)
            t = h[d1]
            h[d1] = h[d2]
            h[d2] = t
            self.population.append(h)
        # запускаем процесс
        while is_already_started and self.cur_gen < self.max_gen:
            self.cur_gen += 1
            lbl_generation.configure(text="Поколение: " + str(self.cur_gen))

            # Рисуем кратчайший
            if self.path_length(self.population[0]) < self.min_len:
                self.min_len = self.path_length(self.population[0])
                self.min_path = self.population[0].copy()
                self.draw_path(self.population[0])
                lbl_length_2.configure(text="Длина: " + str(self.min_len))

            # Скрещивание (скрещиваем половину особей)
            for n in range(int(0.5 * len(self.population))):
                d1 = d2 = 0
                while d1 == d2:
                    d1, d2 = randint(0, len(self.population) - 1), randint(0, len(self.population) - 1)

                cut_point = randint(1, len(self.population[0]) - 2)

                child = []
                for m in range(2):
                    if m == 1:
                        t = d1
                        d1 = d2
                        d2 = t
                    for i in range(0, cut_point):
                        child.append(self.population[d1][i])
                    for j in range(cut_point, len(self.population[0])):
                        if self.population[d2][j] not in child:
                            child.append(self.population[d2][j])
                    if len(child) < len(self.population[0]):
                        for k in range(cut_point, len(self.population[0])):
                            if self.population[d1][k] not in child:
                                child.append(self.population[d1][k])
                    self.population.append(child)
                    child = []

            # Мутации

            for h in self.population:
                if randint(0, 100) <= int(ent_mutation_percentage.get()):
                    d1, d2 = randint(1, len(self.population[0]) - 1), randint(1, len(self.population[0]) - 1)
                    t = h[d1]
                    h[d1] = h[d2]
                    h[d2] = t

            self.population = sorted(self.population, key=self.path_length)

            # Удаляем половину особей (самых плохо приспособленых)

            for i in range(len(self.population)-1, int(0.5*len(self.population)) - 1, -1):
                self.population.pop(i)

            window.update()

    def draw_path(self, path: list):
        self.canvas.delete(ALL)
        path.append(0)
        for i in range(len(path) - 1):
            draw_city(cities[path[i]], is_first=i == 0)
            self.canvas.create_line(cities[path[i]].x, cities[path[i]].y, cities[path[i + 1]].x, cities[path[i + 1]].y,
                                    width=2, arrow='last')
        path.pop(len(path)-1)

def place_city(event_place_city):
    global cities_count

    x = event_place_city.x
    y = event_place_city.y

    city = City(cities_count, x, y)
    cities.append(city)
    cities_count += 1
    draw_city(city, is_first=cities_count==1)


def draw_city(city: City, is_first = False):
    color = 'white'
    if is_first:
        color = 'red'
    map_canvas_1.create_oval(city.x - 5, city.y - 5, city.x + 5, city.y + 5, fill=color, width=2)
    map_canvas_2.create_oval(city.x - 5, city.y - 5, city.x + 5, city.y + 5, fill=color, width=2)

def reset_maps():
    global is_already_started, cities, cities_count
    if is_already_started:
        is_already_started = False
        messagebox.showinfo(message='Процесс остановлен')
        # Останавливаем досрочно
    else:
        # Если уже остановлен, чистим карты
        map_canvas_1.delete(ALL)
        map_canvas_2.delete(ALL)
        cities = []
        cities_count = 0

def generate_distance_matrix():
    global distance_matrix
    distance_matrix = [[0] * cities_count for k in range(cities_count)]
    for i in range(cities_count):
        for j in range(cities_count):
            distance_matrix[i][j] = round(((cities[i].x - cities[j].x)**2 + (cities[i].y - cities[j].y)**2)**0.5, 2)

def start():
    global is_already_started
    population = ent_population.get()
    mutation_percentage = ent_mutation_percentage.get()
    max_generations = ent_max_gen.get()
    if is_already_started:
        messagebox.showwarning(title='Внимание', message='Процесс уже запущен. Вы можете преждевременно прервать его, нажав СБРОС')
    elif population == '' or mutation_percentage == '' or max_generations == '' or len(cities) <= 1:
        messagebox.showerror(title='Ошибка', message='Введены не все данные')
    else:
        population = int(population)
        mutation_percentage = int(mutation_percentage)
        max_generations = int(max_generations)
        if population < 2 or mutation_percentage >= 100 or mutation_percentage < 1 or max_generations < 1:
            messagebox.showerror(title='Ошибка', message='Некорректные данные')
        else:
            # Все ок, запускаем алгоритмы
            is_already_started = True
            generate_distance_matrix()

            genetic_strategy = GeneticStrategy(cities, distance_matrix, map_canvas_2)
            genetic_strategy.start()

            brute_force_strategy = BruteForceStrategy(cities,distance_matrix,map_canvas_1)
            brute_force_strategy.start()


            is_already_started = False

# интерфейс
window = Tk()
window.title('Comm')

s = Style()
s.theme_use('clam')

root = Frame(window)
root.grid(row=0, column=0, sticky=(N, E, S, W))
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

start = Button(root, text='Start')
start.grid(row=0, column=0, sticky='w')
stop = Button(root, text='Stop')
stop.grid(row=0, column=1, sticky='w')
root.rowconfigure(0, pad=10)
root.columnconfigure(0, pad=10)

row = 1
for alg in algorithms:
    c = Canvas(root, width=400, height=400, background='white')
    c.grid(row=row, column=0, columnspan=2, padx=(10, 10), pady=(10, 10), sticky=(N, E, S, W))
    c.create_text(5, 5, text=alg.name, anchor='nw', font='TkFixedFont', fill='black')

    p = Frame(root)
    p.grid(row=row, column=3, sticky='nesw')

    s = Scale(c)
    c.create_window(5, 50, anchor='nw', window=s)


    root.rowconfigure(row, weight=1)
    row += 1

root.columnconfigure(1, weight=1)

# Карты
# map_canvas_1 = Canvas(window, height=300, width=300, background='white')
# map_canvas_1.place(x=20, y=20)
# map_canvas_1.bind("<Button 1>", place_city)

# map_canvas_2 = Canvas(window, height=300, width=300, background='white')
# map_canvas_2.place(x=340, y=20)
# map_canvas_2.bind("<Button 1>", place_city)

# # Подписи под картами
# lbl_iteration = Label(window, text='Итерация: ', background='gray92')
# lbl_iteration.place(x=20, y=325)

# lbl_length_1 = Label(window, text='Длина пути: ', background='gray92')
# lbl_length_1.place(x=165, y=325)

# lbl_generation = Label(window, text='Поколение: ', background='gray92')
# lbl_generation.place(x=340, y=325)

# lbl_length_2 = Label(window, text='Длина пути: ', background='gray92')
# lbl_length_2.place(x=485, y=325)

# # Ввод данных (подписи к полям)
# lbl_population = Label(window, text='Популяция', background='gray92')
# lbl_population.place(x=660, y=20)

# lbl_mutation_percentage = Label(window, text='Процент мутаций', background='gray92')
# lbl_mutation_percentage.place(x=660, y=60)

# lbl_max_gen = Label(window, text='Максимальное кол-во поколений', background='gray92')
# lbl_max_gen.place(x=660, y=100)

# # Ввод данных (поля для ввода)
# ent_population = Entry(width=20)
# ent_population.place(x=860, y=20)

# ent_mutation_percentage = Entry(width=20)
# ent_mutation_percentage.place(x=860, y=60)

# ent_max_gen = Entry(width=20)
# ent_max_gen.place(x=860, y=100)

# # Кнопки
# btn_reset = Button(text='Сброс', width=30, height=2, command=reset_maps)
# btn_reset.place(x=660, y=220)

# btn_start = Button(text='Старт', width=30, height=2, command=start)
# btn_start.place(x=660, y=265)

window.mainloop()
