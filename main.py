import pygame
import sys
import time
import random
from button import Button
from os import listdir
from os.path import isfile, join
from pygame.locals import QUIT

pygame.init()
pygame.mixer.init()

background_music = pygame.mixer.music.load('assets/audio/pirateb.wav')
pygame.mixer.music.play(-1)  # Loop the music indefinitely
coin_sounds = pygame.mixer.Sound('assets/audio/Sonic Ring - Sound Effect (HD).mp3')
fire_hit_sound = pygame.mixer.Sound('assets/audio/Player Fire Hurt (Nr. 3  Minecraft Sound) - Sound Effect for editing.mp3')


gameover_sound = pygame.mixer.Sound('assets/audio/gameover.wav')


WIDTH, HEIGHT = 600, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pirate Project')
block_size = 96
background = pygame.image.load('assets/piratebb.png')


def get_font(size):
  return pygame.font.Font("assets/font.ttf", size)


FPS = 60
PLAYER_VEL = 5

game_over = False


def displayGameOver(window):
  game_over_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
  game_over_surface.fill((0, 0, 0, 128))
  game_over_text = get_font(36).render("GAME OVER!", True, (255, 255, 255))
  text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
  game_over_surface.blit(game_over_text, text_rect)
  window.blit(game_over_surface, (0, 0))


winnerIMG = pygame.image.load('assets/Sprite/Treasure/treasure.png')


def displayWin(window, winnerIMG):
  winnerSurface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
  winnerSurface.fill((0, 0, 0, 128))
  winner_text = get_font(36).render("YOU WIN!", True, (255, 255, 255))
  text_rect2 = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
  winnerSurface.blit(winner_text, text_rect2)
  window.blit(winnerSurface, (0, 0))
  window.blit(winnerIMG, ((WIDTH - winnerIMG.get_width()) // 2,
                          (HEIGHT - winnerIMG.get_height()) // 2))
  pygame.display.update()


def flip(sprites):
  return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
  path = join("assets", dir1, dir2)
  images = [f for f in listdir(path) if isfile(join(path, f))]

  all_sprites = {}
  for image in images:
    sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
    sprites = []
    for i in range(sprite_sheet.get_width() // width):
      surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
      rect = pygame.Rect(i * width, 0, width, height)
      surface.blit(sprite_sheet, (0, 0), rect)
      sprites.append(pygame.transform.scale2x(surface))

    if direction:
      all_sprites[image.replace(".png", "") + "_right"] = sprites
      all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
    else:
      all_sprites[image.replace(".png", "")] = sprites

  return all_sprites


def get_block(size, block_type):
  path = join("assets", "Terrain", "Terrain.png")
  rect = None
  if block_type == "floor":
    rect = pygame.Rect(96, 0, size, size)
  elif block_type == "object":
    rect = pygame.Rect(145, 0, 32, 35)

  image = pygame.image.load(path).convert_alpha()
  surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
  surface.blit(image, (0, 0), rect)
  scaled_surface = pygame.transform.scale2x(surface)
  return scaled_surface


def load_floor_sprite_sheets():
  path = join("assets", "Terrain", "Terrain.png")
  floor_block_size = 96
  floor_block = get_block(floor_block_size, block_type="floor")
  return floor_block


def load_object_sprite_sheets():
  path = join("assets", "Terrain", "Terrain.png")
  object_block_size = 64
  object_block = get_block(object_block_size, block_type="object")
  return object_block


#function calls
floor_block_size = 32
floor_block = get_block(floor_block_size, "floor")

object_block_size = 16
object_block = get_block(object_block_size, "object")


class Player(pygame.sprite.Sprite):
  GRAVITY = 1
  COLOR = (255, 0, 0)
  ANIMATION_DELAY = 5
  HEIGHT = 5

  SPRITES = load_sprite_sheets("Sprite", "character", 32, 32, True)

  def __init__(self, x, y, width, height):
    super().__init__()
    self.rect = pygame.Rect(x, y, width, height)
    self.x_vel = 0
    self.y_vel = 0
    self.mask = None
    self.image = None
    self.direction = "left"
    self.animation_count = 0
    self.fall_count = 0
    self.jump_count = 0
    self.hit = False
    self.hit_count = 0

  def jump(self):
    self.y_vel = -self.GRAVITY * 8
    self.animation_count = 0
    self.jump_count += 1
    if self.jump_count == 1:
      self.fall_count = 0

  def move(self, dx, dy):
    self.rect.x += dx
    self.rect.y += dy

  def make_hit(self):
    self.hit = True
    self.hit_count = 0

  def move_left(self, vel):
    self.x_vel = -vel
    if self.direction != "left":
      self.direction = "left"
      self.animation_count = 0

  def move_right(self, vel):
    self.x_vel = vel
    if self.direction != "right":
      self.direction = "right"
      self.animation_count = 0

  def loop(self, FPS):
    self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)

    if self.hit:
      self.hit_count += 1
    if self.hit_count > FPS * 2:
      self.hit = False
      self.hit_count = 0

    self.fall_count += 1
    self.move(self.x_vel, self.y_vel)
    self.update_sprite()

  def landed(self):
    self.fall_count = 0
    self.y_vel = 0
    self.jump_count = 0

  def hit_head(self):
    self.count = 0
    self.y_vel *= -1

  def update_sprite(self):
    sprite_sheet = "idle"
    if self.hit:
      sprite_sheet = "hit"
    if self.x_vel != 0:
      sprite_sheet = "walk"

    sprite_sheet_name = sprite_sheet + "_" + self.direction
    sprites = self.SPRITES[sprite_sheet_name]
    sprite_index = (self.animation_count //
                    self.ANIMATION_DELAY) % len(sprites)
    self.sprite = sprites[sprite_index]
    self.animation_count += 1
    self.update()

  def update(self, *args, **kwargs):
    self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
    self.mask = pygame.mask.from_surface(self.sprite)

  def draw(self, win, offset_x):
    win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):

  def __init__(self, x, y, width, height, name=None):
    super().__init__()
    self.rect = pygame.Rect(x, y, width, height)
    self.image = pygame.Surface((width, height), pygame.SRCALPHA)
    self.width = width
    self.height = height
    self.name = name

  def draw(self, win, offset_x):
    win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):

  def __init__(self, x, y, size, block_type):
    super().__init__(x, y, size, size)
    block = get_block(size, block_type)
    self.image.blit(block, (0, 0))
    self.mask = pygame.mask.from_surface(self.image)


