import arcade
from pyglet.graphics import Batch
from arcade.gui import UIMessageBox


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "BOSS BREAKERS"
CHARACTER_SCALING = 1


class Level_1(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player_hp = 5
        self.w = width
        self.h = height
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
            arcade.close_window()

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
                attack_1.center_y = (SCREEN_HEIGHT // 3) * 2

                # Рассчитываем направление к курсору
                dx = self.hero_x - (SCREEN_WIDTH // 2 + 2)
                dy = self.hero_y - ((SCREEN_HEIGHT // 3) * 2)
                distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Избегаем деления на 0

                # Устанавливаем скорость
                attack_1.change_x = dx / distance * 10
                attack_1.change_y = dy / distance * 10

                self.attack_list.append(attack_1)

    def on_update(self, delta_time):
        if self.total_time == 0:
            self.sound.play()
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
            if self.bullet_list is not None and self.enemy_list is not None:
                for bullet in self.bullet_list:
                    enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                    for enemy in enemy_hit_list:
                        bullet.remove_from_sprite_lists()  # Удаляем пулю
                        self.boss1_hp -= 1
                        if self.boss1_hp <= 0:
                            self.enemy_list = None  # Удаляем врага
                            self.attack_list = None
                            self.attack_list_2 = None

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
                    attack_2_1 = arcade.Sprite("kulak_vertikal.png", 0.7)
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
                    attack_2_2 = arcade.Sprite("kulak_horizontal.png", 0.8)

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
            self.fonts = arcade.create_text_sprite(f"Поражение!"
                                                   f"Space для выхода.")
            self.texture = self.fonts.texture
            self.enemy_list.clear()
            self.attack_list = None
            self.bullet_list = None
            self.attack_list_2 = None
            self.fonts_list.append(self.fonts)
        if self.enemy_list == None and self.texture != self.fonts_2.texture:
            self.fonts_2 = arcade.create_text_sprite(f"Победац!"
                                                     f"Общее время: {self.total_time // 1} секунд."
                                                     f"Space для выхода.")
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
        if self.enemy_list is not None and self.attack_list is not None and self.attack_list_2 is not None:
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


def main():
    game_view = Level_1(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view.setup()
    arcade.run()

if __name__ == "__main__":
    main()