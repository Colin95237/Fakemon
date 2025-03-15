import pygame
from pygame.locals import *
import time
import math
import random
import openai

#API-Schlüssel für openai
#openai.api_key = "..."

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

    # Methode zum Zurücksetzen von HP und Tränken
    def reset(self):
        self.current_hp = self.max_hp  # Setzt die HP auf den Maximalwert zurück
        self.num_potions = 3  # Setzt die Tränke auf den Anfangswert zurück

    #Angriff auf ein anderes Pokemon, other = das Pokemon was angegriffen wird, move = verwendete Attacke
    def perform_attack(self, other, move):

        #Displaynachricht
        display_message(f'{self.name} used {move.name}')
        
        #2 Sekunden Pause
        time.sleep(2)
        
        #Berechnung des Schadens einer Attacke
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        
        #Typenvorteile/-nachteile berücksichtigen
        type_effectiveness = {
            "fire": {"strong": "grass", "weak": "water"},
            "water": {"strong": "fire", "weak": "grass"},
            "grass": {"strong": "water", "weak": "fire"},
            "normal": {"strong": None, "weak": None}  # Normal hat keine Vor-/Nachteile
        }

        #Falls der Move einen Typ hat, der in der Liste ist
        if move.type in type_effectiveness:
            effectiveness = type_effectiveness[move.type]

            if effectiveness["strong"] and effectiveness["strong"] in other.types:
                damage *= 2  # Doppelschaden
                display_message("It's super effective!")
                time.sleep(1)
            elif effectiveness["weak"] and effectiveness["weak"] in other.types:
                damage *= 0.5  # Halber Schaden
                display_message("It's not very effective...")
                time.sleep(1)
            
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

        #Lebensbalkenposition setzen
        player_pokemon.hp_x = 275
        player_pokemon.hp_y = 250
        rival_pokemon.hp_x = 50
        rival_pokemon.hp_y = 50

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
def create_button(width, height, left, top, label):
    # Mausposition abrufen
    mouse_cursor = pygame.mouse.get_pos()
    
    # Button-Rechteck erstellen
    button = Rect(left, top, width, height)
    
    # Button-Farbe je nach Hover-Zustand setzen
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)
    
    # Schriftart für den Button-Text
    font = pygame.font.Font(pygame.font.get_default_font(), 18)  # Etwas größere Schrift
    
    # Button-Text rendern
    text = font.render(label, True, black)
    
    # Text zentriert im Button platzieren
    text_rect = text.get_rect(center=(left + width // 2, top + height // 2))
    
    # Text auf den Button zeichnen
    game.blit(text, text_rect)
    
    # Button zurückgeben
    return button

# Logik für den Wechsel der Pokémon
def switch_pokemon(team, current_pokemon):
    # Finde das nächste Pokémon im Team
    next_pokemon = team[(team.index(current_pokemon) + 1) % len(team)]
    return next_pokemon

# Beim Switch Pokémon richtig setzen
def handle_switch():
    global player_pokemon, rival_pokemon
        
    player_pokemon = switch_pokemon(player_team, player_pokemon)
        
    # Stellen Sie sicher, dass die neue Position und das Sprite des Pokémon korrekt sind
    player_pokemon.x = 25
    player_pokemon.y = 150
    rival_pokemon.x = 275
    rival_pokemon.y = 0
        
    # Rects aktualisieren
    player_pokemon.rect.topleft = (player_pokemon.x, player_pokemon.y)
    rival_pokemon.rect.topleft = (rival_pokemon.x, rival_pokemon.y)

    # Grösse der Sprites anpassen
    player_pokemon.size = 200
    rival_pokemon.size = 200

    # Sprites setzen
    player_pokemon.set_sprite('front')
    rival_pokemon.set_sprite('front')

    # Lebensbalken nach dem Wechsel zeichnen
    player_pokemon.draw_hp()
    rival_pokemon.draw_hp()

    pygame.display.update()    

def initialize_teams():
    global player_team, rival_team, player_pokemon, rival_pokemon
    # Erstelle neue Pokemon-Objekte (basierend auf den ursprünglichen Werten)
    player_bulbasaur = Pokemon('Bulbasaur', 30, 'grass', 45, 49, 49, 45, bulbasaur_moves, 25, 150)
    player_charmander = Pokemon('Charmander', 30, 'fire', 39, 52, 43, 65, charmander_moves, 175, 150)
    player_squirtle = Pokemon('Squirtle', 30, 'water', 44, 48, 65, 43, squirtle_moves, 325, 150)
    enemy_bulbasaur = Pokemon('Bulbasaur', 30, 'grass', 45, 49, 49, 45, bulbasaur_moves, 25, 150)
    enemy_charmander = Pokemon('Charmander', 30, 'fire', 39, 52, 43, 65, charmander_moves, 175, 150)
    enemy_squirtle = Pokemon('Squirtle', 30, 'water', 44, 48, 65, 43, squirtle_moves, 325, 150)

    player_team = [player_bulbasaur, player_charmander, player_squirtle]
    rival_team = [enemy_charmander, enemy_squirtle, enemy_bulbasaur]

    player_pokemon = player_team[0]
    rival_pokemon = rival_team[0]
    
    # Setze die Lebensbalkenpositionen
    player_pokemon.hp_x = 275
    player_pokemon.hp_y = 250
    rival_pokemon.hp_x = 50
    rival_pokemon.hp_y = 50


#Pokemon-Attacken-Daten
bulbasaur_moves = [Move("Tackle", 40, "normal"), Move("Vine Whip", 45, "grass")]
charmander_moves = [Move("Tackle", 40, "normal"), Move("Ember", 40, "fire")]
squirtle_moves = [Move("Tackle", 40, "normal"), Move("Water Gun", 40, "water")]

#Pokemon-Data
player_bulbasaur = Pokemon('Bulbasaur', 30, 'grass', 45, 49, 49, 45, bulbasaur_moves, 25, 150)
player_charmander = Pokemon('Charmander', 30, 'fire', 39, 52, 43, 65, charmander_moves, 175, 150)
player_squirtle = Pokemon('Squirtle', 30, 'water', 44, 48, 65, 43, squirtle_moves, 325, 150)

enemy_bulbasaur = Pokemon('Bulbasaur', 30, 'grass', 45, 49, 49, 45, bulbasaur_moves, 25, 150)
enemy_charmander = Pokemon('Charmander', 30, 'fire', 39, 52, 43, 65, charmander_moves, 175, 150)
enemy_squirtle = Pokemon('Squirtle', 30, 'water', 44, 48, 65, 43, squirtle_moves, 325, 150)

# the player's and rival's selected pokemon
player_team = [player_bulbasaur, player_charmander, player_squirtle]
rival_team = [enemy_charmander, enemy_squirtle, enemy_bulbasaur]

player_pokemon = player_team[0]
rival_pokemon = rival_team[0]

#Hauptspielschleife
#Rivalen-Pokemonlevel herabsetzen um das Spiel zu vereinfachen
rival_pokemon.level = int(rival_pokemon.level * .75)
                        
#Lebensbalkenposition setzen
player_pokemon.hp_x = 275
player_pokemon.hp_y = 250
rival_pokemon.hp_x = 50
rival_pokemon.hp_y = 50

game_status = 'prebattle' #Pokemon auswählen
while game_status != 'quit': #Läuft bis der Spieler das Spiel beendet
    
    for event in pygame.event.get(): #Durch alle Pygame-Events gehen
        if event.type == QUIT: #Falls das Fenster geschlossen wird
            game_status = 'quit' #Spiel beenden
            
        #Tastendruckevent erkennen
        if event.type == KEYDOWN:
            #Spiel neustarten
            if event.key == K_y:
                initialize_teams()
                game_status = 'prebattle' #Zurück zur Auswahl
                
                # Zurücksetzen der Pokémon (volle HP und Tränke zurücksetzen)
                player_pokemon.reset()
                rival_pokemon.reset()

            #Spiel beenden
            elif event.key == K_n:
                game_status = 'quit'
            
        #Mausklick erkennen
        if event.type == MOUSEBUTTONDOWN:
            #Position des Mausklicks speichern
            mouse_click = event.pos
            
            #Wenn der Spieler an der Reihe ist
            if game_status == 'player turn':
                #Prüfen, ob Fight-Button gedrückt wurde
                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move' #Spieler greift an
                    
                #Prüfen, ob Potion-Button gedrückt wurde
                elif potion_button.collidepoint(mouse_click):
                    #Falls keine Tränke mehr vorhanden sind
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left')
                        time.sleep(2)
                        game_status = 'player move' #Angriff erzwingen
                    else:
                        player_pokemon.use_potion() #Trank verwenden
                        display_message(f'{player_pokemon.name} used potion')
                        time.sleep(2)
                        game_status = 'rival turn' #Gegner ist am Zug

                elif switch_button.collidepoint(mouse_click):
                    player_pokemon = switch_pokemon(player_team, player_pokemon)
                    handle_switch()
                    game_status = 'rival turn'   
                        
            #Wenn der Spieler eine Attacke auswählt
            elif game_status == 'player move':
                
                #Prüfen welche Attacke angeklickt wurde
                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    
                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)
                        
                        #Prüfen, ob der Gegner besiegt wurde
                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
                    
    #Kampfvorbereitung
    if game_status == 'prebattle':
        
        #Pokemon zeichnen
        game.fill(white)
        player_pokemon.draw()
        player_pokemon.draw_hp()  # HP des Spielers anzeigen
        rival_pokemon.draw_hp()   # HP des Gegners anzeigen
        pygame.display.update()
        
        #Pokemon positionieren
        player_pokemon.x = 25
        player_pokemon.y = 150
        rival_pokemon.x = 275
        rival_pokemon.y = 0
        
        #Größe der Sprites anpassen
        player_pokemon.size = 200
        rival_pokemon.size = 200

        #Sprites setzen
        player_pokemon.set_sprite('front')
        rival_pokemon.set_sprite('front')
        
        game_status = 'start battle' #Spielstatus ändern
        
    #Kampf starten
    if game_status == 'start battle':
        
        #Rivalen-Pokemon wird ausgesendet
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
            
        #1 Sekunde Pause
        time.sleep(1)
        
        #Spieler schickt sein Pokemon in den Kampf
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
        
        #Lebensbalken zeichnen
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        #Ausrechnen wer zuerst angreifen darf
        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
        #Pause für eine Sekunde
        time.sleep(1)
        
    #Bildschirm für Buttons "Fight" und "Use Potion"
    if game_status == 'player turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # Button-Größen und Positionen anpassen
        button_width = 150
        button_height = 140
        button_top = 350

        #Button fight und use potion erstellen
        # Button-Positionen gleichmäßig verteilen
        fight_button = create_button(button_width, button_height, 10, button_top, 'Fight')
        potion_button = create_button(button_width, button_height, 170, button_top, f'Use Potion ({player_pokemon.num_potions})')
        switch_button = create_button(button_width, button_height, 340, button_top, f'Switch')

        # Schwarzen Rand zeichnen (gleiche Breite wie alle Buttons zusammen)
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()
        
    #Attacken-Bildschirm
    if game_status == 'player move':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        #Für jede Attacke einen Button zeichnen
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, move.name.capitalize())
            move_buttons.append(button)
            
        #Schwarze Umrandung zeichnen
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    #Rivalen Attackenauswahl und zufällige Attacke wählen
    if game_status == 'rival turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        #leerer Bildschirm und 2 Sekunden Pause
        display_message('')
        time.sleep(2)
        
        #Zufällige Attacke wird ausgewählt
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)
        
        #Überprüfen ob der Spieler besiegt wurde
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
    # Wenn eines der Pokemon besiegt wurde
    if game_status == 'fainted':
        alpha = 255
        while alpha > 0:
            game.fill(white)
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            # Bestimmen, welches Pokémon besiegt wurde
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f'{rival_pokemon.name} fainted!')
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_message(f'{player_pokemon.name} fainted!')
            
            alpha -= 0.4
            pygame.display.update()

        # Wechsel zum nächsten Pokémon, falls noch eines verfügbar ist
        if rival_pokemon.current_hp == 0:
            rival_team.pop(0)  # Besiegtes Pokémon aus der Liste entfernen
            if rival_team:  # Prüfen, ob noch Pokémon übrig sind
                rival_pokemon = rival_team[0]  # Nächstes Pokémon wählen
                # Position und Größe zurücksetzen
                rival_pokemon.x = 275
                rival_pokemon.y = 0
                rival_pokemon.size = 200
                rival_pokemon.set_sprite('front')
                rival_pokemon.reset() # HP und Tränke zurücksetzen
                display_message(f'Rival sends out {rival_pokemon.name}!')
                time.sleep(2)
                game_status = 'player turn'  # Spieler ist am Zug
            else:
                display_message('You won the battle!')
                game_status = 'gameover'
        
        elif player_pokemon.current_hp == 0:
            player_team.pop(0)  # Besiegtes Pokémon entfernen
            if player_team:  # Prüfen, ob noch Pokémon übrig sind
                player_pokemon = player_team[0]  # Nächstes Pokémon wählen
                # Position und Größe zurücksetzen
                player_pokemon.x = 25
                player_pokemon.y = 150
                player_pokemon.size = 200
                player_pokemon.set_sprite('front')
                player_pokemon.reset()  # HP und Tränke zurücksetzen
                display_message(f'You send out {player_pokemon.name}!')
                time.sleep(2)
                game_status = 'rival turn'  # Gegner ist am Zug
            else:
                display_message('You lost the battle!')
                game_status = 'gameover'
        
    #Gameover Bildschirm
    if game_status == 'gameover':
        
        display_message('Play again (Y/N)?')
        
pygame.quit()