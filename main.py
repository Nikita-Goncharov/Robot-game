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
- Исполнение команд роботом. +

Возможности программы:
- Выбор режима игры (поле из файла, пользовательское или случайное);  +
- Запись пользовательского поля в файл; +
- Наличие основной «программы» и «функций» (от 1 до 3);
- Составление «программы» робота из команд; +
- Замена, вставка или удаление любой команды между двумя другими;
- Вывод поля и команд на экран;  +
- Запуск «программы». +

Требования к программе:
- Организация команд в виде созданного вручную списка (отдельный список для основной «программы» и каждой «функции»);  +-
- Максимально предусмотренные ошибки пользователя;  +
- Статические и конст. методы, параметры по умолчанию, перегрузка []; +-
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
import json
from colorama import init, Fore, Back, Style

init(autoreset=True)

"""
Commands(emoji): 
turn left - 👈
turn right - 👉
walk - ?
jump - ?

"""


class GameField:
    wall = ["█", 3]
    barrier = ["≡", 2]
    floor = ["░", 0]
    finish = ["F", -1]
    robot_item = ["©", 1]

    def __init__(self, width=None, height=None):  # Both None if field upload from file
        # Add 2 for making borders
        if width is not None:
            self.width = width + 2
            if height is None:
                self.height = width//3 + 2
            else:
                self.height = height + 2
        else:
            self.width = 0
            self.height = 0
        self.field = []

    def create_field(self):
        for i in range(self.height):
            self.field.append([])
            for j in range(self.width):
                # Add walls around the field
                if i == 0 or i == self.height-1 or j == 0 or j == self.width-1:
                    self.field[i].append([*self.wall, -1, -1])
                else:
                    # Add wall, barrier or ordinary floor in field
                    # If random_number is 0 then add barrier else if 1 add wall else floor

                    # TODO: Do the same for finish
                    if i in [0, 1, 2] and len(self.field[i]) < 3:  # Set constantly square in top left corner with floor elements
                        self.field[i].append([*self.floor, j, i])
                        continue

                    if i == self.height-2 and len(self.field[i]) == self.width-2:  # Add finish element
                        self.field[i].append([*self.finish, j, i])
                        continue

                    if i in [self.height-4, self.height-3, self.height-2] and len(self.field[i]) > self.width-5:  # Set constantly square in bottom right corner with floor elements
                        self.field[i].append([*self.floor, j, i])
                        continue

                    random_number = random.randint(0, 10)
                    if random_number == 0:
                        # Symbol for printing, height of cell, x, y
                        self.field[i].append([*self.barrier, j, i])
                    elif random_number == 1:
                        self.field[i].append([*self.wall, j, i])
                    else:
                        self.field[i].append([*self.floor, j, i])

    def print_field(self, robot_position=None):  # robot_position=[x, y]
        print(' ', end='')
        # Print numbers at the top of the field
        for number in range(1, self.width-1):  # -1 Because we had to add 2 positions for the borders.
            print(str(number)[-1], end='')
        print('')
        for index, row in enumerate(self.field):
            for cell in row:
                if robot_position is not None and robot_position[0] == cell[2] and robot_position[1] == cell[3]:
                    if cell[0:2] != self.wall:  # If cell is not a wall
                        print(Style.BRIGHT + Fore.GREEN + self.robot_item[0], end='')
                    else:
                        os.system('clear')  # cls
                        raise Exception("Next cell it is wall. You are lose")
                else:
                    match cell[0:2]:  # Without coordinates
                        case self.wall:
                            print(Style.BRIGHT + Fore.CYAN + cell[0], end='')
                        case self.barrier:
                            print(Style.BRIGHT + Fore.RED + cell[0], end='')
                        case self.floor:
                            print(cell[0], end='')
                        case self.finish:
                            print(Style.BRIGHT + Back.YELLOW + Fore.BLACK + cell[0], end='')
            # Print numbers at the right of the field
            if index != 0 and index != self.height-1:
                print(str(index)[-1], end='')
            print('')

    def save_field(self):
        height = self.height
        width = self.width
        game_field_json = {
            "width": width,
            "height": height,
            "field": []
        }

        for index, row in enumerate(self.field):
            game_field_json["field"].append([])
            for cell in row:
                game_field_json["field"][index].append(str(cell[1]))

        with open('file.json', 'w') as file:
            json.dump(game_field_json, file)

    def upload_field(self, filename):
        with open(filename, 'r') as file:
            json_object = json.load(file)
            self.width, self.height = json_object["width"], json_object["height"]
            for i in range(self.height):
                self.field.append([])
                for j in range(self.width):
                    # Add walls around the field
                    cell = json_object["field"][i][j]
                    match cell:
                        case '0':  # TODO: Think how make more pretty
                            if i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1:
                                self.field[i].append([*self.floor, -1, -1])
                            else:
                                self.field[i].append([*self.floor, i, j])
                        case '2':
                            if i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1:
                                self.field[i].append([*self.barrier, -1, -1])
                            else:
                                self.field[i].append([*self.barrier, i, j])
                        case '3':
                            if i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1:
                                self.field[i].append([*self.wall, -1, -1])
                            else:
                                self.field[i].append([*self.wall, i, j])


