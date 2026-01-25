import arcade
from arcade.camera import Camera2D
from pyglet.graphics import Batch
import random

import time
import enum
import math
SCREEN_W = 1280
SCREEN_H = 720
TITLE = "HeadBreakers"

# Физика и движение
GRAVITY = 2            # Пикс/с^2
MOVE_SPEED = 6
LADDER_SPEED = 3        # Скорость по лестнице
CAMERA_LERP = 0.12        # Плавность следования камеры


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


# Задаём размеры окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720



class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = 0.3
        self.speed = 300
        self.health = 100

        # Загрузка текстур
        self.idle_texture = arcade.load_texture(
            "гг_вправо_1.png")
        self.texture = self.idle_texture

        self.walk_textures = []
        for i in range(0, 6):
            texture = arcade.load_texture(f"гг_вправо_{i + 1}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1  # секунд на кадр

        self.is_walking = False  # Никуда не идём
        self.face_direction = FaceDirection.LEFT  # и смотрим вправо

        # Центрируем персонажа
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

    def update_animation(self, delta_time: float = 1 / 60):
        """ Обновление анимации """
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                # Поворачиваем текстуру в зависимости от направления взгляда
                if self.face_direction == FaceDirection.RIGHT:
                    self.texture = self.walk_textures[self.current_texture]
                else:
                    self.texture = self.walk_textures[self.current_texture].flip_horizontally()

        else:
            # Если не идём, то просто показываем текстуру покоя
            # и поворачиваем её в зависимости от направления взгляда
            if self.face_direction == FaceDirection.RIGHT:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

    def update(self, delta_time, keys_pressed):
        """ Перемещение персонажа """
        # В зависимости от нажатых клавиш определяем направление движения
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy
        # Поворачиваем персонажа в зависимости от направления движения
        # Если никуда не идём, то не меняем направление взгляда
        if dx < 0:
            self.face_direction = FaceDirection.RIGHT
        elif dx > 0:
            self.face_direction = FaceDirection.LEFT

        # Ограничение в пределах экрана

        # Проверка на движение
        self.is_walking = dx or dy


class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, antialiasing=True)
        self.start_time: float = 0.0
        self.texture = arcade.load_texture('backgroung_texture.png')
        # Камеры
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        # Списки спрайтов
        self.player_list = arcade.SpriteList()

        self.walls = arcade.SpriteList(use_spatial_hash=True)  # Очень много статичных — хэш спасёт вас
        self.platforms = arcade.SpriteList()  # Двигающиеся платформы
        self.ladders = arcade.SpriteList()
        self.mechanics = arcade.SpriteList()
        self.keyboard_1 = arcade.SpriteList()
        self.cabels = arcade.SpriteList()

        # Игрок
        self.player = None
        self.spawn_point = (128, 256)  # Куда респавнить после шипов

        # Физика
        self.engine = None

        # Ввод
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0

        # Счёт
        self.score = 0
        self.batch = Batch()
        self.text_info = arcade.Text("AD/←→ — to walk",
                                     16, 16, arcade.color.GRAY, 20, batch=self.batch)

    def setup(self):
        self.wave = 1
        self.cooldown = True
        self.cooldown2 = True
        self.colors1 = ['Yellow', 'Red', 'Blue']
        self.colors2 = ['Yellow', 'Red', 'Blue']
        self.colors_1 = []
        self.colors_2 = []
        self.bluecabel_y = 0
        self.bluecabel1 = True
        self.redcabel_y = 0
        self.redcabel1 = True
        self.yellowcabel_y = 0
        self.yellowcabel_y2 = 0
        self.redcabel_y2 = 0
        self.numbers1 = [1, 2, 3]
        self.yellowcabel_y2 = 0
        self.yellowcabel1 = True
        self.yellowcabel_y1 = 0
        self.redcabel_y1 = 0
        self.bluecabel_y1 = 0
        self.score_no = True
        self.numbers = [1, 2, 3]
        self.cooldown_red = True
        self.cooldown_yellow = True
        self.cooldown_blue = True
        self.cooldown_red1 = True
        self.cooldown_yellow1 = True
        self.cooldown_blue1 = True
        self.bluecabelmouse = True
        self.redcabelmouse = True
        self.yellowcabelmouse = True
        self.is_active = False
        self.yellowcabel_x = 3
        self.bluecabel_x = 3
        self.redcabel_x = 3
        self.yellowcabelentered = False
        self.bluecabelentered = False
        self.redcabelentered = False
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        self.x1, self.y1 = 0, 0
        self.time1 = 30
        self.time2 = 30
        self.room1_x = 300
        self.room2_x = 910
        self.what_room = True
        self.right_1 = arcade.load_texture('гг_вправо_1.png')
        self.right_1.size = (350, 190)
        self.right_2 = arcade.load_texture('гг_вправо_2.png')
        self.right_2.size = (350, 190)
        self.current_texture = 0
        self.is_walking = False
        self.keys_pressed = set()
        self.textureright = [self.right_1, self.right_2]
        self.cabelentertexture_red = arcade.load_texture('redcabelenter.png')
        self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter.png')
        self.cabelentertexture_blue = arcade.load_texture('bluecabelenter.png')
        self.bluewas_y = 0
        self.waves = 4
        self.x_electrical = 510
        self.complete = {'Red': False, 'Yellow': False, 'Blue': False}
        self.positioncabels = {1: {'start': 1, 'end': 1.3, 'color': None},
                               2: {'start': 1.7, 'end': 2.3, 'color': None},
                               3: {'start': 3, 'end': 3.4, 'color': None}}
        self.positionentercabels = {1: {'start': 1, 'end': 1.3, 'color': None},
                               2: {'start': 1.7, 'end': 2.3, 'color': None},
                               3: {'start': 3, 'end': 3.4, 'color': None}}
        # self.electrical_mechanics()
        self.room1 = arcade.Sprite('background.png', scale=0.4)
        self.room1.center_x = self.room1_x
        self.room1.center_y = 250
        self.room2 = arcade.Sprite('background.png', scale=0.4)
        self.room2.center_x = self.room2_x
        self.room2.center_y = 250
        self.cabels.append(self.room1)
        self.cabels.append(self.room2)
        # --- Игрок ---
        self.player_list.clear()
        self.player = Hero()

        self.player.center_x, self.player.center_y = self.spawn_point
        self.player_list.append(self.player)
        # --- Gui на экране ---
        self.puzzle_1_texture = arcade.load_texture('Puzzle_1_texture.png')


        # --- Для определения какую клавишу отображать ---
        self.keyboard_Number = 0
        # --- Для того чтобы игрок не мог ходить пока находится в головоломке ---
        self.Can_walk = True
        # --- Для отображения головоломки ---
        self.puzzle = 0
        # --- Клавиатура на экране ---
        self.keyboard_E = arcade.Sprite("E_Keyboard.png", 1.3)
        self.keyboard_E.center_x = self.player.center_x
        self.keyboard_E.center_y = self.player.center_y + 10
        self.keyboard_1.append(self.keyboard_E)
        # --- Электро щиток ---
        self.tile = arcade.Sprite("electical_panel_texture.png", scale=0.1)
        self.tile.center_x = self.x_electrical
        self.tile.center_y = 150
        self.mechanics.append(self.tile)
        self.text_timer = arcade.Text(f"Time: {self.time1}",
                                      1000, 600, arcade.color.BRONZE, 40)
        # Пол из «травы»
        for x in range(0, 1800, 64):
            tile = arcade.Sprite("ground.png", scale=0.05)
            tile.center_x = x
            tile.center_y = 64
            self.walls.append(tile)

        for y in range(64, 64 + 64 * 6, 64):
            self.s = arcade.Sprite("ground.png", 0.05)
            self.s.center_x = 1830
            self.s.center_y = y
            self.walls.append(self.s)

        # Пара столбиков-стен
        for y in range(64, 64 + 64 * 6, 64):
            self.s = arcade.Sprite("ground.png", 0.05)
            self.s.center_x = self.room1.center_x - 300
            self.s.center_y = y
            self.walls.append(self.s)

        # --- Физический движок платформера ---
        # Статичные — в walls
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.walls,
        )

        # Сбросим вспомогательные таймеры
    def electrical_mechanics(self):
        for i in range(3 * self.wave):
            if self.cooldown2:
                if not self.colors2:
                    self.cooldown2 = False
                    self.colors2 = ['Yellow', 'Red', 'Blue']
                    self.numbers = [1, 2, 3]
                    self.positioncabels = {1: {'start': 1.3, 'end': 1.3, 'color': None},
                                           2: {'start': 1.7, 'end': 2.3, 'color': None},
                                           3: {'start': 3, 'end': 3.4, 'color': None}}
                    self.yellowcabel_x = 3
                    self.bluecabel_x = 3
                    self.redcabel_x = 3
                    # self.bluewas_y = 0
                    # self.bluewas_x = 0
                    # self.redwas_y = 0
                    # self.redwas_x = 0
                    # self.yellowwas_y = 0
                    # self.yellowwas_x = 0


                self.rand = random.choice(self.colors2)

                if self.positioncabels[2].get('color') != None:
                    try:
                        self.numbers.remove(2)
                    except Exception:
                        pass
                if self.positioncabels[3].get('color') != None:
                    try:
                        self.numbers.remove(3)
                    except Exception:
                        pass
                if self.positioncabels[1].get('color') != None:
                    try:
                        self.numbers.remove(1)
                    except Exception:
                        pass
                if self.rand == 'Yellow':
                    self.colors2.remove('Yellow')
                    self.yellowcabel_y1 = random.choice(self.numbers)
                    if self.positioncabels[self.yellowcabel_y1].get('color') == None:
                        self.positioncabels[int(self.yellowcabel_y1)].update({'color': 'Yellow'})
                    self.yellowcabel1 = True
                elif self.rand == 'Red':
                    self.colors2.remove('Red')
                    self.redcabel_y1 = random.choice(self.numbers)
                    if self.positioncabels[self.redcabel_y1].get('color') == None:
                        self.positioncabels[int(self.redcabel_y1)].update({'color': 'Red'})
                    self.redcabel1 = True
                elif self.rand == 'Blue':
                    self.colors2.remove('Blue')
                    self.bluecabel_y1 = random.choice(self.numbers)
                    if self.positioncabels[self.bluecabel_y1].get('color') == None:
                        self.positioncabels[int(self.bluecabel_y1)].update({'color': 'Blue'})
                    self.bluecabel1 = True
                for i, el in enumerate(self.positioncabels):
                    if self.positioncabels[el]['color'] == 'Blue' and self.cooldown_blue:
                        self.cooldown_blue = False
                        self.bluecabel_y = random.uniform(float(self.positioncabels[el]['start']), float(self.positioncabels[el]['end']))
                    elif self.positioncabels[el]['color'] == 'Red' and self.cooldown_red:
                        self.cooldown_red = False
                        self.redcabel_y = random.uniform(float(self.positioncabels[el]['start']), float(self.positioncabels[el]['end']))
                    elif self.positioncabels[el]['color'] == 'Yellow' and self.cooldown_yellow:
                        self.cooldown_yellow = False
                        self.yellowcabel_y = random.uniform(float(self.positioncabels[el]['start']), float(self.positioncabels[el]['end']))
                        self.bluewas_y = self.yellowcabel_y
            if self.cooldown:
                if not self.colors1:
                    self.cooldown = False
                    self.colors1 = ['Yellow', 'Red', 'Blue']
                    self.numbers1 = [1, 2, 3]
                    self.positionentercabels = {1: {'start': 1.3, 'end': 1.3, 'color': None},
                                           2: {'start': 1.7, 'end': 2.3, 'color': None},
                                           3: {'start': 3, 'end': 3.4, 'color': None}}

                self.rand1 = random.choice(self.colors1)

                if self.positionentercabels[2].get('color') != None:
                    try:
                        self.numbers1.remove(2)
                    except Exception:
                        pass
                if self.positionentercabels[3].get('color') != None:
                    try:
                        self.numbers1.remove(3)
                    except Exception:
                        pass
                if self.positionentercabels[1].get('color') != None:
                    try:
                        self.numbers1.remove(1)
                    except Exception:
                        pass

                if self.rand1 == 'Yellow':
                    self.colors1.remove('Yellow')
                    yellowcabel_y1 = random.choice(self.numbers1)
                    if self.positionentercabels[yellowcabel_y1].get('color') == None:
                        self.positionentercabels[int(yellowcabel_y1)].update({'color': 'Yellow'})
                    self.yellowcabel2 = True
                elif self.rand1 == 'Red':
                    self.colors1.remove('Red')
                    redcabel_y1 = random.choice(self.numbers1)
                    if self.positionentercabels[redcabel_y1].get('color') == None:
                        self.positionentercabels[int(redcabel_y1)].update({'color': 'Red'})
                    self.redcabel2 = True
                elif self.rand1 == 'Blue':
                    self.colors1.remove('Blue')
                    bluecabel_y1 = random.choice(self.numbers1)
                    if self.positionentercabels[bluecabel_y1].get('color') == None:
                        self.positionentercabels[int(bluecabel_y1)].update({'color': 'Blue'})
                    self.bluecabel2 = True
                for i, el in enumerate(self.positionentercabels):
                    if self.positionentercabels[el]['color'] == 'Blue' and self.cooldown_blue1:
                        self.cooldown_blue1 = False
                        self.bluecabel_y2 = random.uniform(float(self.positionentercabels[el]['start']), float(self.positionentercabels[el]['end']))
                    elif self.positionentercabels[el]['color'] == 'Red' and self.cooldown_red1:
                        self.cooldown_red1 = False
                        self.redcabel_y2 = random.uniform(float(self.positionentercabels[el]['start']), float(self.positionentercabels[el]['end']))
                    elif self.positionentercabels[el]['color'] == 'Yellow' and self.cooldown_yellow1:
                        self.cooldown_yellow1 = False
                        self.yellowcabel_y2 = random.uniform(float(self.positionentercabels[el]['start']), float(self.positionentercabels[el]['end']))
        # else:
        #     self.cooldown = True
        #     self.cooldown2 = True
        #     self.cabelentertexture_red = arcade.load_texture('redcabelenter.png')
        #     self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter.png')
        #     self.cabelentertexture_blue = arcade.load_texture('bluecabelenter.png')

    def on_mouse_press(self, x, y, button, modifiers):
       if not self.is_active and self.puzzle == 1:
           if True:
                if ((self.height / 1.2) / float(self.yellowcabel_y) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.yellowcabel_y) + (self.height // 19)) and (((self.width // self.yellowcabel_x) - self.width // 13.2) <= x <= ((self.width // self.yellowcabel_x) + self.width // 13.2)) and not self.yellowcabelentered:

                    if not self.complete['Red']:
                        self.redcabelmouse = True
                        self.redcabelentered = False
                    if not self.complete['Blue']:
                        self.bluecabelmouse = True
                        self.bluecabelentered = False
                    if not self.complete['Yellow']:
                        self.yellowcabelentered = False
                        self.yellowcabelmouse = False
                    if self.complete['Yellow']:
                        self.yellowcabelentered = True
                elif ((self.height / 1.2) / float(self.redcabel_y) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.redcabel_y) + (self.height // 19)) and (((self.width // self.redcabel_x) - self.width // 13.2) <= x <= ((self.width // self.redcabel_x) + self.width // 13.2)) and not self.redcabelentered:

                    if not self.complete['Yellow']:
                        self.yellowcabelmouse = True
                        self.yellowcabelentered = False
                    if not self.complete['Blue']:
                        self.bluecabelmouse = True
                        self.bluecabelentered = False
                    if not self.complete['Red']:
                        self.redcabelentered = False
                        self.redcabelmouse = False
                    if self.complete['Red']:
                        self.redcabelentered = True

                elif ((self.height / 1.2) / float(self.bluecabel_y) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.bluecabel_y) + (self.height // 19)) and (((self.width // self.bluecabel_x) - self.width // 13.2) <= x <= ((self.width // self.bluecabel_x) + self.width // 13.2)) and not self.bluecabelentered:

                    if not self.complete['Yellow']:
                        self.yellowcabelmouse = True
                        self.yellowcabelentered = False
                    if not self.complete['Red']:
                        self.redcabelmouse = True
                        self.redcabelentered = False
                    if not self.complete['Blue']:
                        self.bluecabelentered = False
                        self.bluecabelmouse = False
                    if self.complete['Blue']:
                        self.bluecabelentered = True

           if ((self.width // 1.5) - self.width // 13.2) <= x <= ((self.width // 1.5) + self.width // 13.2):
               if ((self.height / 1.2) / float(self.yellowcabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.yellowcabel_y2) + (self.height // 19)):
                   if not self.yellowcabelmouse:
                       self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter_succes.png')
                       self.complete['Yellow'] = True
                       self.yellowcabelmouse = True
                       self.yellowwas_x = self.yellowcabel_x
                       self.yellowwas_y = self.yellowcabel_y
                       self.yellowcabel_x = 1.77
                       self.yellowcabel_y = self.yellowcabel_y2
               elif ((self.height / 1.2) / float(self.redcabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.redcabel_y2) + (self.height // 19)):
                   if not self.redcabelmouse:
                       self.cabelentertexture_red = arcade.load_texture('redcabelenter_succes.png')
                       self.complete['Red'] = True
                       self.redcabelmouse = True
                       self.redwas_x = self.redcabel_x
                       self.redwas_y = self.redcabel_y
                       self.redcabel_x = 1.77
                       self.redcabel_y = self.redcabel_y2
               elif ((self.height / 1.2) / float(self.bluecabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.bluecabel_y2) + (self.height // 19)):
                   if not self.bluecabelmouse:
                       self.cabelentertexture_blue = arcade.load_texture('bluecabelenter_succes.png')
                       self.complete['Blue'] = True
                       self.bluecabelmouse = True
                       self.bluewas_x = self.bluecabel_x
                       self.bluewas_y = self.bluecabel_y
                       self.bluecabel_x = 1.77
                       self.bluecabel_y = self.bluecabel_y2


    def on_mouse_motion(self, x, y, button, modifiers):
        self.x1, self.y1 = x, y


    def reset(self):
        self.complete = {'Red': False, 'Yellow': False, 'Blue': False}
        self.puzzle = 0
        self.cooldown2 = True
        self.cooldown = True
        self.bluecabelmouse = True
        self.redcabelmouse = True
        self.yellowcabelmouse = True
        self.Can_walk = True
        self.cooldown_red1 = True
        self.cooldown_blue1 = True
        self.cooldown_yellow1 = True
        self.cooldown_red = True
        self.cooldown_blue = True
        self.cooldown_yellow = True
        self.yellowcabelentered = False
        self.bluecabelentered = False
        self.redcabelentered = False
        self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter.png')
        self.cabelentertexture_blue = arcade.load_texture('bluecabelenter.png')
        self.cabelentertexture_red = arcade.load_texture('redcabelenter.png')
        if int(self.waves) >= 1 and self.score_no:
            self.waves -= 1
            self.x_electrical += 610
            self.tile.center_x = self.x_electrical

            if self.what_room and self.waves == 3:
                self.what_room = False

                self.room1_x += 1220
                self.room1.center_x = self.room1_x
                self.player.center_x = self.room2.center_x - 100
            elif self.what_room == False and self.waves == 2:
                self.what_room = True
                self.player.center_x = self.room1.center_x - 100

        if self.score_no:
            self.score += 1
            self.time2 -= 0.1
        self.time1 = self.time2
        self.electrical_mechanics()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.keyboard_E.center_x = self.player.center_x
        self.keyboard_E.center_y = self.player.center_y + 90
        self.is_active = False
        self.electrical_mechanics()
        # --- Мир ---
        self.world_camera.use()
        self.cabels.draw()
        self.walls.draw()
        self.mechanics.draw()
        self.player_list.draw()

        if self.keyboard_Number == 1:
            self.keyboard_1.draw()

        if self.time1 <= 0:
            self.score_no = False
            self.reset()
        if self.complete['Red'] and self.complete['Blue'] and self.complete['Yellow']:
            self.score_no = True
            self.reset()
        # --- GUI ---
        self.gui_camera.use()
        self.batch.draw()
        if self.puzzle == 1:
            self.puzzle_1 = arcade.draw_texture_rect(self.puzzle_1_texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width // 2, self.height // 1.2))
            self.text_timer.text = f"Time: {self.time1:.1f}"
            self.text_timer.draw()
            if self.redcabel1 and self.redcabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('redcabel.png'), arcade.rect.XYWH(self.width // self.redcabel_x, (self.height / 1.2) / float(self.redcabel_y), self.width // 7, self.height // 9))
                    if self.complete['Red']:
                        arcade.draw_line((self.width // self.redwas_x) - 90, (self.height / 1.2) / float(self.redwas_y), self.width // self.redcabel_x, (self.height / 1.2) / float(self.redcabel_y),
                                         arcade.color.RED, 40)
                except Exception as e:
                    print(e)
            else:
                arcade.draw_line((self.width // self.redcabel_x) - 90, (self.height / 1.2) / float(self.redcabel_y), self.x1, self.y1, arcade.color.RED, 40)
            if self.yellowcabel1:
                    if self.yellowcabelmouse:
                        try:
                            arcade.draw_texture_rect(arcade.load_texture('yellowcabel.png'), arcade.rect.XYWH(self.width // self.yellowcabel_x, (self.height / 1.2) / float(self.yellowcabel_y), self.width // 7, self.height // 9))
                            if self.complete['Yellow']:
                                arcade.draw_line((self.width // self.yellowwas_x) - 90,
                                                 (self.height / 1.2) / float(self.yellowwas_y),
                                                 self.width // self.yellowcabel_x,
                                                 (self.height / 1.2) / float(self.yellowcabel_y),
                                                 arcade.color.YELLOW, 40)
                        except Exception as e:
                            print(e)
                    else:
                        arcade.draw_line((self.width // self.yellowcabel_x) - 90, (self.height / 1.2) / float(self.yellowcabel_y), self.x1, self.y1, arcade.color.YELLOW, 40)
            if self.bluecabel1 and self.bluecabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('bluecabel.png'), arcade.rect.XYWH(self.width // self.bluecabel_x, (self.height / 1.2) / float(self.bluecabel_y), self.width // 7, self.height // 9))
                    if self.complete['Blue']:
                        arcade.draw_line((self.width // self.bluewas_x) - 90, (self.height / 1.2) / float(self.bluewas_y), self.width // self.bluecabel_x, (self.height / 1.2) / float(self.bluecabel_y),
                                         arcade.color.BLUE, 40)
                except Exception as e:
                    print(e)
            else:
                arcade.draw_line((self.width // self.bluecabel_x) - 90, (self.height / 1.2) / float(self.bluecabel_y), self.x1, self.y1, arcade.color.BLUE, 40)
            if self.redcabel2:
                try:
                    arcade.draw_texture_rect(self.cabelentertexture_red, arcade.rect.XYWH(self.width // 1.5, (self.height / 1.2) / float(self.redcabel_y2), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)
            if self.yellowcabel2:
                try:
                    arcade.draw_texture_rect(self.cabelentertexture_yellow, arcade.rect.XYWH(self.width // 1.5, (self.height / 1.2) / float(self.yellowcabel_y2), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)
            if self.bluecabel2:
                try:
                    arcade.draw_texture_rect(self.cabelentertexture_blue, arcade.rect.XYWH(self.width // 1.5, (self.height / 1.2) / float(self.bluecabel_y2), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)


    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.E and int(self.keyboard_Number) == 1 and self.Can_walk:
            self.puzzle = 1
            self.Can_walk = False
        # elif key == arcade.key.E and int(self.keyboard_Number) == 1 and not self.Can_walk:
        #     self.puzzle = 0
        #     self.bluecabelmouse = True
        #     self.redcabelmouse = True
        #     self.yellowcabelmouse = True
        #     self.Can_walk = True

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False


    def on_update(self, dt: float):
        self.player_list.update(dt, self.keys_pressed)
        self.player_list.update_animation()
        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()
        if self.puzzle == 1:
            self.time1 -= 0.025
        # Собираем монетки и проверяем опасности
        if arcade.check_for_collision_with_list(self.player, self.mechanics):
            self.keyboard_Number = 1
        else:
            self.keyboard_Number = 0

        # Камера — плавно к игроку и в рамках мира
        target = (self.player.center_x, self.player.center_y)
        cam_x = target[0]
        cam_y = target[1]

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)

        # Обновим счёт
        self.text_score = arcade.Text(f"Score: {self.score}",
                                      16, SCREEN_H - 36, arcade.color.SKY_BLUE,
                                      30, batch=self.batch)


def main():
    game = Platformer()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()