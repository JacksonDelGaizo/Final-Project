import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self,resource,x,y,number,font):
        super().__init__()
        self.x = x
        self.y = y
        self.width = 100
        self.height = 100
        self.size = 100

        self.number = number

        self.resource = resource
        if self.resource == 'wheat':
            self.color = (240, 200, 50)
        elif self.resource == 'ore':
            self.color = (136, 136, 136)
        elif self.resource == 'brick':
            self.color = (178, 74, 44)
        elif self.resource == 'wood':
            self.color = (34,139,34)
        elif self.resource == 'sheep':
            self.color = (144, 238, 144)
        else:
            self.color = (194, 178, 128)
        self.image = pygame.Surface((self.size, self.size))

        self.image = pygame.Surface((self.width, self.height))  # WHAT to draw
        self.image.fill(self.color)  # color it
        self.rect = self.image.get_rect()  # WHERE to draw it
        self.rect.topleft = (self.x, self.y)  # position it

        text_surface = font.render(str(number), True, (0, 0, 0))
        text_x = (self.size // 2) - (text_surface.get_width() // 2)
        text_y = (self.size // 2) - (text_surface.get_height() // 2)
        self.image.blit(text_surface, (text_x, text_y))








