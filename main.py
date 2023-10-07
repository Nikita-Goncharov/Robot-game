"""
Вариант №39: Список «Программа для робота»

Обязательные поля:  ***** Already done ******
- Номер команды (назначается автоматически);
- Действие команды (выбирается пользователем из вариантов поворот налево, поворот направо, шаг вперёд, прыжок и т.д.);
- Поле игры (двумерный динамический массив, каждая ячейка которого – клетка на поле действия, с заданной высотой или препятствием, а также финишем. 
Заполняется из файла);
- Робот (массив из трёх элементов – координат и направления);
- Счётчик количества команд.

Возможности класса:
- Автоматическая инициализация игрового поля;
- Ручная (пользовательская) инициализация игрового поля (макс. 10х10);
- Случайная инициализация игрового поля (по возможности);
- Вывод поля и команд на экран;
- Исполнение команд роботом.

Возможности программы:
- Выбор режима игры (поле из файла, пользовательское или случайное);
- Запись пользовательского поля в файл;
- Наличие основной «программы» и «функций» (от 1 до 3);
- Составление «программы» робота из команд;
- Замена, вставка или удаление любой команды между двумя другими;
- Вывод поля и команд на экран;
- Запуск «программы».

Требования к программе:
- Организация команд в виде созданного вручную списка (отдельный список для основной «программы» и каждой «функции»);
- Максимально предусмотренные ошибки пользователя;
- Статические и конст. методы, параметры по умолчанию, перегрузка [];
- Визуальное отображение псевдографикой (при помощи таблицы ASCII);

Пояснения:
Есть поле, каждая ячейка которого имеет заданную высоту. На поле находится робот, размером в одну ячейку. 
Он может свободно перемещаться по ячейкам, находящимся на одном с ним уровне и прыгать на ячейки, с уровнем отличающимся на один (в любую сторону). 
Разница в больше уровней становится непреодолимым препятствием. Дополнительно можно придумать другие препятствия (например разрушаемые). 
Каждый шаг или прыжок робота перемешает его на одну ячейку, а повороты – нет. Можно придумать и другие команды (например удары или проверки).
Цель робота достичь финиша, который располагается где-то на поле. 
Цель игрока, из имеющихся команд составить «программу», которая доведёт робота до финиша. 
Сложность в том, что действия выполняются не в момент их выбора игроком, а лишь после того как программа будет готова и игрок нажмёт «старт».

"""
import random
from colorama import init, Fore, Back, Style

init(autoreset=True)

"""
█ - wall (height - 3)
≡ - barrier (height - 2)
© - robot (height - 1)
░ - floor (height - 0)
"""

"""
Commands(emoji): 
turn left - 👈
turn right - 👉
walk - 
jump - 

"""


# print(Style.BRIGHT + Back.RED + "█", end='')
# print('≡', end='')
# print(Style.BRIGHT + Back.RED + "█")
# print(Style.BRIGHT + Back.RED + "█", end='')
# print('©', end='')
# print(Style.BRIGHT + Back.RED + "█")


'''
 12345678901234567890123
█████████████████████████ 
█░░░░░░░░░█░░░≡░░░░░█░░░█ 1
█░░░░░█░░░░░░░░█░░░█░░░░█ 2
█   ░©░  ≡    ≡         █ 3
█   ≡      █      █     █ 4
█            ≡      ≡   █ 5
█      █ ≡  █    █      █ 6
█    █       ≡      ≡   █ 7
█         █       █     F 8
█████████████████████████ 
'''


class GameField:
    wall = ("█", 3)
    barrier = ("≡", 2)
    floor = ("░", 0)

    def __init__(self, width, height=None):
        # Add 2 for making borders
        self.width = width + 2
        if height is None:
            self.height = width//3 + 2
        else:
            self.height = height + 2
        self.field = []

    def create_field(self):
        for i in range(self.height):
            self.field.append([])
            for j in range(self.width):
                # Add walls around the field
                if i == 0 or i == self.height-1 or j == 0 or j == self.width-1:
                    self.field[i].append(self.wall)
                else:
                    # Add wall, barrier or ordinary floor in field
                    # If random_number is 0 then add barrier else if 1 add wall else floor
                    random_number = random.randint(0, 5)
                    if random_number == 0:
                        self.field[i].append(self.barrier)
                    elif random_number == 1:
                        self.field[i].append(self.wall)
                    else:
                        self.field[i].append(self.floor)

    def print_field(self, robot_position=None):
        print(' ', end='')
        # Print numbers at the top of the field
        for number in range(1, self.width-1):  # -1 Because we had to add 2 positions for the borders.
            print(str(number)[-1], end='')
        print('')
        for index, row in enumerate(self.field):
            for cell in row:
                match cell:
                    case self.wall:
                        print(Style.BRIGHT + Fore.CYAN + cell[0], end='')
                    case self.barrier:
                        print(Style.BRIGHT + Fore.RED + cell[0], end='')
                    case self.floor:
                        print(cell[0], end='')
            # Print numbers at the right of the field
            if index != 0 and index != self.height-1:
                print(str(index)[-1], end='')
            print('')

    def save_field(self):
        with open('field.txt', 'w') as file:
            for index, row in enumerate(self.field):
                for cell in row:
                    file.write(str(cell[1]))
                file.write('\n')

    def upload_field(self):
        with open('field.txt', 'r') as file:
            for i in range(self.height):
                self.field.append([])
                for j in range(self.width+1):  # Width+1 because in file one more than in field (last symbol \n)
                    # Add walls around the field
                    cell = file.read(1)
                    print(cell, type(cell))
                    match cell:
                        case '0':
                            self.field[i].append(self.floor)
                        case '2':
                            self.field[i].append(self.barrier)
                        case '3':
                            self.field[i].append(self.wall)


class RobotCommand:
    game_field = GameField(20)
    commands_counter = 0
    next_command_id = 0

    def __init__(self, move, amount_of_steps=None):
        # TODO: make just one step command or can in one command do few steps
        self.command_id = RobotCommand.next_command_id
        self.move = move  # turn_right, turn_left, turn_bottom, turn_top, step, jump
        self.robot = [0, 0, 'bottom']
        match self.move:
            case 'turn_right':
                self.robot[2] = 'right'
            case 'turn_left':
                self.robot[2] = 'left'
            case 'turn_bottom':
                self.robot[2] = 'bottom'
            case 'turn_top':
                self.robot[2] = 'top'
            case 'step':
                match self.robot[2]:
                    case 'right':
                        self.robot[0] += amount_of_steps
                    case 'left':
                        self.robot[0] -= amount_of_steps
                    case 'bottom':
                        self.robot[1] -= amount_of_steps
                    case 'top':
                        self.robot[1] += amount_of_steps
            case 'jump':
                pass
        self.next_command = None
        RobotCommand.commands_counter += 1
        RobotCommand.next_command_id += 1


def main():
    game_field = GameField(20)
    # TODO: check if width gt 20
    # game_field.create_field()
    # TODO: if field bigger then in file will bad result, so need take width and height of field from file
    game_field.upload_field()
    game_field.print_field()
    RobotCommand.game_field = game_field
    # TODO: need bidirectional linked list ???
    r1 = RobotCommand('step', 2)
    r2 = RobotCommand('turn_right')
    print(r1.__dict__)
    print(r2.__dict__)
    print(RobotCommand.commands_counter)
    # game_field.save_field()


if __name__ == "__main__":
    main()
