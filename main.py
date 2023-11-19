import os
import random
import time
import json

import emoji
import cfonts
from colorama import init, Fore, Back, Style

__doc__ = """
    File structure:
    class UserWonException
    class UserLoseException
    
    class GameField
    class RobotCommand
    class RobotCommandManager
    
    func start_game
    func field_and_command_preview
    func manage_commands_in_list
    func main (starting point)
"""


init(autoreset=True)


class UserWonException(Exception):
    pass


class UserLoseException(Exception):
    pass


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

                    # Set constantly square in top left corner with floor elements
                    if i in [0, 1, 2] and len(self.field[i]) < 3:
                        self.field[i].append([*self.floor, j, i])
                        continue

                    if i == self.height-2 and len(self.field[i]) == self.width-2:  # Add finish element
                        self.field[i].append([*self.finish, j, i])
                        continue

                    # Set constantly square in bottom right corner with floor elements
                    if i in [self.height-4, self.height-3, self.height-2] and len(self.field[i]) > self.width-5:
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

    # This method like const method in c++
    def print_field(self, robot_position=None):
        print(' ', end='')
        # Print numbers at the top of the field
        for number in range(1, self.width-1):  # -1 Because we had to add 2 positions for the borders.
            print(str(number)[-1], end='')
        print('')
        for index, row in enumerate(self.field):
            for cell in row:
                if robot_position is not None and robot_position["x"] == cell[2] and robot_position["y"] == cell[3]:
                    if cell[0:2] != self.wall:  # If cell is not a wall
                        if cell[0:2] == self.barrier and not robot_position["is_jump"]:  # if barrier and not jump
                            os.system('clear')  # cls
                            raise UserLoseException("Error. Next cell is a barrier, but you didn't jump. You are lose")
                        else:
                            print(Style.BRIGHT + Fore.GREEN + self.robot_item[0], end='')
                            if cell[0:2] == self.finish:
                                os.system('clear')  # cls
                                raise UserWonException("YOU WON")
                    else:
                        os.system('clear')  # cls
                        raise UserLoseException("Error. Next cell it is wall. You are lose")
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

        file_random_section = 0
        all_field_files_stringed = "".join(self.get_game_field_files())
        while file_random_section == 0 or file_random_section in all_field_files_stringed:
            file_random_section = str(random.randint(1000, 9999))
        with open(f"file_{file_random_section}.json", 'w') as file:
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
                    condition = i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1
                    match cell:
                        case '0':
                            self.field[i].append([*self.floor, i, j])
                        case '2':
                            self.field[i].append([*self.barrier, i, j])
                        case '3':
                            if condition:
                                self.field[i].append([*self.wall, -1, -1])
                            else:
                                self.field[i].append([*self.wall, i, j])
                        case '-1':
                            self.field[i].append([*self.finish, i, j])

    @staticmethod
    def get_game_field_files():
        return list(filter(lambda file_name: ".json" in file_name, os.listdir()))


class RobotCommand:
    game_field = GameField(20)
    __next_command_id = 0

    def __init__(self, move):
        self.command_id = RobotCommand.__next_command_id
        self.move = move  # turn_right, turn_left, turn_bottom, turn_top, step, jump
        self.robot = {"x": 1, "y": 1, "direction": "right", "is_jump": False}
        self.prev = None
        self.next = None
        RobotCommand.__next_command_id += 1

    def set_robot(self):
        if self.prev is not None:
            self.robot = self.prev.robot.copy()  # Get from previous command

        match self.move:
            case 'turn_right':
                self.robot["direction"] = 'right'
            case 'turn_left':
                self.robot["direction"] = 'left'
            case 'turn_bottom':
                self.robot["direction"] = 'bottom'
            case 'turn_top':
                self.robot["direction"] = 'top'
            case 'step':
                match self.robot["direction"]:
                    case 'right':
                        self.robot["x"] += 1
                    case 'left':
                        self.robot["x"] -= 1
                    case 'bottom':
                        self.robot["y"] += 1
                    case 'top':
                        self.robot["y"] -= 1
            case 'jump':
                self.robot["is_jump"] = True
                match self.robot["direction"]:
                    case 'right':
                        self.robot["x"] += 1
                    case 'left':
                        self.robot["x"] -= 1
                    case 'bottom':
                        self.robot["y"] += 1
                    case 'top':
                        self.robot["y"] -= 1