class RobotCommand:
    game_field = GameField(20)
    next_command_id = 0

    def __init__(self, move):
        self.command_id = RobotCommand.next_command_id
        self.move = move  # turn_right, turn_left, turn_bottom, turn_top, step, jump
        self.robot = [1, 1, 'bottom']
        self.prev = None
        self.next = None
        RobotCommand.next_command_id += 1

    def set_robot(self):
        if self.prev is not None:
            self.robot = self.prev.robot.copy()  # Get from previous command

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
                        self.robot[0] += 1
                    case 'left':
                        self.robot[0] -= 1
                    case 'bottom':
                        self.robot[1] += 1
                    case 'top':
                        self.robot[1] -= 1
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


class RobotCommandManager:
    # bidirectional list

    def __init__(self):
        self.commands_counter = 0
        self.head = None  # Initally there are no elements in the list
        self.tail = None

    def push_back(self, new_move):  # Adding an element after the last element
        new_node = RobotCommand(new_move)
        new_node.prev = self.tail
        new_node.set_robot()
        if self.tail is None:  # checks whether the list is empty, if so make both head and tail as new node
            self.head = new_node
            self.tail = new_node
            new_node.next = None  # the first element's previous pointer has to refer to null

        else:  # If list is not empty, change pointers accordingly
            self.tail.next = new_node
            new_node.next = None
            self.tail = new_node  # Make new node the new tail
        self.commands_counter += 1

    def __getitem__(self, id):  # returns first element
        if self.head is None:  # checks whether list is empty or not
            print("List is empty")
            return
        i = 0
        command = self.head
        while i < id:
            command = command.next
            i += 1
        return command

    def preview_all_commands(self):
        list_of_moves = []
        command = self.head
        for command_number in range(self.commands_counter):
            list_of_moves.append(f"{command_number+1}) {command.move}")
            command = command.next
        return ", ".join(list_of_moves) or "No commands yet"

    # def insert_after(self, temp_node, new_data):  # Inserting a new node after a given node
    #     if temp_node is None:
    #         print("Given node is empty")
    #
    #     if temp_node is not None:
    #         new_node = RobotCommand(new_data)
    #         new_node.next = temp_node.next
    #         temp_node.next = new_node
    #         new_node.prev = temp_node
    #         if new_node.next is not None:
    #             new_node.next.prev = new_node
    #
    #         if temp_node == self.tail:  # checks whether new node is being added to the last element
    #             self.tail = new_node  # makes new node the new tail
    #
    # def insert_before(self, temp_node, new_data):  # Inserting a new node before a given node
    #     if temp_node is None:
    #         print("Given node is empty")
    #
    #     if temp_node is not None:
    #         new_node = RobotCommand(new_data)
    #         new_node.prev = temp_node.prev
    #         temp_node.prev = new_node
    #         new_node.next = temp_node
    #         if new_node.prev is not None:
    #             new_node.prev.next = new_node
    #
    #         if temp_node == self.head:  # checks whether new node is being added before the first element
    #             self.head = new_node  # makes new node the new head


# TODO: ASK
# В задании написано "Наличие основной «программы» и «функций» (от 1 до 3);"  Юзер может создавать свой маленький список команд - функцию
# Как я понял "программа" это именно последовательность команд для робота
# Тогда что такое "функции", не думаю что это обычные функции в коде

# Обяснить "Организация команд в виде созданного вручную списка (отдельный список для основной «программы» и каждой «функции»)"
# Отдельный список для "функций" ???


