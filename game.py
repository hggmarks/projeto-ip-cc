import pygame as pg 
import sys 
import utils.constants as constants
import utils.matrix_transformations as mt
import sprite_mananger.sprite_mananger as sm
import random
import player.player as entitie_player


clock = pg.time.Clock()
display = pg.display.set_mode(constants.WINDOW_SIZE, 0, 32)

tile_sheet_image = pg.image.load('./resources/atlas/iso_tileset1.png')
tile_sheet = sm.SpriteManganger(tile_sheet_image)

block_black_floor = tile_sheet.get_image(0, 0, constants.FLOOR_SIZE, constants.FLOOR_SIZE, 4, (0, 0, 0))

block_white_floor = tile_sheet.get_image(1, 0, constants.FLOOR_SIZE, constants.FLOOR_SIZE, 4, (0, 0, 0))


#CORES USADAS:
AzulMarinho = (0,0,123) #Player
AzulClaroFosco = (153,153,255) #Imunidade
Ciano = (0,238,238)  #Velocidade

def calcularDistanciaPontos(xA,xB,yA,yB):
    return (((xB-xA)**2)+((yB-yA)**2))**(1/2)

#CONTADORES DE TEMPO SPAWN ITENS

static_timer = None
last_item_time = None

#CONTADORES DE TEMPO DE DANO AO PLAYER
static_timer_player = None
last_hit_time = None

tempo_imune = 3000 #milisegundos

#PLAYER
hits = 0

#BOSS

class Boss(object):
    def __init__(self, bossX, bossY):
        self.bossX = bossX
        self.bossY = bossY
        self.velI = 32
        self.raio = 20
        self.cor = (255,0,0)
        self.walkCount = 2
        self.jump_count = 10
        self.is_jump = True
        self.largura = 0
        self.altura = 0
        self.vida = 400
        self.tamanho_da_barra_vida = 400


    def atualizar(self):
        self.barra_De_vida()
        self.vida_animacao()

    def tomar_dano(self,dano_do_player):
        if self.vida > 0:
            self.vida -= dano_do_player       
        if self.vida <= 0:
            self.vida = 0

    def barra_De_vida(self):
        pg.draw.rect(display, (255, 0, 0), (1300, 110, self.vida, 15))
        pg.draw.rect(display, (0,255,0), (1300,110, self.vida, 15))
        pg.draw.rect(display, (0,0,0), (1300, 110, self.tamanho_da_barra_vida, 15),4)

            


#Clase específica, recebe os parâmetros do boss, mas prioriza o que for dado dentro dela

class Torre(Boss):
    def andar(self):
        if self.walkCount <= 0: # o Boss anda "2" vezes antes de parar
                if distanciaX > 2 or distanciaX < -1: # Para o boss n ficar travando numa posição especifica (passível de mudança)
                    if self.bossX < player.rect[0] and distanciaX > 0: # Direita
                        self.bossX += (torre.velI + 32)
                        sombra.posicao_X += (torre.velI + 32)
                        self.is_jump = True
                        
                    elif self.bossX > player.rect[0] and distanciaX < 0: # Esquerda
                        self.bossX -= (torre.velI + 32)
                        sombra.posicao_X -= (torre.velI + 32)
                        self.is_jump = True
                    
                if distanciaY > 2 or distanciaY < -1:
                    if self.bossY < player.rect[1] and distanciaY > 0: # Baixo
                        self.bossY += self.velI
                        sombra.posicao_Y += self.velI
                        self.is_jump = True
                    
                    elif self.bossY > player.rect[1] and distanciaY < 0: # Cima
                        self.bossY -= self.velI
                        sombra.posicao_Y -= self.velI
                        self.is_jump = True

    def pular(self):
        self.is_jump = True
        if self.jump_count >= -10:
            self.bossY -= (self.jump_count ** 3) / 25
            self.jump_count -= 1

        else:
            self.is_jump = False
            self.jump_count = 10


