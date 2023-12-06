import os
# import sys
import time
import json
import copy
import random
import logging
# from termios import tcflush, TCIOFLUSH

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

logging.basicConfig(level=logging.INFO, filename="robot_game.log", filemode="a", format="%(asctime)s %(levelname)s %(message)s")

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
        # Add 2 for borders
        if width is not None:
            self.width = width + 2
            if height is not None:
                self.height = height + 2
            else:
                self.height = width // 3 + 2
        else:
            self.width = 0
            self.height = 0
        self.field = []
        logging.info(f"Created game field")

    def create_field(self):
        logging.info(f"Fill game field with elements")
        for i in range(self.height):
            self.field.append([])
            for j in range(self.width):
                # Add walls around the field
                if i == 0 or i == self.height-1 or j == 0 or j == self.width-1:
                    self.field[i].append([*self.wall, j, i])
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
        current_command_result = None
        barrier_ex = UserLoseException("Error. Next cell is a barrier, but you didn't jump. You lose :cross_mark:")
        wall_ex = UserLoseException("Error. Next cell it is wall. You lose :cross_mark:")
        user_won_ex = UserWonException("You won!!! :trophy:")

        print(' ', end='')
        # Print numbers at the top of the field
        for number in range(1, self.width-1):  # -1 Because we had to add 2 positions for the borders.
            print(str(number)[-1], end='')
        print('')
        for index, row in enumerate(self.field):
            for cell in row:
                if robot_position is not None and robot_position["x"] == cell[2] and robot_position["y"] == cell[3]:
                    if cell[0:2] == self.wall:  # If cell is a wall
                        current_command_result = wall_ex
                        print(Style.BRIGHT + Back.RED + "×", end='')
                    elif cell[0:2] == self.barrier and not robot_position["is_jump"]:  # if barrier and not jump
                        current_command_result = barrier_ex
                        print(Style.BRIGHT + Back.RED + "×", end='')
                    elif cell[0:2] == self.finish:
                        current_command_result = user_won_ex
                        print(Back.GREEN + Fore.BLACK + self.robot_item[0], end='')
                    else:
                        print(Style.BRIGHT + Fore.GREEN + self.robot_item[0], end='')
                else:
                    match cell[0:2]:  # Without robot coordinates
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
        if current_command_result is not None:
            raise current_command_result

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
        filename = f"file_{file_random_section}.json"
        with open(filename, 'w') as file:
            json.dump(game_field_json, file)
        logging.info(f"Field saved in: {filename}")

    def upload_field(self, filename):
        logging.info(f"Upload field from file: {filename}")
        with open(filename, 'r') as file:
            json_object = json.load(file)
            self.width, self.height = json_object["width"], json_object["height"]
            for i in range(self.height):
                self.field.append([])
                for j in range(self.width):
                    # Add walls around the field
                    cell = json_object["field"][i][j]
                    match cell:
                        case '0':
                            self.field[i].append([*self.floor, j, i])
                        case '2':
                            self.field[i].append([*self.barrier, j, i])
                        case '3':
                            self.field[i].append([*self.wall, j, i])
                        case '-1':
                            self.field[i].append([*self.finish, j, i])

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
        logging.info(f"Created new command: id - {self.command_id}, move - {self.move}")

    def set_robot(self):
        if self.prev is not None:
            self.robot = self.prev.robot.copy()  # Get from previous command
        else:
            self.robot = {"x": 1, "y": 1, "direction": "right", "is_jump": False}

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

    def __repr__(self):
        return f"{self.command_id} - {self.move}: {self.robot}"

    def __del__(self):
        logging.info(f"Command {self} was removed from list")


