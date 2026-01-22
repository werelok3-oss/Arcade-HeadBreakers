import arcade
from arcade.camera import Camera2D
from pyglet.graphics import Batch
import random
import time
SCREEN_W = 1280
SCREEN_H = 720
TITLE = "HeadBreakers"

# Физика и движение
GRAVITY = 2            # Пикс/с^2
MOVE_SPEED = 6
LADDER_SPEED = 3        # Скорость по лестнице
CAMERA_LERP = 0.12        # Плавность следования камеры
WORLD_COLOR = arcade.color.SKY_BLUE




class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, antialiasing=True)
        arcade.set_background_color(WORLD_COLOR)
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
        self.text_info = arcade.Text("WASD/стрелки — ходьба/лестницы • SPACE — прыжок",
                                     16, 16, arcade.color.GRAY, 14, batch=self.batch)


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
        self.left_1 = arcade.load_texture('гг_влево_1.png')
        self.left_1.size = (350, 190)
        self.left_2 = arcade.load_texture('гг_влево_2.png')
        self.left_2.size = (350, 190)
        self.right_1 = arcade.load_texture('гг_вправо_1.png')
        self.right_1.size = (350, 190)
        self.right_2 = arcade.load_texture('гг_вправо_2.png')
        self.right_2.size = (350, 190)
        self.current_texture = 0
        self.is_walking = False
        self.center_x1 = SCREEN_W // 2
        self.center_y1 = SCREEN_H // 2
        self.textureleft = [self.left_1, self.left_2]
        self.textureright = [self.right_1, self.right_2]
        self.cabelentertexture_red = arcade.load_texture('redcabelenter.png')
        self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter.png')
        self.cabelentertexture_blue = arcade.load_texture('bluecabelenter.png')
        self.positioncabels = {1: {'start': 1, 'end': 1.3, 'color': None},
                               2: {'start': 1.7, 'end': 2.3, 'color': None},
                               3: {'start': 3, 'end': 3.4, 'color': None}}
        self.positionentercabels = {1: {'start': 1, 'end': 1.3, 'color': None},
                               2: {'start': 1.7, 'end': 2.3, 'color': None},
                               3: {'start': 3, 'end': 3.4, 'color': None}}
        # self.electrical_mechanics()
        # --- Игрок ---
        self.player_list.clear()
        self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                    scale=0.8)
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
        self.tile.center_x = 800
        self.tile.center_y = 150
        self.mechanics.append(self.tile)
        # Пол из «травы»
        for x in range(0, 1600, 64):
            tile = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            tile.center_x = x
            tile.center_y = 64
            self.walls.append(tile)


        # Пара столбиков-стен
        for y in range(64, 64 + 64 * 3, 64):
            s = arcade.Sprite(":resources:images/tiles/stoneCenter.png", 0.5)
            s.center_x = 0
            s.center_y = y
            self.walls.append(s)

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
                    print(self.positioncabels)
                    self.cooldown2 = False
                    self.colors2 = ['Yellow', 'Red', 'Blue']
                    self.numbers = [1, 2, 3]
                    self.positioncabels = {1: {'start': 1.3, 'end': 1.3, 'color': None},
                                           2: {'start': 1.7, 'end': 2.3, 'color': None},
                                           3: {'start': 3, 'end': 3.4, 'color': None}}


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
                        print(self.bluecabel_y, ' -  Blue')
                    elif self.positioncabels[el]['color'] == 'Red' and self.cooldown_red:
                        self.cooldown_red = False
                        self.redcabel_y = random.uniform(float(self.positioncabels[el]['start']), float(self.positioncabels[el]['end']))
                        print(self.redcabel_y, ' -  Red')
                    elif self.positioncabels[el]['color'] == 'Yellow' and self.cooldown_yellow:
                        self.cooldown_yellow = False
                        self.yellowcabel_y = random.uniform(float(self.positioncabels[el]['start']), float(self.positioncabels[el]['end']))
                        print(self.yellowcabel_y, ' -  Yellow')
            if self.cooldown:
                if not self.colors1:
                    print(self.positioncabels)
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
                        print(self.bluecabel_y2, ' -  Blue')
                    elif self.positionentercabels[el]['color'] == 'Red' and self.cooldown_red1:
                        self.cooldown_red1 = False
                        self.redcabel_y2 = random.uniform(float(self.positionentercabels[el]['start']), float(self.positionentercabels[el]['end']))
                        print(self.redcabel_y, ' -  Red')
                    elif self.positionentercabels[el]['color'] == 'Yellow' and self.cooldown_yellow1:
                        self.cooldown_yellow1 = False
                        self.yellowcabel_y2 = random.uniform(float(self.positionentercabels[el]['start']), float(self.positionentercabels[el]['end']))
                        print(self.yellowcabel_y2, ' -  Yellow')
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
                    self.yellowcabelmouse = False
                    self.bluecabelmouse = True
                    self.redcabelmouse = True
                    self.yellowcabelentered = True
                elif ((self.height / 1.2) / float(self.redcabel_y) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.redcabel_y) + (self.height // 19)) and (((self.width // self.redcabel_x) - self.width // 13.2) <= x <= ((self.width // self.redcabel_x) + self.width // 13.2)) and not self.redcabelentered:
                    self.yellowcabelmouse = True
                    self.bluecabelmouse = True
                    self.redcabelmouse = False
                    self.redcabelentered = True
                elif ((self.height / 1.2) / float(self.bluecabel_y) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.bluecabel_y) + (self.height // 19)) and (((self.width // self.bluecabel_x) - self.width // 13.2) <= x <= ((self.width // self.bluecabel_x) + self.width // 13.2)) and not self.bluecabelentered:
                    self.yellowcabelmouse = True
                    self.bluecabelmouse = False
                    self.redcabelmouse = True
                    self.bluecabelentered = True
           if ((self.width // 1.5) - self.width // 13.2) <= x <= ((self.width // 1.5) + self.width // 13.2):
               if ((self.height / 1.2) / float(self.yellowcabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.yellowcabel_y2) + (self.height // 19)):
                   if not self.yellowcabelmouse:
                       self.cabelentertexture_yellow = arcade.load_texture('yellowcabelenter_succes.png')
                       self.yellowcabelmouse = True
                       self.yellowcabel_x = 1.77
                       self.yellowcabel_y = self.yellowcabel_y2
               elif ((self.height / 1.2) / float(self.redcabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.redcabel_y2) + (self.height // 19)):
                   if not self.redcabelmouse:
                       self.cabelentertexture_red = arcade.load_texture('redcabelenter_succes.png')
                       self.redcabelmouse = True
                       self.redcabel_x = 1.77
                       self.redcabel_y = self.redcabel_y2
               elif ((self.height / 1.2) / float(self.bluecabel_y2) - (self.height // 19)) < y < ((self.height / 1.2) / float(self.bluecabel_y2) + (self.height // 19)):
                   if not self.bluecabelmouse:
                       self.cabelentertexture_blue = arcade.load_texture('bluecabelenter_succes.png')
                       self.bluecabelmouse = True
                       self.bluecabel_x = 1.77
                       self.bluecabel_y = self.bluecabel_y2


    def on_mouse_motion(self, x, y, button, modifiers):
        pass

    def on_draw(self):
        self.clear()
        self.is_active = False
        self.electrical_mechanics()
        # --- Мир ---
        self.world_camera.use()
        self.walls.draw()
        self.mechanics.draw()
        self.player_list.draw()
        self.cabels.draw()
        if self.keyboard_Number == 1:
            self.keyboard_1.draw()

        # --- GUI ---
        self.gui_camera.use()
        self.batch.draw()
        if self.puzzle == 1:
            self.puzzle_1 = arcade.draw_texture_rect(self.puzzle_1_texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width // 2, self.height // 1.2))
            if self.redcabel1 and self.redcabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('redcabel.png'), arcade.rect.XYWH(self.width // self.redcabel_x, (self.height / 1.2) / float(self.redcabel_y), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)
            if self.yellowcabel1 and self.yellowcabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('yellowcabel.png'), arcade.rect.XYWH(self.width // self.yellowcabel_x, (self.height / 1.2) / float(self.yellowcabel_y), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)
            if self.bluecabel1 and self.bluecabelmouse:
                try:
                    arcade.draw_texture_rect(arcade.load_texture('bluecabel.png'), arcade.rect.XYWH(self.width // self.bluecabel_x, (self.height / 1.2) / float(self.bluecabel_y), self.width // 7, self.height // 9))
                except Exception as e:
                    print(e)
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
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.E and int(self.keyboard_Number) == 1 and self.Can_walk:
            self.puzzle = 1
            self.Can_walk = False
        elif key == arcade.key.E and int(self.keyboard_Number) == 1 and not self.Can_walk:
            self.puzzle = 0
            self.bluecabelmouse = True
            self.redcabelmouse = True
            self.yellowcabelmouse = True
            self.Can_walk = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False


    def on_update(self, dt: float):
        # Обработка горизонтального движения
        old_x = self.player.center_x
        old_y = self.player.center_y

        self.player.center_x += 50 * dt
        self.player.center_y += 50 * dt

        # Ограничение в пределах экрана
        self.center_x1 = max(self.player.width / 2, min(SCREEN_W - self.width / 2, self.player.center_x))
        self.center_y1 = max(self.player.height / 2, min(SCREEN_H - self.height / 2, self.player.center_y))

        # Проверка на движение
        self.is_walking = self.player.center_x != old_x or self.player.center_y != old_y
        if self.is_walking:
            self.texture_change_time += dt
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                if self.current_texture >= len(self.textureleft):
                    self.current_texture = 0
        self.player.texture = self.textureleft[self.current_texture]
        move = 0
        if self.left and not self.right and self.Can_walk:
            move = -MOVE_SPEED

        elif self.right and not self.left and self.Can_walk:
            move = MOVE_SPEED
        self.player.change_x = move

        self.keyboard_E.center_x = self.player.center_x
        self.keyboard_E.center_y = self.player.center_y + 40
        grounded = self.engine.can_jump(y_distance=6)  # Есть пол под ногами?
        if grounded:
            self.time_since_ground = 0
        else:
            self.time_since_ground += dt

        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()

        # Собираем монетки и проверяем опасности
        if arcade.check_for_collision_with_list(self.player, self.mechanics):
            self.keyboard_Number = 1
        else:
            self.keyboard_Number = 0

        # Камера — плавно к игроку и в рамках мира
        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        # Ограничим, чтобы за края уровня не выглядывало небо
        world_w = 2000  # Мы руками построили пол до x = 2000
        world_h = 900
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)

        # Обновим счёт
        self.text_score = arcade.Text(f"Счёт: {self.score}",
                                      16, SCREEN_H - 36, arcade.color.DARK_SLATE_GRAY,
                                      20, batch=self.batch)


def main():
    game = Platformer()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()