class Sombra(object): 
    def __init__(self):
        self.raio = torre.raio
        self.posicao_X = torre.bossX - (self.raio // 2) + (torre.raio // 2)
        self.posicao_Y = torre.bossY - (self.raio // 2) + (torre.raio // 2)

    def desenhar(self):
        if torre.is_jump:
            pg.draw.circle(display, (54,54,54), (self.posicao_X, self.posicao_Y,), self.raio)

#Dama = Player(1200,500)
initial_position = (1200, 500)
p_size = (21, 32)
player_image = tile_sheet.get_image(0, 1, p_size[0], p_size[1], 2, (0, 0, 0) )
mov_speed = 5 
vida = 1 


player = entitie_player.Player(initial_position, p_size, mov_speed, vida, 1, player_image)
torre = Torre(constants.WINDOW_SIZE[0] // 2, constants.WINDOW_SIZE[1] // 2) 
sombra = Sombra()          

#PROJÉTIL

class projetil(object):
    def __init__(self):
        self.color = (238,173,14)
        self.tamanho = 10
        self.dano = 30
        self.posicao_projetil_x = 0
        self.posicao_projetil_y = 0
        self.range = 300
        self.destino = None
        self.movimentando = False
        self.hitbox = (self.posicao_projetil_x, self.posicao_projetil_y, self.tamanho)

Espada = projetil()

#COLETÁVEIS

class coletaveis(object):
    def __init__(self, color, tamanho, posicao_coletavel_x, posicao_coletavel_y) -> None:
        self.color = color
        self.tamanho = tamanho
        self.posicao_coletavel_x = posicao_coletavel_x
        self.posicao_coletavel_y = posicao_coletavel_y
        self.hitbox = (self.posicao_coletavel_x, self.posicao_coletavel_y, self.tamanho)

cords_item_Verde = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])

cords_item_vida_drop = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
Vida_item = coletaveis((255,0,226), 10, cords_item_vida_drop[0], cords_item_vida_drop[1])

posicao_da_bala_chao = [0,0]
arma_no_chao = coletaveis((238,173,14), 10, posicao_da_bala_chao[0], posicao_da_bala_chao[1])


item_Verde_coletado = False

item_vida_coletada = False

#ARRUMAR ESSA PARTE
Game_over = False
game_over_img = pg.image.load('game_over.jpg')


#MAIN LOOP

run = True
while run:
    display.fill((146, 244, 255))

#SAIR DO JOGO        
    for event in pg.event.get():
        if event.type == pg.QUIT:            
            run = False
#CONSTRUÇÂO DO TABULEIRO           

    for row in range(8):
        for col in range(8):
            block_coords = mt.mudanca_base(row, col, constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            if (row % 2 == 0 and col % 2 == 0) or (row % 2 == 1 and col % 2 == 1):
                display.blit(block_white_floor, block_coords)
            else:
                display.blit(block_black_floor, block_coords)

#DESENHO DO COLETÁVEL MAIS ATRIBUTO
    
    pg.draw.circle(display, item_Verde.color, (item_Verde.posicao_coletavel_x, item_Verde.posicao_coletavel_y), item_Verde.tamanho )
    pg.draw.circle(display, Vida_item.color, (Vida_item.posicao_coletavel_x, Vida_item.posicao_coletavel_y), Vida_item.tamanho)
    torre.barra_De_vida()

    
#DESENHO DO PLAYER E MOVIMENTAÇÂO COM OOP
    player.draw(display) 
    player.move()
    player.barra_de_vida(display)
    #Dama.desenhar()
    #Dama.andar()
    #Dama.barra_de_vida()

#BALA

    keys = pg.key.get_pressed()

    if keys[pg.K_SPACE] and player.rect[1] <= 735:
        if player.ammo > 0:
            if player.direcao['cima'] == True:
                Espada.destino = (player.rect[0], player.rect[1]-Espada.range)
                posicao_da_bala_chao = Espada.destino
                
            if player.direcao['direita'] == True:
                Espada.destino = (player.rect[0]+Espada.range, player.rect[1])
                posicao_da_bala_chao = Espada.destino

            if player.direcao['esquerda'] == True:
                Espada.destino = (player.rect[0]-Espada.range, player.rect[1])
                posicao_da_bala_chao = Espada.destino

            if player.direcao['baixo'] == True:
                Espada.destino = (player.rect[0], player.rect[1]+Espada.range)
                posicao_da_bala_chao = Espada.destino
        
#BLOCO DE VERIFICAÇÃO SE O TEMPO DA IMUNIDADE DO PLAYER JÁ PASSOU
    if hits > 0:
        last_hit_time = pg.time.get_ticks() - static_timer_player
        if last_hit_time > tempo_imune:
            player.imune = False
            #if Dama.cor == AzulClaroFosco: #VERIFICA SE O PLAYER ESTÁ COM A COR FOSCA DA IMUNIDADE
                #Dama.cor = (0,0,123)
            
#DESENHO DO BOOS E MOVIMENTAÇÃO COM OOP
    if torre.vida > 0: # Se a vida da torre for < 0, a torre morre
        pg.draw.circle(display, torre.cor, (torre.bossX, torre.bossY), torre.raio)
    
        distanciaX = player.rect[0] - torre.bossX # Distancia entre o player e o boss na posição X
        distanciaY = player.rect[1] - torre.bossY # Distancia entre o player e o boss na posição Y

        if not torre.is_jump: #Caso não esteja pulando, anda
            torre.andar()

        else: #Pula e desenha a sombra
            torre.pular()
            sombra.desenhar()

        torre.walkCount += 1
        if torre.walkCount >= 40: #Velocidade do boss
            torre.walkCount = 0

        if not torre.is_jump: #Para ele não bater no player em cima no meio do pulo
            if calcularDistanciaPontos(player.rect[0], torre.bossX, player.rect[1], torre.bossY) <= 40:
                if player.imune == False: # Verifica se o player está imune aos hits ainda (Variável)
                    player.vida -= 1
                    player.imune = True
                    static_timer_player = pg.time.get_ticks()
                    hits+=1
                #if player.imune == True: # Caso o player não esteja mais imune
                    #Dama.cor = (153,153,255)
            if calcularDistanciaPontos(Espada.posicao_projetil_x, torre.bossX, Espada.posicao_projetil_y, torre.bossY) <= 30 and Espada.movimentando:
                torre.tomar_dano(Espada.dano)
                Espada.destino = (Espada.posicao_projetil_x, Espada.posicao_projetil_y)              
                Espada.dano = 0      
                posicao_da_bala_chao = Espada.destino   
                        
    #VERIFICANDO SE PLAYER PERDEU (GAME OVER)
    if player.vida == 0:
        while True:
            display.blit(game_over_img,(0,0))
            pg.display.update()    
            pg.time.delay(1500)
            pg.quit()
                    

#MUDANÇA DE LUGAR DO ITEM / IDENTIFICAÇÃO SE ITEM FOI COLETADO
    
    if item_Verde_coletado:
        
        if last_item_time > 3000:          
            cords_item_Verde = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])
            item_Verde_coletado = False
            player.velocidade -= 2
            #Dama.cor  = (0,0,255)
    
    if item_vida_coletada:

        if last_item_time > 30000:

            cords_item_vida_drop = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            Vida_item = coletaveis((255,0,226), 10, cords_item_vida_drop[0], cords_item_vida_drop[1])
            item_vida_coletada = False
            

            