class RobotCommandManager:
    # bidirectional list

    def __init__(self, title="Main program"):
        self.commands_counter = 0
        self.title = title
        self.head = None
        self.tail = None

    def push_back(self, new_move):
        new_node = RobotCommand(new_move)
        new_node.prev = self.tail
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
            new_node.next = None

        else:
            self.tail.next = new_node
            new_node.next = None
            self.tail = new_node
        self.commands_counter += 1

    def __getitem__(self, command_id):
        if self.head is None:
            print("List is empty")
            return
        i = 0
        command = self.head
        while i < command_id:
            command = command.next
            i += 1
        return command

    def preview_all_commands(self):
        list_of_moves = []
        command = self.head
        for command_number in range(self.commands_counter):
            if command is not None:
                list_of_moves.append(f"{command_number+1}) {command.move}")
                command = command.next
        return ", ".join(list_of_moves) or "No commands yet"

    def remove_command(self, command_id):
        if self.head is None:
            return

        i = 0
        command = self.head
        while command_id != i:
            command = command.next
            i += 1

        self.commands_counter -= 1

        if self.head == command:
            self.head = command.next

        if command.next is not None:
            command.next.prev = command.prev

        if command.prev is not None:
            command.prev.next = command.next

    def change_command(self, command_id, new_move):
        new_command = RobotCommand(new_move)

        if self.head is None:
            return

        i = 0
        command = self.head
        while command_id != i:
            command = command.next
            i += 1

        if self.head == command:
            self.head = new_command
            self.head.next = command.next

        if command.next is not None:
            command.next.prev = new_command
            new_command.next = command.next

        if command.prev is not None:
            command.prev.next = new_command
            new_command.prev = command.prev

    def insert_command_after(self, command_id, move):
        i = 0
        command = self.head
        while command_id != i:
            command = command.next
            i += 1

        if command is not None:
            new_node = RobotCommand(move)
            new_node.next = command.next
            command.next = new_node
            new_node.prev = command
            if new_node.next is not None:
                new_node.next.prev = new_node

            if command == self.tail:
                self.tail = new_node
            self.commands_counter += 1

    def insert_function_after(self, command_id, function):  # TODO: think if main_list is empty
        i = 0
        command = self.head
        while command_id != i:
            command = command.next
            i += 1

        if command is not None:
            function.tail.next = command.next
            command.next = function.head
            function.head.prev = command
            if function.tail.next is not None:
                function.tail.next.prev = function.tail

            if command == self.tail:
                self.tail = function.tail
            self.commands_counter += function.commands_counter

    def insert_command__to_start(self):
        ...

    def insert_function_to_start(self):
        ...

    def __repr__(self):
        return self.title


def start_game(command_list):
    """Setting robot position for every command and printing game progress + awesome emoji

    """

    for command_number in range(command_list.commands_counter):
        os.system('clear')  # cls
        command_list[command_number].set_robot()
        robot_position = command_list[command_number].robot
        command_list[command_number].game_field.print_field(robot_position)

        print(command_list[command_number].move, end='-')
        match command_list[command_number].move:  # TODO: set it in dict with emoji values
            case 'turn_right':
                print(emoji.emojize(':backhand_index_pointing_right:'))
            case 'turn_left':
                print(emoji.emojize(':backhand_index_pointing_left:'))
            case 'turn_bottom':
                print(emoji.emojize(':backhand_index_pointing_down:'))
            case 'turn_top':
                print(emoji.emojize(':backhand_index_pointing_up:'))
            case 'step':
                print(emoji.emojize(':footprints:'))
            case 'jump':
                print(emoji.emojize(':leg:'))
        time.sleep(1)


def field_and_command_preview(game_field, main_command_list):
    """Game field and commands preview for user comfort using

    """

    commands_preview = main_command_list.preview_all_commands()

    game_field.print_field({"x": 1, "y": 1, "direction": "right", "is_jump": False})
    print("List of all commands: ", commands_preview)
    if commands_preview == "No commands yet":
        print("Basic robot direction - right")


