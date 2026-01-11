import pygame, random, math
from pygame import K_ESCAPE, SurfaceType
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sprites_dir = repo_root / 'sprites'
capybara_file = sprites_dir / 'capybara.png'
carrot_file = sprites_dir / 'carrot.png'
shrub_file = sprites_dir / 'shrub.png'

class Game:
    def __init__(self):
        pygame.init()

        # Display configuration
        self.disp_width = 1280
        self.disp_height = 800
        self.banner_height = 120
        self.window = pygame.display.set_mode((self.disp_width, self.disp_height + self.banner_height))

        # Caption configuration
        pygame.display.set_caption('Hungry Capybara')

        # Font configuration
        self.game_font = pygame.font.SysFont('Arial', 24)

        # Clock configuration
        self.clock = pygame.time.Clock()

        # Initiate variables
        self.counter = 0
        self.object_separation = 600
        self.last_difficulty_milestone = 0
        self.shrubs = []
        self.spawn_flag = None

        # Load all images
        self.capybara_img = pygame.image.load(str(capybara_file))
        self.shrub_img = pygame.image.load(str(carrot_file))
        self.carrot_img = pygame.image.load(str(shrub_file))

        self.new_game()

        # Main loop
        self.main_loop()

    # Populates the window with the initial obstacle configuration
    def new_game(self):
        self.capybara = Capybara(self.capybara_img, self)

        self.shrubs.append(Shrub(600, 300, (2, 122, 62), self.shrub_img, self.carrot_img, self))
        self.shrubs.append(Shrub(1200, 100, (2, 122, 62), self.shrub_img, self.carrot_img, self))

        self.spawn_flag = True

    # fixme
    # Handles events and draws sprites on the display
    def main_loop(self):
        while True:
           self.spawn_objects()
           self.check_events()
           self.update_objects(self.shrubs)
           self.draw_window()

    def spawn_objects(self):
        if self.spawn_flag:
            difficulty_milestone = self.counter // 5

            if difficulty_milestone > self.last_difficulty_milestone:
                if self.object_separation > 200:
                    self.object_separation -= 25
                    self.last_difficulty_milestone = difficulty_milestone

            last_shrub = self.shrubs[-1]

            if last_shrub.x <= self.disp_width - self.object_separation:
                top_obstacle_y = random.randrange(100, 500, 100)
                new_shrub = Shrub(self.disp_width, top_obstacle_y, (2, 122, 62), self.shrub_img, self.carrot_img, self)
                self.shrubs.append(new_shrub)

        if self.game_over(self.shrubs):
            self.spawn_flag = False

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                if event.key == pygame.K_F1:
                    self.new_game()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.capybara.rect.y > 0:
            self.capybara.rect.y -= self.capybara.speed
        if keys[pygame.K_DOWN] and self.capybara.rect.y < self.disp_height:
            self.capybara.rect.y += self.capybara.speed

        if self.game_over(self.shrubs):
            self.capybara.speed = 0

    def update_objects(self, shrubs: list):
        for shrub in shrubs:
            shrub.update()
            if shrub.x + shrub.width <= 0:
                shrubs.remove(shrub)

            if self.capybara.rect.colliderect(shrub.carrot_rect) and shrub.carrot_active:
                shrub.carrot_active = False
                self.counter += 1

            if self.game_over(self.shrubs):
                for shrub in shrubs:
                    shrub.speed = 0


    def draw_window(self):
        self.window.fill((144, 203, 152))

        self.capybara.draw(self.window)
        for shrub in self.shrubs:
            shrub.draw(self.window)

        pygame.draw.rect(self.window, (77, 67, 142), (0, self.disp_height, self.disp_width, self.banner_height))

        game_text = self.game_font.render('Objective: Barbara the Capybara is hungry! Help her collect carrots and avoid shrubs.', True, (255, 255, 255))
        self.window.blit(game_text, (25, self.disp_height + game_text.get_height() + 50))

        game_text = self.game_font.render('Score: ' + str(self.counter), True, (255, 255, 255))
        self.window.blit(game_text, (25, self.disp_height + 20))

        game_text = self.game_font.render('Speed: ' + str(self.last_difficulty_milestone + 1), True, (255, 255, 255))
        self.window.blit(game_text, (200, self.disp_height + 20))

        game_text = self.game_font.render('Exit: Esc', True, (255, 255, 255))
        self.window.blit(game_text, (self.disp_width//2 + game_text.get_width()//2 + 275, self.disp_height + 20))

        game_text = self.game_font.render('F1: New game', True, (255, 255, 255))
        self.window.blit(game_text, (self.disp_width//2 + game_text.get_width()//2 + 375, self.disp_height + 20))

        if self.game_over(self.shrubs):
            pygame.draw.rect(self.window, (77, 67, 142), (560, 380, 160, 70))

            game_text = []
            rendered_text = ['Game Over!', 'Score: ' + str(self.counter)]
            for line in rendered_text:
                game_text.append(self.game_font.render(line, True, (255, 255, 255)))

            y_offset = 0
            line_spacing = 30
            for game_text_surface in game_text:
                self.window.blit(game_text_surface, (self.disp_width//2 - game_text_surface.get_width()//2, self.disp_height//2 - game_text_surface.get_height()//2 + y_offset))
                y_offset += line_spacing

        pygame.display.flip()

        self.clock.tick(60)

    def game_over(self, shrubs: list):
        for shrub in shrubs:
            if self.capybara.rect.colliderect(shrub.top_rect) or self.capybara.rect.colliderect(shrub.bottom_rect):
                return True
        return None


class Capybara:
    def __init__(self, image, game):
        self.game = game
        self.image = image
        self.rect = self.image.get_rect(center=(150, game.disp_height//2))
        self.speed = 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Shrub:
    def __init__(self, x: int, top_obstacle_y: int, color: tuple[int, int, int], shrub_image: SurfaceType, carrot_image: SurfaceType, game: 'Game'):
        self.x = x
        self.gap_y = 300
        self.width = 200
        self.top_obstacle_y = top_obstacle_y
        self.color = color
        self.shrub_image = shrub_image
        self.carrot_image = carrot_image
        self.game = game
        self.speed = 7

        # Compute bottom height
        self.bottom_obstacle_y = self.game.disp_height - (self.gap_y + self.top_obstacle_y)

        # Shrub collision rects
        self.top_rect = pygame.Rect(
            self.x,
            0,
            self.width,
            self.top_obstacle_y
        )

        self.bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + self.top_obstacle_y,
            self.width,
            self.bottom_obstacle_y
        )

        # Carrot
        self.carrot_active = True
        carrot_center_x = self.x + self.width // 2
        carrot_center_y = self.top_obstacle_y + self.gap_y // 2
        self.carrot_rect = self.carrot_image.get_rect(center=(carrot_center_x, carrot_center_y))

    def update(self):
        self.x -= self.speed

        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        self.carrot_rect.centerx = self.x + self.width//2

    def draw_shrub_tiled(self, surface, rect: pygame.Rect):
        shrub_width = self.shrub_image.get_width()
        shrub_height = self.shrub_image.get_height()

        num_cols = math.ceil(rect.width / shrub_width)
        num_rows = math.ceil(rect.height / shrub_height)

        for row in range(num_rows):
            for col in range(num_cols):
                x = rect.x + col * shrub_width
                y = rect.y + row * shrub_height
                surface.blit(self.shrub_image, (x, y))


    def draw(self, surface):
        self.draw_shrub_tiled(surface, self.top_rect)
        self.draw_shrub_tiled(surface, self.bottom_rect)

        if self.carrot_active:
            surface.blit(self.carrot_image, self.carrot_rect)



if __name__ == '__main__':
    Game()