#IDENTIFICAÇÃO DE COLISÃO COM O ITEM e CD para SPAWN
        
    distanciaPlayerObjeto = calcularDistanciaPontos(player.rect[0], item_Verde.posicao_coletavel_x, player.rect[1], item_Verde.posicao_coletavel_y)

    
    if distanciaPlayerObjeto <= 20:       
       
        player.velocidade += 2
        #Dama.cor = (0,238,238)           
        item_Verde.posicao_coletavel_x = 0
        item_Verde.posicao_coletavel_y = 0
        item_Verde.color = (146, 244, 255)
        item_Verde.tamanho = 0
        static_timer = pg.time.get_ticks()
    
        item_Verde_coletado = True

    distanciaPlayerObjeto_2 = calcularDistanciaPontos(player.rect[0], Vida_item.posicao_coletavel_x, player.rect[1], Vida_item.posicao_coletavel_y)

    if distanciaPlayerObjeto_2 <= 20:
        if player.vida <= 3:
            player.vida += 1

        Vida_item.posicao_coletavel_x = 0
        Vida_item.posicao_coletavel_y = 0
        Vida_item.tamanho = 0
        static_timer = pg.time.get_ticks()
    
        item_vida_coletada = True
    
    distacia_da_bala_chao = calcularDistanciaPontos(player.rect[0], posicao_da_bala_chao[0], player.rect[1], posicao_da_bala_chao[1])

    if distacia_da_bala_chao <= 20:
        player.ammo = 1
        Espada.destino = None
        Espada.dano = 30


    if static_timer:
        last_item_time = pg.time.get_ticks() - static_timer

