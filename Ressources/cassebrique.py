#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame, os, gzip
from pygame.locals import *
from random import randrange


pygame.mixer.pre_init(44100,-16,2,2048)
pygame.init()
screen=pygame.display.set_mode((640,800))
pygame.display.set_caption('Casse-Brique')
clock=pygame.time.Clock()

# initialisation de la fenetre

screen.fill((0,0,0))
pygame.display.flip()

sonbrique=pygame.mixer.Sound("sons/briquesound.wav")
sonjoueur1=pygame.mixer.Sound("sons/paddlesound.wav")
sonbonus=pygame.mixer.Sound("sons/bonussound.wav")
soncode=pygame.mixer.Sound("sons/codesound.wav")
soncode2=pygame.mixer.Sound("sons/codesound2.wav")
sonboom=pygame.mixer.Sound("sons/boom.wav")
sonmort=pygame.mixer.Sound("sons/deathsound.wav")

# chargement des sons et musiques


spritebonustaille=pygame.image.load('images/bonus/taille.png')
spritebonustaille.set_colorkey((0,0,0))
spritebonusdegat=pygame.image.load('images/bonus/degat.png')
spritebonusdegat.set_colorkey((0,0,0))
spritebonusvitesse=pygame.image.load('images/bonus/vitesse.png')
spritebonusvitesse.set_colorkey((0,0,0))

# chargement des images


class Texte: # gere tout ce qui concerne le texte : afficher, effacer, mettre en surbrillance, ...

    def __init__(self,texte='',x=0,y=0,couleur=(255,255,255,255),font='arcade/ARCADE',taille=30,centre=False,couleurfond=(0,0,0),imagefond=None,typefond=0):
        self.texte=texte
        self.x=x
        self.y=y
        self.centre=centre
        self.couleur=couleur
        self.couleur2=couleur
        self.taille=taille
        self.font=font
        self.font=pygame.font.Font("font/"+self.font+".TTF",self.taille)
        self.surface=self.font.render(self.texte,1,self.couleur2)
        self.width,self.height=self.surface.get_size()
        self.sourisx=self.sourisy=self.anciensourisx=self.anciensourisy=0
        if self.centre==True:
            (self.x,self.y,self.width,self.height)=self.surface.get_rect(centerx=(screen.get_width()/2+self.x),centery=(screen.get_height()/2+self.y)) # centre le texte par rapport au milieu de l'ecran
        self.brille=False
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond

    def afficher(self): # efface puis affiche le texte
        self.effacer()
        self.reafficher()

    def reafficher(self): # affiche le texte
        self.surface=self.font.render(self.texte,1,self.couleur2)
        self.width,self.height=self.surface.get_size()
        temp=pygame.Surface((self.surface.get_width(),self.surface.get_height())).convert() # permet de mettre du texte en transparence
        temp.blit(screen,(-self.x,-self.y))
        temp.blit(self.surface, (0, 0))
        temp.set_alpha(self.couleur2[3])        
        screen.blit(temp, (self.x,self.y))
        pygame.display.update((self.x-10,self.y,self.width+self.taille,self.height))

    def centrer(self,x=0,y=0,largeur=0,longueur=0): # centre le texte par rapport a un point
        self.x=x
        self.y=y
        self.x+=largeur//2
        self.y+=longueur//2
        self.surface=self.font.render(self.texte,1,self.couleur2)
        self.width,self.height=self.surface.get_size()
        self.x-=self.width//2
        self.y-=self.height//2
        self.afficher()

    def intexte(self): # renvoie un booleen indiquant si le curseur de la souris se trouve dans le texte
        (self.sourisx,self.sourisy)=pygame.mouse.get_pos()
        return ((self.sourisx in range(self.x,self.x+self.width+1))and(self.sourisy in range(self.y,self.y+self.height+1)))

    def surbrillance(self):  # affiche en surbrillance (rouge) le texte
        if self.intexte():
            self.couleur2=(255,0,0,255)
        else:
            self.couleur2=self.couleur
        if self.intexte() or((self.anciensourisx in range(self.x,self.x+self.width+1))and(self.anciensourisy in range(self.y,self.y+self.height+1))):
            self.afficher()
        self.anciensourisx,self.anciensourisy=self.sourisx,self.sourisy

    def effacer(self): # efface le texte
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.x-10,self.y,self.width+self.taille,self.height))
            pygame.display.update((self.x-10,self.y,self.width+self.taille,self.height))
        else:
            screen.blit(self.imagefond.subsurface((self.x-10)*int(self.x>=10),(self.y)*int(self.y>=0),(640-self.x)*int(self.x+self.width>640)+(self.width-self.x+self.taille)*int((self.x<10)and(self.x+self.width>0))+(self.width+10)*int(640>=self.x>=10),((480-self.y)*int(self.y+self.height>480)+(self.height+self.y)*int((self.y<0)and(self.y+self.height)>0))*int((480<self.y+self.height)or(self.y+self.height<0))+(self.height)*int(480>=self.y+self.height>=0)),((self.x-10)*int(self.x>=10),(self.y)*int(self.y>=0)))
            pygame.display.update(((self.x-10)*int(self.x>=10),(self.y)*int(self.y>=0),(640-self.x)*int(self.x+self.width>640)+(self.width-self.x+self.taille)*int(self.x<10)+(self.width+10)*int(640>=self.x>=10),((480-self.y)*int(self.y+self.height>480)+(self.height+self.y)*int(self.y<0))*int((480<self.y+self.height)or(self.y+self.height<0))+(self.height)*int(480>=self.y+self.height>=0)))


class Paragraphe: # ensemble de lignes (objets de type texte)

    def __init__(self,lignes=[],x=0,y=0,couleur=(255,255,255,255),font='arcade/ARCADE',taille=30,centre=False,couleurfond=(0,0,0),imagefond=None,typefond=0): # instancie en objet de type texte pour chaque element de la liste (ligne)
        i=0
        self.ligne={}
        for _ in lignes:
            self.ligne[str(i)]=Texte(_,x,y+taille*i+10,couleur,font,taille,centre,couleurfond,imagefond,typefond)
            i+=1

    def afficherlignes(self,ligneaafficher=None): 
        if ligneaafficher==None: # si aucun numero n'est specifie, l'ensemble du paragrapge et efface et affiche
            for _ in self.ligne.keys():
                self.ligne[_].afficher()
        else:
            self.ligne[str(ligne)].afficher() # sinon, seule la ligne concerne l'est

    def modifcouleur(self,ligne=None,couleur=(255,255,255,255)):
        if ligne==None: # si aucun numero n'est specifie, la couleur de l'ensemble des lignes du paragrapge est modifiee
            for _ in self.ligne.keys():
                self.ligne[_].couleur2=couleur
        else:
            self.ligne[ligne].couleur2=couleur # sinon, seule la celle e la ligne concerne l'est


