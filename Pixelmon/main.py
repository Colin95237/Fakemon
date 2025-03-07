import pygame
from pygame.locals import *
import time
import math
import random
import openai

#API-Schlüssel für openai
openai.api_key = ""

#Pygame initialisieren
pygame.init()

#Spielfenster erstellen
game_width = 500
game_height = 500
size = (game_width, game_height)
#Spielfenster mit den definierten Größen
game = pygame.display.set_mode(size)
#Titel des Spielfensters festlegen
pygame.display.set_caption('Pokemon Battle')

#Farben definieren
black = (0, 0, 0)
white = (255, 255, 255)
grey = (200, 200, 200)
dark_grey = (100, 100, 100)
light_grey = (220, 220, 220)
gold = (218, 165, 32)
yellow = (255, 223, 0)
green = (0, 200, 0)
dark_green = (0, 150, 0)
light_green = (144, 238, 144)
red = (200, 0, 0)
dark_red = (150, 0, 0)
light_red = (255, 99, 71)
blue = (0, 0, 255)
dark_blue = (0, 0, 139)
light_blue = (173, 216, 230)

class Move():
    #Attacke erstellen für ein Pokemon
    def __init__(self, name, power, type):
        self.name = name #Name der Attacke
        self.power = power #Angriffskraft der Attacke
        self.type = type #Typ der Attacke 

class Pokemon(pygame.sprite.Sprite):
    #Pokemon-Objekt erstellen
    def __init__(self, name, level, type, hp, attack, defense, speed, moves, x, y, side="front"):
        
        pygame.sprite.Sprite.__init__(self) #Sprite-Klasse initialisieren
        
        self.name = name #Namen des Pokemons
        self.level = level #Level des Pokemons
        self.types = type #Typ des Pokemons
        
        #Position des Pokemons auf dem Bildschirm setzen
        self.x = x
        self.y = y
        
        #Anzahl verfügbarer Tränke
        self.num_potions = 3
        
        #Statuswerte setzen
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.current_hp = self.hp
        self.max_hp = self.hp
        
        #Attacken des Pokemons
        self.moves = moves
        
        #Sprite-Größe setzen
        self.size = 150
        self.image = pygame.Surface((self.size, self.size)) #Oberfläche für das Sprite erstellen
        self.image.fill(grey)  #Sprite mit grauer Farbe als Platzhalter gefüllt
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        #Sprite laden
        self.set_sprite('front')

    #Angriff auf ein anderes Pokemon, other = das Pokemon was angegriffen wird, move = verwendete Attacke
    def perform_attack(self, other, move):

        #Displaynachricht
        display_message(f'{self.name} used {move.name}')
        
        #2 Sekunden Pause
        time.sleep(2)
        
        #Berechnung des Schadens einer Attacke
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        
        #Falls der Attacken-Typ mit einem der Pokémon-Typen übereinstimmt, gibt es einen Schadensabzug von 0.5x.
        if move.type in self.types:
            damage *= 0.5
            
        #Ein kritischer Treffer hat eine Wahrscheinlichkeit von 6,25 % und erhöht den Schaden.
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
            
        #Schaden wird auf eine ganze Zahl abgerundet
        damage = math.floor(damage)
        
        #Gegner erhält den berechneten Schaden
        other.take_damage(damage)

    #Erlittenen Schaden verarbeiten und die HP des getroffenen Pokemons reduzieren
    def take_damage(self, damage):
        #HP des Pokemons um den erhaltenen Schaden verringern
        self.current_hp -= damage
        
        #HP kann nicht unter 0 fallen
        if self.current_hp < 0:
            self.current_hp = 0
    
    #heilt das Pokemon
    def use_potion(self):
        
        #Überprüfen ob noch gehealt werden kann
        if self.num_potions > 0:
            #HP um 30 erhöhen
            self.current_hp += 30
            #HP kann nicht über das Maximale erhöht werden
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
                
            #Healmöglichkeiten um 1 reduzieren
            self.num_potions -= 1
           
    # Methode zum Setzen des Pokémon-Sprites
    def set_sprite(self, side):
        try:
            self.image = pygame.image.load(f"images/{self.name.lower()}_{side}.png")
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except pygame.error:
            print(f"Fehler: Bild für {self.name} ({side}) nicht gefunden!")
    
    #Zeichnet das Pokémon-Sprite auf dem Bildschirm    
    def draw(self, alpha=255):
            
        #Erstellt eine Kopie des Pokémon-Sprites, um das Originalbild nicht zu verändern
        sprite = pygame.transform.scale(self.image, (self.size, self.size))

        # Erstellt eine Transparenzfarbe mit dem gegebenen Alpha-Wert
        transparency = (255, 255, 255, alpha)

        # Zeichnet das Sprite auf das Spielfeld an der gespeicherten Position
        game.blit(sprite, (self.x, self.y))
        
    #Zeichnet die Lebensanzeige (HP-Balken) des Pokémon auf den Bildschirm.
    def draw_hp(self):
        #Berechnet die Skalierung des HP-Balkens basierend auf der maximalen HP. Die gesamte Breite des Balkens beträgt 200 Pixel
        bar_scale = 200 // self.max_hp  

        #Zeichnet die gesamte HP-Leiste in Rot (verlorene HP)
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)  
            pygame.draw.rect(game, red, bar)  

        #Zeichnet die verbleibenden HP in Grün (über die rote Leiste)
        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)  
            pygame.draw.rect(game, green, bar)  

        #Erstellt die HP-Anzeige als Text (z. B. "HP: 35 / 50")
        font = pygame.font.Font(pygame.font.get_default_font(), 16)  
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)  

        #Positioniert den Text unterhalb des Balkens
        text_rect = text.get_rect()  
        text_rect.x = self.hp_x  
        text_rect.y = self.hp_y + 30  

        #Zeichnet den Text auf das Spielfeld
        game.blit(text, text_rect)
        
    #Gibt das Rechteck des Pokemon zurück    
    def get_rect(self):
        
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