class RobotCommandManager:
    # bidirectional list

    def __init__(self, title="Main program"):
        logging.info(f"Created new commands list with name: {title}")
        self.commands_counter = 0
        self.title = title
        self.head = None
        self.tail = None

    def push_back(self, new_move):
        logging.info(f"Add command '{new_move}' to end")
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
        logging.info(f"Remove {command_id + 1} command")
        if self.head is None:
            return

        command = self[command_id]

        if command.prev is not None:
            command.prev.next = command.next
        else:
            self.head = command.next

        if command.next is not None:
            command.next.prev = command.prev
        else:
            self.tail = command.prev

        self.commands_counter -= 1

    def change_command(self, command_id, new_move):
        logging.info(f"Change command with '{new_move}' after {command_id + 1} command")
        if self.head is None:
            return

        new_command = RobotCommand(new_move)
        command = self[command_id]

        if self.head == command:
            self.head = new_command
            self.head.next = command.next
            self.head.next.prev = new_command
        elif self.tail == command:
            self.tail = new_command
            self.tail.prev = command.prev
            self.tail.prev.next = new_command
        else:
            new_command.next = command.next
            new_command.prev = command.prev
            new_command.next.prev = new_command
            new_command.prev.next = new_command

    def insert_command_after(self, command_id, move):
        logging.info(f"Insert new command after {command_id+1} command")
        if command_id == -1:
            self.__insert_command_to_start(move)
        else:
            command = self[command_id]

            if command is not None:
                new_command = RobotCommand(move)
                new_command.next = command.next
                command.next = new_command
                new_command.prev = command
                if new_command.next is not None:
                    new_command.next.prev = new_command

                if command == self.tail:
                    self.tail = new_command
                self.commands_counter += 1

    def __insert_command_to_start(self, move):
        new_head_command = RobotCommand(move)
        if self.head is None:
            self.push_back(move)
            return

        head = self.head
        new_head_command.next = head
        head.prev = new_head_command

        self.head = new_head_command
        self.commands_counter += 1

    def insert_function_after(self, command_id, function):
        logging.info(f"Insert function after {command_id+1} command")
        if command_id == -1:
            self.__insert_function_to_start(function)
        else:
            function_duplicate_head, function_duplicate_tail = self.__duplicate_function_list(function)
            command = self[command_id]
            function_duplicate_tail.next = command.next
            if command.next:
                command.next.prev = function_duplicate_tail
            command.next = function_duplicate_head
            function_duplicate_head.prev = command
            if command == self.tail:
                self.tail = function_duplicate_tail
            self.commands_counter += function.commands_counter

    def __insert_function_to_start(self, function):
        head = self.head
        function_duplicate_head, function_duplicate_tail = self.__duplicate_function_list(function)
        if head is not None:
            function_duplicate_tail.next = head
            head.prev = function_duplicate_tail

            if head == self.tail:
                self.tail = function_duplicate_tail
            self.head = function_duplicate_head
        else:
            self.tail = function_duplicate_tail
            self.head = function_duplicate_head

        self.commands_counter += function.commands_counter

    @staticmethod
    def __duplicate_function_list(function):
        logging.info(f"Make duplicates of all commands in function")
        command = head_duplicate = copy.copy(function.head)
        while command is not None:
            if command.next is not None:
                command.next = copy.copy(command.next)
                command.next.prev = command
            else:
                tail_duplicate = command
            command = command.next

        return head_duplicate, tail_duplicate

    def __repr__(self):
        return self.title


def start_game(command_list, game_field):
    """Setting robot position for every command and printing game progress + awesome emoji

    """

    move_emoji_dict = {
        "turn_right": ":backhand_index_pointing_right:",
        "turn_left": ":backhand_index_pointing_left:",
        "turn_bottom": ":backhand_index_pointing_down:",
        "turn_top": ":backhand_index_pointing_up:",
        "step": ":footprints:",
        "jump": ":leg:"
    }
    # Print first position of robot always
    os.system('clear')  # cls
    game_field.print_field({"x": 1, "y": 1, "direction": "right", "is_jump": False})
    print("START GAME")
    time.sleep(1)

    for command_number in range(command_list.commands_counter):
        os.system('clear')  # cls
        command_list[command_number].set_robot()
        robot_position = command_list[command_number].robot
        logging.info(f"Current robot data: {robot_position}")

        command_list[command_number].game_field.print_field(robot_position)

        move_emoji = move_emoji_dict[command_list[command_number].move]
        print(f"{command_number+1}) {command_list[command_number].move}", end='-')
        print(emoji.emojize(move_emoji))
        time.sleep(0.5)