class Coin(Object):

  def __init__(self, x, y, width, height, image):
    super().__init__(x, y, width, height)
    self.image = image

  def update_position(self, dx):
    self.rect.x += dx

  def check_collision_with_player(self, player_rect):
    return self.rect.colliderect(player_rect)

  def draw(self, win, offset_x):
    win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Fire(Object):
  ANIMATION_DELAY = 3

  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height, "fire")
    self.fire = load_sprite_sheets("Traps", "Fire", width, height)
    self.image = self.fire["off"][0]
    self.mask = pygame.mask.from_surface(self.image)
    self.animation_count = 0
    self.animation_name = "off"

  def on(self):
    self.animation_name = "on"

  def off(self):
    self.animation_name = "off"

  def loop(self):
    sprites = self.fire[self.animation_name]
    sprite_index = (self.animation_count //
                    self.ANIMATION_DELAY) % len(sprites)
    self.image = sprites[sprite_index]
    self.animation_count += 1

    self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
    self.mask = pygame.mask.from_surface(self.image)

    if self.animation_count // self.ANIMATION_DELAY > len(sprites):
      self.animation_count = 0


def draw(window, background, player, objects, coins, offset_x):
  window.blit(background, (0, 0))
  for obj in objects:
    obj.draw(window, offset_x)

  for coin in coins:
    coin.draw(window, offset_x)
  player.draw(window, offset_x)
  pygame.display.update()


def handle_vertical_collision(player, objects, dy):
  collided_objects = []
  for obj in objects:
    if pygame.sprite.collide_mask(player, obj):
      if dy > 0:
        player.rect.bottom = obj.rect.top
        player.landed()
      elif dy < 0:
        player.rect.top = obj.rect.bottom
        player.hit_head()

      collided_objects.append(obj)

  return collided_objects


def collide(player, objects, dx):
  player.move(dx, 0)
  player.update()
  collided_object = None
  for obj in objects:
    if pygame.sprite.collide_mask(player, obj):
      collided_object = obj
      break

  player.move(-dx, 0)
  player.update()
  return collided_object


