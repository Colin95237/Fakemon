import pygame
from os.path import join 
from os import walk

#Settings
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 
COLORS = {
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': 'gray',
    'white': '#ffffff',
}
MONSTER_DATA = {
	'Plumette':    {'element': 'plant', 'health': 90},
	'Ivieron':     {'element': 'plant', 'health': 140},
	'Pluma':       {'element': 'plant', 'health': 160},
	'Sparchu':     {'element': 'fire',  'health': 70},
	'Cindrill':    {'element': 'fire',  'health': 100},
	'Charmadillo': {'element': 'fire',  'health': 120},
	'Finsta':      {'element': 'water', 'health': 50},
	'Gulfin':      {'element': 'water', 'health': 80},
	'Finiette':    {'element': 'water', 'health': 100},
	'Atrox':       {'element': 'fire',  'health': 50},
	'Pouch':       {'element': 'plant', 'health': 80},
	'Draem':       {'element': 'plant', 'health': 110},
	'Larvea':      {'element': 'plant', 'health': 40},
	'Cleaf':       {'element': 'plant', 'health': 90},
	'Jacana':      {'element': 'fire',  'health': 60},
	'Friolera':    {'element': 'water', 'health': 70},
}
ABILITIES_DATA = {
	'scratch': {'damage': 20,  'element': 'normal', 'animation': 'scratch'},
	'spark':   {'damage': 35,  'element': 'fire',   'animation': 'fire'},
	'nuke':    {'damage': 50,  'element': 'fire',   'animation': 'explosion'},
	'splash':  {'damage': 30,  'element': 'water',  'animation': 'splash'},
	'shards':  {'damage': 50,  'element': 'water',  'animation': 'ice'},
    'spiral':  {'damage': 40,  'element': 'plant',  'animation': 'green'}
}
ELEMENT_DATA = {
    'fire':   {'water': 0.5, 'plant': 2,   'fire': 1,   'normal': 1},
    'water':  {'water': 1,   'plant': 0.5, 'fire': 2,   'normal': 1},
    'plant':  {'water': 2,   'plant': 1,   'fire': 0.5, 'normal': 1},
    'normal': {'water': 1,   'plant': 1,   'fire': 1,   'normal': 1},
}


# support
def folder_importer(*path):
    surfs = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            surfs[file_name.split('.')[0]] = pygame.image.load(full_path).convert_alpha()
    return surfs
def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            audio_dict[file_name.split('.')[0]] = pygame.mixer.Sound(join(folder_path, file_name))
    return audio_dict


# timer
class Timer:
	def __init__(self, duration, repeat = False, autostart = False, func = None):
		self.duration = duration
		self.start_time = 0
		self.active = False
		self.repeat = repeat
		self.func = func
		
		if autostart:
			self.activate()

	def __bool__(self):
		return self.active

	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		if self.repeat:
			self.activate()

	def update(self):
		if self.active:
			if pygame.time.get_ticks() - self.start_time >= self.duration:
				if self.func and self.start_time != 0: self.func()
				self.deactivate()


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups 
        self.all_sprites = pygame.sprite.Group()

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.all_sprites.update(dt)

            # draw  
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()
        
        pygame.quit()
    
if __name__ == '__main__':
    game = Game()
    game.run()