# I KNOW, IT IS DIRTY FUNCTION, TODO: IF I`LL HAVE IDEAS HOW CHANGE IT - I`LL CHANGE
def manage_commands_in_list(game_field, command_list, functions, main_list=False):
    """Commands management for main program and for functions(adding, updating, deleting, etc)

    """

    command_number_dict = {
        "0": "turn_right",
        "1": "turn_left",
        "2": "turn_top",
        "3": "turn_bottom",
        "4": "step",
        "5": "jump",
        "": "step"
        # "6": it is for exit
    }

    # If function then stroke insertion function ability
    main_list_extension = "3 - Insert function\n" if main_list else "\u0336".join("3 - Insert function\n")  # "\u0336" +

    menu_manage_commands = ("0 - Add commands\n"
                            "1 - Change command\n"
                            "2 - Add command after another\n"
                            f"{main_list_extension}"
                            "4 - Remove command\n"
                            "5 - Exit\n")

    menu_commands = ("0 - Turn right\n"
                     "1 - Turn left\n"
                     "2 - Turn top\n"
                     "3 - Turn bottom\n"
                     "4 - Step\n"
                     "5 - Jump\n"
                     "6 - Exit\n")

    while True:
        print(menu_manage_commands)
        manage_commands_choice = input("Select(default - 0): ")
        # os.system("clear")  # cls

        if manage_commands_choice == '' or manage_commands_choice == '0':
            while True:
                field_and_command_preview(game_field, command_list)
                print(menu_commands)
                command_choice = input("Select(default - 4): ")
                if command_choice == "6":
                    break
                elif command_number_dict.get(command_choice, False):
                    command_list.push_back(command_number_dict[command_choice])
                os.system("clear")  # cls

        elif manage_commands_choice == '1':
            while True:
                field_and_command_preview(game_field, command_list)
                print(menu_commands)
                new_command_choice = input("Select(default - 4): ")
                if new_command_choice == "6":
                    break

                command_choice = int(input("Select which command you would like to change(number): "))
                if command_choice > 0 and command_choice <= command_list.commands_counter:
                    if command_number_dict.get(new_command_choice, False):
                        command_list.change_command(command_choice-1, command_number_dict[new_command_choice])
                    os.system("clear")  # cls
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")

        elif manage_commands_choice == '2':
            while True:
                field_and_command_preview(game_field, command_list)
                print(menu_commands)
                new_command_choice = input("Select(default - 4): ")
                if new_command_choice == "6":
                    break

                command_choice = int(input("Select command after which you would like to add new command(number): "))
                if command_choice > 0 and command_choice <= command_list.commands_counter:
                    if command_number_dict.get(new_command_choice, False):
                        command_list.insert_command_after(command_choice-1, command_number_dict[new_command_choice])
                    os.system("clear")  # cls
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")

        elif manage_commands_choice == '3':
            if main_list:
                while True:
                    field_and_command_preview(game_field, command_list)
                    for index, func in enumerate(functions):
                        print(f"{index}) {func.title}. Commands preview: {command_list.preview_all_commands()}")
                    print(f"{len(functions)}) Exit")
                    function_for_insertion = input("Select the function which you want to insert(default - 0): ")
                    function_for_insertion = int(function_for_insertion) if function_for_insertion.isnumeric() else 0
                    if function_for_insertion >= 0 and function_for_insertion <=len(functions):
                        if function_for_insertion == len(functions):
                            break
                        command_choice = int(input("Select command after which you would like to add function(number): "))
                        if command_choice > 0 and command_choice <= command_list.commands_counter:
                            command_list.insert_function_after(command_choice-1, functions[function_for_insertion])
                        else:
                            os.system("clear")  # cls
                            print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")
                    else:
                        os.system("clear")  # cls
                        print(Back.RED + Fore.WHITE + "Error. There is no this function.")
            else:
                os.system("clear")  # cls
                print(Back.RED + Fore.WHITE + "Error. There is no this option for function now")

        elif manage_commands_choice == '4':
            while True:
                field_and_command_preview(game_field, command_list)
                command_choice = input("Select which command you would like to remove(number): ")
                command_choice = int(command_choice) if command_choice.isnumeric() else command_list.commands_counter+10
                if command_choice > 0 and command_choice <= command_list.commands_counter:
                    command_list.remove_command(command_choice-1)
                    os.system("clear")  # cls
                    field_and_command_preview(game_field, command_list)
                    exit = input("For exit press 'x': ")
                    if exit.lower() == 'x':
                        break
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")
        elif manage_commands_choice == '5':
            break
        else:
            os.system("clear")
            print(Back.RED + Fore.WHITE + "Error. There is no this option")
            continue