#Textbox mit Nachricht am unteren Bildschirmrand
def display_message(message):
    
    #Weiße Box als Hintergrund wird gezeichnet
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    #Schwarze Umrandung für die Box
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    
    #Schirftart für den Text
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    #Nachrichtentext in Schwarz gerendert
    text = font.render(message, True, black)
    #Position des Textes in der Box
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    #Zeichnet den Text auf den Bildschirm
    game.blit(text, text_rect)
    #Bildschirmaktualisierung
    pygame.display.update()

#Button mit Textlabel
def create_button(width, height, left, top, text_cx, text_cy, label):
    
    #Aktuelle Position des Mauszeigers speichern
    mouse_cursor = pygame.mouse.get_pos()
    
    #Rechteck für den Button an der angegebenen Position
    button = Rect(left, top, width, height)
    
    #Überprüfen ob der Mauszeiger über dem Button ist
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button) #Button wird gold
    else:
        pygame.draw.rect(game, white, button)
        
    #Schriftart für Button-Text
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    #Button in Schwarz rendern
    text = font.render(f'{label}', True, black)
    #Text zentrieren im Button
    text_rect = text.get_rect(center=(text_cx, text_cy))
    #Text auf den Button zeichnen
    game.blit(text, text_rect)
    #Rückgabe des Buttons
    return button
        
# create the starter pokemons with hardcoded stats
bulbasaur_moves = [Move("Tackle", 40, "normal"), Move("Vine Whip", 45, "grass")]
charmander_moves = [Move("Tackle", 40, "normal"), Move("Ember", 40, "fire")]
squirtle_moves = [Move("Tackle", 40, "normal"), Move("Water Gun", 40, "water")]

bulbasaur = Pokemon('Bulbasaur', 30, 'grass', 45, 49, 49, 45, bulbasaur_moves, 25, 150)
charmander = Pokemon('Charmander', 30, 'fire', 39, 52, 43, 65, charmander_moves, 175, 150)
squirtle = Pokemon('Squirtle', 30, 'water', 44, 48, 65, 43, squirtle_moves, 325, 150)

pokemons = [bulbasaur, charmander, squirtle]

# the player's and rival's selected pokemon
player_pokemon = None
rival_pokemon = None

