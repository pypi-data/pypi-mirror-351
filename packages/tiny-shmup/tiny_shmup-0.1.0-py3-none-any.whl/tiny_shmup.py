import pygame, math, random
class tiny_shmup:
    def __init__(self, player_hitbox_size = 10):
        self.player_hitbox_size = player_hitbox_size
        pass

    def draw_bullet(self, surface, color, origin, size):
        pygame.draw.circle(surface, color, origin, size)
        pygame.draw.circle(surface, "white", origin, int(size * 0.5))

    def draw_player(self, surface, color, origin, size):
        origin_x, origin_y = origin

        half_size = size * 0.5
        wing_start = size * 0.1
        wing_start_b = size * 0.3
        pygame.draw.line(surface, color, (origin_x - wing_start, origin_y - wing_start), (origin_x - half_size, origin_y - half_size), 3)
        pygame.draw.line(surface, color, (origin_x - wing_start_b, origin_y - wing_start), (origin_x - half_size, origin_y - half_size), 3)
        pygame.draw.line(surface, color, (origin_x - wing_start_b, origin_y - wing_start), (origin_x + half_size, origin_y), 3)

        #flip y
        pygame.draw.line(surface, color, (origin_x - wing_start, origin_y + wing_start), (origin_x - half_size, origin_y + half_size), 3)
        pygame.draw.line(surface, color, (origin_x - wing_start_b, origin_y + wing_start), (origin_x - half_size, origin_y + half_size), 3)
        pygame.draw.line(surface, color, (origin_x - wing_start_b, origin_y + wing_start), (origin_x + half_size, origin_y), 3)

        pygame.draw.circle(surface, "white", origin, self.player_hitbox_size * 0.5)

    def draw_bit(self, surface, color, origin, size):
        origin_x, origin_y = origin

        half_size = size * 0.5
        wing_start = size * 0.1
        wing_start_b = size * 0.3
        pygame.draw.line(surface, color, (origin_x + wing_start, origin_y - wing_start), (origin_x + half_size, origin_y - half_size), 3)
        pygame.draw.line(surface, color, (origin_x + wing_start_b, origin_y - wing_start), (origin_x + half_size, origin_y - half_size), 3)
        pygame.draw.line(surface, color, (origin_x + wing_start_b, origin_y - wing_start), (origin_x - half_size, origin_y), 3)

        #flip y
        pygame.draw.line(surface, color, (origin_x + wing_start, origin_y + wing_start), (origin_x + half_size, origin_y + half_size), 3)
        pygame.draw.line(surface, color, (origin_x + wing_start_b, origin_y + wing_start), (origin_x + half_size, origin_y + half_size), 3)
        pygame.draw.line(surface, color, (origin_x + wing_start_b, origin_y + wing_start), (origin_x - half_size, origin_y), 3)


    def draw_enemy(self, surface, color, origin, size):
        origin_x, origin_y = origin
        spread = int(size * 0.33)
        for i in range(4):
            pygame.draw.circle(surface, color, (origin_x + random.randrange(-spread, spread), origin_y + random.randrange(-spread, spread)), size)
            
        
        pygame.draw.circle(surface, "black", origin, size)
        pygame.draw.circle(surface, color, origin, size * 0.50)

        pygame.draw.circle(surface, "black", origin, size * 0.33)
        pygame.draw.circle(surface, color, origin, size * 0.25)
        pass

    def draw_beam(self, surface, color, origin, size, direction):
            origin_x, origin_y = origin
            if direction == 6: #fwd
                pygame.draw.circle(surface, color, origin, int(size * 0.75))
                
                pygame.draw.rect(surface, color, (origin_x, origin_y - int(size * 0.5), 2000, size))
                pygame.draw.rect(surface, "white", (origin_x, origin_y - int(size * 0.25), 2000, int(size * 0.5)))

                pygame.draw.circle(surface, "white", origin, int(size * 0.5))

    def towards(self, origin, target):
        origin_x, origin_y = origin
        target_x, target_y = target
        vector = pygame.Vector2(target_x - origin_x, target_y - origin_y).normalize()
        return [vector.x, vector.y]
    
    