def main():
    """Main program function(game creation, commands adding, start game)

    """
    field_from_file = False

    # In multi string are added unnecessary spaces
    menu = ("0) Auto set width and height of field\n"
            "1) Random set width and height of field(starts from 25 cells)\n"
            "2) User set width and height of field\n"
            "3) Select from file\n")

    cfonts.say("ROBOT GAME", gradient=["blue", "white"], align="center", font="simple3d")  # font="block"

    # Game field creation
    while True:
        print(menu)
        select_field_settings = input("Select(default - 0): ")
        # TODO: if set like that, this error will not raise "Error. There is no this option"
        select_field_settings = int(select_field_settings) if select_field_settings.isnumeric() else 0

        if select_field_settings == 0:
            game_field = GameField(30)
            break
        elif select_field_settings == 1:
            random_width = random.randint(25, 50)
            game_field = GameField(random_width)
            break
        elif select_field_settings == 2:
            width = int(input("Field width: "))
            height = int(input("Field height: "))
            if width > 20 and height > 10:
                game_field = GameField(width, height)
                break
            else:
                os.system('clear')  # cls
                print(Back.RED + Fore.WHITE + "Error. Width and height must be more than 20")
                continue
        elif select_field_settings == 3:
            field_from_file = True
            game_field = GameField()
            while True:
                all_field_files = GameField.get_game_field_files()
                for index, filename in enumerate(all_field_files):
                    print(f"{index+1}) {filename}")
                file_choice = input("Number of file from which you want load field: ")
                if file_choice != '' and int(file_choice) <= len(all_field_files):
                    break
                else:
                    os.system('clear')  # cls
                    print(Back.RED + Fore.WHITE + "Error.  There is no this option")
            game_field.upload_field(all_field_files[int(file_choice)-1])
            break
        else:
            os.system('clear')  # cls
            print(Back.RED + Fore.WHITE + "Error. There is no this option")

    if not field_from_file:
        game_field.create_field()  # If from file field will create by default

    RobotCommand.game_field = game_field
    os.system('clear')  # cls

    print("Field preview: ")
    game_field.print_field()
    time.sleep(1)  # TODO: in production make 5 seconds
    if not field_from_file:
        save_field = input("If do you want save this field type 'yes'(default - no):  ")
        if save_field == "yes":
            game_field.save_field()
    os.system('clear')  # cls

    # Command management
    command_list = RobotCommandManager()
    functions = [RobotCommandManager(title=f"Function {i+1}") for i in range(3)]

    while True:
        print("0) Main program")
        for index, func in enumerate(functions):
            print(f"{index+1}) {func.title}")
        print(f"{len(functions)+1}) Create new function")
        print(f"{len(functions)+2}) Start game")
        main_manage_choice = input(f"Select(default - {len(functions)+2}): ")
        # TODO: if set like that, this error will not raise "Error. There is no this option"
        main_manage_choice = int(main_manage_choice) if main_manage_choice.isnumeric() else len(functions)+2
        if main_manage_choice == 0:
            manage_commands_in_list(game_field, command_list, functions, main_list=True)

        elif 1 <= main_manage_choice <= len(functions):
            function = functions[main_manage_choice-1]
            manage_commands_in_list(game_field, function, functions)
            functions[main_manage_choice-1] = function

        elif main_manage_choice == len(functions)+1:
            new_func_name = input("Select name for new function: ")
            functions.append(RobotCommandManager(title=new_func_name))

        elif main_manage_choice == len(functions)+2:
            try:
                start_game(command_list)
                os.system('clear')  # cls
                print(Back.RED + Fore.WHITE + "There weren't enough commands for the robot to reach the end")
            except UserWonException as ex:
                os.system('clear')  # cls
                print(Back.GREEN + Fore.WHITE + str(ex))
                break
            except UserLoseException as ex:
                os.system('clear')  # cls
                print(Back.RED + Fore.WHITE + str(ex))
        else:
            os.system("clear")  # cls
            print(Back.RED + Fore.WHITE + "Error. There is no this option")

# TODO:
# Деструктор  ???
# Приватні методи та поля +-
# Доробити функції
# Закрити всі Тудушки


# TODO: После удаления последней команды почему-то перестают добавляться в конец новые
# TODO: При заполнении одной из "функций" в остальных появляются такие же команды


# побудова блок-схеми;
# написання записки;
# складання презентації;
# написання промови до захисту;


# Как лучше когда a > 0 and a < 10 или 0 < a < 10  ???

# Разница в больше уровней становится непреодолимым препятствием. Итог: Не сделаю

if __name__ == "__main__":
    main()