def handle_move(player, objects, dt):
  keys = pygame.key.get_pressed()
  player.x_vel = 0
  collide_left = collide(player, objects, -PLAYER_VEL * 2)
  collide_right = collide(player, objects, PLAYER_VEL * 2)

  if keys[pygame.K_LEFT] and not collide_left:
    player.move_left(PLAYER_VEL)
  if keys[pygame.K_RIGHT] and not collide_right:
    player.move_right(PLAYER_VEL)

  verticle_collide = handle_vertical_collision(player, objects, player.y_vel)
  to_check = [collide_left, collide_right, *verticle_collide]
  for obj in to_check:
    if obj and obj.name == "fire":
      player.make_hit()
      return True
    else:
      return False


def play(window):
  global game_over
  clock = pygame.time.Clock()
  dt = clock.tick(60) / 1000.0

  background = pygame.image.load('assets/piratebb.png')

  block_size = 96
  player = Player(100, 100, 50, 50)

  fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
  fire.on()
  fire2 = Fire(300, HEIGHT - block_size - 64, 16, 32)
  fire2.on()
  fire3 = Fire(600, HEIGHT - block_size - 64, 16, 32)
  fire3.on()
  fire4 = Fire(1100, HEIGHT - block_size - 64, 16, 32)
  fire4.on()
  fire5 = Fire(1270, HEIGHT - block_size - 64, 16, 32)
  fire5.on()
  floor = [
      Block(i * block_size, HEIGHT - block_size, block_size, "floor")
      for i in range(-WIDTH // block_size, (WIDTH * 100) // block_size)
  ]
  
  
  # Define additional blocks
  block1 = Block(400, HEIGHT - block_size * 2, block_size, "object")
  block2 = Block(500, HEIGHT - block_size * 3, block_size, "object")
  block3 = Block(700, HEIGHT - block_size * 3, block_size, "object")
  block4 = Block(900, HEIGHT - block_size * 3, block_size, "object")
  block5 = Block(1100, HEIGHT - block_size * 2, block_size, "object")
  block6 = Block(1200, HEIGHT - block_size * 3, block_size, "object")
  block7 = Block(1400, HEIGHT - block_size * 2, block_size, "object")
  block8 = Block(1500, HEIGHT - block_size * 3, block_size, "object")
  block9 = Block(1700, HEIGHT - block_size * 2, block_size, "object")
  block10 = Block(1800, HEIGHT - block_size * 3, block_size, "object")

  #block11 = Block(900, HEIGHT - block_size * 2, block_size, "object")
  #block12 = Block(900, HEIGHT - block_size * 3, block_size, "object")
  #block13 = Block(900, HEIGHT - block_size * 2, block_size, "object")
  #block14 = Block(900, HEIGHT - block_size * 3, block_size, "object")
  #block15 = Block(900, HEIGHT - block_size * 2, block_size, "object")
  #block16 = Block(900, HEIGHT - block_size * 3, block_size, "object")
  #block17 = Block(900, HEIGHT - block_size * 2, block_size, "object")
  #block18 = Block(900, HEIGHT - block_size * 3, block_size, "object")
  #block19 = Block(900, HEIGHT - block_size * 2, block_size, "object")
  #block20 = Block(900, HEIGHT - block_size * 3, block_size, "object")

  object_positions = [(400, HEIGHT - block_size * 2, "object"),
                      (500, HEIGHT - block_size * 3),
                      (700, HEIGHT - block_size * 3, "object"),
                      (900, HEIGHT - block_size * 3, "object")]
  object_sizes = [block_size] * len(object_positions)

  objects = [
      *floor,
      Block(0, HEIGHT - block_size * 2, block_size, "object"),
      Block(1, HEIGHT - block_size * 2, block_size, "object"),
      Block(block_size * 3, HEIGHT - block_size * 4, block_size,
            "object"), fire, fire2, fire3, fire4, fire5, block1, block2, block3, block4, block5, block6,
      block7, block8, block9, block10
  ]

  offset_x = 0
  scroll_area_width = 200
  # Lives
  lives = 3
  heart_image = pygame.image.load('assets/Sprite/character/heart.png')

  # Trap cooldown
  last_trap_collision_time = {fire: 0, fire2: 0, fire3: 0}
  cooldown_duration = 3

  #coin function
  coins = []
  for block in floor:
    coin_x = block.rect.centerx - 16
    coin_y = block.rect.top - 50

    block_at_coin = False
    fire_at_coin = False
    for obj in objects:
      if isinstance(obj, Block) and obj.rect.collidepoint(coin_x, coin_y):
        block_at_coin = True
        break

      elif isinstance(obj, Fire) and obj.rect.collidepoint(coin_x, coin_y):
        fire_at_coin = True
        break

    if not block_at_coin:
      coin = Coin(coin_x, coin_y, 32, 32,
                  pygame.image.load('assets/Sprite/Treasure/coin_0.png'))
      coins.append(coin)
    if not fire_at_coin:
      coin = Coin(coin_x + 40, coin_y, 32, 32,
                  pygame.image.load('assets/Sprite/Treasure/coin_0.png'))

  score = 0
  player_rect = pygame.Rect(100, 100, 32, 32)
  score_text = get_font(10).render("Score: " + str(score), True, (29, 30, 40))
  score_text_rect = score_text.get_rect(topleft=(10, 10))
  window.blit(score_text, score_text_rect)

  while not game_over:
    current_time = time.time()  # Get current time in seconds

    # Win if score is 20
    if score == 20:
      displayWin(window, winnerIMG)
      pygame.display.update()
      pygame.time.delay(4000)
      break

    # Lives
    for l in range(lives):
      window.blit(heart_image, (10 + (l * 20), 0))
    if lives <= 0:
      displayGameOver(window)
      pygame.display.update()
      pygame.time.delay(4000)
      break

    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        quit()
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          player.jump()

    player.loop(FPS)
    fire.loop()
    fire2.loop()
    fire3.loop()

    # Check collision with traps with cooldown
    for trap in [fire, fire2, fire3]:
      if player.rect.colliderect(trap.rect):
        if current_time - last_trap_collision_time[trap] > cooldown_duration:
          last_trap_collision_time[trap] = int(current_time)
          player.make_hit()
          lives -= 1
          if lives <= 0:
            lives = 0

          fire_hit_sound.play()

          break

    handle_move(player, objects, dt)
    game_over = handle_move(player, objects, dt)

    for coin in coins:
      if coin.check_collision_with_player(player.rect):
        coins.remove(coin)
        score += 1
        coin_sounds.play()

    draw(window, background, player, objects, coins, offset_x)

    if game_over or lives <= 0:
      displayGameOver(window)  # Display game over screen
      pygame.mixer.music.stop()
      gameover_sound.play()
      pygame.display.update()
      pygame.time.delay(4000)
      break

    if ((player.rect.right - offset_x >= WIDTH - scroll_area_width
         and player.x_vel > 0)
        or (player.rect.left - offset_x <= scroll_area_width
            and player.x_vel < 0)):
      offset_x += player.x_vel

    # Update score display
    score_text = get_font(10).render("Score: " + str(score), True,
                                     (255, 255, 255))
    window.blit(score_text, (20, 55))

    # Draw lives
    for l in range(lives):
      window.blit(heart_image, (10 + (l * 20), 0))

    pygame.display.update()


def main_menu(window):
  while True:
    MENU_MOUSE_POS = pygame.mouse.get_pos()

    MENU_TEXT = get_font(20).render("MAIN MENU", True, "#61141F")
    MENU_RECT = MENU_TEXT.get_rect(center=(300, 90))

    PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"),
                         pos=(300, 170),
                         text_input="PLAY",
                         font=get_font(10),
                         base_color="Black",
                         hovering_color="#61141F")

    QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"),
                         pos=(300, 250),
                         text_input="QUIT",
                         font=get_font(10),
                         base_color="Black",
                         hovering_color="#61141F")

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.MOUSEBUTTONDOWN:
        if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
          play(window)

        elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
          pygame.quit()
          sys.exit()

    window.blit(background, (0, 0))
    window.blit(MENU_TEXT, MENU_RECT)
    for button in [PLAY_BUTTON, QUIT_BUTTON]:
      button.changeColor(MENU_MOUSE_POS)
      button.update(window)

    pygame.display.update()


if __name__ == "__main__":
  main_menu(window)
