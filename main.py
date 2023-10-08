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
- Автоматическая инициализация игрового поля;  +
- Ручная (пользовательская) инициализация игрового поля (макс. 10х10);  +
- Случайная инициализация игрового поля (по возможности);  +
- Вывод поля и команд на экран;  +
- Исполнение команд роботом.

Возможности программы:
- Выбор режима игры (поле из файла, пользовательское или случайное);  +
- Запись пользовательского поля в файл;
- Наличие основной «программы» и «функций» (от 1 до 3);
- Составление «программы» робота из команд;
- Замена, вставка или удаление любой команды между двумя другими;
- Вывод поля и команд на экран;  +
- Запуск «программы».

Требования к программе:
- Организация команд в виде созданного вручную списка (отдельный список для основной «программы» и каждой «функции»);
- Максимально предусмотренные ошибки пользователя;  +
- Статические и конст. методы, параметры по умолчанию, перегрузка [];
- Визуальное отображение псевдографикой (при помощи таблицы ASCII);  +

Пояснения:
Есть поле, каждая ячейка которого имеет заданную высоту. На поле находится робот, размером в одну ячейку. 
Он может свободно перемещаться по ячейкам, находящимся на одном с ним уровне и прыгать на ячейки, с уровнем отличающимся на один (в любую сторону). 
Разница в больше уровней становится непреодолимым препятствием. Дополнительно можно придумать другие препятствия (например разрушаемые). 
Каждый шаг или прыжок робота перемешает его на одну ячейку, а повороты – нет. Можно придумать и другие команды (например удары или проверки).
Цель робота достичь финиша, который располагается где-то на поле. 
Цель игрока, из имеющихся команд составить «программу», которая доведёт робота до финиша. 
Сложность в том, что действия выполняются не в момент их выбора игроком, а лишь после того как программа будет готова и игрок нажмёт «старт».

"""
import os
import random
import time
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
walk - ?
jump - ?

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

    def upload_field(self, filename):
        with open(filename, 'r') as file:
            for i in range(self.height):
                self.field.append([])
                for j in range(self.width+1):  # Width+1 because in file one more than in field (last symbol \n)
                    # Add walls around the field
                    cell = file.read(1)
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
        self.command_id = RobotCommand.next_command_id
        self.move = move  # turn_right, turn_left, turn_bottom, turn_top, step, jump
        self.robot = [0, 0, 'bottom']  # Get from previous command
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
                match self.robot[2]:
                    case 'right':
                        self.robot[0] += 1
                    case 'left':
                        self.robot[0] -= 1
                    case 'bottom':
                        self.robot[1] -= 1
                    case 'top':
                        self.robot[1] += 1
        self.prev_command = None
        self.next_command = None
        RobotCommand.commands_counter += 1
        RobotCommand.next_command_id += 1


# TODO: ASK
# Как я понял нужно создать связанный список для команд, верно ???

# Можно ли создать 3 класса, один для поля игры, второй для команды как элемента списка,
# а третий как менеджер этого самого списка

# На защите можно будет создать виртуальное окружение(python venv) и если да,
# то какой там питон будет стоять(я юзаю match в коде)

# Когда юзер даёт роботу команду идти, то это нужно делать только один шаг
# или можно спрашивать у юзера сколько шагов он желает сделать

# В задании написано "Ручная (пользовательская) инициализация игрового поля (макс. 10х10);"
# Можно изменить значение 10х10, потому что это реально очень мало ???

# В задании написано "Наличие основной «программы» и «функций» (от 1 до 3);"
# Как я понял "программа" это именно последовательность команд для робота
# Тогда что такое "функции", не думаю что это обычные функции в коде

# Пояснить "Организация команд в виде созданного вручную списка (отдельный список для основной «программы» и каждой «функции»)"
# Отдельный список для "функций" ???

# Требования к программе это пря жесткие, жесткие или можно какой-то из подпунктов пункта не делать.
# Смущает перегрузка [], она тут мне по сути не сильно и нужна

# И возможен ли вариант вынести какие-то функции в отдельные файлы(P.S. чисто на будущее)

# При команде прыжок, робот запрыгивает на препятствие или перепрыгивает его ???


def main():
    field_from_file = False
    while True:
        # In multi string are added unnecessary spaces
        menu = ("0 - Auto set width and height of field\n"
                "1 - Random set width and height of field(starts from 25 cells)\n"
                "2 - User set width and height of field\n"
                "3 - Select from file\n")
        print(menu)

        select_field_settings = input("Select(default - 0): ")
        if select_field_settings == '0':
            game_field = GameField(30)
            break
        elif select_field_settings == '1':
            random_width = random.randint(25, 50)
            game_field = GameField(random_width)
            break
        elif select_field_settings == '2':
            width = int(input("Field width: "))
            height = int(input("Field height: "))
            if width > 20 and height > 10:
                game_field = GameField(width, height)
                break
            else:
                os.system('clear')  # cls
                print("Error. Width and height must be more than 20")
                continue
        elif select_field_settings == '3':
            field_from_file = True
            # TODO: select from file
            # TODO: if field bigger then in file will bad result, so need take width and height of field from file(save in json???)
            pass
        elif select_field_settings == '':
            game_field = GameField(30)
            break
        else:
            os.system('clear')  # cls
            print("Error. There is no this variant")
            continue
    game_field.create_field()
    RobotCommand.game_field = game_field
    os.system('clear')  # cls
    print("Your game field: ")
    game_field.print_field()
    time.sleep(5)
    os.system('clear')  # cls

    if not field_from_file:
        while True:
            save_field = input("If do you want save this field type 'yes'(default - no):  ")
            if save_field == "yes":
                # TODO: Save this field
                pass
            else:
                pass
            break

    while True:
        # TODO: Create commands
        break

    # TODO: Print for user field and commands which will be launched ???
    # TODO: Menu: change command in list, add to list, remove from list

    # game_field.upload_field()
    # game_field.print_field()

    # TODO: THINK HOW AND ADD FINISH TO FIELD

    # TODO: need bidirectional linked list ???
    # r1 = RobotCommand('step', 2)
    # r2 = RobotCommand('turn_right')
    # print(r1.__dict__)
    # print(r2.__dict__)
    # print(RobotCommand.commands_counter)
    # game_field.save_field()


if __name__ == "__main__":
    main()
