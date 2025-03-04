import pygame
from os.path import join 
from os import walk
from random import choice, sample

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

def tile_importer(cols, *path):
    attack_frames = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            surf = pygame.image.load(full_path).convert_alpha()
            attack_frames[file_name.split('.')[0]] = []
            cutout_width = surf.get_width() / cols
            for col in range(cols):
                cutout_surf = pygame.Surface((cutout_width, surf.get_height()), pygame.SRCALPHA)
                cutout_rect = pygame.Rect(cutout_width * col, 0, cutout_width, surf.get_height())
                cutout_surf.blit(surf, (0,0), cutout_rect)
                attack_frames[file_name.split('.')[0]].append(cutout_surf)
    return attack_frames            

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

class Creature:
    def get_data(self, name):
        self.element = MONSTER_DATA[name]['element']
        self._health = self.max_health = MONSTER_DATA[name]['health']
        self.abilities = sample(list(ABILITIES_DATA.keys()),4)
        self.name = name

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = min(self.max_health, max(0, value))

class Monster(pygame.sprite.Sprite, Creature):
    def __init__(self, name, surf):
        super().__init__()
        self.image = surf
        self.rect = self.image.get_rect(bottomleft=(100, WINDOW_HEIGHT))
        self.get_data(name)

    def __repr__(self):
        return f'{self.name}: {self.health}/{self.max_health}'

class Opponent(pygame.sprite.Sprite, Creature):
    def __init__(self, name, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom = (WINDOW_WIDTH - 250, 300))
        self.get_data(name)

