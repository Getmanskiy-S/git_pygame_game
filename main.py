import os
import sys
import pygame

# map_name = input('Введите название карты: ')
map_name = 'level_infinity.txt'

pygame.init()

FPS = 50
WIDTH = 400
HEIGHT = 400
STEP = 50
level_map = ''

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename, arg=None):
    global level_map
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    if arg is None:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    elif arg == 'LEFT':
        for i in range(len(level_map)):
            level_map[i] = level_map[i][-1] + level_map[i][:-1]
    elif arg == 'RIGHT':
        for i in range(len(level_map)):
            level_map[i] = level_map[i][1:] + level_map[i][0]
    elif arg == 'UP':
        level_map = [level_map[-1]] + level_map[:-1]
    elif arg == 'DOWN':
        level_map = level_map[1:] + [level_map[0]]
    if arg is not None:
        for i in range(len(level_map)):
            if '@' in level_map[i]:
                level_map[i] = level_map[i].replace('@', '.')
        level_map[4] = level_map[4][:4] + '@' + level_map[4][5:]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png', -1)

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.x, self.y = pos_x, pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


player, level_x, level_y = generate_level(load_level(map_name))
start_screen()
camera = Camera()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and level_map[player.y][player.x - 1] != '#' and player.x > 0:
                    all_sprites.empty()
                    player_group.empty()
                    tiles_group.empty()
                    player, level_x, level_y = generate_level(load_level(map_name, 'LEFT'))
                if event.key == pygame.K_RIGHT and level_map[player.y][player.x + 1] != '#':
                    all_sprites.empty()
                    player_group.empty()
                    tiles_group.empty()
                    player, level_x, level_y = generate_level(load_level(map_name, 'RIGHT'))
                if event.key == pygame.K_UP and level_map[player.y - 1][player.x] != '#' and player.y > 0:
                    all_sprites.empty()
                    player_group.empty()
                    tiles_group.empty()
                    player, level_x, level_y = generate_level(load_level(map_name, 'UP'))
                if event.key == pygame.K_DOWN and level_map[player.y + 1][player.x] != '#':
                    all_sprites.empty()
                    player_group.empty()
                    tiles_group.empty()
                    player, level_x, level_y = generate_level(load_level(map_name, 'DOWN'))
        except Exception:
            pass
    screen.fill(pygame.Color(0, 0, 0))
    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    tiles_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

terminate()
