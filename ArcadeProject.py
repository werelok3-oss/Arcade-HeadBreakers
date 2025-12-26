import arcade
from arcade.camera import Camera2D
from pyglet.graphics import Batch

SCREEN_W = 1280
SCREEN_H = 720
TITLE = "Прыгскокология"

# Физика и движение
GRAVITY = 2            # Пикс/с^2
MOVE_SPEED = 6          # Пикс/с

LADDER_SPEED = 3        # Скорость по лестнице

         # С двойным прыжком всё лучше, но не сегодня

# Камера
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
        self.tile = arcade.Sprite(":resources:images/tiles/stoneCenter.png", scale=0.5)
        self.tile.center_x = 500
        self.tile.center_y = 120
        self.mechanics.append(self.tile)
        # --- Мир: сделаем крошечную арену руками ---
        # Пол из «травы»
        for x in range(0, 1600, 64):
            tile = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            tile.center_x = x
            tile.center_y = 64
            self.walls.append(tile)

        # Пара столбиков-стен
        for y in range(64, 64 + 64 * 6, 64):
            s = arcade.Sprite(":resources:images/tiles/stoneCenter.png", 0.5)
            s.center_x = 800
            s.center_y = y
            self.walls.append(s)

        # Лестница
        for y in range(64, 64 + 64 * 4, 64):
            l = arcade.Sprite(":resources:images/tiles/ladderMid.png", 0.5)
            l.center_x = 600
            l.center_y = y
            self.ladders.append(l)

        # Двигающаяся платформа (влево-вправо)
        plat = arcade.Sprite(":resources:images/tiles/grassHalf_left.png", 0.5)
        plat.center_x = 400
        plat.center_y = 265
        # Говорим движку, куда платформе можно кататься
        plat.boundary_left = 300
        plat.boundary_right = 700
        plat.change_x = 5  # Поедем вправо
        self.platforms.append(plat)



        # --- Физический движок платформера ---
        # Статичные — в walls, подвижные — в platforms, лестницы — ladders.
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.walls,
            platforms=self.platforms,
            ladders=self.ladders
        )

        # Сбросим вспомогательные таймеры


    def on_draw(self):
        self.clear()

        # --- Мир ---
        self.world_camera.use()
        self.walls.draw()
        self.platforms.draw()
        self.ladders.draw()
        self.mechanics.draw()
        self.player_list.draw()
        if self.keyboard_Number == 1:
            self.keyboard_1.draw()

        # --- GUI ---
        self.gui_camera.use()
        self.batch.draw()
        if self.puzzle == 1:
            self.puzzle_1 = arcade.draw_texture_rect(self.puzzle_1_texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width // 2, self.height // 1.2))

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif arcade.key.E and int(self.keyboard_Number) == 1 and self.Can_walk:
            self.puzzle = 1
            self.Can_walk = False
        elif arcade.key.E and int(self.keyboard_Number) == 1 and not self.Can_walk:
            self.puzzle = 0
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
        move = 0
        if self.left and not self.right and self.Can_walk:
            move = -MOVE_SPEED
        elif self.right and not self.left and self.Can_walk:
            move = MOVE_SPEED
        self.player.change_x = move

        self.keyboard_E.center_x = self.player.center_x
        self.keyboard_E.center_y = self.player.center_y + 40
        # Лестницы имеют приоритет над гравитацией: висим/лезем
        on_ladder = self.engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            # По лестнице вверх/вниз
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0

        # Если не на лестнице — работает обычная гравитация движка
        # Прыжок: can_jump() + койот + буфер
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