def field_and_command_preview(game_field, main_command_list, main_list=False):
    """Game field and commands preview for user comfort using

    """

    commands_preview = main_command_list.preview_all_commands()

    game_field.print_field({"x": 1, "y": 1, "direction": "right", "is_jump": False})
    print("List of all commands: ", commands_preview)
    if commands_preview == "No commands yet" and main_list:
        print("Basic robot direction - right")


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
    main_list_extension = "3 - Insert function\n" if main_list else "\u0336" + "\u0336".join("3 - Insert function\n")

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

    os.system("clear")
    while True:
        print(menu_manage_commands)
        manage_commands_choice = input("Select(default - 0): ")
        os.system("clear")  # cls

        if manage_commands_choice == '' or manage_commands_choice == '0':
            while True:
                field_and_command_preview(game_field, command_list, main_list)
                print(menu_commands)
                command_choice = input("Select(default - 4): ")
                if command_choice == "6":
                    os.system("clear")  # cls
                    break
                elif command_number_dict.get(command_choice, False):
                    logging.info(f"Add new command to back: {command_number_dict[command_choice]}")
                    command_list.push_back(command_number_dict[command_choice])
                    os.system("clear")  # cls
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no this option")

        elif manage_commands_choice == '1':
            while True:
                field_and_command_preview(game_field, command_list, main_list)
                print(menu_commands)
                new_command_choice = input("Select(default - 4): ")
                if new_command_choice == "6":
                    os.system("clear")  # cls
                    break

                command_choice = input("Select which command you would like to change(number): ")
                command_choice = int(command_choice) if command_choice.isnumeric() else -1
                if command_choice > 0 and command_choice <= command_list.commands_counter:
                    if command_number_dict.get(new_command_choice, False):
                        logging.info(f"Change command {command_choice} with new: {command_number_dict[new_command_choice]}")
                        command_list.change_command(command_choice-1, command_number_dict[new_command_choice])
                        os.system("clear")  # cls
                    else:
                        os.system("clear")  # cls
                        print(Back.RED + Fore.WHITE + "Error. There is no this option")
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")

        elif manage_commands_choice == '2':
            while True:
                field_and_command_preview(game_field, command_list, main_list)
                print(menu_commands)
                new_command_choice = input("Select(default - 4): ")
                if new_command_choice == "6":
                    os.system("clear")  # cls
                    break

                command_choice = input("Select command after which you would like to add new command(number, if want add to start - 0): ")
                command_choice = int(command_choice) if command_choice.isnumeric() else -1
                if command_choice >= 0 and command_choice <= command_list.commands_counter:
                    if command_number_dict.get(new_command_choice, False):
                        logging.info(f"Add command: {command_number_dict[new_command_choice]} after {command_choice} in list")
                        command_list.insert_command_after(command_choice-1, command_number_dict[new_command_choice])
                        os.system("clear")  # cls
                    else:
                        os.system("clear")  # cls
                        print(Back.RED + Fore.WHITE + "Error. There is no this option")
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")

        elif manage_commands_choice == '3':
            if main_list:
                while True:
                    field_and_command_preview(game_field, command_list, main_list)
                    for index, func in enumerate(functions):
                        print(f"{index}) {func.title}. Commands preview: {func.preview_all_commands()}")
                    print(f"{len(functions)}) Exit")
                    function_for_insertion = input("Select the function which you want to insert(default - 0): ")
                    function_for_insertion = int(function_for_insertion) if function_for_insertion.isnumeric() else 0
                    if function_for_insertion >= 0 and function_for_insertion <= len(functions):
                        if function_for_insertion == len(functions):
                            os.system("clear")  # cls
                            break
                        command_choice = input("Select command after which you would like to add function(number, if want add to start - 0): ")
                        command_choice = int(command_choice) if command_choice.isnumeric() else -1
                        if command_choice >= 0 and command_choice <= command_list.commands_counter:
                            copy_of_function = copy.copy(functions[function_for_insertion])
                            if copy_of_function.commands_counter != 0:
                                logging.info(f"Insert function: {copy_of_function}, after {command_choice} command")
                                command_list.insert_function_after(
                                    command_choice-1,
                                    copy_of_function
                                )
                            os.system("clear")  # cls
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
                field_and_command_preview(game_field, command_list, main_list)
                command_choice = input("Select which command you would like to remove(number): ")
                command_choice = int(command_choice) if command_choice.isnumeric() else command_list.commands_counter+10
                if command_list.commands_counter == 0:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command now is list")
                    break

                if command_choice > 0 and command_choice <= command_list.commands_counter:
                    logging.info(f"Remove command: {command_choice}")
                    command_list.remove_command(command_choice-1)
                    os.system("clear")  # cls
                    field_and_command_preview(game_field, command_list, main_list)
                    break
                else:
                    os.system("clear")  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no command with this index in the list")
        elif manage_commands_choice == '5':
            os.system("clear")
            break
        else:
            os.system("clear")
            print(Back.RED + Fore.WHITE + "Error. There is no this option")


