
import pygame, sys, os
from pygame.locals import *

pygame.init() 
pygame.mixer.init()
Clock = pygame.time.Clock()
FPS = 60
Clock.tick(FPS)
deltatime = 0

screen = pygame.display.set_mode((800, 440))
pygame.display.set_caption('Gra')
pygame.mixer.music.load("jump.wav")
backgroundImg = pygame.image.load('tło.jpg')

if not os.path.exists("wyniki.txt"):    #jeśli nie istnieje plik tekstowy z wynikami to go tworzymy
    open("wyniki.txt", "w+")

def loadImage(name, useColorKey = False):
    """Funkcja dodająca obraz z możliwością zastosowania przezroczystego tła."""
    image = pygame.image.load(name)
    image = image.convert()  
    if useColorKey:
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image

def best_score(file):
    """Funkcja zwracająca listę 3 najlepszych wyników."""
    f = open(file, "r")
    list_scores = f.read().split()
    list_scores2 = []
    for i in list_scores:
        list_scores2.append(int(i))
    list_scores2 = sorted(list_scores2, reverse = True)[:3]
    f.close()
    return list_scores2
    
class Player(pygame.sprite.Sprite):
    """
    Klasa gracza, w której poza inicjalizacją obrazu i początkowego położenia
    definiujemy funkcje umożliwiające skakanie.
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.playerImg = loadImage('pingwin.png', True)
        self.rect = self.playerImg.get_rect()
        self.x = 200
        self.y = 260
        self.dy = 0   #prędkość (początkowo 0)
        self.jumping = False   #zmienna pomocna przy funkcji skakania
        
    def jump(self):
        if self.onTheGround():   #pingwin może skakać tylko jeśli jest na ziemi
            self.dy -= 200
            self.jumping = True
            
    def onTheGround(self):
        if self.y >= 260:   #żeby pingwin nie spadał w nieskończoność
            return True
        else:
            return False  
        
    def inTheAir(self):
        if self.y <= 70:     #wysokość do jakiej może podskoczyć pingwin
            return True
        else:
            return False

    def update(self, deltatime):
        if self.inTheAir():
            self.dy += 200
            self.jumping = False
        if self.onTheGround() and not self.jumping:
            self.dy = 0
            self.y = 260            
        self.y += self.dy * deltatime   #potrzebne aby skok był "płynny"

    
class Obstacle(pygame.sprite.Sprite):
    """Klasa przeszkód."""    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.obstacleImg = [loadImage('przeszk1.png', True), loadImage('przeszk2.png', True)]    #dwa rodzaje przeszkód
        self.rect1 = self.obstacleImg[0].get_rect()
        self.rect2 = self.obstacleImg[1].get_rect()
        self.x1 = 1500    #pierwsza przeszkoda ma początkową wartość x 1500 czyli poza ekranem, druga o 1000 więcej
        self.x2 = 2500
        self.y = 300
        self.dx = -5   #prędkość z jaką przesuwają się przeszkody (taka sama co przy ścieżce)
        
    def update(self):
        self.x1 += self.dx 
        self.x2 += self.dx
        if self.x1 == -1000:    #przeszkody pojawiać się będą co 1000 jednostek
            self.x1 = 1000      #kiedy przeszkoda ma wartość x -1000 (poza ekranem), przesuwamy ją na wartość x 1000
        if self.x2 == -1000:
            self.x2 = 1000

            
class Path():
    """Klasa ścieżki."""
    def __init__(self):
        self.pathImg = [pygame.image.load('droga.png'),pygame.image.load('droga.png')] 
        self.rectPath = self.pathImg[0].get_rect()
        self.width = self.rectPath.width -4
        self.x1 = 0
        self.x2 = self.width
        self.y = 380
        self.dx = -5    #prędkość z jaką przesuwa się ścieżka
        
    def update(self):
        self.x1 += self.dx 
        if self.x1 <= -self.width:  
            self.x1 = self.width
        self.x2 += self.dx
        if self.x2 <= -self.width:
            self.x2 = self.width

            
class Score:
    """
    Klasa punktów, które naliczają się względem sekund. 
    Za każdą sekundę gry gracz otrzymuje jeden punkt.
    """
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Calibri", 28)
        self.count = 0
        text = "SCORE  " + str(self.count)
        self.scoreText = self.font.render(text, 1, (0, 0, 0))
        self.check = 0
 
    def update(self):
        self.check += 1
        if self.check == 60:    
            self.count += 1
            self.check = 0
        text = "SCORE  " + str(self.count) 
        self.scoreText = self.font.render(text, 1, (0, 0, 0))
        
class Lifes:
    """Klasa żyć. Początkowa ilość to 3."""
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Calibri", 28)
        self.count = 3
        text = str(self.count)
        self.Text = self.font.render(text, 1, (0, 0, 0))
        self.lifesImg = loadImage('lifes.png', True)
 
    def update(self):
        self.count -= 1
        text = str(self.count) 
        self.Text = self.font.render(text, 1, (0, 0, 0))

            
player = Player()
obstacle = Obstacle()
path = Path()
score = Score()
lifes = Lifes()

collision_before = False     
running = False            #ustawiamy zmienne logiczne
show_menu = True
show_score = False

while True:    #pętla główna
                
    if show_menu:    #warunek wyświetlający menu początkowe

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show_menu = False
                pygame.quit()
                sys.exit()

        if pygame.key.get_pressed()[K_p]:    #przyciskiem p rozpoczynamy grę
            running = True
            show_menu = False    
    
        if pygame.key.get_pressed()[K_ESCAPE]:      #przyciskiem escape zamykamy okno gry
            pygame.quit()
            sys.exit()

        screen.fill((225, 221, 238))    
        font1 = pygame.font.SysFont("Calibri", 40)    #zasady gry
        font2 = pygame.font.SysFont("Calibri", 28)
        font3 = pygame.font.SysFont("Calibri", 20)
        text1 = "WCIŚNIJ P ABY ZAGRAĆ"
        text1Text = font2.render(text1, 1, (0, 0, 0))
        text2 = "WCIŚNIJ Q ABY ZAKOŃCZYĆ GRĘ"
        text2Text = font2.render(text2, 1, (0, 0, 0))
        text3 = "WCIŚNIJ ESCAPE ABY ZAMKNĄĆ OKNO GRY"
        text3Text = font2.render(text3, 1, (0, 0, 0))
        text4 = "JAK GRAĆ?"
        text4Text = font2.render(text4, 1, (0, 0, 0))
        text5 = "PRZESKAKUJ NAD PRZESZKODAMI WCISKAJĄC SPACJĘ"
        text5Text = font2.render(text5, 1, (0, 0, 0))
        text6 = "autor Julia Janiak"
        text6Text = font3.render(text6, 1, (0, 0, 0)) 
        screen.blit(text1Text, (60, 80))
        screen.blit(text2Text, (60, 140))
        screen.blit(text3Text, (60, 200))
        screen.blit(text4Text, (60, 280))
        screen.blit(text5Text, (60, 340))
        screen.blit(text6Text, (60, 420))
        
        pygame.display.update()


    if running:    #warunek "właściwej" gry

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        if pygame.key.get_pressed()[K_ESCAPE]:   #przyciskiem escape zamykamy grę
            running = False
            pygame.quit()
            sys.exit()
            
        if pygame.key.get_pressed()[K_q]:     #przyciskiem q wychodzimy z gry i wyświetla się nasz wynik
            plik = open("wyniki.txt", "a+")    #wpisujemy nasz wynik do pliku z wynikami
            plik.write(str(score.count) + " ")
            plik.close()
            show_score = True 
            running = False

        if pygame.key.get_pressed()[K_SPACE]:   #spacją skaczemy
            player.jump()        
            pygame.mixer.music.play()   #przy skakaniu odtworzy się dźwięk

        x1s = player.x + 5   #zmienne pomocne przy definiowaniu kolizji
        x2s = player.x + player.rect.width - 5
        ys = player.y + player.rect.height
        collision = (obstacle.x1 <= x2s and obstacle.x1 >= x1s and ys >= obstacle.y) or (obstacle.x2 <= x2s and obstacle.x2 >= x1s and ys >= obstacle.y)
        if collision:
            if collision_before == False:     #potrzebne aby przy dotknięciu przeszkody życie odejmowało się tylko raz           
                lifes.update()
                score.count -= 10
                if lifes.count == 0:    #w przypadku straty wszystkich 3 żyć wyświetla się wynik
                    plik = open("wyniki.txt", "a+")    #wpisujemy nasz wynik do pliku z wynikami
                    plik.write(str(score.count) + " ")
                    plik.close()
                    show_menu = False    
                    show_score = True
                    running = False
            collision_before = True    #jeśli kolizja nastąpiła zmieniamy zmienną logiczną na true
        else:
            collision_before = False

        deltatime = Clock.tick(FPS)/1000

        screen.fill((255, 255, 255))
        screen.blit(backgroundImg, (0, 0))  
        screen.blit(obstacle.obstacleImg[0], (obstacle.x1, obstacle.y)) 
        screen.blit(obstacle.obstacleImg[1], (obstacle.x2, obstacle.y))
        screen.blit(player.playerImg, (player.x, player.y))
        screen.blit(path.pathImg[0], (path.x1, path.y))
        screen.blit(path.pathImg[1], (path.x2, path.y))
        screen.blit(score.scoreText, (160, 10))
        screen.blit(lifes.Text, (60, 10))
        screen.blit(lifes.lifesImg, (10, 5))

        obstacle.update()
        score.update()
        path.update()
        player.update(deltatime)
        pygame.display.update()
        
    if show_score:    #warunek wyświetający wynik po skończeniu gry

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show_score = False
                pygame.quit()
                sys.exit()
                
        if pygame.key.get_pressed()[K_ESCAPE]:    #przyciskiem escape zamykamy grę  
            show_score = False
            pygame.quit()
            sys.exit()
        
        screen.fill((0,0,0))
        
        bs = best_score("wyniki.txt")
        if bs[0] != score.count:
            text8 = "Niestety nie pobiłeś rekordu:("
        else:
            text8 = "GRATULACJE! Ustanowiłeś nowy rekord!"
        text7 = "Twój wynik to: " + str(score.count)
        text7Text = font1.render(text7, 1, (255, 255, 255))
        screen.blit(text7Text, (220, 100))
        text8Text = font2.render(text8, 1, (255, 255, 255))
        screen.blit(text8Text, (180,180))
        text9 = "Najlepsze wyniki to:" 
        text9Text = font3.render(text9, 1, (255, 255, 255))
        screen.blit(text9Text, (220,260))
        score1 = "I. " + str(bs[0])
        score1Text = font3.render(score1, 1, (255, 255, 255))
        screen.blit(score1Text, (220, 300))
        if len(bs) >= 2:
            score2 = "II. " + str(bs[1])
            score2Text = font3.render(score2, 1, (255, 255, 255))
            screen.blit(score2Text, (220, 340))
        if len(bs) == 3:
            score3 = "III. " + str(bs[2])
            score3Text = font3.render(score3, 1, (255, 255, 255))
            screen.blit(score3Text, (220, 380))       
        
        pygame.display.update()
        
