import pygame, sys

from pygame.locals import *

pygame.init()
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
WINDOW_SIZE = (1200, 800)
fullscreen = False

screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
display = pygame.Surface((300, 200))

pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

grass_image = pygame.image.load("grass.png")
stone_image = pygame.image.load("stone.png")
indoor_stone_image = pygame.image.load("indoor_stone.png")

TILE_SIZE = grass_image.get_width()


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


game_map = load_map('map')

global animation_frames
animation_frames = {}


def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


animation_database = {}
animation_database['run'] = load_animation('C:/Users/patcu/PycharmProjects/platformer/player_animations/run', [7, 7])
animation_database['idle'] = load_animation('C:/Users/patcu/PycharmProjects/platformer/player_animations/idle',
                                            [40, 40])
animation_database['jump'] = load_animation('C:/Users/patcu/PycharmProjects/platformer/player_animations/jump',
                                            [40, 40])
player_action = 'idle'
player_frame = 0


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

player_X_momentum = 0
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True

    return rect, collision_types


moving_right = False
moving_left = False

player_Y_momentum = 0
air_timer = 0
scroll = [0, 0]

player_rect = pygame.Rect(140, 800, 14, 16)

while True:

    scroll[0] += (player_rect.x - scroll[0] - 140) / 10
    scroll[1] += (player_rect.y - scroll[1] - 90) / 10
    display.fill((227, 242, 253))
    tile_rects = []

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(stone_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '2':
                display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '3':
                display.blit(indoor_stone_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile != '0' and tile != '3':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    player_frame += 1

    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]

    display.blit(player_image, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    player_movement = [0, 0]

    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_Y_momentum
    player_Y_momentum += 0.3
    if player_Y_momentum > 8:
        player_Y_momentum = 8

    if player_movement[0] != 0 and player_movement[1] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')

    if player_movement[0] == 0 and player_movement[1] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')

    if player_movement[1] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'jump')

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_Y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    if collisions['top']:
        player_Y_momentum = 0.2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_SPACE:
                if air_timer < 6:
                    player_Y_momentum = -7
            if event.type == VIDEORESIZE:
                if not fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((monitor_size), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(screen.get_width(), screen.get_height(), pygame.RESIZABLE)
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)