# Game loop
game_status = 'select pokemon'
while game_status != 'quit':
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'
            
        # detect keypress
        if event.type == KEYDOWN:
            
            # play again
            if event.key == K_y:
                # reset the pokemons
                bulbasaur = Pokemon('Bulbasaur', 25, 150)
                charmander = Pokemon('Charmander', 175, 150)
                squirtle = Pokemon('Squirtle', 325, 150)
                pokemons = [bulbasaur, charmander, squirtle]
                game_status = 'select pokemon'
                
            # quit
            elif event.key == K_n:
                game_status = 'quit'
            
        # detect mouse click
        if event.type == MOUSEBUTTONDOWN:
            
            # coordinates of the mouse click
            mouse_click = event.pos
            
            # for selecting a pokemon
            if game_status == 'select pokemon':
                
                # check which pokemon was clicked on
                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        # assign the player's and rival's pokemon
                        player_pokemon = pokemons[i]
                        rival_pokemon = pokemons[(i + 1) % len(pokemons)]
                        
                        # lower the rival pokemon's level to make the battle easier
                        rival_pokemon.level = int(rival_pokemon.level * .75)
                        
                        # set the coordinates of the hp bars
                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50
                        
                        game_status = 'prebattle'
            
            # for selecting fight or use potion
            elif game_status == 'player turn':
                
                # check if fight button was clicked
                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move'
                    
                # check if potion button was clicked
                if potion_button.collidepoint(mouse_click):
                    
                    # force to attack if there are no more potions
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left')
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} used potion')
                        time.sleep(2)
                        game_status = 'rival turn'
                        
            # for selecting a move
            elif game_status == 'player move':
                
                # check which move button was clicked
                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    
                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)
                        
                        # check if the rival's pokemon fainted
                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
            
    # pokemon select screen
    if game_status == 'select pokemon':
        
        game.fill(white)
        
        # draw the starter pokemons
        bulbasaur.draw()
        charmander.draw()
        squirtle.draw()
        
        # draw box around pokemon the mouse is pointing to
        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:
            
            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)
        
        pygame.display.update()
        
    # get moves from the API and reposition the pokemons
    if game_status == 'prebattle':
        
        # draw the selected pokemon
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()
        
        # reposition the pokemons
        player_pokemon.x = 25
        player_pokemon.y = 150
        rival_pokemon.x = 275
        rival_pokemon.y = 0
        
        # resize the sprites
        player_pokemon.size = 200
        rival_pokemon.size = 200


        player_pokemon.set_sprite('front')
        rival_pokemon.set_sprite('front')
        
        game_status = 'start battle'
        
    # start battle animation
    if game_status == 'start battle':
        
        # rival sends out their pokemon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
            
        # pause for 1 second
        time.sleep(1)
        
        # player sends out their pokemon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
        
        # draw the hp bars
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # determine who goes first
        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
        # pause for 1 second
        time.sleep(1)
        
    # display the fight and use potion buttons
    if game_status == 'player turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # create the fight and use potion buttons
        fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
        potion_button = create_button(240, 140, 250, 350, 370, 412, f'Use Potion ({player_pokemon.num_potions})')

        # draw the black border
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # display the move buttons
    if game_status == 'player move':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # create a button for each move
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y, move.name.capitalize())
            move_buttons.append(button)
            
        # draw the black border
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # rival selects a random move to attack with
    if game_status == 'rival turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # empty the display box and pause for 2 seconds before attacking
        display_message('')
        time.sleep(2)
        
        # select a random move
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)
        
        # check if the player's pokemon fainted
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
    # one of the pokemons fainted
    if game_status == 'fainted':
        
        alpha = 255
        while alpha > 0:
            
            game.fill(white)
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            # determine which pokemon fainted
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f'{rival_pokemon.name} fainted!')
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_message(f'{player_pokemon.name} fainted!')
            alpha -= .4
            
            pygame.display.update()
            
        game_status = 'gameover'
        
    # gameover screen
    if game_status == 'gameover':
        
        display_message('Play again (Y/N)?')
        
pygame.quit()
