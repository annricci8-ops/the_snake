"""Игра «Змейка» на Python.

Модуль реализует игровую логику змейки: движение, столкновение, поедание
яблока.
Использует библиотеку pygame для рендеринга и random для генерации
позиций и typing для аннотаций типов.
"""

from random import choice, randint
from typing import Optional, Tuple

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)


pg.display.set_caption('Змейка')


clock = pg.time.Clock()


class GameObject:
    """Родительский класс."""

    def __init__(
        self,
        position: Tuple[int, int] = START_POSITION,
        body_color: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """Инициализирует объект в центре поля."""
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Отрисовывает объект. Здесь - пропуск."""
        raise NotImplementedError(
            f'Метод draw не реализован'
            f'в классе {self.__class__.__name__}'
        )

    @staticmethod
    def draw_cell(screen, position, color, border_color=None, width=0):
        """Статический метод для отрисовки."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color:
            pg.draw.rect(screen, border_color, rect, width)


class Apple(GameObject):
    """Дочерний класс яблока в игре.

    Наследуется от GameObject, устанавливает цвет яблока
    и генерирует случайную позицию на игровом поле.
    """

    def __init__(
            self,
            occupied_positions: Optional[set[Tuple[int, int]]] = None
    ) -> None:
        """Инициализирует яблоко.

        Вызывает конструктор родительского класса, устанавливает
        цвет яблока и сразу генерирует его случайную позицию.
        """
        super().__init__(body_color=APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = set()

        self.randomize_position(occupied_positions)

    def randomize_position(
            self,
            occupied_positions: set[tuple[int, int]]
    ) -> None:
        """Генерирует случайную позицию на поле для яблока."""
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if (x, y) not in occupied_positions:
                self.position = (x, y)
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на поле."""
        self.draw_cell(screen, self.position, self.body_color, BORDER_COLOR, 1)


class Snake(GameObject):
    """Класс, управляющий логикой и состоянием змейки.

    Наследуется от GameObject. Отвечает за движение, рост, проверку
    столкновений и отрисовку сегментов змейки.
    """

    def __init__(self, position: tuple[int, int] = START_POSITION) -> None:
        """Инициализирует змейку в центре поля.

        Устанавливает начальную длину (1 сегмент), позицию,
        направление движения (вправо) и цвет.
        """
        super().__init__(position=position, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновляет направление движения после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self) -> bool:
        """
        Выполняет шаг змейки.

        Возвращает False при столкновении с собственным телом, иначе True.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )
        if new_head in self.positions[1:]:
            return False
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None
        return True

    def reset(self) -> None:
        """Сбрасывает состояние змейки в начальное."""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.position = START_POSITION
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self) -> None:
        """Отрисовывает все сегменты змейки.

        И затирает последний при движении.
        """
        head_pos = self.get_head_position()
        self.draw_cell(screen, head_pos, self.body_color, BORDER_COLOR, 1)
        if self.last is not None:
            self.draw_cell(screen, self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object, running) -> bool:
    """Обрабатывает события клавиатуры и закрытия окна."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False
            if event.key in TURNS:
                new_dir, opposite = TURNS[event.key]
                if game_object.direction != opposite:
                    game_object.next_direction = new_dir
    return running


def main() -> None:
    """Основной игровой цикл."""
    pg.init()
    snake = Snake(START_POSITION)
    apple = Apple(set(snake.positions))

    running = True
    while running:
        clock.tick(SPEED)
        running = handle_keys(snake, running)

        if not running:
            break

        snake.update_direction()

        if not snake.move():
            snake.reset()
            apple.randomize_position(set(snake.positions))
            continue

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(set(snake.positions))

        snake.draw()
        apple.draw()
        pg.display.update()
    pg.quit


if __name__ == '__main__':
    main()
