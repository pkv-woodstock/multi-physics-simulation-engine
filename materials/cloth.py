import pygame
import numpy as np

from pygame.locals import *

class Cloth():

    def __init__(self, x, y, width, height, spacing):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.spacing = spacing
        self.locked = [[]]
        self.acceleration = np.array([0,0])

    def generate_points(self):
        self.pos_current = np.empty((self.height, self.width,2))
        for i, h in enumerate(self.pos_current):
            for j, w in enumerate(self.pos_current[0]):
                self.pos_current[i][j] = [self.x + self.spacing * j,self.y + self.spacing * i]
        
        self.pos_old = np.copy(self.pos_current)

    def generate_sticks(self):
        self.sticks = []
        for h in range(self.height):
            for w in range(self.width):
                if (h+1 < self.height):
                    self.sticks.append([self.pos_current[h][w], self.pos_current[h+1][w]])
                if (w+1 < self.width):
                    self.sticks.append([self.pos_current[h][w], self.pos_current[h][w+1]])
        self.sticks = np.array(self.sticks)

    def update(self, dt):
        GRAVITY = np.array([0,500])
        substeps = 1

        for s in range(substeps):
            self.accelerate(GRAVITY)
            self.update_pos(dt/substeps)
            self.resolve_constraints()
        self.generate_sticks()

    def update_pos(self, dt):
        velocity = np.subtract(self.pos_current, self.pos_old)

        #Save current position
        self.pos_old = self.pos_current

        #Perform Verlet Integration
        self.pos_current = self.pos_current + velocity + (self.acceleration * dt * dt)

        self.pos_current[0] = self.pos_old[0]
        self.pos_current[self.point[0]][self.point[1]] = self.pos_old[self.point[0]][self.point[1]]

        #Reset acceleration
        self.acceleration = np.array([0,0])
    
    def resolve_constraints(self):
        for h, i in enumerate(self.pos_current):
            for w, j in enumerate(self.pos_current[0]):
                if (h+1 < self.height):
                    if not h == 0:
                        output = self.resolve_constraint(self.pos_current[h][w], self.pos_current[h+1][w], False)
                    else:
                        output = self.resolve_constraint(self.pos_current[h][w], self.pos_current[h+1][w], True)
                    self.pos_current[h][w], self.pos_current[h+1][w] = output
                if (w+1 < self.width):
                    output = self.resolve_constraint(self.pos_current[h][w], self.pos_current[h][w+1], False)
                    self.pos_current[h][w], self.pos_current[h][w+1] = output

    def resolve_constraint(self, p1, p2, pinned):
        distance = np.linalg.norm(p1-p2)
        output = [p1,p2]
        if abs(distance - self.spacing) > 0.01:
            #Unit vector of transformation axis
            transform_axis = (p1 - p2) / distance

            #How much the distance will change
            change_distance = self.spacing - distance

            #Creates a vector along the transform axis, divided by two because 
            #both p1 and p2 will move in opposite directions 
            #in the same length
            change_vec = transform_axis * (change_distance)

            #Moves points towards each other
            if not pinned:
                output[0] = p1 + change_vec/2
                output[1] = p2 - change_vec/2
            else:
                output[0] = p1
                output[1] = p2 - change_vec
        return output

    def accelerate(self, acc):
        self.acceleration = np.add(self.acceleration, acc)

    def mouse_click(self, mouse_pos):
        if self.point == [0,0]:
            closest = np.linalg.norm(mouse_pos-self.pos_current[0][0])
            self.point = [0,0]
            for i, x in enumerate(self.pos_current):
                for j, y in enumerate(self.pos_current[i]):
                    distance = np.linalg.norm(mouse_pos-self.pos_current[i][j])
                    if distance < closest:
                        closest = distance
                        self.point = [i,j]
            self.pos_current[self.point[0]][self.point[1]] = mouse_pos
        else:
            self.pos_current[self.point[0]][self.point[1]] = mouse_pos
    
    def mouse_reset(self):
        self.point = [0,0]

def update_fps():
    fps = f"FPS: {str(int(clock.get_fps()))}"
    return text_render(fps)

def text_render(string):
    return font.render(string, 1, pygame.Color("white"))
 
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
 
gameOn = True
update_count = 0

cloth = Cloth(200,10,20,20,20)
cloth.generate_points()

while gameOn:
    clock.tick(120)
    update_count+=1

    left, middle, right = pygame.mouse.get_pressed()
    if left:
        cloth.mouse_click(pygame.mouse.get_pos())
    if not left:
        cloth.mouse_reset()

    #Create background
    screen.fill((0,0,0))

    #Update fps
    screen.blit(update_fps(), (10,0))
    screen.blit(text_render(f"Frame #: {update_count}"), (10,30))
    
    cloth.update(clock.get_time()/1000)

    for stick in cloth.sticks:
        pygame.draw.line(screen, (120,120,255), (stick[0][0], stick[0][1]), (stick[1][0], stick[1][1]))

    # Update the display using flip
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            gameOn = False
            pygame.quit()
            continue

pygame.quit()