class UI:
    def __init__(self, monster, player_monsters, simple_surfs, get_input):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2 - 100
        self.top = WINDOW_HEIGHT / 2 + 50
        self.monster = monster
        self.simple_surfs = simple_surfs
        self.get_input = get_input

        # control
        self.general_options = ['attack', 'potions', 'switch', 'escape']
        self.general_index = {'col': 0, 'row': 0}
        self.attack_index = {'col': 0, 'row': 0}
        self.state = 'general'
        self.rows, self.cols = 2,2
        self.visible_monsters = 4
        self.player_monsters = player_monsters
        self.available_monsters = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]
        self.switch_index = 0

    def input(self):
        keys = pygame.key.get_pressed()
        if self.state == 'general':
            self.general_index['row'] = (self.general_index['row'] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.general_index['col'] = (self.general_index['col'] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE]:
                self.state = self.general_options[self.general_index['col'] + self.general_index['row'] * 2]

        elif self.state == 'attack':
            self.attack_index['row'] = (self.attack_index['row'] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.attack_index['col'] = (self.attack_index['col'] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE]:
                attack = self.monster.abilities[self.attack_index['col'] + self.attack_index['row'] * 2]
                self.get_input(self.state, attack)
                self.state = 'general'
                
        elif self.state == 'switch':
            if self.available_monsters:
                self.switch_index = (self.switch_index + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % len(self.available_monsters)

                if keys[pygame.K_SPACE]:
                    self.get_input(self.available_monsters[self.switch_index])
                    self.state = 'general'

        elif self.state == 'heal':
            self.get_input('heal')
            self.state = 'general'

        elif self.state == 'escape':
            self.get_input('escape')    

        if keys[pygame.K_ESCAPE]:
            self.state = 'general'  
            self.general_index = {'col': 0, 'row': 0}
            self.attack_index = {'col': 0, 'row': 0}   
            self.switch_index = 0   

    def quad_select(self, index, options):
        # bg
        rect = pygame.Rect(self.left + 40, self.top + 60, 400, 200)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        # menu
        for col in range(self.cols):
            for row in range(self.rows):
                x = rect.left + rect.width / (self.cols * 2) + (rect.width / self.cols) * col
                y = rect.top + rect.height / (self.rows * 2) + (rect.height / self.rows) * row
                i = col + 2 * row
                color = COLORS['gray'] if col == index['col'] and row == index['row'] else COLORS['black']

                text_surf = self.font.render(options[i], True, color)
                text_rect = text_surf.get_rect(center = (x,y))
                self.display_surface.blit(text_surf, text_rect)

    def switch(self):
        # bg
        rect = pygame.Rect(self.left + 40, self.top - 140, 400, 400)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        # menu
        v_offset = 0 if self.switch_index < self.visible_monsters else -(self.switch_index - self.visible_monsters + 1) * rect.height / self.visible_monsters
        for i in range(len(self.available_monsters)):
            x = rect.centerx
            y = rect.top + rect.height / (self.visible_monsters * 2) + rect.height / self.visible_monsters * i + v_offset
            color = COLORS['gray'] if i == self.switch_index else COLORS['black']
            name = self.available_monsters[i].name 

            simple_surf = self.simple_surfs[name]
            simple_rect = simple_surf.get_rect(center = (x - 100, y))

            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_rect(midleft = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(simple_surf, simple_rect)

    def stats(self):
        # bg
        rect = pygame.Rect(self.left, self.top, 250, 80)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        # data
        name_surf = self.font.render(self.monster.name, True, COLORS['black'])
        name_rect = name_surf.get_rect(topleft = rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        # health bar
        health_rect = pygame.Rect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surface, COLORS['gray'], health_rect)
        self.draw_bar(health_rect, self.monster.health, self.monster.max_health)

    def draw_bar(self, rect, value, max_value):
        ratio = rect.width / max_value
        progress_rect = pygame.Rect(rect.topleft, (value * ratio, rect.height))
        pygame.draw.rect(self.display_surface, COLORS['red'], progress_rect)   

    def update(self):
        self.input()
        self.available_monsters = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]

    def draw(self):
        match self.state:
            case 'general': self.quad_select(self.general_index, self.general_options)
            case 'attack': self.quad_select(self.attack_index, self.monster.abilities)
            case 'switch': self.switch()      

        if self.state != 'switch':
            self.stats()      

class OpponentUI:
    def __init__(self, monster):
        self.display_surface = pygame.display.get_surface()
        self.monster = monster
        self.font = pygame.font.Font(None, 30)

    def draw(self):
        # bg
        rect = pygame.Rect((0, 0, 250, 80))
        rect.midleft = (500, self.monster.rect.centery)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        # name
        name_surf = self.font.render(self.monster.name, True, COLORS['black'])
        name_rect = name_surf.get_rect(topleft = rect.topleft + pygame.Vector2(rect.width * 0.05))
        self.display_surface.blit(name_surf, name_rect)

        # health
        health_rect = pygame.Rect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        ratio = health_rect.width / self.monster.max_health
        progress_rect = pygame.Rect(health_rect.topleft, (self.monster.health * ratio, health_rect.height))
        pygame.draw.rect(self.display_surface, COLORS['gray'], health_rect)
        pygame.draw.rect(self.display_surface, COLORS['red'], progress_rect)

class AttackAnimationSprite(pygame.sprite.Sprite):
    def __init__(self, target, frames, groups):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = target.rect.center)

    def update(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()        

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.import_assets()
        self.player_active = True
        
        # groups 
        self.all_sprites = pygame.sprite.Group()

        # data
        player_monster_list = ['Sparchu', 'Cleaf', 'Jacana', 'Gulfin', 'Pouch', 'Larvea']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)

        # ui
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)

        # timers
        self.timers = {'player end': Timer(1000, func = self.opponent_turn), 'opponent end': Timer(1000, func = self.player_turn)}

    def get_input(self, state, data = None):
        if state == 'attack':
            self.apply_attack(self.opponent, data)
        elif state == 'heal':
            self.monster.health += 50
            AttackAnimationSprite(self.monster, self.attack_frames['green'], self.all_sprites)
        elif state == 'switch':
            self.monster.kill()
            self.monster = data
            self.all_sprites.add(self.monster)
            self.ui.monster = self.monster

        if state == 'escape':
            self.running = False
        self.player_active = False
        self.timers['player end'].activate()    

    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        attack_multiplier = ELEMENT_DATA[attack_data['element']][target.element]
        target.health -= attack_data['damage'] * attack_multiplier
        AttackAnimationSprite(target, self.attack_frames[attack_data['animation']], self.all_sprites)

    def opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            monster_name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(monster_name, self.front_surfs[monster_name], self.all_sprites)
            self.opponent_ui.monster = self.opponent
        else:
            attack = choice(self.opponent.abilities)
            self.apply_attack(self.monster, attack)
            self.timers['opponent end'].activate()

    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
            if available_monsters:
                self.monster.kill()
                self.monster = available_monsters[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                self.running = False    

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def import_assets(self):
        self.back_surfs = folder_importer('images', 'back')
        self.front_surfs = folder_importer('images', 'front')
        self.bg_surfs = folder_importer('images', 'other')
        self.simple_surfs = folder_importer('images', 'simple')
        self.attack_frames = tile_importer(4, 'images', 'attacks')

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surfs['floor'].get_rect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surfs['floor'], floor_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active:    
                self.ui.update()

            # draw
            self.display_surface.blit(self.bg_surfs['bg'], (0,0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()
        
        pygame.quit()
    
if __name__ == '__main__':
    game = Game()
    game.run()