import os
import random
import time
import json

import emoji
from colorama import init, Fore, Back, Style

init(autoreset=True)


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
            list_of_moves.append(f"{command_number+1}) {command.move}")
            command = command.next
        return ", ".join(list_of_moves) or "No commands yet"

    def remove_command(self, command_id):
        pass

    def change_command(self, command_id):
        pass

    def insert_command_after(self, command_id):
        pass

    def insert_after(self, temp_node, new_data):  # Inserting a new node after a given node
        if temp_node is None:
            print("Given node is empty")

        if temp_node is not None:
            new_node = RobotCommand(new_data)
            new_node.next = temp_node.next
            temp_node.next = new_node
            new_node.prev = temp_node
            if new_node.next is not None:
                new_node.next.prev = new_node

            if temp_node == self.tail:  # checks whether new node is being added to the last element
                self.tail = new_node  # makes new node the new tail


def start_game(command_list):
    for command_number in range(command_list.commands_counter):
        os.system('clear')  # cls
        robot_position = command_list[command_number].robot[:2]
        command_list[command_number].game_field.print_field(robot_position)

        print(command_list[command_number].move, end='-')
        match command_list[command_number].move:
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

    # TODO: Maybe need create game field object in one layer and then set width height
    if not field_from_file:
        game_field.create_field()  # If from file field will create by default

    RobotCommand.game_field = game_field
    os.system('clear')  # cls

    print("Field preview: ")
    game_field.print_field()
    time.sleep(5)
    if not field_from_file:
        save_field = input("If do you want save this field type 'yes'(default - no):  ")
        if save_field == "yes":
            game_field.save_field()
    os.system('clear')  # cls

    # Command management
    command_list = RobotCommandManager()
    while True:
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
            while True:
                game_field.print_field()
                print("List of all commands: ", command_list.preview_all_commands())
                command_choice = input("Select which command you would like to change(number): ")
                if command_choice > command_list.commands_counter:
                    pass

                menu_commands = ("0 - Turn right\n"
                                 "1 - Turn left\n"
                                 "2 - Turn top\n"
                                 "3 - Turn bottom\n"
                                 "4 - Step\n"
                                 "5 - Jump\n"
                                 "6 - Exit\n")
                print(menu_commands)
                command_choice = input("Select(default - 4): ")
                # TODO: change from switch cases to dicts
                match command_choice:
                    case '':
                        command_list.change_command('step')
                    case '0':
                        command_list.change_command('turn_right')
                    case '1':
                        command_list.change_command('turn_left')
                    case '2':
                        command_list.change_command('turn_top')
                    case '3':
                        command_list.change_command('turn_bottom')
                    case '4':
                        command_list.change_command('step')
                    case '5':
                        command_list.change_command('jump')
                    case '6':
                        break
                os.system("clear")  # cls
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
            os.system("clear")
            print("Error. There is no this option")
            continue

    # TODO: Add ability to make small lists of commands and add them in main list (functions)
    # TODO: HOW check if robot jump on the barrier ??? (If not - lose)
    # TODO: Adding command between another, change command between, remove between
    # TODO: Make check if robot at the end

    # Start game
    os.system('clear')  # cls
    start_game(command_list)


if __name__ == "__main__":
    main()
