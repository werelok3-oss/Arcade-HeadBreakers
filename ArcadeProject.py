import arcade
from arcade.camera import Camera2D
from pyglet.graphics import Batch
import random
import sqlite3
import enum
from arcade.gui import UIManager,UITextureButton, UILabel, UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIBoxLayout  # А это менеджеры компоновки, как в pyQT

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
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
SCREEN_W, SCREEN_H = 800, 600

SCREEN_TITLE = "BOSS BREAKERS"
CHARACTER_SCALING = 1


class Level_1(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_hp = 5
        self.w = SCREEN_WIDTH
        self.h = SCREEN_HEIGHT
        self.fonts = arcade.Sprite
        self.fonts_2 = arcade.Sprite
        self.fonts_list = arcade.SpriteList()
        self.attack_list = arcade.SpriteList()
        self.texture = arcade.load_texture("puzataya_arena.png")
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.hero = arcade.Sprite("gg_cowboy.png", scale=0.2)
        self.player_list.append(self.hero)
        self.enemy_list = arcade.SpriteList()
        self.gg_hp = 5
        self.boss1_hp = 100
        self.bullet_list = arcade.SpriteList()
        self.total_time = 0.0
        self.attack_list_2 = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.w // 2, self.h // 2, self.w, self.h))
        arcade.start_render()
        if self.player_list is not None:
            self.player_list.draw()
            self.player_sprite.draw()
        self.player_sprite.center_x += 1
        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.center_x = 0
        if self.enemy_list is not None:
            self.enemy_list.draw()

    def setup(self):
        self.hero_x = SCREEN_WIDTH // 2
        self.hero_y = SCREEN_HEIGHT // 5
        self.hero_speed = 300
        self.keys_pressed = set()
        self.bullets = []
        self.sound = arcade.load_sound("boss_1_music.mp3")
        enemy = arcade.Sprite("boss_1.png", 0.3)
        enemy.center_x = SCREEN_WIDTH // 2 + 2
        enemy.center_y = SCREEN_HEIGHT // 2 - 7
        self.enemy_list.append(enemy)

        # Создаём физический движок
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.hero,
            self.wall_list
        )

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.SPACE and (self.player_list == None or self.enemy_list == None):
            menu = Menu()
            # self.manager.disable()
            # self.manager.clear()

            self.window.show_view(menu)


    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.bullet_list is not None: # Создаём пулю
                bullet = arcade.Sprite("bullet.png", 0.5)

                # Позиция пули — перед персонажем
                bullet.center_x = self.hero.center_x
                bullet.center_y = self.hero.center_y

                # Рассчитываем направление к курсору
                dx = x - self.hero.center_x
                dy = y - self.hero.center_y
                distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Избегаем деления на 0

                # Устанавливаем скорость
                bullet.change_x = dx / distance * 10
                bullet.change_y = dy / distance * 10

                self.bullet_list.append(bullet)

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.attack_list is not None:  # Создаём пулю
                attack_1 = arcade.Sprite("punch.png", 0.4)

                # Позиция пули — перед персонажем
                attack_1.center_x = SCREEN_WIDTH // 2 + 2
                attack_1.center_y = SCREEN_HEIGHT // 2

                # Рассчитываем направление к курсору
                dx = self.hero_x - (SCREEN_WIDTH // 2 + 2)
                dy = self.hero_y - (SCREEN_HEIGHT // 2)
                distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Избегаем деления на 0

                # Устанавливаем скорость
                attack_1.change_x = dx / distance * 10
                attack_1.change_y = dy / distance * 10

                self.attack_list.append(attack_1)

    def on_update(self, delta_time):
        if self.total_time == 0:
            self.backgound_player = self.sound.play(loop=True, volume=0.5)
        dx, dy = 0, 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= self.hero_speed * delta_time
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += self.hero_speed * delta_time
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            dy += self.hero_speed * delta_time
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            dy -= self.hero_speed * delta_time

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            factor = 0.7071  # ≈ 1/√2
            dx *= factor
            dy *= factor

        self.hero_x += dx
        self.hero_y += dy

        # Ограничение в пределах экрана
        self.hero_x = max(20, min(SCREEN_WIDTH - 20, self.hero_x))
        self.hero_y = max(20, min(SCREEN_HEIGHT - 20, self.hero_y))

        if self.bullet_list is not None:
            for bullet in self.bullet_list:
                bullet.center_x += bullet.change_x
                bullet.center_y += bullet.change_y

                # Удаляем пули за пределами экрана
                if (bullet.bottom > SCREEN_HEIGHT or bullet.top < 0 or
                        bullet.right < 0 or bullet.left > SCREEN_WIDTH):
                    bullet.remove_from_sprite_lists()

                # Проверяем столкновение пуль с врагами
            if self.bullet_list != None and self.enemy_list != None:
                for bullet in self.bullet_list:
                    if bullet and self.enemy_list:
                        try:
                            enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                            if enemy_hit_list:
                                for enemy in enemy_hit_list:
                                    bullet.remove_from_sprite_lists()  # Удаляем пулю
                                    self.boss1_hp -= 1
                                    if self.boss1_hp <= 0:
                                        self.enemy_list = None  # Удаляем врага
                                        self.attack_list = None
                                        self.attack_list_2 = None
                        except Exception as e:
                            print(e)

            if self.enemy_list is not None:
                for enemy1 in self.enemy_list:
                    player_hit_list = arcade.check_for_collision_with_list(enemy1, self.player_list)
                    for player in player_hit_list:
                        self.player_hp -= 1
                        if self.player_hp <= 0:
                            self.player_list = None
                            self.bullet_list = None

        if self.attack_list is not None:
            for attack_1 in self.attack_list:
                attack_1.center_x += attack_1.change_x
                attack_1.center_y += attack_1.change_y

                # Удаляем пули за пределами экрана
                if (attack_1.bottom > SCREEN_HEIGHT or attack_1.top < 0 or
                    attack_1.right < 0 or attack_1.left > SCREEN_WIDTH):
                    attack_1.remove_from_sprite_lists()

        # Проверяем столкновение пуль с врагами
        if self.attack_list is not None and self.player_list is not None:
            for hero in self.player_list:
                player_hit_list = arcade.check_for_collision_with_list(hero, self.attack_list)
                for attack_1 in player_hit_list:
                    attack_1.remove_from_sprite_lists()  # Удаляем пулю
                    self.player_hp -= 1
                    if self.player_hp <= 0:
                        self.player_list = None
                        self.bullet_list = None

        self.total_time += delta_time

        if self.attack_list_2 is not None:
            if (self.total_time >= 5 and self.total_time <= 15) or (self.total_time >= 35 and self.total_time <= 45):
                self.attack_list_2.clear()
                for i in range(2):
                    attack_2_1 = arcade.Sprite("kulak_vertikal.png", SCREEN_HEIGHT / 900)
                    if i == 0:
                    # Позиция пули — перед персонажем
                        attack_2_1.center_x = SCREEN_WIDTH // 10
                        attack_2_1.center_y = SCREEN_HEIGHT // 2
                    elif i == 1:
                        attack_2_1.center_x = SCREEN_WIDTH - SCREEN_WIDTH // 10
                        attack_2_1.center_y = SCREEN_HEIGHT // 2
                    self.attack_list_2.append(attack_2_1)

            elif (self.total_time >= 20 and self.total_time <= 30) or (
                    self.total_time >= 50 and self.total_time <= 60):
                self.attack_list_2.clear()
                for i in range(2):
                    attack_2_2 = arcade.Sprite("kulak_horizontal.png", SCREEN_WIDTH / 1000)

                    if i == 0:
                        # Позиция пули — перед персонажем
                        attack_2_2.center_x = SCREEN_WIDTH // 2
                        attack_2_2.center_y = SCREEN_HEIGHT // 7

                    elif i == 1:
                        attack_2_2.center_x = SCREEN_WIDTH // 2
                        attack_2_2.center_y = SCREEN_HEIGHT - SCREEN_HEIGHT // 7

                    self.attack_list_2.append(attack_2_2)

        # Проверяем столкновение пуль с врагами
            if self.attack_list_2 is not None and self.player_list is not None:
                for hero in self.player_list:
                    player_hit_list = arcade.check_for_collision_with_list(hero, self.attack_list_2)
                    for attack_2 in player_hit_list:
                        attack_2.remove_from_sprite_lists()  # Удаляем пулю
                        self.player_hp -= 1
                        if self.player_hp <= 0:
                            self.player_list = None  # Удаляем врага
                            self.bullet_list = None

        if self.total_time > 60:
            self.player_list = None

        self.batch = Batch()
        if self.player_list == None and self.texture != self.fonts.texture:
            self.fonts = arcade.create_text_sprite(f"Поражение!\nSpace для выхода.",
                                                   font_size=20)
            arcade.stop_sound(self.backgound_player)
            self.texture = self.fonts.texture
            self.enemy_list.clear()
            self.attack_list = None
            self.bullet_list = None
            self.attack_list_2 = None
            self.fonts_list.append(self.fonts)
        if self.enemy_list == None and self.texture != self.fonts_2.texture:
            self.fonts_2 = arcade.create_text_sprite(f"Победа!\nОбщее время: {self.total_time // 1} сек.\nSpace для выхода.",
                                                     font_size=20)
            arcade.stop_sound(self.backgound_player)
            self.fonts_list.append(self.fonts_2)
            self.texture = self.fonts_2.texture
            self.player_list.clear()
            self.bullet_list = None
            self.attack_list = None
            self.attack_list_2 = None
        self.physics_engine.update()

    def on_draw(self):
        self.clear()  # Иначе будет оставаться след от фигуры
        self.batch.draw()
        self.fonts_list.draw()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.w // 2, self.h // 2, self.w, self.h))
        self.hero.center_x, self.hero.center_y = self.hero_x, self.hero_y
        if self.player_list is not None:
            self.player_list.draw()
        self.wall_list.draw()
        if self.bullet_list is not None:
            self.bullet_list.draw()
        if self.enemy_list != None and self.attack_list != None and self.attack_list_2 != None:
            self.enemy_list.draw()
            self.attack_list.draw()
            self.attack_list_2.draw()


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = 1.0
        self.speed = 300
        self.health = 100
        # Жёстко ставим персонажа в центр экрана (лучше передавать позицию в __init__)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

    def update(self, delta_time):
        """ Перемещение персонажа """
        self.center_x += 50 * delta_time
        self.center_y += 50 * delta_time

        # Ограничение в пределах экрана
        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
        self.center_y = max(self.height / 2, min(SCREEN_HEIGHT - self.height / 2, self.center_y))


class Hero1(arcade.Sprite):
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
        self.center_x = SCREEN_W // 2
        self.center_y = SCREEN_H // 2

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


class Platformer(arcade.View):
    def __init__(self, infinity=False):
        super().__init__()
        self.start_time: float = 0.0
        self.texture = arcade.load_texture('backgroung_texture.png')
        # Камеры
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.infinity = infinity
        self.total_time = 0
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
        self.manager_win = UIManager()
        self.manager_win.enable()
        self.box_layout_choice1 = UIBoxLayout(vertical=False, space_between=40, x=(self.window.width / 3),
                                             y=(self.window.height / 3))  # Вертикальный сте
        # Добавим все виджеты в box, потом box в anchor
        self.manager_win.add(self.box_layout_choice1)  # Всё в manager
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали
        # Layout для организации — как полки в шкафу
        self.box_layout_choice = UIBoxLayout(vertical=False, space_between=40, x=(self.window.width / 120), y=(self.window.height / 1.191))  # Вертикальный сте
        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниж
        self.manager.add(self.box_layout_choice)  # Всё в manager

    def setup_widgets(self):


        play_texture_button3 = arcade.load_texture("menubutton.png")
        self.back_button3 = UITextureButton(texture=play_texture_button3,
                                            scale=SCREEN_WIDTH / 13000)

        play_texture_button = arcade.load_texture("play_again_button.png")
        self.back_button = UITextureButton(texture=play_texture_button,
                                            scale=SCREEN_WIDTH / 13000)
        play_texture_button1 = arcade.load_texture("Back_to_menu.png")
        self.back_button1 = UITextureButton(texture=play_texture_button1,
                                           scale=SCREEN_WIDTH / 13000)
        play_texture_button4 = arcade.load_texture("you_won_label.png")
        self.back_button4 = UITextureButton(texture=play_texture_button4,
                                           scale=SCREEN_WIDTH / 13000)
        self.text = UILabel(text=f'Your time: {self.total_time} sec', x=(SCREEN_WIDTH / 2.6), y=(SCREEN_HEIGHT / 2), text_color=arcade.color.BLACK, font_size=(SCREEN_WIDTH // 40))
        self.text1 = UILabel(text=f'Your best time: {0} sec', x=(SCREEN_WIDTH / 2.7), y=(SCREEN_HEIGHT / 2.3),
                            text_color=arcade.color.BLACK, font_size=(SCREEN_WIDTH // 60))
        self.manager_win.add(self.text1)
        self.manager_win.add(self.text)
        self.manager_win.add(self.box_layout_choice1)

        self.back_button4.on_click = lambda event: print('lol')
        self.back_button4.center_x, self.back_button4.center_y = (self.window.width / 2), (self.window.height / 1.5)
        self.manager_win.add(self.back_button4)
        self.size1 = self.back_button1.size
        self.back_button1.on_click = lambda event: self.leave()
        self.box_layout_choice1.add(self.back_button1)
        self.size2 = self.back_button.size
        self.back_button.on_click = lambda event: self.play_again()
        self.box_layout_choice1.add(self.back_button)
        self.size3 = self.back_button3.size
        self.back_button3.on_click = lambda event: self.leave()
        self.box_layout_choice.add(self.back_button3)
        self.manager_win.add(self.box_layout_choice1)


    def play_again(self):
        self.manager_win.disable()
        self.manager.disable()
        Platformer()
        self.keyboard_1.pop(0)
        self.mechanics.pop(0)
        self.setup()

    def leave(self):
        menu = Menu()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(menu)


    def setup(self):
        self.wave = 1
        self.total_time = 0
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
        self.room3_x = 1520
        self.what_room = 0
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
        self.room3 = arcade.Sprite('background.png', scale=0.4)
        self.room3.center_x = self.room3_x
        self.room3.center_y = 250
        self.cabels.append(self.room1)
        self.cabels.append(self.room2)
        self.cabels.append(self.room3)
        self.start = True
        self.won = False
        # --- Игрок ---
        self.player_list.clear()
        self.player = Hero1()
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
                                      (self.width / 8) * 6, (self.height / 2), arcade.color.BRONZE, 20)
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
        for y in range(64, 64 + 64 * 6, 64):
            self.s = arcade.Sprite("ground.png", 0.05)
            self.s.center_x = 610
            self.s.center_y = y
            self.walls.append(self.s)
        for y in range(64, 64 + 64 * 6, 64):
            self.s = arcade.Sprite("ground.png", 0.05)
            self.s.center_x = 1220
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
        if self.score_no:
            if self.infinity:
                self.x_electrical += 610
                self.tile.center_x = self.x_electrical
                if self.what_room == 0:
                    self.what_room = 1
                    if not self.start:
                        self.room3.center_x += 1830
                        self.walls.move(change_x=610, change_y=0)
                    self.player.center_x = self.room2.center_x - 100
                elif self.what_room == 1:
                    self.what_room = 2
                    self.room1.center_x += 1830
                    if self.start:
                        self.start = False
                    self.walls.move(change_x=610, change_y=0)
                    self.player.center_x = self.room3.center_x - 100
                elif self.what_room == 2:
                    self.what_room = 0
                    self.room2.center_x += 1830
                    self.walls.move(change_x=610, change_y=0)
                    self.player.center_x = self.room1.center_x - 100

            else:
                if int(self.waves) >= 1:
                    self.waves -= 1
                    self.x_electrical += 610
                    self.tile.center_x = self.x_electrical

                    if self.what_room == 0 and self.waves == 3:
                        self.what_room = 1
                        self.player.center_x = self.room2.center_x - 100
                    elif self.what_room == 1 and self.waves == 2:
                        self.what_room = 2
                        self.player.center_x = self.room3.center_x - 100
                if self.waves <= 1:
                    self.won = True
                    self.score = 0
                    con = sqlite3.connect("your_best_time.db")

                    # Создание курсора
                    cur = con.cursor()

                    # Выполнение запроса и получение всех результатов
                    result = cur.execute("""SELECT time FROM best_time""").fetchall()

                    if result:
                        for elem in result:
                            for el in elem:
                                try:
                                    if float(self.total_time) <= float(el):
                                        cur.execute(f"""UPDATE best_time
                                        SET time = '{self.total_time:.1f}'""")
                                        con.commit()
                                        self.text1.text = f'Your best time: {self.total_time:.1f} sec'
                                    else:
                                        self.text1.text = f'Your best time: {el} sec'
                                except Exception as e:
                                    print(e)
                    else:
                        cur.execute(f'''INSERT INTO best_time(time) VALUES({self.total_time:.1f})''')
                        self.text1.text = f'Your best time: {self.total_time:.1f} sec'
                        con.commit()

                    con.close()
                    self.text.text = f'Your time: {self.total_time:.1f} sec'



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
        if self.won:
            arcade.draw_texture_rect(arcade.load_texture('backround.png'), arcade.rect.XYWH((SCREEN_WIDTH / 200) + self.player.center_x, (SCREEN_HEIGHT / 3), (SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2)))
            self.manager_win.draw()
            self.manager_win.enable()
            self.manager.disable()
        else:
            self.manager_win.disable()
            self.manager.enable()
            self.manager.draw()
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
            self.text_timer.text = f"Time: {self.time1:.1f} sec"
            self.text_timer.draw()
            if self.redcabel1 and self.redcabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('redcabel.png'), arcade.rect.XYWH(self.width // self.redcabel_x, (self.height / 1.2) / float(self.redcabel_y), self.width // 7, self.height // 9))
                    if self.complete['Red']:
                        arcade.draw_line((self.width // self.redwas_x) - (self.width // 18), (self.height / 1.2) / float(self.redwas_y), self.width // self.redcabel_x, (self.height / 1.2) / float(self.redcabel_y),
                                         arcade.color.RED, 40)
                except Exception as e:
                    print(e)
            else:
                arcade.draw_line((self.width // self.redcabel_x) - (self.width / 18), (self.height / 1.2) / float(self.redcabel_y), self.x1, self.y1, arcade.color.RED, 40)
            if self.yellowcabel1:
                    if self.yellowcabelmouse:
                        try:
                            arcade.draw_texture_rect(arcade.load_texture('yellowcabel.png'), arcade.rect.XYWH(self.width // self.yellowcabel_x, (self.height / 1.2) / float(self.yellowcabel_y), self.width // 7, self.height // 9))
                            if self.complete['Yellow']:
                                arcade.draw_line((self.width // self.yellowwas_x) - (self.width / 18),
                                                 (self.height / 1.2) / float(self.yellowwas_y),
                                                 self.width // self.yellowcabel_x,
                                                 (self.height / 1.2) / float(self.yellowcabel_y),
                                                 arcade.color.YELLOW, 40)
                        except Exception as e:
                            print(e)
                    else:
                        arcade.draw_line((self.width // self.yellowcabel_x) - (self.width / 18), (self.height / 1.2) / float(self.yellowcabel_y), self.x1, self.y1, arcade.color.YELLOW, 40)
            if self.bluecabel1 and self.bluecabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('bluecabel.png'), arcade.rect.XYWH(self.width // self.bluecabel_x, (self.height / 1.2) / float(self.bluecabel_y), self.width // 7, self.height // 9))
                    if self.complete['Blue']:
                        arcade.draw_line((self.width // self.bluewas_x) - (self.width / 18), (self.height / 1.2) / float(self.bluewas_y), self.width // self.bluecabel_x, (self.height / 1.2) / float(self.bluecabel_y),
                                         arcade.color.BLUE, 40)
                except Exception as e:
                    print(e)
            else:
                arcade.draw_line((self.width // self.bluecabel_x) - (self.width / 18), (self.height / 1.2) / float(self.bluecabel_y), self.x1, self.y1, arcade.color.BLUE, 40)
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
        self.total_time += dt
        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()
        if self.puzzle == 1:
            self.time1 -= 0.025
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
                                      SCREEN_W / 20, SCREEN_H / 2, arcade.color.SKY_BLUE,
                                      30, batch=self.batch)

class Info(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.YELLOW)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.box_layout = UIBoxLayout(vertical=True, space_between=5, align='left', size_hint=(1, -1))  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.manager.add(self.box_layout)  # Всё в manager

    def setup_widgets(self):
        play_texture_button = arcade.load_texture("normal_button_back.png")
        play_texture_hovered = arcade.load_texture("hover_button_back.png")
        play_button = UITextureButton(texture=play_texture_button,
                                        texture_hovered=play_texture_hovered,
                                        scale=SCREEN_WIDTH / 2100)
        play_button.on_click = lambda event: self.back() # Не только лямбду, конечно
        self.box_layout.add(play_button)
        text = UILabel(text='Soon...', x=400, y=400, text_color=arcade.color.BLACK, font_size=(SCREEN_WIDTH // 40))
        self.manager.add(text)

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def back(self):
        menu = Menu()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(menu)

class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)
        self.texture = arcade.load_texture('lobby.png')

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.box_layout = UIBoxLayout(vertical=True, space_between=5, align='left')  # Вертикальный стек
        self.box_layout.size_hint = ()

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.manager.add(self.box_layout)  # Всё в manager


    def setup_widgets(self):
        play_texture_button = arcade.load_texture("normal_button_play.png")
        play_texture_hovered = arcade.load_texture("hover_button_play.png")
        play_button = UITextureButton(texture=play_texture_button,
                                        texture_hovered=play_texture_hovered,
                                        scale=SCREEN_WIDTH / 2100)
        play_button.on_click = lambda event: self.play()  # Не только лямбду, конечно
        self.box_layout.add(play_button)
        info_texture_button = arcade.load_texture("normal_button_info.png")
        info_texture_hovered = arcade.load_texture("hover_button_info.png")
        info_texture_button = UITextureButton(texture=info_texture_button,
                                              texture_hovered=info_texture_hovered,
                                              scale=SCREEN_WIDTH / 2530)
        info_texture_button.on_click = lambda event: self.info()  # Не только лямбду, конечно
        self.box_layout.add(info_texture_button)
        exit_texture_button = arcade.load_texture("normal_button_exit.png")
        exit_texture_hovered = arcade.load_texture("hover_button_exit.png")
        exit_texture_button = UITextureButton(texture=exit_texture_button,
                                              texture_hovered=exit_texture_hovered,
                                              scale=SCREEN_WIDTH / 2960)
        exit_texture_button.on_click = lambda event: self.are_you_sure_to_leave()  # Не только лямбду, конечно
        self.box_layout.add(exit_texture_button)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.manager.draw()  # Рисуй GUI поверх всего

    def info(self):
        info = Info()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(info)

    def play(self):
        play = Choice()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(play)

    def are_you_sure_to_leave(self):
        message_box = UIMessageBox(
            width=SCREEN_WIDTH / 3, height=SCREEN_WIDTH / 7,
            message_text="EXIT\nAre you sure?",
            buttons=("Yes", "No")
        )
        message_box.on_action = self.on_message_button
        self.manager.add(message_box)

    def on_message_button(self, message):
        if ('Yes' or 'Да') in str(message):
            self.window.close()

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает

class Choice(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BRONZE)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.box_layout = UIBoxLayout(vertical=True, space_between=5, align='left')  # Вертикальный стек
        self.box_layout_choice = UIBoxLayout(vertical=False, space_between=5, x=SCREEN_WIDTH / 7, y=SCREEN_HEIGHT / 2)  # Вертикальный сте
        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже
        self.manager.add(self.box_layout)  # Всё в manager
        self.manager.add(self.box_layout_choice)  # Всё в manager

    def setup_widgets(self):
        back_texture_button = arcade.load_texture("normal_button_back.png")
        back_texture_hovered = arcade.load_texture("hover_button_back.png")
        back_button = UITextureButton(texture=back_texture_button,
                                        texture_hovered=back_texture_hovered,
                                        scale=SCREEN_WIDTH / 2100)
        play_texture_button1 = arcade.load_texture("what_room.png")
        play_texture_hovered1 = arcade.load_texture("door_puzzle_down.png")
        self.play_button1 = UITextureButton(texture=play_texture_button1,
                                            texture_hovered=play_texture_hovered1,
                                            scale=SCREEN_WIDTH / 4000)
        play_texture_button3 = arcade.load_texture("what_room.png")
        play_texture_hovered3 = arcade.load_texture("door_wonders_farmers.png")
        self.play_button3 = UITextureButton(texture=play_texture_button3,
                                      texture_hovered=play_texture_hovered3,
                                      scale=SCREEN_WIDTH / 4000)
        play_texture_button2 = arcade.load_texture("what_room.png")
        play_texture_hovered2 = arcade.load_texture("door_breaker_dungeon.png")
        self.play_button2 = UITextureButton(texture=play_texture_button2,
                                            texture_hovered=play_texture_hovered2,
                                            scale=SCREEN_WIDTH / 4000)
        self.size2 = self.play_button2.size
        self.size3 = self.play_button3.size
        self.play_button2.on_click = lambda event: self.choice_Breaker_Dungeon()
        self.play_button3.on_click = lambda event: print('hi')
        self.size1 = self.play_button1.size
        self.play_button1.on_click = lambda event: self.choice_puzzle_down()
        self.box_layout_choice.add(self.play_button1)
        self.box_layout_choice.add(self.play_button2)
        self.box_layout_choice.add(self.play_button3)
        back_button.on_click = lambda event: self.back() # Не только лямбду, конечно
        self.box_layout.add(back_button)

    def choice_puzzle_down(self):
        choice = Choice_puzzle_down()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(choice)

    def choice_Breaker_Dungeon(self):
        choice = Level_1()
        choice.setup()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(choice)

    def on_draw(self):
        self.clear()
        if self.play_button1.hovered:
            self.play_button1.size = (SCREEN_WIDTH / 2.5, SCREEN_WIDTH / 2.5)
            self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
        else:
            self.play_button1.size = self.size1
        if self.play_button2.hovered:
            self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
            self.play_button2.size = (SCREEN_WIDTH / 3, SCREEN_WIDTH / 3)
        else:
            self.play_button2.size = self.size2
        if self.play_button3.hovered:
            self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
            self.play_button3.size = (SCREEN_WIDTH / 3, SCREEN_WIDTH / 3)
        else:
            self.play_button3.size = self.size3
        self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
        self.manager.draw()  # Рисуй GUI поверх всего

    def back(self):
        menu = Menu()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(menu)

class Choice_puzzle_down(arcade.View):
    def __init__(self, can_press=False):
        super().__init__()
        arcade.set_background_color(arcade.color.RED)
        self.y1 = 400
        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали
        # Layout для организации — как полки в шкафу
        self.box_layout = UIBoxLayout(vertical=True, space_between=5, align='left')  # Вертикальный стек
        self.box_layout_choice = UIBoxLayout(vertical=False, space_between=40, x=SCREEN_WIDTH / 7, y=SCREEN_HEIGHT / 2)  # Вертикальный сте
        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.manager.add(self.box_layout)  # Всё в manager
        self.manager.add(self.box_layout_choice)  # Всё в manager

    def setup_widgets(self):
        back_texture_button = arcade.load_texture("normal_button_back.png")
        back_texture_hovered = arcade.load_texture("hover_button_back.png")
        back_button = UITextureButton(texture=back_texture_button,
                                        texture_hovered=back_texture_hovered,
                                        scale=SCREEN_WIDTH / 2100)
        play_texture_button1 = arcade.load_texture("normal_button_puzzle_down.png")
        self.play_button1 = UITextureButton(texture=play_texture_button1,
                                            scale=SCREEN_WIDTH / 3900)
        play_texture_button3 = arcade.load_texture("infinity_button_puzzle_down.png")
        self.play_button3 = UITextureButton(texture=play_texture_button3,
                                      scale=SCREEN_WIDTH / 3900)

        self.size1 = self.play_button1.size
        self.size3 = self.play_button3.size
        self.play_button3.on_click = lambda event: self.infinity()
        self.play_button1.on_click = lambda event: self.normal()
        self.box_layout_choice.add(self.play_button1)
        self.box_layout_choice.add(self.play_button3)
        back_button.on_click = lambda event: self.back() # Не только лямбду, конечно
        self.box_layout.add(back_button)

    def on_draw(self):
        self.clear()
        if self.play_button1.hovered:
            self.play_button1.size = (SCREEN_WIDTH / 2.5, SCREEN_WIDTH / 2.5)
            self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
        else:
            self.play_button1.size = self.size1
        if self.play_button3.hovered:
            self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
            self.play_button3.size = (SCREEN_WIDTH / 2.5, SCREEN_WIDTH / 2.5)
        else:
            self.play_button3.size = self.size3
        self.box_layout_choice.center_y = SCREEN_HEIGHT / 2
        self.manager.draw()  # Рисуй GUI поверх всего

    def infinity(self):
        game = Platformer(True)
        game.setup()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(game)

    def normal(self):
        game = Platformer()
        game.setup()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(game)

    def back(self):
        menu = Choice()
        self.manager.disable()
        self.manager.clear()
        self.window.show_view(menu)

def main():
    game = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, 'Menu')
    game.center_window()
    menu = Menu()
    game.show_view(menu)
    arcade.run()

if __name__ == "__main__":
    main()