def start_game(command_list):
    for command_number in range(command_list.commands_counter):
        os.system('clear')  # cls
        robot_position = command_list[command_number].robot[:2]
        command_list[command_number].game_field.print_field(robot_position)
        time.sleep(1)


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
            game_field = GameField()
            game_field.upload_field('file.json')
            break
        elif select_field_settings == '':
            game_field = GameField(30)
            break
        else:
            os.system('clear')  # cls
            print("Error. There is no this variant")
            continue

    if not field_from_file:
        game_field.create_field()  # If from file field will create by default

    RobotCommand.game_field = game_field
    os.system('clear')  # cls

    # TODO: Field preview
    print("Field preview: ")
    game_field.print_field()
    if not field_from_file:
        save_field = input("If do you want save this field type 'yes'(default - no):  ")
        if save_field == "yes":
            game_field.save_field()

    command_list = RobotCommandManager()
    while True:
        os.system('clear')  # cls
        menu_manage_commands = ("0 - Add commands\n"
                                "1 - Change command\n"
                                "2 - Remove command\n"
                                "3 - Start game\n")
        print(menu_manage_commands)
        manage_commands_choice = input("Select(default - 0): ")
        if manage_commands_choice == '' or manage_commands_choice == '0':
            while True:
                game_field.print_field()
                print("List of all commands: ", command_list.preview_all_commands())
                menu_commands = ("0 - Turn right\n"
                                 "1 - Turn left\n"
                                 "2 - Turn top\n"
                                 "3 - Turn bottom\n"
                                 "4 - Step\n"
                                 "5 - Jump\n"
                                 "6 - Exit\n")
                print(menu_commands)
                command_choice = input("Select(default - 4): ")
                match command_choice:
                    case '':
                        command_list.push_back('step')
                    case '0':
                        command_list.push_back('turn_right')
                    case '1':
                        command_list.push_back('turn_left')
                    case '2':
                        command_list.push_back('turn_top')
                    case '3':
                        command_list.push_back('turn_bottom')
                    case '4':
                        command_list.push_back('step')
                    case '5':
                        command_list.push_back('jump')
                    case '6':
                        break
                os.system("clear")  # cls
        elif manage_commands_choice == '1':
            pass
            # while True:
            #     game_field.print_field()
            #     print("List of all commands: ", command_list.preview_all_commands())
            #     menu_commands = ("0 - Turn right\n"
            #                      "1 - Turn left\n"
            #                      "2 - Turn top\n"
            #                      "3 - Turn bottom\n"
            #                      "4 - Step\n"
            #                      "5 - Jump\n"
            #                      "6 - Exit\n"
            #                      )
            #     print(menu_commands)
            #     command_choice = input("Select(default - 4): ")
            #     match command_choice:
            #         case '':
            #             command_list.push_back('step')
            #         case '0':
            #             command_list.push_back('turn_right')
            #         case '1':
            #             command_list.push_back('turn_left')
            #         case '2':
            #             command_list.push_back('turn_top')
            #         case '3':
            #             command_list.push_back('turn_bottom')
            #         case '4':
            #             command_list.push_back('step')
            #         case '5':
            #             command_list.push_back('jump')
            #         case '6':
            #             break
            #     os.system("clear")  # cls
        elif manage_commands_choice == '2':
            pass
            # while True:
            #     game_field.print_field()
            #     print("List of all commands: ", command_list.preview_all_commands())
            #     menu_commands = ("0 - Turn right\n"
            #                      "1 - Turn left\n"
            #                      "2 - Turn top\n"
            #                      "3 - Turn bottom\n"
            #                      "4 - Step\n"
            #                      "5 - Jump\n"
            #                      "6 - Exit\n"
            #                      )
            #     print(menu_commands)
            #     command_choice = input("Select(default - 4): ")
            #     match command_choice:
            #         case '':
            #             command_list.push_back('step')
            #         case '0':
            #             command_list.push_back('turn_right')
            #         case '1':
            #             command_list.push_back('turn_left')
            #         case '2':
            #             command_list.push_back('turn_top')
            #         case '3':
            #             command_list.push_back('turn_bottom')
            #         case '4':
            #             command_list.push_back('step')
            #         case '5':
            #             command_list.push_back('jump')
            #         case '6':
            #             break
            #     os.system("clear")  # cls
        elif manage_commands_choice == '3':  # Start game
            break
        else:
            pass  # TODO: Print message ???

    # Start game
    start_game(command_list)

    # TODO: THINK HOW AND ADD FINISH TO FIELD


if __name__ == "__main__":
    main()