def main():
    """Main program function(game creation, commands adding, start game)

    """
    logging.info(f"")
    logging.info(f"****Start program****")
    os.system("clear")  # cls
    field_from_file = False

    # In multi string are added unnecessary spaces
    menu = ("0) Auto set width and height of field\n"
            "1) Random set width and height of field(starts from 25 cells)\n"
            "2) User set width and height of field\n"
            "3) Select from file\n")

    cfonts.say("ROBOT GAME", gradient=["blue", "white"], align="center", font="simple3d")

    # Game field creation
    while True:
        print(menu)
        select_field_settings = input("Select(default - 0): ")

        if select_field_settings == '0' or select_field_settings == '':
            logging.info(f"Auto create field")
            game_field = GameField(30)
            break
        elif select_field_settings == '1':
            logging.info(f"Random create field")
            random_width = random.randint(25, 50)
            game_field = GameField(random_width)
            break
        elif select_field_settings == '2':
            logging.info(f"User create field")
            while True:
                print("Width should be more than 20 and height more than 10")
                width = input("Field width: ")
                width = int(width) if width.isnumeric() else -1
                height = input("Field height: ")
                height = int(height) if height.isnumeric() else -1
                if width > 20 and height > 10:
                    game_field = GameField(width, height)
                    break
                else:
                    os.system('clear')  # cls
                    print(Back.RED + Fore.WHITE + "Error. Width or height is not a valid value")
            break
        elif select_field_settings == '3':
            logging.info(f"Upload field from file")
            all_field_files = GameField.get_game_field_files()
            if len(all_field_files) == 0:
                os.system('clear')  # cls
                print(Back.RED + Fore.WHITE + "Error. There is no field files now. Try another option.")
                continue
            game_field = GameField()
            while True:
                for index, filename in enumerate(all_field_files):
                    print(f"{index+1}) {filename}")
                file_choice = input("Number of file from which you want load field: ")
                file_choice = int(file_choice) if file_choice.isnumeric() else -1
                if file_choice > 0 and file_choice <= len(all_field_files):
                    break
                else:
                    os.system('clear')  # cls
                    print(Back.RED + Fore.WHITE + "Error. There is no this option")
            game_field.upload_field(all_field_files[int(file_choice)-1])
            field_from_file = True
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
    time.sleep(5)
    if not field_from_file:
        save_field = input("If do you want save this field type 'yes'(default - no):  ")
        logging.info(f"Save field answer: {save_field}")
        if save_field == "yes":
            game_field.save_field()
    os.system('clear')  # cls

    # Command management
    command_list = RobotCommandManager()
    functions = [RobotCommandManager(title=f"Function {i+1}") for i in range(3)]
    logging.info(f"Main command list: {command_list}")
    logging.info(f"Functions of commands: {functions}")

    while True:
        print("0) Main program")
        for index, func in enumerate(functions):
            print(f"{index+1}) {func.title}")
        print(f"{len(functions)+1}) Create new function")
        print(f"{len(functions)+2}) Start game")
        print(f"{len(functions) + 3}) Stop program")
        main_manage_choice = input(f"Select(default - {len(functions)+2}): ")

        if main_manage_choice.isnumeric():
            main_manage_choice = int(main_manage_choice)
        elif main_manage_choice == '':
            main_manage_choice = len(functions)+2
        else:
            main_manage_choice = -1

        if main_manage_choice == 0:
            os.system("clear")  # cls
            logging.info(f"Operations with main command list")
            manage_commands_in_list(game_field, command_list, functions, main_list=True)

        elif 1 <= main_manage_choice <= len(functions):
            os.system("clear")  # cls
            logging.info(f"Operations with one of functions")
            function = functions[main_manage_choice-1]
            manage_commands_in_list(game_field, function, functions)
            functions[main_manage_choice-1] = function

        elif main_manage_choice == len(functions)+1:
            os.system("clear")  # cls
            new_func_name = input("Select name for new function: ")
            logging.info(f"Created new funtion with name: {new_func_name}")
            functions.append(RobotCommandManager(title=new_func_name))
            logging.info(f"Updated functions: {functions}")

        elif main_manage_choice == len(functions)+2:
            logging.info(f"Start game")
            try:
                start_game(command_list, game_field)
                raise UserLoseException("There weren't enough commands for the robot to reach the end")
            except UserLoseException as ex:
                logging.info(f"Game ended with error: {str(ex)}")
                print(Back.RED + Fore.WHITE + emoji.emojize(str(ex)))
                print()
            except UserWonException as ex:
                logging.info(f"User won!")
                print(Back.GREEN + Fore.WHITE + emoji.emojize(str(ex)))
                print()
                break
            # For clear input, but also it can remove some previous prints(Not good idea)
            # tcflush(sys.stdin, TCIOFLUSH)
        elif main_manage_choice == len(functions) + 3:
            break
        else:
            os.system("clear")  # cls
            print(Back.RED + Fore.WHITE + "Error. There is no this option")

# Upgrades I made:
# * Write game fields to unique files
# * Loading game fields into the game (the user can select one of the files and load it)
# * The user can create new “functions” and give them a meaningful name
# * The user can see where the robot has hit an obstacle or wall and then remake the robot’s program based on their mistakes
# * Logging


if __name__ == "__main__":
    main()