class Champs: # champs de texte dans lequel on peut entrer/effacer un ou plusieurs caracteres

    def __init__(self,x=0,y=0,largeur=0,font='arcade/ARCADE',taille=30,seul=True,couleurfond=(0,0,0,0),imagefond=None,typefond=0,couleur=(255,255,255,255),textecentre=False):
        self.x=x
        self.y=y
        self.largeur=largeur
        self.font=font
        self.taille=taille
        self.texte=''
        self.touches=[K_q,K_w,K_e,K_r,K_t,K_y,K_u,K_i,K_o,K_p,K_a,K_s,K_d,K_f,K_g,K_h,K_j,K_k,K_l,K_SEMICOLON,K_z,K_x,K_c,K_v,K_b,K_n,K_SPACE,K_SLASH,K_m,K_COMMA,K_PERIOD,K_4,K_KP0,K_KP1,K_KP2,K_KP3,K_KP4,K_KP5,K_KP6,K_KP7,K_KP8,K_KP9]
        self.caracteresmaj=['A','Z','E','R','T','Y','U','I','O','P','Q','S','D','F','G','H','J','K','L','M','W','X','C','V','B','N',' ','!','?','.',':',"'",'0','1','2','3','4','5','6','7','8','9']
        self.caracteresmin=['a','z','e','r','t','y','u','i','o','p','q','s','d','f','g','h','j','k','l','m','w','x','c','v','b','n',' ','!',',',';',':',"'",'0','1','2','3','4','5','6','7','8','9']
        self.choisi=True
        self.seul=seul
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond
        self.couleur=couleur
        self.textecentre=textecentre

    def modiftexte(self,caracterespossibles='tout',event=None):
        if self.choisi==True: 
            pygame.event.pump()
            if event!=None:
                self.ajoutercaractere(caracterespossibles,event)
            self.effacercaractere()
        if self.seul==False: # si il existe plusieurs champs, il faut specifie si il peut etre modifie ou non
            if pygame.mouse.get_pressed()[0]:
                (sourisx,sourisy)=pygame.mouse.get_pos()
                if (sourisx in range(self.x-45,self.x+46))and(sourisy in range(self.y,self.y+self.taille+1)): # le champs est considere comme choisi si l'utilisateur clique dessus
                    self.choisi=True
                else:
                    self.choisi=False
        
    def ajoutercaractere(self,caracterespossibles='tout',event=None): # ajoute un caractere parmis ceux disponibles
        if event!=None:
            if(len(self.texte)<self.largeur): # verifie que le texte ne depasse pas la limite fixee
                if event.type==KEYDOWN and self.choisi==True:
                    if caracterespossibles=='nombres':
                        touches=self.touches[32:] # ne prend que les nombres
                    elif 'lettres' in caracterespossibles:
                        touches=self.touches[:26] # ne prend que les lettres
                    else:
                        touches=self.touches # tous les caracteres sont disponibles
                    for _ in touches:
                            if event.key==_:
                                if self.texte=='' or pygame.key.get_pressed()[K_LSHIFT] or caracterespossibles=='lettresmaj': # si c'est le premier caractere ou que la touche maj est appuyee, on le transforme en majuscule
                                    self.texte+=self.caracteresmaj[self.touches.index(_)]
                                else:
                                    self.texte+=self.caracteresmin[self.touches.index(_)] # sinon on prend la minuscule
                                self.afficher()
                            
                    
    def effacercaractere(self): # efface le dernier caractere
        if self.texte!='':
            if pygame.key.get_pressed()[K_BACKSPACE] and self.choisi==True:
                clock.tick(10) # peu de fps pour limiter la vitesse d'effacement des lettres
                self.texte=self.texte[:-1]
                self.texteaffiche.effacer()
                self.afficher()


    def afficher(self): # affiche le texte associe au champs
        if self.textecentre==False:
            self.texteaffiche=Texte(self.texte,couleur=self.couleur,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
            self.texteaffiche.centrer(self.x,self.y+self.taille//2,self.largeur)
        else:
            self.texteaffiche=Texte(self.texte,self.x,self.y,couleur=self.couleur,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,centre=True)
            self.texteaffiche.afficher()


class Pointeur:

    def __init__(self,valeur=0,x=0,y=0,largeur=0,longueur=0):
        self.valeur=valeur
        self.x=x
        self.y=y
        self.largeur=largeur
        self.longueur=longueur
        self.ancienx=x
        self.ancieny=y
      

class CurseurMod: # barre horizontal ou verticale possedant un pointeur que l'on peut deplacer (droite/gauche ou haut/bas)

    def __init__(self,nom='',x=10,y=10,largeur=0,longueur=0,valeurmini=0,valeurmaxi=0,pas=0,valeurpointeur=0,typeaffichage=0,tailletexte=30,couleur=(255,255,255)):
        self.x=x
        self.y=y
        self.tailletexte=tailletexte
        self.nom=Texte(nom,self.x,self.y,taille=self.tailletexte)
        self.largeur=largeur
        self.longueur=longueur
        self.valeurmini=valeurmini
        self.valeurmaxi=valeurmaxi
        self.pas=pas
        self.valeurpointeur=valeurpointeur
        self.typeaffichage=typeaffichage
        self.pressed=False
        self.couleur=couleur
        self.orientation=int(self.largeur>=self.longueur) # defini si la barre est verticale ou horizontale pour l'afficher
        if self.orientation: # place le pointeur en fonction de l'orientation de la barre
            self.pointeurlargeur=int(640/(self.largeur//self.pas)/5)
            self.pointeurlongueur=4+int(self.longueur*1.5)
            self.pointeurx=self.x+self.valeurpointeur*self.pas
            self.pointeury=self.y
        else:
            self.pointeurlargeur=4+int(self.largeur*1.5)
            self.pointeurlongueur=int(640/(self.longueur//self.pas)/5)
            self.pointeury=self.y+self.valeurpointeur*self.pas
            self.pointeurx=self.x
        self.pointeurlargeur+=int(self.pointeurlargeur==0)
        self.pointeurx-=self.pointeurlargeur//2
        self.pointeury-=self.pointeurlongueur//2
        self.pointeur=Pointeur(valeurpointeur,self.pointeurx,self.pointeury,self.pointeurlargeur,self.pointeurlongueur)
        self.afficherpointeur()
        if self.typeaffichage==0:
            self.nom.centrer(self.x-self.nom.width//1.5*int(self.largeur<self.longueur),self.y+self.nom.height*int(self.largeur>self.longueur),self.largeur,self.longueur)
        else:
            self.nom.centrer(self.x-self.nom.width//1.5*int(self.largeur>self.longueur),self.y+self.nom.height//6)
        self.reafficherbarre()
        self.texte=Texte(str(self.valeurpointeur),taille=self.tailletexte)
        self.valtextemax=Texte(str(self.valeurmaxi),taille=self.tailletexte)
        if self.typeaffichage==0: # affiche la valeur centre par rapport a la barre ou a la fin de celle-ci
            self.texte.centrer(self.x-self.nom.width//(1.5+14.5*int(self.largeur>self.longueur))-5*int(self.largeur<self.longueur),self.y+self.nom.height*(1+int(self.largeur>self.longueur)),self.largeur,self.longueur)
        else:
            self.texte.centrer(self.x+self.largeur*(1-0.5)*int(self.largeur>self.longueur)+self.valtextemax.width,self.y+self.longueur*(1-0.5)*int(self.longueur>self.largeur)+self.valtextemax.height//8,self.largeur,self.longueur)

    def afficherpointeur(self): # efface le pointeur, reaffiche la barre et affiche le pointeur
        screen.fill((0,0,0),(self.pointeur.ancienx,self.pointeur.ancieny,self.pointeur.largeur+self.largeur*int(self.longueur>self.largeur),self.pointeur.longueur+self.longueur*int(self.longueur<self.largeur)))
        self.reafficherbarre()
        screen.fill(self.couleur,(self.pointeur.x,self.pointeur.y,self.pointeur.largeur+self.largeur*int(self.longueur>self.largeur),self.pointeur.longueur+self.longueur*int(self.longueur<self.largeur)))
        pygame.display.update([(self.pointeur.ancienx,self.pointeur.ancieny,self.pointeur.largeur+self.largeur*int(self.longueur>self.largeur),self.pointeur.longueur+self.longueur*int(self.longueur<self.largeur)),(self.pointeur.x,self.pointeur.y,self.pointeur.largeur+self.largeur*int(self.longueur>self.largeur),self.pointeur.longueur+self.longueur*int(self.longueur<self.largeur))])
        self.pointeur.ancienx=self.pointeur.x
        self.pointeur.ancieny=self.pointeur.y

    def deplacementpointeur(self): # gere les deplacements du pointeur en fonction de la position de la souris
        if pygame.mouse.get_pressed()[0]:
            (self.sourisx,self.sourisy)=pygame.mouse.get_pos()
            if(self.sourisx in range(self.x,self.x+self.largeur+1))and(self.sourisy in range(self.y,self.y+self.longueur+1)):
                self.pressed=True
            if self.pressed==True:
                if self.orientation:
                    if(self.x<=self.sourisx<=self.x+self.largeur):
                        self.pointeur.x=self.sourisx-self.pointeur.largeur//2
                    else:
                        if self.x>=self.sourisx:
                            self.pointeur.x=self.x-self.pointeur.largeur//2
                        elif self.sourisx>=self.x+self.largeur:
                            self.pointeur.x=self.x+self.largeur-self.pointeur.largeur//2
                else:
                    if(self.y<=self.sourisy<=self.y+self.longueur):
                        self.pointeur.y=self.sourisy-self.pointeur.longueur//2
                    else:
                        if self.y>=self.sourisy:
                            self.pointeur.y=self.y-self.pointeur.longueur//2
                        elif self.sourisy>=self.y+self.longueur:
                            self.pointeur.y=self.y+self.longueur-self.pointeur.longueur//2
                if self.valeurpointeur!=((self.pointeur.x+self.pointeur.largeur//2-self.x)*int(self.largeur>self.longueur)+(self.pointeur.y+self.pointeur.longueur//2-self.y)*int(self.largeur<self.longueur))//self.pas: # modifie la position du pointeur si il atteint des valeurs entieres differentes
                    self.valeurpointeur=((self.pointeur.x+self.pointeur.largeur//2-self.x)*int(self.largeur>self.longueur)+(self.pointeur.y+self.pointeur.longueur//2-self.y)*int(self.largeur<self.longueur))//self.pas
                    for val in range(self.valeurmini,self.valeurmaxi+1): # cherche la valeur correspondante
                        if self.valeurpointeur==val:
                            if self.orientation:
                                self.pointeur.x=self.x+val*self.pas-self.pointeur.largeur//2
                            else:
                                self.pointeur.y=self.y+val*self.pas-self.pointeur.longueur//2
                    screen.fill((0,0,0),(self.texte.x,self.texte.y,self.texte.width,self.texte.height))
                    pygame.display.update((self.texte.x,self.texte.y,self.texte.width,self.texte.height))
                    self.texte=Texte(str(self.valeurpointeur),taille=self.tailletexte)
                    if self.typeaffichage==0:
                        self.texte.centrer(self.x-self.nom.width//(1.5+14.5*int(self.largeur>self.longueur))-5*int(self.largeur<self.longueur),self.y+self.nom.height*(1+int(self.largeur>self.longueur)),self.largeur,self.longueur)
                    else:
                        self.texte.centrer(self.x+self.largeur*(1-0.5)*int(self.largeur>self.longueur)+self.valtextemax.width,self.y+self.longueur*(1-0.5)*int(self.longueur>self.largeur)+self.valtextemax.height//8,self.largeur,self.longueur)
                    self.afficherpointeur()
        else:
            self.pressed=False

    def reafficherbarre(self): # reaffiche la barre
        if self.orientation:
            for _ in range(0,self.largeur+1,self.pas):
                if self.couleur==(255,255,255):
                    screen.fill(self.couleur,(self.x-1+_,self.y-2,2,self.longueur+4)) # affiche les differents pics si la barre est blanche
                    pygame.display.update((self.x-1+_,self.y-2,2,self.longueur+4))
                else:
                    pass
        else:
            for _ in range(0,self.longueur+1,self.pas):
                if self.couleur==(255,255,255):
                    screen.fill(self.couleur,(self.x-2,self.y-1+_,self.largeur+4,2))
                    pygame.display.update((self.x-2,self.y-1+_,self.largeur+4,2))
                else:
                    pass
        if self.couleur==(255,255,255): # affiche la barre 
            screen.fill(self.couleur,(self.x,self.y,self.largeur,self.longueur))
        else:
            if self.orientation: # si la couleur est differente du blanc, il y a un degrade
                for p in range(0,self.largeur+1):
                    screen.fill((self.couleur[0]*p//self.largeur,self.couleur[1]*p//self.largeur,self.couleur[2]*p//self.largeur),(self.x+p,self.y,1,self.longueur))
            else:
                for p in range(0,self.longueur+1):
                    screen.fill((self.couleur[0]*p//self.longueur,self.couleur[1]*p//self.longueur,self.couleur[2]*p//self.longueur),(self.x,self.y+p,1,self.largeur))
        pygame.display.update((self.x,self.y,self.largeur,self.longueur))
            

class Brique:

    def __init__(self,nom='',x=0,y=0,vie=0,largeur=50,hauteur=10,couleurfond=(0,0,0),imagefond=None,typefond=0):
        self.nom=nom
        self.x=x
        self.y=y
        self.ancienx=x
        self.ancieny=y
        self.vie=vie
        self.possessionbonus()
        self.sound=sonbrique
        self.largeur=largeur
        self.hauteur=hauteur
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond
        self.sprite()

    def afficher(self): # affiche la brique
        screen.fill(self.couleur,(self.x,self.y,self.largeur,self.hauteur))
        pygame.display.update((self.x,self.y,self.largeur,self.hauteur))

    def effacerbrique(self,x=False,y=False): # efface au coordonnee donnees. Si aucune coordonnee n'est donne, celle de la brique sont utilisees
        if x==False:
            x=self.x
        if y==False:
            y=self.y
        if self.typefond==0:
            screen.fill(self.couleurfond,(x,y,self.largeur,self.hauteur))
        else:
            screen.blit(self.imagefond.subsurface(x,y,self.largeur,self.hauteur),(x,y))
        pygame.display.update((x,y,self.largeur,self.hauteur))

    def sprite(self): # defini la couleur de la brique en fonction de sa vie
        if self.vie<=0:
            self.couleur=self.couleurfond
        if self.vie==1:
            self.couleur=(255,255,255)
        if self.vie==2:
            self.couleur=(255,0,0)
            self.afficher()
        if self.vie==3:
            self.couleur=(0,151,0)
        if self.vie==4:
            self.couleur=(0,0,255)
        if self.vie==5:
            self.couleur=(255,255,0)
        if self.vie==6:
            self.couleur=(255,151,255)
        if self.vie==7:
            self.couleur=(255,0,255)
        if self.vie==8:
            self.couleur=(255,151,0)
        if self.vie==9:
            self.couleur=(0,151,255)
        if self.vie==10:
            self.couleur=(151,151,151)
        if self.vie>10:
            self.couleur=(192,192,192)
        if self.vie>0:
            self.afficher()
        else:
            self.effacerbrique() # si la brique n'a plus de vie, elle est effacee

    def possessionbonus(self): # donne un bonus ou non a la brique
        self.bonus=False
        if self.vie<=50:
            if randrange(100)<=self.vie: # plus la brique a de vie, plus elle a de chance d'avoir un bonus
                self.bonus=True
        else:
            if randrange(2)==1:
                self.bonus=True


class Ennemi(Brique): # brique ayant la possibilite de se deplacer

    def __init__(self,x=0,y=0,vie=0,largeur=50,hauteur=10,direction=1,vitesse=2,couleurfond=(0,0,0),imagefond=None,typefond=0): # instancie une brique correspondante
        Brique.__init__(self,'',x,y,vie,largeur,hauteur,couleurfond,imagefond,typefond)
        self.direction=direction
        self.vitesse=vitesse

    def deplacement(self): # gere les deplacements de l'ennemi
        self.ancienx,self.ancieny=self.x,self.y
        if self.direction==1:  # 4 directions sont utilisees (dans le sens des aiguilles d'une montre) : 1 : vers le haut, 2 : vers la droite, 3 : vers le bas, 4: vers la gauche  
            self.y-=self.vitesse
        elif self.direction==2:
            self.x+=self.vitesse
        elif self.direction==3:
            self.y+=self.vitesse
        else:
            self.x-=self.vitesse
        self.effacerbrique(self.ancienx,self.ancieny)
        self.afficher()
        self.limite()

    def limite(self): # efface l'ennemi si il atteint des coordonnes limites
        if self.x>=620 or self.x<=20 or self.y>=400 or self.y<=50:
            self.effacerbrique()
            return (True)

class Boss(Brique): # brique ayant la possibilite de se deplacer et de creer des ennemis

    def __init__(self,x=0,y=0,vie=0,couleurfond=(0,0,0),imagefond=None,typefond=0,longueur=70,largeur=10): # instancie la brique correspondante
        Brique.__init__(self,'',x,y,vie,longueur,largeur,couleurfond,imagefond,typefond)
        self.vitesse=10
        self.cooldown=200

    def deplacement(self,direction=0): # gere les deplacements du boss
        if direction!=0:  # si la direction est >0, le boss va vers la droite, si elle est <0, le boss va vers la gauche
            self.ancienx,self.ancieny=self.x,self.y
            if direction<0:
                self.x-=self.vitesse*int(self.x>=100)
            elif direction>0:
                self.x+=self.vitesse*int(self.x<=540)
            self.effacerbrique(self.ancienx,self.ancieny)
            self.afficher()
                

class Joueur:

    def __init__(self,couleurfond=(0,0,0),imagefond=None,typefond=0,couleur=(255,255,255,255)):
        self.x=320
        self.y=460
        self.ancienx=320
        self.ancieny=460
        self.vie=3
        self.points=0
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond
        self.score=Texte('Score : '+str(self.points),x=10,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
        self.nombreballe=1
        self.sound1=sonjoueur1
        self.taille=50
        self.vitesse=6
        self.listebonus=[]
        self.couleur=couleur
        self.nom='???'

    def effacer(self): # efface le joueur a ses anciennes coordonnnees
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.ancienx,self.ancieny,self.taille,10))
        else:
            screen.blit(self.imagefond.subsurface(self.ancienx,self.ancieny,self.taille,10),(self.ancienx,self.ancieny))
        pygame.display.update((self.ancienx,self.ancieny,self.taille,10))
        
    def mouvement(self): # efface et reaffiche le joueur
        self.effacer()
        temp=pygame.Surface((self.taille,10)).convert()
        temp.blit(screen,(-self.x,-self.y))
        temp.fill(self.couleur)
        temp.set_alpha(self.couleur[3])        
        screen.blit(temp, (self.x,self.y))
        pygame.display.update((self.x,self.y,self.taille,10))

    def gauche(self): # deplace le joueur vers la gauche
        self.ancienx=self.x
        self.x-=int(self.vitesse*int(self.x>=10))
        if self.x<10: self.x=10
        self.mouvement()

    def droite(self): # deplace le joueur vers la droite
        self.ancienx=self.x
        self.x+=int(self.vitesse*int(self.x<=630-self.taille))
        if self.x>630-self.taille:
            self.x=630-self.taille
        self.mouvement()


class Bonus():

    def __init__(self,x=0,y=0,modif=0,couleurfond=(0,0,0),imagefond=None,typefond=0):
        self.x=x
        self.y=y
        self.modif=modif
        self.effet()
        (self.height,self.width)=self.sprite.get_size() # recupere les dimensions du bonus
        self.x+=(50-self.height)//2 # et le recentre par rapport a la brique
        self.ancienx=self.x
        self.ancieny=self.y
        self.son=sonbonus
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond

    def effet(self): # associe une image a l'effet du bonus
        if self.modif=='taille':
            self.sprite=spritebonustaille
        elif self.modif=='vitesse':
            self.sprite=spritebonusvitesse
        elif self.modif=='degat':
            self.sprite=spritebonusdegat
            
    def deplacement(self): # gere les deplacements du bonus
        self.ancieny=self.y
        self.y+=2
        self.effacer()

    def afficher(self): # affiche le bonus
        screen.blit(self.sprite,(self.x,self.y))
        pygame.display.update((self.x,self.y,self.height,self.width))
        
    def effacer(self): # efface le bonus a ses anciennes coordonnees
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.ancienx,self.ancieny,self.height,self.width))
        else:
            if self.ancieny+self.width<=480:
                screen.blit(self.imagefond.subsurface(self.ancienx,self.ancieny,self.height,self.width),(self.ancienx,self.ancieny))
            else:
                screen.blit(self.imagefond.subsurface(self.ancienx,self.ancieny,self.height,480-self.ancieny),(self.ancienx,self.ancieny))
        pygame.display.update((self.ancienx,self.ancieny,self.height,self.width))

    def supprimer(self): # efface le bonus
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.x,self.y,self.height,self.width))
        else:
            if self.y+self.width<=480:
                screen.blit(self.imagefond.subsurface(self.x,self.y,self.height,self.width),(self.x,self.y))
            else:
                screen.blit(self.imagefond.subsurface(self.x,self.y,self.height,480-self.y),(self.x,self.y))
        pygame.display.update((self.x,self.y,self.height,self.width))

                
class Balle:

    def __init__(self,direction=0,couleurfond=(0,0,0),imagefond=None,typefond=0,cote=10):
        self.x=315
        self.y=445
        self.ancienx=self.x
        self.ancieny=self.y
        self.sens=1
        self.direction=direction
        self.accelerationx=0
        self.accelerationy=0
        self.degat=1
        self.collision=False
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond
        self.touche=False
        self.modifcouleur()
        self.coordxcoll,self.coordycoll=0,0
        self.coordlargeur,self.coordhauteur=0,0
        self.cote=cote
        self.brique=''

    def balleintexte(self,texte): # verifie si la balle se trouvait dans le texte (et en a donc efface une partie)
        if(self.ancienx in range(texte.x-self.cote,texte.x+texte.width+1))and(self.ancieny in range(texte.y-self.cote,texte.y+texte.height+1)):
            temp=pygame.Surface((texte.surface.get_width(),texte.surface.get_height())).convert()
            temp.blit(screen,(-texte.x,-texte.y))
            temp.blit(texte.surface, (0, 0))
            temp.set_alpha(texte.couleur2[3])        
            screen.blit(temp, (texte.x,texte.y))
            pygame.display.update((self.ancienx,self.ancieny,self.cote,self.cote))

    def effacer(self): # efface la balle a ses anciennes coordonnees
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.ancienx,self.ancieny,self.cote,self.cote))
        else:
            if self.ancieny+self.cote<=480:
                screen.blit(self.imagefond.subsurface(self.ancienx,self.ancieny,self.cote,self.cote),(self.ancienx,self.ancieny))
            else:
                screen.blit(self.imagefond.subsurface(self.ancienx,self.ancieny,self.cote,480-self.ancieny),(self.ancienx,self.ancieny))
        pygame.display.update((self.ancienx,self.ancieny,self.cote,self.cote))

    def afficher(self): # affiche la balle
        temp=pygame.Surface((self.cote,self.cote)).convert()
        temp.blit(screen,(-self.x,-self.y))
        temp.fill(self.couleur)
        temp.set_alpha(self.couleur[3])        
        screen.blit(temp, (self.x,self.y))
        pygame.display.update((self.x,self.y,self.cote,self.cote))

    def affeff(self): # efface puis affiche la balle
        self.effacer()
        self.afficher()
        
    def modifcouleur(self): # modifie la couleur de la balle en fonction de ses degats
        self.couleur=(255,255,255,255)
        if self.degat==2:
            self.couleur=(255,220,60,255)
        elif self.degat==3:
            self.couleur=(192,192,192,255)

    def supprimer(self): # efface la balle
        if self.typefond==0:
            screen.fill(self.couleurfond,(self.x,self.y,self.cote,self.cote))
        else:
            if self.y+self.cote<=480:
                screen.blit(self.imagefond.subsurface(self.x,self.y,self.cote,self.cote),(self.x,self.y))
            else:
                screen.blit(self.imagefond.subsurface(self.x,self.y,self.cote,480-self.y),(self.x,self.y))
        pygame.display.update((self.x,self.y,self.cote,self.cote))
           

class Niveau: # instancie et gere l'ensemble des briques composant le niveau 

    def __init__(self,numero=0,debutx=70,debuty=50,distancex=480,distancey=270,pasx=75,pasy=30,liste=[],largeurbrique=50,hauteurbrique=10,couleurfond=(0,0,0),imagefond=None,typefond=0,complet=False):
        self.numero=numero
        self.contenu={}
        self.numerospe=[10,11,18]
        self.numeroautre=[5,7,8,12,13,16,17,20]
        self.debutx=debutx
        self.debuty=debuty
        self.distancex=distancex
        self.distancey=distancey
        self.distancey+=30*int(self.numero==20)
        self.pasx=pasx
        self.pasy=pasy
        self.liste=liste
        self.largeurbrique=largeurbrique
        self.hauteurbrique=hauteurbrique
        self.couleurfond=couleurfond
        self.imagefond=imagefond
        self.typefond=typefond
        self.complet=complet
        self.autre()
        self.i=0
        i=0
        if (self.numero!=19 or (self.numero==19 and self.complet==False)) and ("BOSS" not in self.liste): # defini chaque element du dictionnaire contenant les briques en fonction du numero du niveau
            for _ in range(self.debuty,self.debuty+self.distancey+1,self.pasy):
                for __ in range(self.debutx,self.debutx+self.distancex+1,self.pasx):
                    if(self.numero not in self.numerospe)and(self.numero not in self.numeroautre)and(self.numero>0)or((self.numero==19)or(self.numero==20) and self.complet==False): # niveaux aleatoires
                        self.contenu[str(i)]=Brique('brique'+str(i),__,_,(1+(int(__ in range(100,450))*int(self.numero>1)+int(__ in range(150,400))*int(self.numero>2))*int(_ in range(80,300))+int(__ in range(200,400))*int(self.numero>3))*int(self.numero<5)+randrange(10)*int(self.numero>=5),self.largeurbrique,self.hauteurbrique,self.couleurfond,self.imagefond,self.typefond)
                    elif self.numero in self.numerospe: # niveaux non aleatoires "simples"
                        if self.numero==18:
                            self.contenu[str(i)]=Brique('brique'+str(i),__,_,20,self.largeurbrique,self.hauteurbrique,self.couleurfond,self.imagefond,self.typefond)
                        else:
                            self.contenu[str(i)]=Brique('brique'+str(i),__,_,10,self.largeurbrique,self.hauteurbrique,self.couleurfond,self.imagefond,self.typefond)
                    else: # niveaux non aleatoires "complexes" ou crees par le joueur
                        self.contenu[str(i)]=Brique('brique'+str(i),__,_,int(self.liste[i]),self.largeurbrique,self.hauteurbrique,self.couleurfond,self.imagefond,self.typefond)
                    if self.contenu[str(i)].vie>0:
                        self.contenu[str(i)].afficher()
                    else:
                        del self.contenu[str(i)]
                    i+=1
            if self.numero==20 and self.complet==True: # modifie le son de chaque brique pour le niveau final
                for _ in self.contenu.keys():
                    self.contenu[_].sound=sonboom
        else: # niveau du boss
            pygame.mixer.music.load("sons/Butterfly_Tea_-_Divine_Weapon.wav")
            if abs(self.numero)==19:
                self.contenu['0']=Boss(285,235,20,self.couleurfond,self.imagefond,self.typefond)
                self.contenu['0'].viemax=self.contenu['0'].vie
                self.contenu['0'].sprite()
            else:
                self.contenu['0']=Boss(debutx+2*pasx,debuty+3*pasy,20,self.couleurfond,self.imagefond,self.typefond,35,5) # utilise pour l'affichage du niveau miniature
        if self.numero>0: # redefini "proprement" (rajout, si besoin, de 0) la liste du niveau pour etre sauvegarde ensuite
            self.liste=[]
            for _ in range(77):
                try:
                    self.liste.append(self.contenu[str(_)].vie)
                except:
                    self.liste.append(0)
            

    def autre(self): # niveaux non aleatoires "complexes"
        if self.numero in self.numeroautre:
            if self.numero==5:
                self.liste=[0,1,2,3,0,0,0,4,0,0,0,0,0,0,5,0,4,3,2,0,0,6,0,0,0,1,0,0,0,7,8,9,0,0,0,0,0,0,5,6,7,0,0,0,8,0,0,0,7,0,0,9,0,0,0,6,0,0,1,0,0,0,5,0,0,0,2,3,4,0]
            if(self.numero==7)or(self.numero==8):
                self.liste=[0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1]
                if self.numero==8:
                    for _ in self.liste:
                        if _==1:
                            self.liste[self.liste.index(_)]=randrange(9)+1
            if self.numero==12:
                self.liste=[0,2,0,0,0,2,0,2,0,2,0,2,0,2,2,0,0,2,0,0,2,2,0,0,2,0,0,2,2,0,0,0,0,0,2,2,0,0,0,0,0,2,0,2,0,0,0,2,0,0,0,2,0,2,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0]
            if self.numero==13:
                self.liste=[0,1,0,0,4,4,0,1,1,0,4,0,0,4,0,1,0,0,0,4,0,1,1,1,4,4,4,4,3,3,3,5,0,5,0,0,3,3,5,5,5,5,3,3,3,0,0,5,0,0,0,2,2,2,2,0,0,0,2,2,2,0,0,0,2,2,2,2,2,0]
            if self.numero==16:
                self.liste=[0,0,5,5,5,0,0,0,5,5,5,5,5,0,0,5,5,5,5,5,0,5,5,0,5,0,5,5,5,5,5,0,5,5,5,5,5,5,5,5,5,5,5,5,5,0,5,5,5,5,5,0,5,0,5,5,0,5,5,5,5,5,0,0,0,5,5,5,0,0,0,0,0,0,0,0,0]
            if self.numero==17:
                self.liste=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,0,0,0,20,0,20,0,20,0,20,0,20,20,0,0,20,0,0,20,20,0,20,0,20,0,20,0,20,0,0,0,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            if self.numero==20:
                self.liste=[0,0,9,9,9,0,0,0,9,8,9,9,9,0,9,8,8,9,9,9,9,9,8,9,9,9,9,9,9,8,9,9,9,9,9,9,9,9,9,8,9,9,9,9,9,9,8,8,9,9,9,8,9,8,8,9,9,9,8,9,9,8,9,0,9,9,8,9,9,0,0,0,9,9,9,0,0]
                
                

class Niveauminiature(Niveau): # niveau non jouable que l'on peut selectionner

    def __init__(self,nom='',numero=-1,debutx=70,debuty=50,distancex=60,distancey=45,pasx=10,pasy=5,liste='',largeurbrique=5,hauteurbrique=2): # instancie le niveau correspondant
        Niveau.__init__(self,numero,debutx,debuty,distancex,distancey,pasx,pasy,liste,largeurbrique,hauteurbrique)
        self.nom=nom
        self.listevies=liste
        if len(self.nom)>20: # si le nom est trop long, une partie est remplacee par '...'
            self.nom=self.nom[:17]+'...'
        self.nomaffiche=Texte(self.nom,taille=int(20/(1+0.5*int(len(self.nom)>15))))
        self.nomaffiche.centrer(self.debutx+34,self.debuty+65)
        (self.sourisx,self.sourisy)=pygame.mouse.get_pos()
        self.anciensourisx=self.sourisx
        self.anciensourisy=self.sourisy
        self.choisi=0

    def choisir(self): # renvoie si l'utilisateur a selectionne ou nom le niveau
        (self.sourisx,self.sourisy)=pygame.mouse.get_pos()
        if(self.sourisx in range(self.debutx,self.debutx+self.distancex+1))and((self.sourisy in range(self.debuty,self.debuty+self.distancey+1))):
            self.nomaffiche.couleur2=(255,0,0,255)
            self.choisi+=1
        else:
            self.nomaffiche.couleur2=self.nomaffiche.couleur
            self.choisi=0
        if((self.anciensourisx in range(self.debutx,self.debutx+self.distancex+1))and(self.anciensourisy in range(self.debuty,self.debuty+self.distancey+1)))or(self.sourisx in range(self.debutx,self.debutx+self.distancex+1))and((self.sourisy in range(self.debuty,self.debuty+self.distancey+1))):
            self.nomaffiche.afficher()
        self.anciensourisx,self.anciensourisy=self.sourisx,self.sourisy
        return(self.choisi)

        
class Time: # gere tout ce qui concerne le temps (temps de jeu, decompte, ...)

    def __init__(self,secondes=0,minutes=0,heures=0):
        self.secondes=secondes
        self.minutes=minutes
        self.heures=heures
        self.total=self.secondes+60*self.minutes+3600*self.heures

    def ajout(self,valeur=1): # ajoute un multiple de 1/60
        self.total+=valeur/60
        self.secondes+=valeur/60

    def retrait(self,valeur=1): # retire un multiple de 1/60
        self.total-=valeur/60
        self.secondes-=valeur/60

    def getsecondes(self): # renvoie le nombre de secondes actuel 
        return int(self.secondes%60)

    def getminutes(self): # renvoie le nombre de minutes actuel 
        return int((self.minutes+self.secondes//60)%60)

    def getheures(self): # renvoie le nombre d'heures actuel 
        return int(self.heures+(self.minutes+self.secondes//60)//60)

    def affichertemps(self): # affiche le temps sous la forme : heures : minutes : secondes
        self.secondes,self.minutes,self.heures=self.getsecondes(),self.getminutes(),self.getheures()
        self.temps='0'*int(len(str(int(self.heures)))==1)+str(int(self.heures))+" : "+'0'*int(len(str(int(self.minutes)))==1)+str(int(self.minutes))+" : "+'0'*int(len(str(int(self.secondes)))==1)+str(int(self.secondes))
        return (self.temps)

    def decompte(self,valeur=1): # retire un multiple de 1/60 et affiche le temps restant en secondes
        self.retrait(valeur)
        self.temps=Texte(str(int(self.secondes)),taille=50,centre=True)
        if int(self.secondes)!=int(self.secondes+1/60):
            self.temps.afficher()

class Jeu:

    def __init__(self,couleurfond=(0,0,0),imagefond=None,typefond=0):
        screen=pygame.display.set_mode((640,480))
        pygame.mouse.set_visible(False)
        self.continuer=True
        self.soundon=True
        self.balles={}
        self.balleseff=[]
        self.gameoversound=pygame.mixer.Sound("sons/gameover.wav")
        self.pause=False
        self.stage=20
        self.nombrestages=0
        self.pointslimites=0
        self.arretvolontaire=False
        self.mort=0
        self.bonus=['taille','taille','vitesse','vitesse','degat','degat']
        self.listebonus={}
        self.touches=[K_q,K_w,K_e,K_r,K_t,K_y,K_u,K_i,K_o,K_p,K_a,K_d,K_f,K_g,K_h,K_j,K_k,K_l,K_SEMICOLON,K_z,K_x,K_c,K_v,K_b,K_n,K_LEFT,K_RIGHT,K_UP,K_DOWN]
        self.caractereassocie=['a','z','e','r','t','y','u','i','o','p','q','d','f','g','h','j','k','l','m','w','x','c','v','b','n','G','D','H','B']
        self.code=''
        self.hardcore=False
        self.enjeu=self.modifmusic=True
        self.couleurfond=couleurfond
        self.typefond=typefond
        self.imagefond=imagefond
        self.joueur=Joueur(self.couleurfond,self.imagefond,self.typefond)
        self.duel=False
        self.tempsdejeu=Time()
        self.record=-1
        self.nombretriche=0
        self.modifson=True
        self.nomniveau='???'
        self.narration=False

    def retourniveau(self): # repositionne le joueur et les balles
        self.joueur.score.afficher()
        self.applicationbonusjoueur()
        self.joueur.x,self.joueur.y=320-self.joueur.taille//2,460
        self.joueur.mouvement()
        self.calculballes(100*int((self.stage==11)or(self.stage==18)))
        self.applicationbonusjoueur()
        self.applicationbonusballes()
        for _ in self.balles.keys():
            self.balles[_].modifcouleur()
            self.balles[_].afficher()

    def affnomniveau(self): # affiche le numero du stage ainsi que son nom (si le jeu est en mode histoire)
        screen.fill((0,0,0))
        pygame.display.flip()
        Texte("Stage "+str(self.stage),y=-100,taille=90,centre=True).afficher()
        if self.illimite==False:
            if self.stage==1:
                self.nomniveau="Hello World"
                Texte("Hello World",taille=50,centre=True).afficher()
            if self.stage==2:
                self.nomniveau="The Beginning"
                Texte("The Beginning",taille=50,centre=True).afficher()
            if self.stage==3:
                self.nomniveau="Not Really The Beginning But Kind Of"
                Texte("Not Really The Beginning",taille=50,centre=True).afficher()
                Texte("But Kind Of",y=50,taille=50,centre=True).afficher()
            if self.stage==4:
                self.nomniveau="Still The Easy Part"
                Texte("Still The Easy Part",taille=50,centre=True).afficher()
            if self.stage==5:
                self.nomniveau="GO GO POWER RANGERS !"
                Texte("GO GO",taille=50,centre=True).afficher()
                Texte("POWER RANGERS !",y=50,taille=50,centre=True).afficher()
            if self.stage==6:
                self.nomniveau="Randomness"
                Texte("Randomness",taille=50,centre=True).afficher()
            if self.stage==7:
                self.nomniveau="Laziness"
                Texte("Laziness",taille=50,centre=True).afficher()
            if self.stage==8:
                self.nomniveau="Both"
                Texte("Both",taille=50,centre=True).afficher()
            if self.stage==9:
                self.nomniveau="It's Getting old-ness"
                Texte("It's Getting old-ness",taille=50,centre=True).afficher()
            if self.stage==10:
                self.nomniveau="Too Long"
                Texte("Too Long",taille=50,centre=True).afficher()
            if self.stage==11:
                self.nomniveau="One More Time"
                Texte("One More Time",taille=50,centre=True).afficher()
            if self.stage==12:
                self.nomniveau="You Can't Hurt Me"
                Texte("You Can't Hurt Me",taille=50,centre=True).afficher()
            if self.stage==13:
                self.nomniveau="The Final Countdown"
                Texte("The Final Countdown",taille=50,centre=True).afficher()
            if self.stage==14:
                self.nomniveau="Bye"
                Texte("Bye",taille=50,centre=True).afficher()
            if self.stage==15:
                self.nomniveau="You Though It Was Over ?" 
                Texte("You Though It Was Over ?",taille=50,centre=True).afficher()
            if self.stage==16:
                self.nomniveau="I've had enough"
                Texte("I've had enough",taille=50,centre=True).afficher()
            if self.stage==17:
                self.nomniveau="It's Endless, You Know..."
                Texte("It's Endless,",taille=50,centre=True).afficher()
                Texte("You Know...",y=50,taille=50,centre=True).afficher()
            if self.stage==18:
                self.nomniveau="The End"
                Texte("The End",taille=50,centre=True).afficher()
            if self.stage==19:
                self.nomniveau="Face To Face"
                Texte("Face",taille=50,centre=True).afficher()
                Texte("To",y=50,taille=50,centre=True).afficher()
                Texte("Face",y=100,taille=50,centre=True).afficher()
            if self.stage==20:
                self.nomniveau="Good Bye World !"
                Texte("Good Bye World !",taille=50,centre=True).afficher()
            if len(self.nomniveau)>20: # modifie la taille si besoin pour etre sauvegarde ensuite
                self.nomniveau=self.nomniveau[:17]+'...'
        self.enjeu=self.modifmusic=False
        self.lancement()
        if self.continuer==True:
            if self.typefond==0: 
                screen.fill(self.couleurfond)
            else:
                screen.blit(self.imagefond,(0,0))
            pygame.display.flip()
        self.enjeu=self.modifmusic=True
 
    def chargerniveau(self): # initialise les stages (ecran nom + structure du niveau)
        self.mort=0
        self.recommencer=False
        self.countdown=Time(11)
        self.affnomniveau()
        if self.continuer==True:
            self.retourniveau()
            self.niveau=Niveau(self.stage,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,complet=not(self.illimite))
            self.stageaffiche=Texte("Stage "+str(self.stage),x=500,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
            self.stageaffiche.afficher()
            if self.illimite==False:
                self.joueur.vieaffichee=Texte("Vie(s) : "+str(self.joueur.vie),x=250,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                self.joueur.vieaffichee.afficher()
            if (self.stage==19 and self.illimite==False) or self.niveau.numero==-19: # attribue la vie du boss en fonction du nombre de balles du joueur
                self.niveau.contenu['0'].vie=7*len(self.balles)
                if self.niveau.contenu['0'].vie<20:
                    self.niveau.contenu['0'].vie=20
                self.niveau.contenu['0'].cooldown=10*self.niveau.contenu['0'].vie
                if self.niveau.contenu['0'].cooldown>200:
                    self.niveau.contenu['0'].cooldown=200
                self.niveau.contenu['0'].viemax=self.niveau.contenu['0'].vie
                self.niveau.contenu['0'].sprite()
            pygame.mixer.stop()
            self.lancement()
            if ((self.stage==19 and self.illimite==False)or(self.niveau.numero==-19))and self.continuer==True:
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volume*int(self.soundon==True))

    def calculballes(self,base=0): # instancie les balles du joueur
        self.balles={}
        direction=randrange(2)
        for _ in range(base*int(not(self.hardcore))+self.joueur.nombreballe+(self.stage//10)*int(not(self.hardcore))):
            self.balles['balle'+str(_+1)]=Balle(direction,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)

    def getcontrol(self): # renvoie l'etat de la touche control gauche (pressee 1, relachee 0)
        pygame.event.pump()
        return pygame.key.get_pressed()[K_LCTRL]

    def lancement(self): # a.k.a. pause
        pygame.event.clear()
        cooldowncode=0
        retour=finlancement=False
        if self.continuer==True:
            self.pause=True
            if self.modifmusic==True: # met l'audio en pause
                pygame.mixer.pause()
                pygame.mixer.music.pause()
            while(finlancement==False)and((self.arretvolontaire==False)and(self.continuer==True))and(retour==False):
                clock.tick(60)
                pygame.event.pump()
                event=pygame.event.poll()
                if cooldowncode>0:
                    cooldowncode-=1
                elif cooldowncode==0: # le temps entre 2 touche est ecoule, le code se remet a zero
                    self.code=''
                    cooldowncode=-1
                self.verifquit(event)
                if event.type==KEYDOWN:
                    if event.key in self.touches:
                        self.code+=self.caractereassocie[self.touches.index(event.key)] # recupere les touches entrees pour les ajouter au code
                        cooldowncode=60
                    if (event.key==K_RETURN) or (event.key==K_SPACE): # arrete la pause si le joueur appuie sur entree ou espace
                        finlancement=True
                if self.getcontrol() and self.narration==True: # passe les pauses si il y a du texte a l'ecran 
                    finlancement=True
                if self.enjeu==True and self.hardcore==False and self.duel==False:
                    if self.code=='HHBBGDGDba' or self.code=='abDGDGBBHH': # verifie si le code entre est correcte
                        cooldowncode=0
                        if self.code=='HHBBGDGDba':
                            soncode.set_volume(self.volume*int(self.soundon==True))
                            soncode.play()
                            self.nombretriche+=1
                            self.bonus,self.joueur.bonus=[],[] # associe tous les bonus au joueur et les retire des bonus pouvant etre perdus
                            if self.joueur.vie<30:
                                self.joueur.vie=30
                            self.hardcore=False
                        else:
                            if self.niveau.numero!=-1:
                                soncode2.set_volume(self.volume*int(self.soundon==True))
                                soncode2.play()
                                retour=True
                                volume=self.volume
                                soundon=self.soundon
                                self.effacerbonus()
                        taille=self.joueur.taille
                        self.joueur.ancienx,self.joueur.ancieny=self.joueur.x,self.joueur.y
                        self.joueur.effacer()
                        self.applicationbonusjoueur()
                        self.applicationbonusballes()
                        self.joueur.x=self.joueur.x-(self.joueur.taille-taille)//2 # repositionne le joueur par rapport a sa nouvelle taille
                        if self.joueur.x<10:
                            self.joueur.x=10
                        elif self.joueur.x+self.joueur.taille>630:
                            self.joueur.x=630-self.joueur.taille
                        self.joueur.ancienx=self.joueur.x
                        self.joueur.mouvement()
                        for _ in self.balles:
                            self.balles[_].afficher()
                        if self.illimite==False:
                            self.joueur.vieaffichee=Texte("Vie(s) : "+str(self.joueur.vie),x=250,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                            self.joueur.vieaffichee.afficher()
                        self.code=''
                else:
                    self.code=''
            if retour==True: # retour au stage 1
                self.__init__(self.couleurfond,self.imagefond,self.typefond) # reinitialise le jeu
                self.hardcore=True
                self.bonus,self.joueur.bonus,self.joueur.vie,self.nombretriche=['taille','taille','vitesse','vitesse','degat','degat'],[],1,-1 # enleve tous les bonus du joueur et empeche le jeu d'en faire apparaitre
                self.volume=volume
                self.soundon=soundon
                self.chargerniveau()
            self.pause=self.narration=False
            if self.modifmusic==True:
                pygame.mixer.unpause()
                pygame.mixer.music.unpause() # remet la musique et les sont en marche

    def stopsound(self): # arrete/remet le son
        if self.modifson==True:
            self.soundon=not(self.soundon) # inverse l'etat actuel du son (marche/arret)
            if self.soundon==False: # met le volume de tous les sons et de la musique a 0
                pygame.mixer.music.set_volume(0)
                self.joueur.sound1.set_volume(0)
                try :
                    for _ in self.niveau.contenu.keys():
                        self.niveau.contenu[_].sound.set_volume(0)
                    for _ in self.listebonus.keys():
                        self.listebonus[_].son.set_volume(0)
                except:
                    pass
            elif self.soundon==True: # remet le volume des sons et de la musique
                pygame.mixer.music.set_volume(self.volumemusique)
                self.joueur.sound1.set_volume(self.volume)
                try:
                    for _ in self.niveau.contenu.keys():
                        self.niveau.contenu[_].sound.set_volume(self.volume)
                    for _ in self.listebonus.keys():
                        self.listebonus[_].son.set_volume(self.volume)
                except:
                    pass

    def applicationbonusjoueur(self): # applique les effets des bonus sur le joueur
        self.joueur.taille=50
        self.joueur.vitesse=6
        if self.bonus.count('taille')<=1:
            self.joueur.taille-=10*(self.bonus.count('taille')-2)
        if self.bonus.count('vitesse')<=1:
            self.joueur.vitesse-=(self.bonus.count('vitesse')-2)

    def applicationbonusballes(self): # applique les effets des bonus sur la balle
        for _ in self.balles.keys():
            self.balles[_].degat=1
        for __ in self.balles.keys():
            self.balles[__].degat-=(self.bonus.count('degat')-2)
            self.balles[__].modifcouleur()

    def animation(self): # gere le deroulement de la partie
        clock.tick(60)
        self.tempsdejeu.ajout()
        for event in pygame.event.get():
            if event.type==KEYDOWN:
                if(event.key==K_SPACE)or(event.key==K_RETURN):
                    self.pause=True
            self.verifquit(event)
        if(self.pause==False)and(self.continuer==True):
            if (pygame.key.get_pressed()[K_LEFT])or(pygame.key.get_pressed()[K_a]): # deplacements du joueur
                self.joueur.gauche()
            if (pygame.key.get_pressed()[K_RIGHT])or(pygame.key.get_pressed()[K_d]):
                self.joueur.droite()
            self.deplacementballes() # deplacement des balles
            self.renvoi() # collisions balle/brique et balle/joueur
            for _ in self.listebonus.keys():
                self.listebonus[_].deplacement() # deplacement des bonus
            if (self.stage==19 and self.illimite==False)or(self.niveau.numero==-19): # cas specifique au stage du boss
                effacerennemi=[]
                for _ in self.niveau.contenu.keys(): # deplacements de tous les ennemis
                    if _ =='0':
                        self.niveau.contenu[_].deplacement(self.directionboss) # deplacement du boss
                        self.niveau.contenu[_].cooldown-=1
                    else:
                        self.niveau.contenu[_].deplacement() # deplacement des ennemis lambdas
                        if self.niveau.contenu[_].limite():
                            effacerennemi.append(_)
                if self.niveau.contenu['0'].vie>0:
                    self.niveau.contenu['0'].afficher()
                else:
                    for _ in self.niveau.contenu.keys(): # si le boss n'a plus de vie, tous les ennemis lambdas disparaissent
                        if _!='0' and (_ not in effacerennemi):
                            effacerennemi.append(_)
                    pygame.mixer.music.set_volume(0) # et la musique s'arrete
                    pygame.mixer.music.stop()
                for _ in effacerennemi: # suppression des ennemis lambdas
                    self.niveau.contenu[_].effacerbrique()
                    del self.niveau.contenu[_]
                if self.niveau.contenu['0'].vie>0:
                    if self.niveau.contenu['0'].cooldown==0: # creation de briques ennemis en fonction des caracteristiques actuelles du boss
                        directionennemi=randrange(4)+1
                        largeurennemi=self.niveau.contenu['0'].largeur
                        hauteurennemi=10
                        if directionennemi==2 or directionennemi==4:
                            largeurennemi=10
                            hauteurennemi=self.niveau.contenu['0'].largeur
                        self.niveau.contenu[str(self.niveau.i+1)]=Ennemi(self.niveau.contenu['0'].x-10*int(directionennemi==4)+self.niveau.contenu['0'].largeur*int(directionennemi==2),self.niveau.contenu['0'].y-(self.niveau.contenu['0'].largeur//2-self.niveau.contenu['0'].hauteur//2)*int((directionennemi==2)or(directionennemi==4)),randrange(self.niveau.contenu['0'].vie-int(self.niveau.contenu['0'].vie>1))+1,largeurennemi,hauteurennemi,directionennemi,3-2*(self.niveau.contenu['0'].vie//self.niveau.contenu['0'].viemax),self.couleurfond,self.imagefond,self.typefond)
                        self.niveau.contenu['0'].cooldown=10*self.niveau.contenu['0'].vie # redefinie le temps entre chaque creation de brique
                        if self.niveau.contenu['0'].cooldown>200:
                            self.niveau.contenu['0'].cooldown=200
                        self.niveau.i+=1
            self.bonusinbrique() # verifie si les bonus sont dans une brique
            self.bonusinjoueur() # idem mais avec le joueur
            self.effacerbonus()
            for _ in self.balleseff: # efface l'ensemble des balles ayant atteint la limite de l'ecran
                del self.balles[_]
            self.balleseff=[]
        elif(self.pause==True): # met le jeu en pause
            self.lancement()
        self.suite() # mal de tete


    def suite(self):
        if((len(self.niveau.contenu)==0 or len(self.balles)==0)or(((self.illimite==False and self.stage==19)or(self.niveau.numero==-19))and self.niveau.contenu['0'].vie<=0)or(self.duel==True))and(self.continuer==True): # blablabla...
            if self.duel==False:
                self.enjeu=self.modifmusic=self.illimite
                self.effacerbonus()
                for _ in self.balles.keys():
                    self.balles[_].afficher() # reaffiche les balles pour que ce soit plus zoli
            if (len(self.balles)>0 or (self.duel==True))and(self.continuer==True):
                while pygame.mixer.get_busy(): # attend que tous les sons se terminent
                    clock.tick(60)
                    pass
                if self.niveau.numero!=-1:
                    if (self.stage==19 and self.illimite==False)or(self.niveau.numero==-19): # initialisation de la deuxieme partie du combat de boss
                        self.pause=True
                        if self.duel==False:
                            self.duel=True
                            self.niveau.contenu['0'].vie=1
                            self.niveau.contenu['0'].sprite()
                            self.lancement()
                            cooldowncine=0
                            self.pause=True
                            while (self.joueur.x not in range(self.niveau.contenu['0'].x-5,self.niveau.contenu['0'].x+5))and(self.continuer==True): # deplace le joueur pou qu'il soit en face du boss
                                clock.tick(60)
                                self.verifquit()
                                if self.joueur.x>self.niveau.contenu['0'].x:
                                    self.joueur.gauche()
                                else:
                                    self.joueur.droite()
                            if self.continuer==True:
                                self.joueur.ancienx=self.joueur.x
                                self.joueur.x=self.niveau.contenu['0'].x+(50-self.joueur.taille)//2
                                self.joueur.mouvement()
                                for _ in self.balles.keys():
                                    self.balles[_].ancienx=self.balles[_].x
                                    self.balles[_].ancieny=self.balles[_].y
                                    self.balles[_].effacer()
                            t=True
                            while t==self.continuer==True:
                                clock.tick(60)
                                self.verifquit()
                                t=False
                                for _ in self.balles.keys(): # deplace toutes les balles pour quelles aillent dans la "Balle Ultime"
                                    self.balles[_].ancienx,self.balles[_].ancieny=self.balles[_].x,self.balles[_].y
                                    if self.balles[_].x not in range(self.joueur.x+self.joueur.taille//2-10,self.joueur.x+self.joueur.taille//2+10):
                                        if self.balles[_].x<self.joueur.x+self.joueur.taille//2-5: # si elles sont a gauche, on augmente leur x
                                            if abs(self.balles[_].x-(self.joueur.x+self.joueur.taille//2-5))>=6+2*int(self.balles[_].accelerationx):
                                                self.balles[_].x+=6+2*int(self.balles[_].accelerationx) 
                                            else:
                                                self.balles[_].x+=abs(self.balles[_].x-(self.joueur.x+self.joueur.taille//2-5))
                                        else: # si elles sont a droite, on le diminue
                                            if abs(self.balles[_].x-(self.joueur.x+self.joueur.taille//2-5))>=6+2*int(self.balles[_].accelerationx):
                                                self.balles[_].x-=6+2*int(self.balles[_].accelerationx) 
                                            else:
                                                self.balles[_].x-=abs(self.balles[_].x-(self.joueur.x+self.joueur.taille//2-5))
                                    if self.balles[_].y not in range(self.joueur.y-35,self.joueur.y-20):
                                        if self.balles[_].y>self.joueur.y-20:
                                            self.balles[_].y-=6+2*int(self.balles[_].accelerationy) # si elles sont en dessous on diminue leur y
                                        else:
                                            self.balles[_].y+=6+2*int(self.balles[_].accelerationy) # sinon, on l'augmente
                                    if self.balles[_].x!=self.balles[_].ancienx or self.balles[_].y!=self.balles[_].ancieny: # verifie que toutes les balles sont immobiles
                                        self.balles[_].affeff()
                                        t=True
                                    if self.balles[_].ancienx in range(self.niveau.contenu['0'].x-10,self.niveau.contenu['0'].x+51):
                                        if self.balles[_].ancieny in range(self.niveau.contenu['0'].y-10,self.niveau.contenu['0'].y+11): # reaffiche le boss si une balle etait dedans
                                            self.niveau.contenu['0'].afficher()
                                    if self.balles[_].ancienx in range(self.joueur.x-10,self.joueur.x+self.joueur.taille+1):
                                        if self.balles[_].ancieny in range(self.joueur.y-10,self.joueur.y+11):
                                            self.joueur.mouvement()
                                    self.balles[_].balleintexte(self.joueur.score) # avec le score,
                                    if self.niveau.numero!=-19:
                                        self.balles[_].balleintexte(self.stageaffiche) # le numero du stage
                                        self.balles[_].balleintexte(self.joueur.vieaffichee) # et les vies aussi
                                cooldowncine+=5*int(cooldowncine<500)
                                if t==False:
                                    t=bool(cooldowncine<500) # veriife que la cinematique n'est pas terminee meme si les balles ne bougent plus
                                screen.fill((255,255,255),(self.joueur.x+self.joueur.taille//2-cooldowncine//20,self.joueur.y-cooldowncine//10-10,cooldowncine//10,cooldowncine//10)) # augmente la taille de la balle en fonction
                                pygame.display.update((self.joueur.x+self.joueur.taille//2-cooldowncine//20,self.joueur.y-cooldowncine//10-10,cooldowncine//10,cooldowncine//10)) # de l'avancement de la cinematique
                            effacer=[]
                            for _ in self.balles.keys():
                                effacer.append(_)
                            for _ in effacer:
                                del self.balles[_] # efface et supprime toutes les balles du joueur
                            self.lancement()
                            self.pause=True
                            y=self.joueur.y-60
                            while (y>=305)and(self.continuer==True): # deplace la "Balle Ultime" jusqu'aux coordonnees de "L'Affrontement Utlime"
                                clock.tick(15)
                                self.verifquit()
                                screen.fill((255,255,255),(self.joueur.x+self.joueur.taille//2-25,y,50,50))
                                if self.typefond==0:
                                    screen.fill(self.couleurfond,(self.joueur.x+self.joueur.taille//2-25,y+55,50,5))
                                else:
                                    screen.blit(self.imagefond.subsurface((self.joueur.x+self.joueur.taille//2-25,y+55,50,5)),(self.joueur.x+self.joueur.taille//2-25,y+55))
                                pygame.display.update([(self.joueur.x+self.joueur.taille//2-25,y,50,50),(self.joueur.x+self.joueur.taille//2-25,y+55,50,50)])
                                y-=5
                            if self.continuer==True:
                                pygame.mixer.music.set_volume(self.volume*int(self.soundon==True)) # relance la musique
                                self.volumemusique=self.volume
                                pygame.mixer.music.play()
                                self.niveau.contenu['0'].largeur=70
                                self.niveau.contenu['0'].vie=100
                                self.niveau.contenu['0'].couleur=(192,192,192)
                                self.niveau.contenu['0'].x-=10
                                self.niveau.contenu['0'].afficher() # le boss regroupe ses dernieres forces et...
                                pygame.time.wait(1200)
                                self.niveau.contenu['1']=Ennemi(self.niveau.contenu['0'].x,self.niveau.contenu['0'].y+65,20,70,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond) # BAM ! Creation de la brique pour le QTE 
                        if self.continuer==True:
                            Balle_Ultime=Balle(0,self.couleurfond,self.imagefond,self.typefond,50)
                            Balle_Ultime.x,Balle_Ultime.y=self.joueur.x+self.joueur.taille//2-25,310
                            Balle_Ultime.ancienx=self.joueur.x+self.joueur.taille//2-25
                            smashing=100
                            pygame.mixer.music.set_volume((1-(smashing/200))*self.volume*int(self.soundon==True))
                            self.volumemusique=(1-(smashing/200))*self.volume
                            cooldowntexte=0
                            Textesmash=Texte("Espace",taille=25,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                            Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                            while (200>smashing>0)and(self.continuer==True): # QTE numero 1
                                clock.tick(30)
                                self.tempsdejeu.ajout(0.5)
                                smashing-=0.2 # action du boss     
                                event=pygame.event.poll()
                                self.verifquit(event)
                                if event.type==KEYDOWN:
                                    if event.key==K_SPACE: # action du joueur
                                        smashing+=2
                                cooldowntexte+=1
                                if cooldowntexte==15: # affiche le texte en plus ou moins grand pour donner l'impression d'un "martellage"
                                    Textesmash=Texte("Espace",taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                    Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                                elif cooldowntexte==30:
                                    Textesmash.effacer()
                                    Textesmash=Texte("Espace",taille=25,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                    Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                                    cooldowntexte=0
                                self.niveau.contenu['1'].effacerbrique()
                                self.niveau.contenu['1'].y=350-smashing//2
                                self.niveau.contenu['1'].vie=40-smashing//5 # efface, repositionne et reattribue la vie a la brique ennemi en fonction de l'avancee du QTE
                                Balle_Ultime.ancieny=Balle_Ultime.y
                                Balle_Ultime.y=360-smashing//2
                                Balle_Ultime.affeff() # efface et repositionne la "Balle Ultime" en fonction de l'avancee du QTE
                                self.niveau.contenu['1'].sprite()  
                                pygame.mixer.music.set_volume((1-(smashing/400))*self.volume*int(self.soundon==True)) # met a jour le volume de la musique
                                self.volumemusique=(1-(smashing/400))*self.volume
                        if self.continuer==True:
                            if(smashing>=200): # en cas de victoire du joueur
                                self.duel=False
                                Textesmash.effacer()
                                self.joueur.points+=4000
                                self.pointslimites+=4000
                                if self.pointslimites>=100000 and self.illimite==False:
                                    self.joueur.vie+=int(self.hardcore==False)
                                    self.joueur.vieaffichee.texte='Vie(s) : '+str(self.joueur.vie)
                                    self.joueur.vieaffichee.afficher()
                                    self.pointslimites-=100000
                                self.joueur.score.texte='Score : '+str(self.joueur.points)
                                self.joueur.score.afficher()
                                sonbrique.set_volume(self.volume*int(self.soundon==True))
                                sonbrique.play()
                                pygame.time.wait(1000)
                                while Balle_Ultime.y>self.niveau.contenu['0'].y+10: # positionne la "Balle Ultime" juste en dessou du boss
                                    clock.tick(30)
                                    self.verifquit()
                                    Balle_Ultime.ancieny=Balle_Ultime.y
                                    Balle_Ultime.y-=1
                                    Balle_Ultime.affeff()
                                smashing=0
                                del self.niveau.contenu['1']
                                cooldowntexte=0
                                Textesmash=Texte("Espace",taille=25,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                                while(100>smashing)and(self.continuer==True): # QTE numero 2
                                    clock.tick(30)
                                    self.tempsdejeu.ajout(0.5)
                                    cooldowntexte+=1
                                    if cooldowntexte==15:
                                        Textesmash=Texte("Espace",taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                        Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                                    elif cooldowntexte==30:
                                        Textesmash.effacer()
                                        Textesmash=Texte("Espace",taille=25,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                        Textesmash.centrer(Balle_Ultime.x+200*(1-2*int(Balle_Ultime.x>340)),310)
                                        cooldowntexte=0     
                                    event=pygame.event.poll()
                                    self.verifquit(event)
                                    if event.type==KEYDOWN:
                                        if event.key==K_SPACE:
                                            smashing+=1 # action du joueur
                                            self.joueur.points+=100
                                            self.pointslimites+=100
                                            if self.pointslimites>=100000 and self.illimite==False:
                                                self.joueur.vie+=int(self.hardcore==False)
                                                self.joueur.vieaffichee.texte='Vie(s) : '+str(self.joueur.vie)
                                                self.joueur.vieaffichee.afficher()
                                                self.pointslimites-=100000
                                            self.joueur.score.texte='Score : '+str(self.joueur.points)
                                            self.joueur.score.afficher()
                                            sonbrique.set_volume(self.volume*int(self.soundon==True))
                                            sonbrique.play()
                                    self.niveau.contenu['0'].effacerbrique()
                                    self.niveau.contenu['0'].y=235-smashing
                                    self.niveau.contenu['0'].vie=(100-smashing)//10+1 # efface, repositionne et reattribue la vie du boss en fonction de l'avancee du QTE
                                    Balle_Ultime.ancieny=Balle_Ultime.y
                                    Balle_Ultime.y=245-smashing
                                    Balle_Ultime.affeff() # efface et repositionne la "Balle Ultime" en fonction de l'avancee du QTE
                                    self.niveau.contenu['0'].sprite()  
                                    pygame.mixer.music.set_volume((0.5-(smashing/200))*self.volume*int(self.soundon==True)) # met a jour le volume de la musique
                                    self.volumemusique=(0.5-(smashing/200))*self.volume
                                if self.continuer==True:
                                    Textesmash.effacer()
                                    del Textesmash
                                    while(Balle_Ultime.y>5)and(self.continuer==True): # fait remonter la "Balle Ultime" jusque hors de l'ecran
                                        clock.tick(60)
                                        self.verifquit()
                                        Balle_Ultime.ancieny=Balle_Ultime.y
                                        Balle_Ultime.y-=5
                                        if self.niveau.numero!=-19:
                                            self.stageaffiche.afficher()
                                        self.joueur.score.afficher()
                                        if self.illimite==False:
                                            self.joueur.vieaffichee.afficher()
                                        Balle_Ultime.affeff()
                                        self.niveau.contenu['0'].afficher()
                                if self.continuer==True:
                                    Balle_Ultime.ancieny=Balle_Ultime.y
                                    Balle_Ultime.effacer() # efface la "Balle Ultime"
                                    if self.niveau.numero!=-19:
                                        self.stageaffiche.afficher()
                                    self.joueur.score.afficher()
                                    if self.illimite==False:
                                        self.joueur.vieaffichee.afficher()
                                    pygame.time.wait(1000)
                                    listepixels=[]
                                    for x in range(self.niveau.contenu['0'].x,self.niveau.contenu['0'].x+70,2): # recupere l'ensemble des coordonnees des pixels du boss
                                        for y in range(self.niveau.contenu['0'].y,self.niveau.contenu['0'].y+10,2):
                                            listepixels.append((x,y))
                                    t=1
                                    while(listepixels!=[])and(self.continuer==True):
                                        clock.tick(int(t))
                                        pygame.event.pump()
                                        self.verifquit()
                                        pixel=listepixels[randrange(len(listepixels))]
                                        listepixels.remove(pixel)
                                        if self.typefond==0: # fait disparaitre chaque pixel du boss de maniere aleatoire
                                            screen.fill(self.couleurfond,(pixel[0],pixel[1],2,2))
                                        else:
                                            screen.blit(self.imagefond.subsurface(pixel[0],pixel[1],2,2),(pixel[0],pixel[1]))
                                        pygame.display.update((pixel[0],pixel[1],2,2))
                                        sonmort.set_volume(self.volume*int(self.soundon==True))
                                        sonmort.play()
                                        t+=60/175
                                    del self.niveau.contenu['0'] # le boss est mort... vive le boss !
                                    while pygame.mixer.get_busy(): # attend que tous les sons se terminent
                                        clock.tick(60)
                                        pass
                    if self.duel==False:
                        if self.mort<=1: # si le joueur n'a pas perdu trop de vie sur le niveau
                            self.joueur.points+=(10000//(1+int(self.mort==1))) # il gagne des points bonus
                            self.pointslimites+=(10000//(1+int(self.mort==1)))
                            if self.pointslimites>=100000 and self.illimite==False:
                                self.joueur.vie+=int(self.hardcore==False)
                                self.joueur.vieaffichee=Texte("Vie(s) : "+str(self.joueur.vie),x=250,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                self.joueur.vieaffichee.afficher()
                                self.pointslimites-=100000
                            self.joueur.score.texte="Score : "+str(self.joueur.points)
                            self.joueur.score.afficher()
                            self.joueur.nombreballe+=int(not(self.hardcore)) # et une balle !
                        if self.niveau.numero<0: # arrete le jeu si c'est en mode Chargement de Niveau
                            self.lancement()
                            self.continuer=False
                        if self.illimite==False:
                            if self.stage not in [6,8,9,11,14,15]: # ajoute le stage dans le dossier 'stageperso' pour qu'il puisse ensuite etre directement charge
                                listeniveaux=os.listdir("stageperso")
                                if self.nomniveau+'.txt' not in listeniveaux:
                                    fichier=open('stageperso/'+self.nomniveau+'.txt','w')
                                    if self.stage!=19:
                                        for __ in self.niveau.liste:
                                            fichier.write(str(__)+',')
                                    else:
                                        fichier.write("BOSS,")
                                    fichier.close()
                        self.stage+=1
                        if self.illimite==False:
                            if self.stage==20: # essaye de charger le fond etoile pour le dernier stage du jeu
                                try:
                                    self.imagefond2=self.imagefond
                                    self.imagefond=pygame.image.load('images/fonds/stars.png')
                                    self.typefond2=self.typefond
                                    self.typefond=1
                                except:
                                    pass
                        self.nombrestages+=1
                        if self.nombrestages==5: # tous les 5 stages, le joueur gagne une vie
                            self.joueur.vie+=int(self.hardcore==False)
                            self.nombrestages=0
                        self.lancement()
                        if self.continuer==True:
                            if self.illimite==True or (self.illimite==False and self.stage<=20):
                                if self.stage==20 and self.illimite==False:
                                    self.joueur.typefond=self.joueur.score.typefond=self.typefond # modifie, si besoin, le type de fond et l'image du fond pour le dernier stage
                                    self.joueur.imagefond=self.joueur.score.imagefond=self.imagefond
                                elif self.stage>20 and self.illimite==False:
                                    self.typefond=self.joueur.typefond=self.joueur.score.typefond=self.typefond2 # remet le type de fond et l'image de fond a leurs valeurs d'origine
                                    self.imagefond=self.joueur.imagefond=self.joueur.score.imagefond=self.imagefond2
                                self.chargerniveau()
                            else: # le jeu est (presque) termine !
                                self.joueur.points+=10000*self.joueur.vie
                                self.joueur.points-=1000000*self.nombretriche #  tricher... c'est mal !...
                                if self.joueur.points<0:
                                    self.joueur.points=0
                                self.joueur.score.texte="Score : "+str(self.joueur.points)
                                self.joueur.score.afficher()
                                for _ in self.balles.keys(): # pour faire zoli
                                    self.balles[_].afficher()
                                    self.balles[_].ancienx=self.balles[_].x
                                    self.balles[_].ancieny=self.balles[_].y
                                self.joueur.mouvement() # idem
                                self.joueur.ancienx=self.joueur.x
                                if self.continuer==True:
                                    for t in range(51): # rend de plus en plus transparent ce qu'il y a a l'ecran
                                        self.verifquit()
                                        self.joueur.score.couleur2=(self.joueur.score.couleur2[0],self.joueur.score.couleur2[1],self.joueur.score.couleur2[2],255-5*t-5)
                                        self.joueur.vieaffichee.couleur2=(self.joueur.vieaffichee.couleur2[0],self.joueur.vieaffichee.couleur2[1],self.joueur.vieaffichee.couleur2[2],255-5*t-5)
                                        self.stageaffiche.couleur2=(self.stageaffiche.couleur2[0],self.stageaffiche.couleur2[1],self.stageaffiche.couleur2[2],255-5*t-5)
                                        self.joueur.couleur=(self.joueur.couleur[0],self.joueur.couleur[1],self.joueur.couleur[2],255-5*t-5)
                                        self.joueur.score.afficher()
                                        self.joueur.vieaffichee.afficher()
                                        self.stageaffiche.afficher()
                                        for _ in self.balles.keys():
                                            self.balles[_].couleur=(self.balles[_].couleur[0],self.balles[_].couleur[1],self.balles[_].couleur[2],255-5*t-5)
                                            self.balles[_].effacer()
                                            self.balles[_].afficher()
                                        self.joueur.mouvement()
                                        pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                    prologue=Paragraphe(["Once upon a time, an Evil Being from a","forgotten past, came back to life."," "," ","For the first time, Mankind,","gathered around a Legendary Hero,","was bound to strive for one's freedom..."],x=50,y=100,taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                    epilogue=Paragraphe(["However, against the Evil Being's","Almighty power, the Legendary Hero","could not resist...", " ","And soon, the world was doomed by the","dreadful, atrocious and frightful..."," "," ","Please, enter your name here : "],x=50,y=80,taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                    for t in range(51): # fait apparaitre le prologue
                                        self.verifquit()
                                        prologue.modifcouleur(couleur=(255,255,255,t*5+5))
                                        prologue.afficherlignes()
                                        pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                    self.narration=True
                                    self.lancement()
                                if self.continuer==True:
                                    for t in range(51): # fait disparaitre le prologue
                                        self.verifquit()
                                        prologue.modifcouleur(couleur=(255,255,255,255-5*t-5))
                                        prologue.afficherlignes()
                                        pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                    for t in range(51):# fait apparaitre l'epilogue
                                        self.verifquit()
                                        epilogue.modifcouleur(couleur=(255,255,255,t*5+5))
                                        epilogue.afficherlignes()
                                        pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                    self.entrernomjoueur=True
                                    self.champsnom=Champs(320,380,3,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                                    while self.entrernomjoueur==True and self.continuer==True: # le joueur est invite a rentrer son nom
                                        clock.tick(60)
                                        event=pygame.event.poll()
                                        self.verifquit(event)
                                        self.champsnom.modiftexte('lettresmaj',event)
                                        if pygame.key.get_pressed()[K_RETURN]:
                                            if len(self.champsnom.texte)==3:
                                                self.joueur.nom=self.champsnom.texte
                                                self.entrernomjoueur=False
                                    if self.continuer==True:
                                        for t in range(51): # fait disparaitre l'epilogue
                                            self.verifquit()
                                            epilogue.modifcouleur(couleur=(255,255,255,255-t*5-5))
                                            self.champsnom.texteaffiche.couleur2=(self.champsnom.texteaffiche.couleur2[0],self.champsnom.texteaffiche.couleur2[1],self.champsnom.texteaffiche.couleur2[2],255-5*t-5)
                                            epilogue.afficherlignes()
                                            self.champsnom.texteaffiche.afficher()
                                            pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                        if self.hardcore==True:
                                            self.joueur.nom='*'+self.joueur.nom+'*' # cette ligne ne sera jamais lue !
                                        if self.continuer==True:
                                            textefin=Texte("Fin",centre=True,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond) # Fin
                                            textefin.afficher()
                                            self.narration=True
                                            self.lancement()
                                            if self.continuer==True:
                                                for t in range(51): # fait disparaitre "Fin"
                                                    self.verifquit()
                                                    textefin.couleur2=(textefin.couleur2[0],textefin.couleur2[1],textefin.couleur2[2],255-5*t-5)
                                                    textefin.afficher()
                                                    pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                                            self.credits(True) # les credits ! Snif... HAHA !
                                            if self.continuer==True:
                                                self.chargerhighscore("Hall of Fame")
                                                self.modifhighscore("Hall of Fame")
                                                if self.record!=-1:
                                                    self.afficherhighscore() # Bienvenue dans le... Hall of Fame !
                                                    self.lancement()
                                try:
                                    fichier=open('images/fonds/mercidenepaseffacercefichier.txt','r') # parce que le joueur a tenu jusqu'au bout, cadeau !
                                    liste=[]
                                    for _ in fichier.readlines():
                                        if _[:-1]!='' and _[:-1]!=' ':
                                            liste.append(_[:-1])
                                    fichier.close()
                                    if 'stars' not in liste:
                                        liste.append('stars')
                                        fichier= open('images/fonds/mercidenepaseffacercefichier.txt','w')
                                        for _ in liste:
                                            fichier.write(_+'\n')
                                        fichier.close()
                                except:
                                    pass
                                self.continuer=False
                else:
                    if self.niveau.numero<0:
                        self.lancement()
                        self.continuer=False
            if len(self.balles)==0 and self.continuer==True: # boooouuuuh !!!
                self.joueur.vie-=int(self.illimite==False)
                if self.duel==True and self.joueur.vie>=0:
                    while Balle_Ultime.y<self.joueur.y-50: # retour a l'envoyeur
                        clock.tick(60)
                        Balle_Ultime.ancieny=Balle_Ultime.y
                        Balle_Ultime.y+=5
                        Balle_Ultime.affeff()
                    if self.volume!=0 and self.soundon==True:
                        self.joueur.sound1.set_volume(self.volume)
                    self.joueur.sound1.play()
                    if self.niveau.numero!=-19:
                        self.joueur.vieaffichee.texte="Vie(s) : "+str(self.joueur.vie)
                        self.joueur.vieaffichee.afficher()
                    volume=1
                    if self.joueur.vie>0:
                        while Balle_Ultime.y>310: # remet la "Balle Ultime" en place
                            clock.tick(60)
                            Balle_Ultime.ancieny=Balle_Ultime.y
                            Balle_Ultime.y-=5
                            if Balle_Ultime.y<360:
                                clock.tick(15)
                                self.niveau.contenu['1'].effacerbrique()
                                self.niveau.contenu['1'].y-=5
                                volume-=0.045
                                self.niveau.contenu['1'].afficher()
                                pygame.mixer.music.set_volume(volume*self.volume*int(self.soundon==True))
                                self.volumemusique=volume*self.volume
                            Balle_Ultime.affeff()
                            self.joueur.mouvement()
                    else: # si pres...
                        self.duel=False
                if self.duel==False:
                    if len(self.joueur.listebonus)>0:
                        bonus=randrange(len(self.joueur.listebonus)) # on choisi un bonus au hasard
                        self.bonus.append(self.joueur.listebonus[bonus]) # on remet le bonus en jeu. Literallement.
                        del self.joueur.listebonus[bonus] # on enleve le bonus du joueur
                    self.mort+=int(self.illimite==False)
                    if self.illimite==False:
                        self.joueur.vieaffichee.texte="Vie(s) : "+str(self.joueur.vie)
                        self.joueur.vieaffichee.afficher()
                    self.joueur.nombreballe-=int(self.joueur.nombreballe>1)*int(self.illimite==False)
                    self.calculballes()
                    if self.typefond==0:
                        screen.fill(self.couleurfond,(315,445,10,10))
                    else:
                        screen.blit(self.imagefond.subsurface(315,445,10,10),(315,445))
                    pygame.display.update((315,445,10,10))
                    if self.joueur.vie==0:
                        self.enjeu=self.modifmusic=False
                        pygame.mixer.music.stop()
                        pygame.mixer.stop()
                        screen.fill((0,0,0))
                        pygame.display.flip()
                        if self.hardcore==False:
                            self.pause=True
                            Texte("Continuer ?",y=-50,taille=50,centre=True).afficher()
                            while(self.countdown.secondes>1)and(self.recommencer==False)and(self.continuer==True): # tic tac... tic tac...
                                clock.tick(60*(1+3*self.getcontrol()))
                                self.countdown.decompte()
                                pygame.event.pump()
                                self.verifquit()
                                if(pygame.key.get_pressed()[K_SPACE])or(pygame.key.get_pressed()[K_RETURN]):
                                    self.recommencer=True
                        if self.recommencer==False and self.continuer==True:
                            self.gameoversound.set_volume(self.volume*int(self.soundon==True))
                            self.gameoversound.play()                                
                            screen.fill((0,0,0))
                            pygame.display.flip()
                            Texte("GAME OVER",taille=100,centre=True).afficher() # doooooonng
                            self.lancement()
                            if self.nombretriche>=0:
                                self.joueur.points-=1000000*self.nombretriche # tricher... c'est mal !...
                            else:
                                self.joueur.points+=10000*(self.stage-1)
                            if self.joueur.points<0:
                                self.joueur.points=0
                            if self.continuer==True:
                                self.chargerhighscore("Hall of Shame")
                                self.modifhighscore("Hall of Shame")
                                if self.record!=-1:
                                    self.listenoms[self.record]=''
                                    self.afficherhighscore()
                                    champsnom=Champs(-270,55+52*(self.record-4),3,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,couleur=(255,0,0,255),textecentre=True)
                                    entrernomjoueur=True
                                    while entrernomjoueur==True and self.continuer==True: # le joueur est invite a rentrer son nom
                                        clock.tick(60)
                                        event=pygame.event.poll()
                                        self.verifquit(event)
                                        champsnom.modiftexte('lettresmaj',event)
                                        if pygame.key.get_pressed()[K_RETURN]:
                                            if len(champsnom.texte)==3:
                                                self.joueur.nom='*'*int(self.hardcore==True)+champsnom.texte+'*'*int(self.hardcore==True)
                                                self.listenoms[self.record]=self.joueur.nom
                                                entrernomjoueur=False
                                                self.sauvegarderhighscore("Hall of Shame") # Bienvenue... ?
                                                if '*' in self.joueur.nom:
                                                    self.afficherhighscore()
                                                    self.lancement()
                                    if self.continuer==False:
                                        self.listenoms.pop(self.record) # retire le joueur des highscores si il quitte avant de valider son nom
                                        self.listescores.pop(self.record)
                                        self.listetemps.pop(self.record)
                                        self.sauvegarderhighscore("Hall of Shame")
                            self.hardcore=False
                            self.continuer=False
                        else:
                            if self.continuer==True:
                                self.bonus=['taille','taille','vitesse','vitesse','degat','degat'] # on reinitialise les bonus,
                                self.listebonus={}
                                self.joueur=Joueur(self.couleurfond,self.imagefond,self.typefond) # le joueur
                                self.chargerniveau() # et le niveau
                    else:
                        self.modifmusic=False
                        self.lancement()
                        if self.continuer==True:
                            if self.typefond==0:
                                screen.fill(self.couleurfond,(self.joueur.x,self.joueur.y,self.joueur.taille,10))
                            else:
                                screen.blit(self.imagefond.subsurface(self.joueur.x,self.joueur.y,self.joueur.taille,10),(self.joueur.x,self.joueur.y))
                            pygame.display.update((self.joueur.x,self.joueur.y,self.joueur.taille,10))
                            self.retourniveau() # on repart a l'assaut !
                            self.enjeu=True
                            self.lancement()
                            self.modifmusic=True
                else:
                    self.suite() # fiou... C'est fini !


    def renvoi(self): # gere les collisions entre les balles et les briques, les balles et le joueur et les balles et l'ecran
        self.collisionbrique()
        self.collisionjoueur()
        for _ in self.balles.keys():
            if(self.balles[_].x<=0)or(self.balles[_].x>=630):  # modifie la trajectoire si la balle tape contre l'un des deux cotes de l'ecran
                self.balles[_].direction=not(self.balles[_].direction)
                if self.balles[_].x<=0:
                    self.balles[_].x=0
                else:
                    self.balles[_].x=630
            if(self.balles[_].y<=0): # modifie la trajectoire si la balle tape contre le haut de l'ecran
                self.balles[_].sens=not(self.balles[_].sens)
                self.balles[_].y=0
            if self.balles[_].brique in self.niveau.contenu.keys(): # "libere" la balle pour qu'elle puisse a nouveau toucher une brique (permer d'eviter qu'elle ne touche une brique deux fois de suite)
                self.balles[_].coordxcoll,self.balles[_].coordycoll=self.niveau.contenu[self.balles[_].brique].x,self.niveau.contenu[self.balles[_].brique].y
                self.balles[_].coordlargeur,self.balles[_].coordhauteur=self.niveau.contenu[self.balles[_].brique].largeur,self.niveau.contenu[self.balles[_].brique].hauteur
                if ((self.balles[_].x-self.balles[_].coordxcoll)**2+(self.balles[_].y-self.balles[_].coordycoll)**2>6800)or(self.balles[_].x not in range(self.balles[_].coordxcoll-10,self.balles[_].coordxcoll+self.balles[_].coordlargeur+1))or(self.balles[_].y not in range(self.balles[_].coordycoll-10,self.balles[_].coordycoll+self.balles[_].coordhauteur+1)):
                    self.balles[_].touche=False
                    self.balles[_].brique=''
            else:
                self.balles[_].touche=False
                self.balles[_].brique=''
                

    def collisionbrique(self): # gere les collisions avec les briques
        briquesaeffacer=[]
        for _ in self.balles.keys(): # pour chaque balle
            for __ in self.niveau.contenu.keys(): # pour chaque brique
                if (self.balles[_].x-self.niveau.contenu[__].x)**2+(self.balles[_].y-self.niveau.contenu[__].y)**2<=5000: # on regarde d'abord si la balle n'est pas top loin
                    if self.niveau.contenu[__].vie>0: # et si la brique a encore de la vie
                        if self.balles[_].x in range(self.niveau.contenu[__].x-10,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur+1):
                            if self.balles[_].y in range(self.niveau.contenu[__].y-10,self.niveau.contenu[__].y+self.niveau.contenu[__].hauteur+1): # est-ce que la balle est dans la brique                                           
                                if self.balles[_].touche==False: # est-ce qu'elle a deja touchee une brique
                                    self.balles[_].brique=__
                                    self.balles[_].coordxcoll,self.balles[_].coordycoll=self.niveau.contenu[__].x,self.niveau.contenu[__].y
                                    self.balles[_].coordlargeur,self.balles[_].coordhauteur=self.niveau.contenu[__].largeur,self.niveau.contenu[__].hauteur
                                    self.balles[_].touche=True
                                    self.balles[_].collision=True # on recupere la brique touchee
                                    if self.balles[_].degat<=self.niveau.contenu[__].vie: # si la brique a plus de vie que de degats infliges, les points sont en fonctions des degats
                                        for d in range(self.balles[_].degat):
                                            self.joueur.points+=100
                                            self.pointslimites+=100
                                    else:
                                        for d in range(self.niveau.contenu[__].vie): # sinon c'est en fonction des points de vie de la brique
                                            self.joueur.points+=100
                                            self.pointslimites+=100
                                    if self.pointslimites>=100000 and self.illimite==False:
                                        self.joueur.vie+=int(self.hardcore==False)
                                        self.joueur.vieaffichee.texte='Vie(s) : '+str(self.joueur.vie)
                                        self.joueur.vieaffichee.afficher()
                                        self.pointslimites-=100000
                                    self.joueur.score.texte='Score : '+str(self.joueur.points)
                                    self.joueur.score.afficher()
                                    self.niveau.contenu[__].vie-=self.balles[_].degat
                                    if (self.stage==19 and self.illimite==False)or(self.niveau.numero==-19): # traitement special pour le boss
                                        if __=='0':
                                            pygame.mixer.music.set_volume((self.niveau.contenu['0'].vie/self.niveau.contenu['0'].viemax)*self.volume*int(self.soundon==True)) # mise a jour du volume de la musique
                                            self.volumemusique=(self.niveau.contenu['0'].vie/self.niveau.contenu['0'].viemax)*self.volume
                                            self.niveau.contenu['0'].effacerbrique()
                                            tailleavant=self.niveau.contenu['0'].largeur
                                            if self.niveau.contenu['0'].cooldown>10*self.niveau.contenu['0'].vie: # mise a jour du cooldown entre chaque creation de brique
                                                self.niveau.contenu['0'].cooldown=10*self.niveau.contenu['0'].vie
                                            if self.niveau.contenu['0'].vie/self.niveau.contenu['0'].viemax<=2/3: # le boss est blesse
                                                self.niveau.contenu['0'].largeur=60
                                                self.niveau.contenu['0'].x+=(tailleavant-self.niveau.contenu['0'].largeur)
                                                self.niveau.contenu['0'].vitesse=8
                                                tailleavant=self.niveau.contenu['0'].largeur
                                            if self.niveau.contenu['0'].vie/self.niveau.contenu['0'].viemax<=1/3: # le boss est mourrant
                                                self.niveau.contenu['0'].largeur=50
                                                self.niveau.contenu['0'].x+=(tailleavant-self.niveau.contenu['0'].largeur)
                                                self.niveau.contenu['0'].vitesse=6
                                            self.niveau.contenu['0'].sprite()
                                    self.niveau.contenu[__].sound.stop() # evite une cacophonie
                                    self.niveau.contenu[__].sound.set_volume(self.volume*int(self.soundon==True))
                                    self.niveau.contenu[__].sound.play()
                                    self.balles[_].accelerationx+=0.1*int(self.balles[_].accelerationx<=1.9)
                                    self.balles[_].accelerationy+=0.1*int(self.balles[_].accelerationy<=1.9)
                                    self.balles[_].ancienx,self.balles[_].ancieny=self.balles[_].x,self.balles[_].y
                                    if((self.balles[_].x in range(self.niveau.contenu[__].x-10,self.niveau.contenu[__].x))and(self.balles[_].direction==1))or((self.balles[_].x in range(self.niveau.contenu[__].x+self.niveau.contenu[__].largeur-5,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur+1))and(self.balles[_].direction==0)):
                                        self.balles[_].sens=not(self.balles[_].sens)
                                    elif self.balles[_].x in range(self.niveau.contenu[__].x,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur-5):
                                        self.balles[_].sens=not(self.balles[_].sens)
                                    elif(self.balles[_].x in range(self.niveau.contenu[__].x-10,self.niveau.contenu[__].x))and(self.balles[_].direction==0):
                                        self.balles[_].direction=1
                                    elif(self.balles[_].x in range(self.niveau.contenu[__].x+self.niveau.contenu[__].largeur-5,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur+1))and(self.balles[_].direction==1):
                                        self.balles[_].direction=0
                                    self.balles[_].affeff() # modifications de la trajectoire de la balle
                                    if __ not in briquesaeffacer:
                                        if (((self.stage==19)and(self.illimite==False))or(self.niveau.numero==-19)) and __=='0':
                                            pass
                                        else:
                                            briquesaeffacer.append(__) # ajout de la brique dans les briques touchees
        for _ in briquesaeffacer:
            self.niveau.contenu[_].sprite() # on change la couleur de la brique
            if self.niveau.contenu[_].vie<=0: # on efface la brique
                if self.niveau.contenu[_].bonus==True:
                    if len(self.bonus)>0 and self.hardcore==False:
                        self.listebonus[_]=Bonus(self.niveau.contenu[_].x,self.niveau.contenu[_].y,self.bonus[randrange(len(self.bonus))],couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond)
                del self.niveau.contenu[_]

    def collisionjoueur(self): # gere les collisions avec le joueur
        n=0
        son1=son2=son3=son4=False
        for _ in self.balles.keys(): # pour toutes les balles
            if((self.balles[_].x-self.joueur.x)**2+(self.balles[_].y-self.joueur.y)**2<=(self.joueur.taille**2+10**2)): # on verifie que la balle est assez proche du joueur
                if self.balles[_].sens==0: # et qu'elle va vers le bas
                    if (self.balles[_].collision==False and n==0)or(self.balles[_].collision==True): # tant qu'une balle n'a pas rencontre une brique, elle se trouve au meme endroit que les autres. Cette ligne permet de limiter le nombre de calculs.
                        if self.balles[_].x in range(self.joueur.x-8,self.joueur.x+self.joueur.taille-1):
                            if self.balles[_].y in range(self.joueur.y-10,self.joueur.y+6): # on verifie que la balle se trouve dans le joueur
                                n+=int(self.balles[_].collision==False)
                                if(self.balles[_].ancienx not in range(self.joueur.x-10,self.joueur.x+self.joueur.taille+1))or(self.balles[_].ancieny not in range(self.joueur.y-10,self.joueur.y+6)): # et qu'elle n'y etait pas avant
                                    self.balles[_].sens=1
                                    self.balles[_].accelerationx,self.balles[_].accelerationy=0,0
                                    if(self.balles[_].x+self.balles[_].cote in range(self.joueur.x+7*self.joueur.taille//20,self.joueur.x+13*self.joueur.taille//20+1)): # zone centrale
                                        if son1==False:
                                            self.joueur.sound1.set_volume(self.volume*int(self.soundon==True))
                                            self.joueur.sound1.play()
                                            son1=True
                                        self.balles[_].accelerationx=0
                                        self.balles[_].accelerationy=1
                                    elif(self.balles[_].x+self.balles[_].cote in range(self.joueur.x+self.joueur.taille//5,self.joueur.x+4*self.joueur.taille//5+1)): # zone peripherique
                                        if son2==False:
                                            self.joueur.sound1.set_volume(self.volume*int(self.soundon==True))
                                            self.joueur.sound1.play()
                                            self.joueur.sound1.fadeout(600)
                                            son2=True
                                        self.balles[_].accelerationy=1
                                        self.balles[_].accelerationx=1
                                    elif(self.balles[_].x+self.balles[_].cote in range(self.joueur.x+self.joueur.taille//12,self.joueur.x+11*self.joueur.taille//12+1)): # zone encore plus peripherique
                                        if son3==False:
                                            self.joueur.sound1.set_volume(self.volume*int(self.soundon==True))
                                            self.joueur.sound1.play()
                                            self.joueur.sound1.fadeout(300)
                                            son3=True
                                        self.balles[_].accelerationx=1
                                        self.balles[_].accelerationy=-1
                                    else: # zone externe
                                        if (self.balles[_].x<self.joueur.x and self.balles[_].direction==0)or(self.balles[_].x>self.joueur.x and self.balles[_].direction==1): # si la balle arrive par la droite et touche le cote droit du joueur et inversement
                                            if son4==False:
                                                self.joueur.sound1.set_volume(self.volume*int(self.soundon==True))
                                                self.joueur.sound1.play()
                                                self.joueur.sound1.fadeout(150)
                                                son4=True
                                            self.balles[_].accelerationy=0
                                            self.balles[_].accelerationx=1
                                            self.balles[_].direction=not(self.balles[_].direction)
                                        else:
                                            if son3==False:
                                                self.joueur.sound1.set_volume(self.volume*int(self.soundon==True))
                                                self.joueur.sound1.play()
                                                self.joueur.sound1.fadeout(300)
                                                son3=True
                                            self.balles[_].accelerationx=1
                                            self.balles[_].accelerationy=-1
                                self.balles[_].ancieny=self.balles[_].y
                                self.balles[_].ancienx=self.balles[_].x
                                self.balles[_].y=445
                                self.balles[_].affeff()
                                if self.balles[_].collision==False: # associe les modifications a toutes les balles qui n'ont pas encore rencontre de briques
                                    for __ in self.balles.keys():
                                        if (self.balles[__].collision==False and self.balles[__]!=self.balles[_]):
                                            self.balles[__].sens=1
                                            self.balles[__].x,self.balles[__].y,self.balles[__].accelerationx,self.balles[__].accelerationy=self.balles[_].x,self.balles[_].y,self.balles[_].accelerationx,self.balles[_].accelerationy
                                            self.balles[__].ancienx,self.balles[__].ancieny=self.balles[__].x,self.balles[__].y
                            self.joueur.ancienx=self.joueur.x
                            self.joueur.mouvement()
                        if self.balles[_].ancienx in range(self.joueur.x-8,self.joueur.x+self.joueur.taille-1): # reaffiche le joueur si la balle est de dans mais qu'elle est trop basse pour etre renvoyee
                            if self.balles[_].ancieny in range(self.joueur.y-10,self.joueur.y+11):
                                self.joueur.mouvement()
                        
    def deplacementballes(self): # gere les deplacements des balles
        n=0
        m=0
        self.directionboss=0
        for _ in self.balles.keys(): # pour toutes les balles
            self.balles[_].ancienx,self.balles[_].ancieny=self.balles[_].x,self.balles[_].y
            if self.balles[_].direction==1:
                self.balles[_].x-=3+int(self.balles[_].accelerationx)
            else:
                self.balles[_].x+=3+int(self.balles[_].accelerationx)
            if self.balles[_].sens==1:
                self.balles[_].y-=3+int(self.balles[_].accelerationy)
            else:
                self.balles[_].y+=3+int(self.balles[_].accelerationy)
            if (self.balles[_].collision==True)or(self.balles[_].collision==False and m==0): # n'efface qu'une seule fois pour les balles n'ayant pas encore rencontre de briques
                self.balles[_].effacer()
                if self.balles[_].collision==False:
                    m=1
            for __ in self.niveau.contenu.keys():
                if self.balles[_].ancienx in range(self.niveau.contenu[__].x-10,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur+1):
                    if self.balles[_].ancieny in range(self.niveau.contenu[__].y-10,self.niveau.contenu[__].y+self.niveau.contenu[__].hauteur+1): # reaffiche une brique si la balle se trouvait dans celle-ci
                       screen.fill(self.niveau.contenu[__].couleur,(self.niveau.contenu[__].x,self.niveau.contenu[__].y,self.niveau.contenu[__].largeur,self.niveau.contenu[__].hauteur))
                       pygame.display.update((self.niveau.contenu[__].x,self.niveau.contenu[__].y,self.niveau.contenu[__].largeur,self.niveau.contenu[__].hauteur))
            if (self.balles[_].collision==True)or(self.balles[_].collision==False and n==0): # n'affiche qu'une seule fois pour les balles n'ayant pas encore rencontre de briques
                self.balles[_].afficher()
                self.balles[_].balleintexte(self.joueur.score)
                if self.niveau.numero>0:
                    self.balles[_].balleintexte(self.stageaffiche)
                if self.illimite==False:
                    self.balles[_].balleintexte(self.joueur.vieaffichee)
                if self.balles[_].collision==False:
                    n=1
            if self.balles[_].y>=485: # la balle et hors de l'ecran
                self.balleseff.append(_)
            if ((self.stage==19 and self.illimite==False)or(self.niveau.numero==-19)) and len(self.niveau.contenu)>0: # "IA" du boss
                if (self.balles[_].y-self.niveau.contenu['0'].y)**2+(self.balles[_].x-self.niveau.contenu['0'].x)**2<=(self.niveau.contenu['0'].largeur**2+self.balles[_].cote**2+self.niveau.contenu['0'].largeur*5): # verifie que la balle est assez proche
                    if self.balles[_].x<self.niveau.contenu['0'].x: # si la balle est a sa gauche, il augmente ses chances d'aller a droite
                            self.directionboss+=1
                    elif self.balles[_].x>self.niveau.contenu['0'].x: # sinon, il augmente ses chances d'aller a gauche
                            self.directionboss-=1

    def bonusinbrique(self): # reaffiche une brique si un bonus se trouvait a l'interieur
        for _ in self.listebonus.keys(): # pour tous les bonus
            for __ in self.niveau.contenu.keys(): # pour toutes les briques
                if self.listebonus[_].x in range(self.niveau.contenu[__].x-self.listebonus[_].height,self.niveau.contenu[__].x+self.niveau.contenu[__].largeur+1):
                    if self.listebonus[_].y in range(self.niveau.contenu[__].y-self.listebonus[_].width,self.niveau.contenu[__].y+self.niveau.contenu[__].hauteur+1): # verifie que le boinus etait dans une brique
                        self.niveau.contenu[__].afficher()
            if not(self.listebonus[_].y>480 or len(self.niveau.contenu)==0 or len(self.balles)==0 or self.hardcore==True): # reaffiche le bonus si il est encore a l'ecran
                self.listebonus[_].afficher()

    def bonusinjoueur(self): # verifie si le joueur ramasse un bonus
        bonusaeffacer=[]
        for _ in self.listebonus.keys(): # pour tous les bonus
            if self.listebonus[_].x in range(self.joueur.x-self.listebonus[_].height,self.joueur.x+self.joueur.taille+1):
                if self.listebonus[_].y in range(self.joueur.y-self.listebonus[_].width,self.joueur.y+11): # verifie si le bonus se trouve dans le joueur
                    if self.bonus.count(self.listebonus[_].modif)>=1: # verifie que l'effet n'est pas deja applique 2 fois
                        self.listebonus[_].son.set_volume(self.volume*int(self.soundon==True))
                        self.listebonus[_].son.play()
                        self.bonus.remove(self.listebonus[_].modif) # retire le bonus des bonus en jeu
                        self.joueur.listebonus.append(self.listebonus[_].modif) # et l'ajoute au bonus du joueur
                        self.applicationbonusjoueur()
                        self.applicationbonusballes()
                        if self.listebonus[_].modif=='taille': # repositionne le joueur au besoin
                            self.joueur.x-=5
                            if self.joueur.x<10:
                                self.joueur.x=10
                            elif self.joueur.x+self.joueur.taille>630:
                                self.joueur.x=630-self.joueur.taille
                    bonusaeffacer.append(_)
        for _ in bonusaeffacer: # efface et supprime les bonus
            self.listebonus[_].supprimer()
            del self.listebonus[_]
        if len(bonusaeffacer)>0: # reaffiche le joueur
            self.joueur.ancienx=self.joueur.x
            self.joueur.mouvement()

    def effacerbonus(self): # efface et supprime tous les bonus a l'ecran
        bonusaeffacer=[]
        for _ in self.listebonus.keys(): # pour tous les bonus
            if (self.listebonus[_].y>480 or len(self.niveau.contenu)==0 or len(self.balles)==0)or(self.hardcore==True) or (self.illimite==False and (self.stage==19 and self.niveau.contenu['0'].vie<=0)):
                self.listebonus[_].supprimer()
                self.bonusinbrique()
                bonusaeffacer.append(_)
        for _ in bonusaeffacer:
            del self.listebonus[_]

    def verifquit(self,event=None): # verifie et agit en consequence si le joueur quitte la partie ou le programme. Gere aussi l'etat du son
        if event==None: # si aucun evenement n'est donne, on en recupere un
            event=pygame.event.poll()
        if event.type==QUIT: # le joueur souhaite quitter le programme
            self.continuer=False
            self.arretvolontaire=True
            self.duel=False
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        elif event.type==KEYDOWN: # le joueur souhaite quitter la partie
            if event.key==K_DELETE and self.pause==True:
                self.continuer=False
                self.hardcore=False
                pygame.mixer.stop()
                pygame.mixer.music.stop()
            elif event.key==K_s: # le joueur souhaite couper/mettre le son
                self.stopsound()

    def credits(self,full=False): # affiche et fait defiler les credits
        self.pause=True
        if self.continuer==True:
            listetextescredits={}
            textes=["LZ Butterfly Studio"+20*'\n',"Programmer"+4*'\n',"Edorh Francois"+8*'\n',"Scriptwriter"+4*'\n',"Edorh Francois"+8*'\n',"Animator"+4*'\n',"Edorh Francois"+8*'\n',"Level Design"+4*'\n',"Edorh Francois"+3*'\n',"Eliott Bricout"+3*'\n',"You"+6*'\n',"Sound Effects"+4*'\n',"Sfxr by Dr Petter"+8*'\n',"Musics"+4*'\n',"Boss Theme :"+3*'\n',"Divine Weapon"+3*'\n',"by"+3*'\n',"Butterfly Tea"+4*'\n',"End Theme :"+3*'\n',"The Darkness"+3*'\n',"by"+3*'\n',"Giorgio Campagnano"+6*'\n',"Font"+4*'\n',"Arcade"+3*'\n',"by"+3*'\n',"Jakob Fischer"+10*'\n',("The Legendary Hero"+3*'\n')*int(full),("Him"+5*'\n')*int(full),("The Evil Being"+3*'\n')*int(full),(self.joueur.nom+11*'\n')*int(full),("Thank you for playing my game !"+11*'\n')*int(full),("Now make it yours !")*int(full)]
            tailles=[45,50,30,50,30,50,30,50,30,30,30,50,30,50,40,30,20,30,40,30,20,30,50,30,20,30,50,30,50,30,30,30]
            ytexte=0
            for numerotexte in range(len(textes)): # defini et met en forme les textes en fonction de leur taille (souligne, gras, italic). Le caractere '\n' permet de "passer une ligne"
                if textes[numerotexte]!='':
                    if textes[numerotexte].count('\n')!=0:
                        listetextescredits[str(numerotexte)]=Texte(textes[numerotexte][:textes[numerotexte].index('\n')],taille=tailles[numerotexte],y=ytexte,centre=True,imagefond=self.imagefond,couleurfond=self.couleurfond,typefond=self.typefond)
                    else:
                        listetextescredits[str(numerotexte)]=Texte(textes[numerotexte],taille=tailles[numerotexte],y=ytexte,centre=True,imagefond=self.imagefond,couleurfond=self.couleurfond,typefond=self.typefond)
                    if listetextescredits[str(numerotexte)].taille==50 or listetextescredits[str(numerotexte)].taille==45:
                        listetextescredits[str(numerotexte)].font.set_underline(True)
                    if listetextescredits[str(numerotexte)].taille==40 or listetextescredits[str(numerotexte)].taille==45:
                        listetextescredits[str(numerotexte)].font.set_italic(True)
                    if listetextescredits[str(numerotexte)].taille==45:
                        listetextescredits[str(numerotexte)].font.set_bold(True)
                        listetextescredits[str(numerotexte)].x-=45
                    ytexte+=textes[numerotexte].count('\n')*25+75*int(numerotexte==0)
            pygame.mixer.music.load("sons/Giorgio_Campagnano_-_The_Darkness.wav")
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            if full==False: # les credits ne sont pas complets (credits accessibles des le menu)
                pygame.mixer.music.fadeout(85000)
            pygame.mouse.set_visible(True)
            for t in range(75): # fait apparaitre "LZ Butterfly Studio"
                pygame.event.pump()
                self.verifquit()
                listetextescredits['0'].couleur2=(listetextescredits['0'].couleur[0],listetextescredits['0'].couleur[1],listetextescredits['0'].couleur[2],3.4*t)
                listetextescredits['0'].afficher()
                pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
            maxtextes=len(listetextescredits)-1
            listetextesaeffacer=[]
            self.pause=True
            while listetextescredits[str(maxtextes)].y>(240-(240+listetextescredits[str(maxtextes)].height)*int(full==False)) and self.continuer==True:
                clock.tick(30*(1+3*self.getcontrol()))
                pygame.event.pump()
                self.verifquit()
                for _ in listetextescredits.keys(): # pour tous les textes 
                    if 480>listetextescredits[_].y>-listetextescredits[_].height: # si le texte est l'ecran, on l'efface
                        listetextescredits[_].effacer()
                    listetextescredits[_].y-=1.5
                    if 480>listetextescredits[_].y>-listetextescredits[_].height:  # si le texte est l'ecran, on l'affiche
                        listetextescredits[_].afficher()
                    if listetextescredits[_].y+listetextescredits[_].height<0: # le texte est sorti de l'ecran, on est pres a le supprimer
                        if full==True or (full==False and _!=str(maxtextes)):
                            listetextesaeffacer.append(_)
                if full==True: # partie bonus des credits
                    if str(maxtextes-4) in listetextescredits.keys():
                        if listetextescredits[str(maxtextes-4)].y==170.5: # si l'avant avant avant dernier texte est aux bonnes coordonnees
                            r=0
                            for t in range(51): # on efface les 4 derniers textes apres un certain temps
                                pygame.event.pump()
                                self.verifquit()
                                if t>25:
                                        r+=1
                                for texte in range(4):
                                    if t>25:
                                        listetextescredits[str(numerotexte-5+texte)].couleur2=(listetextescredits[str(numerotexte-5+texte)].couleur[0],listetextescredits[str(numerotexte-5+texte)].couleur[1],listetextescredits[str(numerotexte-5+texte)].couleur[2],255-r*10-5)
                                        listetextescredits[str(numerotexte-5+texte)].afficher()
                                    if str(numerotexte-5+texte) not in listetextesaeffacer:
                                        listetextesaeffacer.append(str(numerotexte-5+texte))
                                pygame.time.wait(int(((100*int(self.continuer==True))/(1+3*self.getcontrol()))))
                for _ in listetextesaeffacer:
                    listetextesaeffacer.remove(_)
                    del listetextescredits[_]
            if full==False:
                del listetextescredits[str(maxtextes)]
            else:
                self.lancement()
            pygame.mixer.music.stop()
            self.continuer=not(self.arretvolontaire)

    def chargerhighscore(self,nom="Hall of Shame"): # charge le highscore correspondant
        self.listenoms=[]
        self.listescores=[]
        self.listetemps=[]
        i=0
        try:
            fichier=gzip.open(nom+'.txt',"rb") # ouvre le fichier highscore correspondant
        except:
            pass
        else:
            for _ in fichier.readlines(): # et charge les informations
                try:
                    _=str(_,"utf-8")
                    _=_[:-1]
                    if i==0:
                        self.listenoms.append(_)
                        i+=1
                    elif i==1:
                        self.listescores.append(int(_))
                        i+=1
                    else:
                        self.listetemps.append(int(_))
                        i=0
                except:
                    pass               
            fichier.close()

    def sauvegarderhighscore(self,nom="Hall of Shame"): # enregistre les donnees dans le highscore corrspondant 
        fichier=gzip.open(nom+'.txt',"wb")
        for _ in range(8):
            try:
                fichier.write(bytes(self.listenoms[_]+'\n',"utf-8"))
                fichier.write(bytes(str(self.listescores[_])+'\n',"utf-8"))
                fichier.write(bytes(str(self.listetemps[_])+'\n',"utf-8"))
            except:
                pass
        fichier.close()

    def modifhighscore(self,nom="Hall of Shame"): # modifie les donnees du highscore correpondant et les sauvegarde
        c=0
        if len(self.listescores)>0:
            for _ in self.listescores:
                if c==0:
                    if (self.joueur.points>_) or (self.joueur.points==_ and int(self.tempsdejeu.total)<=self.listetemps[self.listescores.index(_)]):
                        self.record=self.listescores.index(_)
                        self.listenoms.insert(self.record,self.joueur.nom)
                        self.listescores.insert(self.record,self.joueur.points)
                        self.listetemps.insert(self.record,int(self.tempsdejeu.total))
                        self.sauvegarderhighscore(nom)
                        c=1
        if len(self.listescores)==0 or (len(self.listescores)<8 and c==0):
            self.listenoms.append(self.joueur.nom)
            self.listescores.append(self.joueur.points)
            self.listetemps.append(int(self.tempsdejeu.total))
            self.record=len(self.listescores)-1

    def afficherhighscore(self): # affiche le highscore qui a ete charge
        if self.typefond==0:
            screen.fill(self.couleurfond)
        else:
            screen.blit(self.imagefond,(0,0))
        Texte("Nom",25,10,taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond).afficher()
        Texte("Score",175,10,taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond).afficher()
        Texte("Temps de jeu",390,10,taille=30,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond).afficher()
        for _ in range(8):
            coul=(255,255,255,255)
            if _==self.record: # met en rouge les donnees de la ligne correpodant au joueur
                coul=(255,0,0,255)
            try:
                Texte(self.listenoms[_],-270,55+52*(_-4),taille=30,couleur=coul,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,centre=True).afficher()
                Texte(str(self.listescores[_]),-100,55+52*(_-4),taille=30,couleur=coul,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,centre=True).afficher()
                Texte(Time(self.listetemps[_]).affichertemps(),170,55+52*(_-4),taille=30,couleur=coul,couleurfond=self.couleurfond,imagefond=self.imagefond,typefond=self.typefond,centre=True).afficher()
            except:
                pass
        pygame.draw.line(screen,(255,255,255),(0,50),(640,50))
        pygame.draw.line(screen,(255,255,255),(340,0),(340,480))
        pygame.draw.line(screen,(255,255,255),(100,0),(100,480))
        pygame.display.flip()

def fadeouttext(self,listetextes,transparence,delai,pas): # je l'utilise cette fonction au moins ?...
    for t in range(255//pas):
        for texte in listetextes:
            self.verifquit()
            listetextes[texte].couleur2=(listetextes[texte].couleur2[0],listetextes[texte].couleur2[1],listetextes[texte].couleur2[2],(255-t*pas-pas)*int((255-t*pas-pas)>0))
            listetextes[texte].afficher()
            pygame.time.wait(100*int(self.continuer==True))
        if self.continuer==False:
            t=transparence

                
class Menu:

    def __init__(self):
        screen=pygame.display.set_mode((640,600))
        screen.fill((0,0,0))
        pygame.display.flip()
        pygame.mouse.set_visible(True)
        Texte("Menu",y=-250,taille=60,centre=True).afficher()
        self.modehistoire=Texte("Mode Histoire",y=-150,taille=35,centre=True)
        self.modehistoire.afficher()
        self.jeulibre=Texte("Jeu Libre",y=-110,taille=35,centre=True)
        self.jeulibre.afficher()
        self.editeur=Texte("Editeur de Niveau",y=-50,taille=35,centre=True)
        self.editeur.afficher()
        self.chargerniveau=Texte("Charger Niveau",y=-10,taille=35,centre=True)
        self.chargerniveau.afficher()
        self.commandes=Texte("Commandes",y=60,taille=35,centre=True)
        self.commandes.afficher()
        self.options=Texte("Options",y=120,taille=35,centre=True)
        self.options.afficher()
        self.highscore1=Texte("Hall Of Fame",y=180,taille=35,centre=True)
        self.highscore1.afficher()
        self.highscore2=Texte("Hall Of Shame",y=220,taille=35,centre=True)
        self.highscore2.afficher()
        self.credits=Texte("Credits",y=280,taille=35,centre=True)
        self.credits.afficher()
        self.marche=True
        self.stage={}
        self.edition=False
        self.lancerniveau=False
        self.lireoptions()
        self.initouvrirfichierniveau()

    def lireoptions(self): # charge les differentes options du jeu
        try:
            fichier=open('options.txt','r')
            self.volume=float(fichier.readline()[:-1])
            self.typefond=int(fichier.readline()[:-1])
            rouge=int(fichier.readline()[:-1])
            vert=int(fichier.readline()[:-1])
            bleu=int(fichier.readline()[:-1])
            self.couleurfond=(rouge,vert,bleu)
            self.imagefond=fichier.readline()[:-1]
            fichier.close()
        except:
            self.volume=1
            self.couleurfond=(0,0,0)
            self.typefond=0
            self.imagefond=''
        try:
            pygame.image.load('images/fonds/'+self.imagefond+'.png')
        except:
            self.imagefond=''

    def enregistreroptions(self): # sauvegarde les options
        fichier=open('options.txt','w')
        fichier.write(str(self.volume)+'\n')
        fichier.write(str(self.typefond)+'\n')
        for _ in range(3):
            fichier.write(str(self.couleurfond[_])+'\n')
        fichier.write(self.imagefond+'\n')
        fichier.close()

    def reinit(self): # reinitialise le menu
        if self.marche==True:
            self.__init__()
        pygame.event.clear()

    def arret(self): # arrete toutes les boucles
        self.marche=False
        self.edition=False
        self.lancerniveau=False
        self.chargerniveauedite=False
        self.modifoptions=False
        pygame.event.clear()


    def initouvrirfichierniveau(self): # initialise l'ouverture d'un fichier contenant un niveau
        self.ouvrirfichier=True
        self.page=[]
        self.ensemblepages={}
        self.ensemblepages['0']=[]
        self.stagespage={}

    def verifquit(self,event=None): # verifie si le joueur quitte ou non et arrete les boucles en consequence
        if event==None:
            event=pygame.event.poll()
        if event.type==QUIT:
            self.arret()
        
    def choix(self): # gere TOUT le menu
        mode=-1
        while self.marche==True:
            clock.tick(60)
            event=pygame.event.poll()
            if event.type==QUIT:
                self.arret()
            if self.marche==True:
                if event.type==MOUSEMOTION: # met le texte en rouge si le joueur place sa souris dessus
                    self.modehistoire.surbrillance()
                    self.jeulibre.surbrillance()
                    self.editeur.surbrillance()
                    self.chargerniveau.surbrillance()
                    self.commandes.surbrillance()
                    self.options.surbrillance()
                    self.highscore1.surbrillance()
                    self.highscore2.surbrillance()
                    self.credits.surbrillance()
                if event.type==MOUSEBUTTONUP:
                    if(self.modehistoire.intexte()): # indique quel mode de jeu est choisi
                        mode=1
                    elif (self.jeulibre.intexte()):
                        mode=0
                    if mode!=-1: # le jeu en lui meme
                        try :
                            self.jeu=Jeu(self.couleurfond,pygame.image.load('images/fonds/'+self.imagefond+'.png'),self.typefond)
                        except:
                            self.typefond=0
                            self.jeu=Jeu(self.couleurfond,None,self.typefond)
                        self.jeu.volume=self.jeu.volumemusique=self.volume
                        self.jeu.illimite=not(mode) # vrai si les vies du joueur sont illimitees, faux sinon
                        if self.jeu.illimite==False:
                            screen.fill((0,0,0))
                            pygame.display.flip()
                            prologue=Paragraphe(["Once upon a time, an Evil Being from a","forgotten past, came back to life."," "," ","For the first time, Mankind,","gathered around a Legendary Hero,","was bound to strive for one's freedom..."],x=50,y=100,taille=30,couleurfond=(0,0,0),typefond=0)
                            prologue.afficherlignes()
                            self.jeu.narration=True
                            self.jeu.lancement()
                            for t in range(51): # fait disparaitre le prologue
                                self.jeu.verifquit()
                                prologue.modifcouleur(couleur=(255,255,255,255-5*t-5))
                                prologue.afficherlignes()
                                pygame.time.wait(int(((100*int(self.jeu.continuer==True))/(1+3*self.jeu.getcontrol()))))
                        if self.jeu.continuer==True:
                            self.jeu.volume=self.jeu.volumemusique=self.volume
                            screen.fill((0,0,0))
                            pygame.display.flip()
                            self.jeu.chargerniveau()
                            while self.jeu.continuer==True: # le jeu peut commencer !
                                self.jeu.animation()
                            pygame.mixer.stop()
                            mode=-1
                        if self.jeu.arretvolontaire==True or self.jeu.continuer==False: # arret du jeu
                            mode=-1
                            self.marche=not(self.jeu.arretvolontaire)
                            self.reinit()
                    elif self.editeur.intexte(): # editeur de texte
                        del self.editeur
                        self.edition=True
                        self.ecranedition()
                        while self.edition==True:
                            clock.tick(60)
                            pygame.event.pump()
                            self.curseur.deplacementpointeur()
                            self.curseur2.deplacementpointeur() # deplacement des pointeurs
                            self.clns=self.curseur.valeurpointeur
                            self.lgns=self.curseur2.valeurpointeur # modification du nombre de ligne et de colonnes en consequence
                            self.creationstage()
                            for event in pygame.event.get():
                                if event.type==QUIT:
                                    self.arret()
                                elif event.type==KEYDOWN:
                                    if event.key==K_r:
                                        self.edition=False
                                    elif event.key==K_c: # chargement d'un niveau a partir de ceuw enregistres
                                        self.initouvrirfichierniveau()
                                        self.chargerniveauedite=True
                                        while self.chargerniveauedite==True:
                                            self.chargerfichierniveau()
                                            if self.lancerniveau==True: # le joueur a selectionne stage
                                                self.ecranedition() # retour a l'ecran d'edition
                                                self.champs.texte=self.stagespage[self.numerostage].nom
                                                self.champs.afficher() # affichage du nom du stage
                                                self.curseur=CurseurMod('Lgns',valeurpointeur=11,x=70,y=40,largeur=5,longueur=330,pas=30)
                                                self.curseur2=CurseurMod('Clns',valeurpointeur=7,x=70,y=410,largeur=525,longueur=5,pas=75)
                                                i=0
                                                for _ in range(11): # creation du stage
                                                    for __ in range(7):
                                                        self.stage['0'*int(_<10)+str(_)+str(__)]=Brique(x=100+__*50+__*25,y=40+_*20+_*10,vie=self.stagespage[self.numerostage].liste[i],largeur=50,hauteur=20)
                                                        i+=1
                                                for _ in self.stagespage.keys(): # les autres stages sont remis a zero
                                                    self.stagespage[_].choisi=0
                                            else:
                                                self.ecranedition() # retour a l'ecran d'edition
                                    elif event.key==K_s and self.stage!={}: # initialisation de la sauvegarde du stage si il contient au moins une brique
                                        c=0
                                        for _ in self.stage.keys():
                                            if c==0:
                                                if self.stage[_].vie>0: 
                                                    c+=1
                                        if c>0: # et que les briques aient au moins 1 point de vie
                                            pygame.mouse.set_visible(False)
                                            pygame.event.clear()
                                            self.sauvegardecreation=True
                                            pygame.time.wait(100)
                                            while self.sauvegardecreation==True and self.marche==True:
                                                clock.tick(60)
                                                event=pygame.event.poll()
                                                self.verifquit(event)
                                                self.champs.modiftexte(event=event) # ajout ou retrait de lettres
                                                if pygame.key.get_pressed()[K_RETURN]: # validation
                                                    if self.champs.texte!='': # si le nom est compose d'au moins 1 lettre
                                                        self.sauvegarderstage(self.champs.texte)
                                                        self.sauvegardecreation=False
                                                        self.champs.texte=''
                                                if pygame.key.get_pressed()[K_DELETE]: # annulation
                                                    self.sauvegardecreation=False
                                                    self.champs.texteaffiche.effacer()
                                                    self.champs.texte=''
                                                    self.champs.afficher()
                                                    pygame.mouse.set_visible(True)
                        self.reinit()
                    elif self.chargerniveau.intexte(): # chargement de niveau
                        del self.chargerniveau
                        self.chargerniveauedite=True
                        while self.chargerniveauedite==True:
                            self.chargerfichierniveau()
                            if self.lancerniveau==True: # le joueur a selectionne un stage
                                try :
                                    self.jeu=Jeu(self.couleurfond,pygame.image.load('images/fonds/'+self.imagefond+'.png'),self.typefond)
                                except:
                                    self.typefond=0
                                    self.jeu=Jeu(self.couleurfond,None,self.typefond)
                                self.jeu.volume=self.jeu.volumemusique=self.volume
                                if self.typefond==0:
                                    screen.fill(self.jeu.couleurfond)
                                else:
                                    screen.blit(self.jeu.imagefond,(0,0))
                                pygame.display.flip()
                                if "BOSS" not in self.stagespage[self.numerostage].liste:
                                    self.jeu.niveau=Niveau(-1,distancey=300,liste=self.stagespage[self.numerostage].liste,couleurfond=self.jeu.couleurfond,imagefond=self.jeu.imagefond,typefond=self.jeu.typefond)
                                else:
                                    self.jeu.niveau=Niveau(-19,distancey=300,liste=self.stagespage[self.numerostage].liste,couleurfond=self.jeu.couleurfond,imagefond=self.jeu.imagefond,typefond=self.jeu.typefond)
                                self.jeu.retourniveau()
                                self.jeu.illimite=True
                                self.jeu.lancement()
                                if "BOSS" in self.stagespage[self.numerostage].liste and self.jeu.continuer==True:
                                    pygame.mixer.music.play(loops=-1)
                                    pygame.mixer.music.set_volume(self.jeu.volume*int(self.jeu.soundon==True))
                                while self.jeu.continuer==True:
                                    self.jeu.animation()
                                if self.jeu.arretvolontaire==False: # retour a l'ecran de chargement de niveau
                                    self.initouvrirfichierniveau()
                                    pygame.event.clear()
                                    for _ in self.stagespage.keys():
                                        self.stagespage[_].choisi=0
                                else:
                                    self.arret()
                        self.reinit()
                    elif self.options.intexte(): # options
                        stop=False
                        pygame.event.clear()
                        self.ecranoptions()
                        chargerimagefond=False
                        while self.modifoptions==True:
                            clock.tick(60)
                            pygame.event.pump()
                            self.curseurvolume.deplacementpointeur()
                            self.volumeprovisoire=self.curseurvolume.valeurpointeur/100
                            for _ in self.couleursfond.keys():
                                self.couleursfond[_].deplacementpointeur()
                            for event in pygame.event.get():
                                if event.type==KEYDOWN:
                                    if event.key==K_r: # retourne sur le menu
                                        self.modifoptions=False
                                    elif event.key==K_RETURN: # valide les options
                                        self.volume=self.volumeprovisoire
                                        self.couleurfond=self.couleurfondprovisoire
                                        self.enregistreroptions()
                                        self.modifoptions=False
                                if event.type==MOUSEBUTTONUP:
                                    if self.optionscouleur.intexte(): # le type de fond est defini comme une couleur
                                        self.typefond=0
                                        self.optionscouleur.couleur2=(255,0,0,255)
                                        self.optionsimage.couleur2=(255,255,255,255)
                                        self.optionscouleur.afficher()
                                        self.optionsimage.afficher()
                                    elif self.optionsimage.intexte(): # le type de fond est defini comme une image
                                        self.typefond=1
                                        self.optionscouleur.couleur2=(255,255,255,255)
                                        self.optionsimage.couleur2=(255,0,0,255)
                                        self.optionscouleur.afficher()
                                        self.optionsimage.afficher()
                                    elif self.optionschargerimage.intexte(): # charger une image pour l'utiliser comme fond
                                        chargerimagefond=True
                                        screen.fill((0,0,0))
                                        try :
                                            fichier=open('images/fonds/mercidenepaseffacercefichier.txt','r') # ouvre le fichier contenant (normalement...) l'ensemble des noms des images
                                            listeimages=[]
                                            for _ in fichier.readlines():
                                                try :
                                                    verifimage=pygame.image.load('images/fonds/'+_[:-1]+'.png')
                                                    print(_[-1])
                                                    if(verifimage.get_size()[0]>=640) and (verifimage.get_size()[1]>=480): # verifie que l'image eciste et qu'elle possede les bonnes dimensions
                                                        listeimages.append(_[:-1])
                                                except :
                                                    pass
                                            fichier.close()
                                            numeroimage=0
                                            if len(listeimages)>0: # au moins une image
                                                image=pygame.image.load('images/fonds/'+listeimages[0]+'.png')
                                                screen.blit(image,(0,0))
                                                Texte(str(1)+'/'+str(len(listeimages)),x=550,y=500,taille=20).afficher() # charge et affiche l'image ainsi que le numero de la page
                                            else:
                                                screen.fill((0,0,0))
                                                Texte("404 not found",centre=True).afficher() # sinon, 404 not found
                                            pygame.display.flip()
                                        except :
                                            fichier=open('images/fonds/mercidenepaseffacercefichier.txt','w')
                                            fichier.close()
                                if event.type==MOUSEMOTION:
                                    self.optionschargerimage.surbrillance()
                                if event.type==QUIT:
                                    self.arret()
                                    stop=True
                            if chargerimagefond==True:
                                self.optionschargerimage.effacer()
                                if len(listeimages)>0:
                                    Texte("Gauche : Page precedente",x=50,y=500,taille=20).afficher()
                                    Texte("Droite : Page suivante",x=300,y=500,taille=20).afficher()
                                    Texte("B : Premiere page",x=50,y=530,taille=20).afficher()
                                    Texte("N : Derniere page",x=300,y=530,taille=20).afficher()
                                    Texte("R : Retour",x=50,y=560,taille=20).afficher()
                                    Texte("Entree : Valider",x=300,y=560,taille=20).afficher() # initialisaton de l'ecran de selection d'image
                                del self.optionscouleur,self.optionsimage,self.optionschargerimage
                            while chargerimagefond==True:
                                clock.tick(60)
                                for event in pygame.event.get():
                                    if event.type==KEYDOWN:
                                        if event.key in [K_LEFT,K_RIGHT,K_b,K_n,K_a,K_d] and len(listeimages)>0: # deplacement entre les images
                                            numeroavant=numeroimage
                                            if event.key==K_LEFT or event.key==K_a: # gauche
                                                numeroimage-=1
                                                if numeroimage<0:
                                                    numeroimage=len(listeimages)-1
                                            elif event.key==K_RIGHT or event.key==K_d: # droite
                                                numeroimage+=1
                                                if numeroimage>len(listeimages)-1:
                                                    numeroimage=0
                                            elif event.key==K_n: # derniere
                                                numeroimage=len(listeimages)-1
                                            else: # premiere
                                                numeroimage=0
                                            if numeroimage!=numeroavant:
                                                image=pygame.image.load('images/fonds/'+listeimages[numeroimage]+'.png')
                                                screen.blit(image,(0,0))
                                                pygame.display.update((0,0,640,480))
                                                Texte(str(numeroimage+1)+'/'+str(len(listeimages)),x=550,y=500,taille=20).afficher()
                                        elif event.key==K_r: # retour a l'ecran des options
                                            chargerimagefond=False
                                            self.ecranoptions()
                                        elif event.key==K_RETURN: # validation
                                            if len(listeimages)>0:
                                                self.imagefond=listeimages[numeroimage]
                                            else:
                                                self.imagefond=''
                                            chargerimagefond=False
                                            self.ecranoptions()
                                    elif event.type==QUIT:
                                        stop=True
                                        chargerimagefond=False
                                        self.arret()
                            pygame.event.clear()
                            if stop==False:
                                self.couleurfondprovisoire=(self.couleursfond['1'].valeurpointeur,self.couleursfond['2'].valeurpointeur,self.couleursfond['3'].valeurpointeur)
                                screen.fill(self.couleurfondprovisoire,(100,380,50,50))
                                pygame.display.update((100,380,50,50))
                        self.reinit()
                    elif self.credits.intexte(): # credits
                        try:
                            pygame.image.load('images/fonds/'+'stars'+'.png')
                            self.jeu=Jeu(self.couleurfond,pygame.image.load('images/fonds/'+'stars'+'.png'),1) # essaye de charger le fond etoile
                            screen.blit(self.jeu.imagefond,(0,0))
                        except:
                            self.jeu=Jeu(self.couleurfond,None,0)
                            screen.fill(self.couleurfond)
                        self.jeu.volume=self.jeu.volumemusique=self.volume
                        pygame.display.flip()
                        self.jeu.credits()
                        if self.jeu.continuer==False:
                            self.arret()
                        del self.jeu
                        self.reinit()
                    elif self.highscore1.intexte() or self.highscore2.intexte(): # highscores
                        hall=int(self.highscore1.intexte())
                        try:
                            self.jeu=Jeu(self.couleurfond,pygame.image.load('images/fonds/'+self.imagefond+'.png'),self.typefond)
                        except:
                            self.typefond=0
                            self.jeu=Jeu(self.couleurfond,None,self.typefond)
                        self.jeu.modifson=False
                        self.jeu.chargerhighscore("Hall of Fame"*hall+"Hall of Shame"*(1-hall)) # charge l'un des deux highscores
                        self.jeu.afficherhighscore()
                        while self.jeu.continuer==True:
                            clock.tick(60)
                            event2=pygame.event.poll()
                            self.jeu.verifquit(event2)
                            if event2.type==KEYDOWN:
                                if event2.key==K_r:
                                    self.jeu.continuer=False
                        if self.jeu.arretvolontaire==True:
                            self.arret()
                        del self.jeu
                        self.reinit()
                    elif self.commandes.intexte(): # commandes
                        lookcommandes=True
                        screen.fill((0,0,0))
                        pygame.display.update()
                        Texte("Commandes",y=-250,taille=60,centre=True).afficher()
                        Texte("Deplacements",x=50,y=150,taille=25).afficher()
                        Texte("'<-'/'->' ou 'Q'/'D'",x=160,y=-138,taille=25,centre=True).afficher()
                        Texte("Pause",x=50,y=250,taille=25).afficher()
                        Texte("'Espace'/'Entree'",x=160,y=-38,taille=25,centre=True).afficher()
                        Texte("Couper/mettre le son",x=50,y=350,taille=25,).afficher()
                        Texte("'S'",x=160,y=58,taille=25,centre=True).afficher()
                        Texte("Accelerer la vitesse",x=50,y=450,taille=25).afficher()
                        Texte("du texte",x=50,y=480,taille=25).afficher()
                        Texte("'Ctrl' (gauche)",x=160,y=158,taille=25,centre=True).afficher()
                        Texte("Quitter la partie",x=50,y=550,taille=25).afficher()
                        Texte("'Suppr'",x=160,y=258,taille=25,centre=True).afficher()
                        while (lookcommandes==self.marche==True):
                            clock.tick(60)
                            event2=pygame.event.poll()
                            self.verifquit(event2)
                            if event2.type==KEYDOWN:
                                if event2.key==K_r:
                                    lookcommandes=False
                        self.reinit()

                        
                        
    def ecranoptions(self): # initialise et affiche l'ecran des options
        if self.marche==True:
            pygame.event.clear()
            screen=pygame.display.set_mode((640,600))
            screen.fill((0,0,0))
            pygame.display.flip()
            self.curseurvolume=CurseurMod("Volume",valeurpointeur=int(self.volume*100),x=75,y=50,largeur=500,longueur=5,pas=5)
            Texte("Fond :",x=50,y=250).afficher()
            self.optionscouleur=Texte("Couleur :",x=70,y=340,couleur=(255,255*int(self.typefond==1),255*int(self.typefond==1),255))
            self.optionsimage=Texte("Image :",x=70,y=500,couleur=(255,255*int(self.typefond==0),255*int(self.typefond==0),255))
            self.optionscouleur.afficher()
            self.optionsimage.afficher()
            self.optionschargerimage=Texte(self.imagefond+"Charger une image"*int(self.imagefond==''),x=250,y=500)
            self.optionschargerimage.afficher()
            self.couleursfond={}
            self.couleursfond['1']=CurseurMod("",250,300,255,5,0,255,1,self.couleurfond[0],1,couleur=(255,0,0))
            self.couleursfond['2']=CurseurMod("",250,350,255,5,0,255,1,self.couleurfond[1],1,couleur=(0,255,0))
            self.couleursfond['3']=CurseurMod("",250,400,255,5,0,255,1,self.couleurfond[2],1,couleur=(0,0,255))
            for _ in self.couleursfond.keys():
                self.couleursfond[_].afficherpointeur()
            self.modifoptions=True
                                        
    def ecranedition(self): # initialise et affiche l'ecran d'edition de niveau
        if self.marche==True:
            screen=pygame.display.set_mode((640,600))
            screen.fill((0,0,0))
            pygame.display.flip()
            Texte("R : Retour",x=50,y=500,taille=20).afficher()
            Texte("C : Charger",x=300,y=500,taille=20).afficher()
            Texte("S : Sauvegarder",x=50,y=550,taille=20).afficher()
            Texte("Suppr : Annuler Sauvegarde",x=300,y=550,taille=20).afficher()
            self.champs=Champs(340,370,20)
            self.curseur=CurseurMod('Lgns',valeurpointeur=0,x=70,y=40,largeur=5,longueur=330,pas=30,valeurmini=0,valeurmaxi=11)
            self.curseur2=CurseurMod('Clns',x=70,y=410,largeur=525,longueur=5,pas=75,valeurmini=0,valeurmaxi=7)
            self.chargerniveauedite=False

    def creationstage(self): # cree le stage correspondant
        self.creationbriques()
        self.effacerbriques()
        self.modifierviebriques()

    def creationbriques(self): # cree les briques manquantes du stage
        if self.clns*self.lgns>len(self.stage):
            for _ in range(self.clns):
                for __ in range(self.lgns):
                    if '0'*int(_<10)+str(_)+str(__) not in self.stage.keys(): # regarde si la brique existe dans le stage
                        self.stage['0'*int(_<10)+str(_)+str(__)]=Brique(x=100+__*50+__*25,y=40+_*20+_*10,vie=1,largeur=50,hauteur=20)

    def effacerbriques(self): # efface et supprime les briques en trop du stage
        self.listebriquesaeffacer=[]
        if self.clns*self.lgns<len(self.stage):
            for _ in self.stage.keys():
                if(int(_[:2])>=self.clns)or(int(_[2])>=self.lgns):
                    self.listebriquesaeffacer.append(_)
            for _ in self.listebriquesaeffacer:
                self.stage[_].effacerbrique()
                del self.stage[_]

    def modifierviebriques(self): # modifie la vie des briques
        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
             (self.sourisx,self.sourisy)=pygame.mouse.get_pos()
             for _ in self.stage.keys():
                 if self.sourisx in range(self.stage[_].x,self.stage[_].x+self.stage[_].largeur+1):
                     if self.sourisy in range(self.stage[_].y,self.stage[_].y+self.stage[_].hauteur+1):
                         clock.tick(10)
                         self.stage[_].vie+=pygame.mouse.get_pressed()[0]-pygame.mouse.get_pressed()[2]*int(self.stage[_].vie>0) # clique gauche, la vie augmente ; clique droit, la vie diminue
                         self.stage[_].sprite()

    def sauvegarderstage(self,nom='stage'): # sauvegarde l'ensemble des vies des briques dans un fichier texte portant le nom du stage
        self.stagecree=open('stageperso/'+nom+'.txt','w')            
        for _ in range(11):
                for __ in range(7):
                    if '0'*int(_<10)+str(_)+str(__) not in self.stage.keys():
                        self.stage['0'*int(_<10)+str(_)+str(__)]=Brique()
                    self.stagecree.write(str(self.stage['0'*int(_<10)+str(_)+str(__)].vie)+',')
        self.stagecree.close()
        self.champs.texteaffiche.effacer()

    def affichageminiatureniveau(self,nom='',x=0,y=0): # renvoie le niveau (en miniature) du stage correspondant
        if nom!='':
            self.nomstageminiature=open('stageperso/'+nom+'.txt','r')
            listevies=self.nomstageminiature.read()
            self.listevies=[]
            vie=''
            for caractere in listevies:
                if caractere!=',':
                        vie+=caractere
                else:
                    if vie!="BOSS":
                        self.listevies.append(int(vie))
                    else:
                        self.listevies.append(vie)
                    vie=''
            self.nomstageminiature.close()
            if (len(self.listevies)==77)or("BOSS" in self.listevies):
                return (Niveauminiature(nom,-1,x,y,60,50,10,5,self.listevies,5,2)) # renvoie le stage
            else:
                print("Le niveau",nom,"n'a pas pu etre charge !" )
                return (Niveauminiature(nom,-1,x,y,60,50,10,5,[1]*77,5,2)) # sinon, renvoie un stage "par defaut"

    def chargerfichierniveau(self): # charge, affiche et gere la selection des niveaux
            screen=pygame.display.set_mode((640,600))
            pygame.mouse.set_visible(True)
            screen.fill((0,0,0))
            pygame.display.flip()
            n=m=d=0
            nomasupprimer=''
            if self.ouvrirfichier==True:
                self.ouvrirfichier=False
                self.z=0 # numero de la page
                for f in os.listdir("stageperso"): # parcours le dossier "stageperso"
                    if not(os.path.isdir(f)): # verifie que f n'est pas un dossier
                        try :
                            fichier=open("stageperso/"+f,"r") # ouvre le fichier et ajoute son nom a l'ensemble des noms de stages de la page temporaire
                            self.page.append(f[:-4])
                            d+=1
                            if d==12: # limite de stages par page atteinte
                                self.ensemblepages[str(self.z)]=self.page # la page z recupere l'ensemble des stages definitivement
                                self.page=[]
                                self.z+=1 # on passe a la page suivante
                                d=0
                            fichier.close()
                        except:
                            pass
                if self.page!=[]: # la page z recupere l'ensemble des stages definitivement
                    self.ensemblepages[str(self.z)]=self.page
                else:
                    self.z-=1 # la page n'est pas utilisee, on retourne a la precedente
                d=0
            if self.ensemblepages['0']!=[]: # au moins 1 stage est charge
                self.numeropage=0
                selectionniveau=True
                for _ in self.ensemblepages['0']: # calcul chiant (n correspond au decalage en x du stage, m represente son decallage en y)
                    self.stagespage[str(d)]=self.affichageminiatureniveau(_,n*150+50,m*150+50)
                    n+=1
                    d+=1
                    if n==4: # on va au debut de la ligne suivante
                        m+=1
                        n=0
                    if m==3:
                        n=m=0
                Texte(str(self.numeropage+1)+'/'+str(self.z+1),x=550,y=450,taille=20).afficher()
                Texte("Gauche : Page precedente",x=50,y=500,taille=20).afficher()
                Texte("Droite : Page suivante",x=300,y=500,taille=20).afficher()
                Texte("B : Premiere page",x=50,y=530,taille=20).afficher()
                Texte("N : Derniere page",x=300,y=530,taille=20).afficher()
                Texte("R : Retour",x=50,y=560,taille=20).afficher()
                if self.edition==True:
                    Texte("Suppr : Supprimer niveau",x=300,y=560,taille=20).afficher()
                while selectionniveau==True:
                    clock.tick(60)
                    pygame.event.pump()
                    if((pygame.key.get_pressed()[K_n] or pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]) and self.numeropage<self.z)or((pygame.key.get_pressed()[K_b] or pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]) and self.numeropage>=1):
                        screen.fill((0,0,0))
                        pygame.display.update((0,0,640,480))
                        self.numeropage+=int((pygame.key.get_pressed()[K_RIGHT])or(pygame.key.get_pressed()[K_d]))-int((pygame.key.get_pressed()[K_LEFT])or(pygame.key.get_pressed()[K_a]))
                        if pygame.key.get_pressed()[K_b]:
                            self.numeropage=0
                        elif pygame.key.get_pressed()[K_n]:
                            self.numeropage=self.z
                        Texte(str(self.numeropage+1)+'/'+str(self.z+1),x=550,y=450,taille=20).afficher()
                        n=m=0
                        self.stagespage={}
                        for _ in self.ensemblepages[str(self.numeropage)]: # on affiche la page actuelle
                            self.stagespage[str(d)]=self.affichageminiatureniveau(_,n*150+50,m*150+50)
                            n+=1
                            d+=1
                            if n==4:
                                m+=1
                                n=0
                            if m==3:
                                n=m=0
                    for event in pygame.event.get():
                        if event.type==QUIT:
                            self.arret()
                            selectionniveau=False
                            self.chargerniveauedite=False
                            self.lancerniveau=False
                            pygame.event.clear()
                        if event.type==KEYDOWN:
                            if event.key==K_r:
                                selectionniveau=False
                                self.chargerniveauedite=False
                                self.lancerniveau=False
                                pygame.event.clear()
                        for _ in self.stagespage.keys():
                            if event.type==MOUSEBUTTONUP:
                                self.stagespage[_].choisir()                        
                            if self.stagespage[_].choisi==2: # le stage est choisi
                                if ((self.edition==True)and("BOSS" not in self.stagespage[_].listevies))or(self.edition==False):
                                    selectionniveau=False
                                    self.lancerniveau=True
                                    self.numerostage=_
                                else: # si c'est le menu d'edition, le stage du boss ne peut pas etre edite (et donc choisi)
                                    self.stagespage[_].choisi=1
                            if self.edition==True:
                                if self.stagespage[_].choisi==1 and event.type==KEYDOWN: # on supprime le stage en mode edition
                                    if event.key==K_DELETE:
                                        selectionniveau=False
                                        nomasupprimer=self.stagespage[_].nom
                    if nomasupprimer!='': # suppression du stage et reformation des pages
                        self.supprimerstage(nomasupprimer)
                        self.initouvrirfichierniveau()
                        self.chargerfichierniveau()
            else:
                screen.fill((0,0,0))
                Texte("404 not found",centre=True).afficher()
                event=pygame.event.wait()
                while((event.type!=KEYDOWN)or(event.type==KEYDOWN)and((event.key!=K_RETURN)and(event.key!=K_r)))and(self.marche==True):
                    clock.tick(60)
                    if event.type==QUIT:
                        self.arret()
                    event=pygame.event.poll()
                self.chargerniveauedite=False                   

    def supprimerstage(self,nom=''): # supprime le stage correspondant
        try:
            os.remove('stageperso/'+nom+'.txt')
        except:
            print('Ce fichier ne peut etre efface.')
        
        


                                            
menu=Menu()

while menu.marche==True:
    menu.choix()
pygame.quit()