#MOVIMENTAÇÃO DO PROJÉTIL
    if player.ammo > 0:
        if player.direcao['cima']:
            Espada.posicao_projetil_x = player.rect[0]
            Espada.posicao_projetil_y = player.rect[1]-20
            
        elif player.direcao['direita']:
            Espada.posicao_projetil_x = player.rect[0]+20
            Espada.posicao_projetil_y = player.rect[1]
            
        elif player.direcao['esquerda']:
            Espada.posicao_projetil_x = player.rect[0]-20
            Espada.posicao_projetil_y = player.rect[1]
            
        elif player.direcao['baixo']:
            Espada.posicao_projetil_x = player.rect[0]
            Espada.posicao_projetil_y = player.rect[1]+20

#
            
    if Espada.destino != None:
        if not Espada.destino == (Espada.posicao_projetil_x, Espada.posicao_projetil_y):
            Espada.movimentando = True
            player.ammo = 0
            #
            if Espada.destino[0]>Espada.posicao_projetil_x:
                if (Espada.destino[0] - Espada.posicao_projetil_x)<5:
                    
                    Espada.posicao_projetil_x = Espada.destino[0]
                    
                else:
                    Espada.posicao_projetil_x += 5
                    
            if Espada.destino[0]<Espada.posicao_projetil_x:
                if (Espada.posicao_projetil_x - Espada.destino[0])<5:
                    
                    Espada.posicao_projetil_x = Espada.destino[0]
                    
                else:
                    Espada.posicao_projetil_x -= 5
            #
            if Espada.destino[1]>Espada.posicao_projetil_y:
                if (Espada.destino[1] - Espada.posicao_projetil_y)<5:
                    
                    Espada.posicao_projetil_y = Espada.destino[1]
                    
                else:
                    Espada.posicao_projetil_y += 5
                    
            if Espada.destino[1]<Espada.posicao_projetil_y:
                if (Espada.posicao_projetil_y - Espada.destino[1])<5:
                    
                    Espada.posicao_projetil_y = Espada.destino[1]
                    
                else:
                    Espada.posicao_projetil_y -= 5
                    
        else:
            Espada.destino = None #Caso tenha chegado no destino, volta a ser destino = None
    else:
        Espada.movimentando = False #Já que o destino virou None no tick passado, ele deixa de estar em movimento
   
    pg.draw.circle(display, Espada.color, (Espada.posicao_projetil_x, Espada.posicao_projetil_y), Espada.tamanho)

    pg.display.update()
    clock.tick(60)
    
