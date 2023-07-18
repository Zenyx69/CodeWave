import re
import os
import time
from colorama import Fore, Style

class CommandHandler:
    def __init__(self):
        self.commands = {
            '/log': self.log_command,
            '/var': self.variable_command,
            '/clear': self.clear_command,
            '/list': self.list_command,
            '/wait': self.wait_command,
            '/load': self.load_command,
            '/execute': self.execute_command
        }
        self.variables = {}

    def handle_command(self, command, params):
        if command in self.commands:
            self.commands[command](params)
        else:
            self.return_error('ValueError', f'Command "{command}" is not defined')

    def log_command(self, params):
        self.return_log(" ".join(params))

    def variable_command(self, params):
        available_modes = ['create', 'delete', 'edit', 'get', 'operation', 'list']
        if len(params) < 2 or params[0] not in available_modes:
            self.return_error('ValueError', f'Unexpected command: {params[0]}')
            return

        mode = params[0]
        if mode == 'create':
            self.create_variable(params[1], " ".join(params[2:]))
        elif mode == 'delete':
            self.delete_variable(params[1])
        elif mode == 'edit':
            self.edit_variable(params[1], " ".join(params[2:]))
        elif mode == 'get':
            self.get_variable(params[1])
        elif mode == 'operation':
            self.perform_operation(params[1], params[2], params[3])
        elif mode == 'list':
            self.list_variables()

    def create_variable(self, name, value):
        if name in self.variables:
            self.return_error('VariableError', f'Variable "{name}" already exists')
        else:
            self.variables[name] = value
            self.return_log(f'Successfully Created Variable: {name}')

    def delete_variable(self, name):
        if name in self.variables:
            del self.variables[name]
            self.return_log(f'Successfully Deleted Variable: {name}')
        else:
            self.return_error('ValueError', f'Variable "{name}" not defined')

    def edit_variable(self, name, value):
        if name in self.variables:
            self.variables[name] = value
            self.return_log(f'Successfully Edited Variable: {name}')
        else:
            self.return_error('ValueError', f'Variable "{name}" not defined')

    def get_variable(self, name):
        if name in self.variables:
            self.return_log(f'{name}: {self.variables[name]}')
        else:
            self.return_error('ValueError', f'Variable "{name}" not defined')

    def perform_operation(self, variable1, operator, variable2):
        if variable1 not in self.variables:
            self.return_error('VariableError', f'Variable "{variable1}" not defined')
            return

        try:
            value1 = float(self.variables[variable1])
        except ValueError:
            self.return_error('VariableError', f'Invalid value for Variable "{variable1}"')
            return

        if variable2 in self.variables:
            try:
                value2 = float(self.variables[variable2])
            except ValueError:
                self.return_error('VariableError', f'Invalid value for Variable "{variable2}"')
                return
        else:
            try:
                value2 = float(variable2)
            except ValueError:
                self.return_error('VariableError', f'Invalid value: {variable2}')
                return

        if operator == '+=':
            value1 += value2
        elif operator == '-=':
            value1 -= value2
        elif operator == '*=':
            value1 *= value2
        elif operator == '/=':
            try:
                value1 /= value2
            except ZeroDivisionError:
                self.return_error('OperatorError', 'Cannot divide by zero')
                return
        elif operator == '%=':
            try:
                value1 %= value2
            except ZeroDivisionError:
                self.return_error('OperatorError', 'Cannot perform modulo operation. Divide by zero error')
                return
        else:
            self.return_error('OperatorError', f'Invalid operator: {operator}')
            return

        self.variables[variable1] = str(value1)
        self.return_log('Operation success at Variables.')

    def list_variables(self):
        self.return_log(str(self.variables))

    def clear_command(self, params):
        os.system('clear')
        print(f'{Fore.LIGHTMAGENTA_EX}CodeWave Prompt')
        print(f'{Fore.LIGHTCYAN_EX}Version: 1.0 | celes | 1')
        print('Channel: Stable')
        print(Style.RESET_ALL)

    def list_command(self, params):
        if params[0] == 'variables':
            self.list_variables()
        elif params[0] == 'commands':
            self.return_log(str(self.commands))
        else:
            self.return_error('ValueError', f'Invalid list option: {params[0]}')

    def wait_command(self, params):
        try:
            duration = int(params[0])
        except ValueError:
            self.return_error('ValueError', f'Invalid duration: {params[0]}')
            return

        time.sleep(duration)

    def load_command(self, params):
        if not params[0].endswith('.cw'):
            self.return_error('ValueError', 'Invalid file extension. Only .cw files are supported.')
            return

        if not os.path.exists(params[0]):
            self.return_error('ValueError', f'Unable to find file: {params[0]}')
            return

        with open(params[0], 'r') as file:
            lines = file.readlines()
            if len(lines) > 0:
                match = re.search(r'\d+', lines[0])
                if match:
                    os.system('clear')
                    delay = int(match.group())
                    print(f'{Fore.LIGHTMAGENTA_EX}CodeWave CW Prompt')
                    print(f'{Fore.LIGHTCYAN_EX}Version: 1.0 | celes | 1')
                    print(f'Delay: {delay}')
                    print(Style.RESET_ALL)

                    for line in lines[1:]:
                        self.run_command(line.strip())
                        time.sleep(delay)

                    input('\nPress Enter to continue...')
                else:
                    self.return_error('ValueError', f'File "{params[0]}" returned an error. Delay-per-command not found.')
                    quit('Force Quit. \nError Code: 000')

    def execute_command(self, params):
        if params[0] == 'if':
            self.execute_if_command(params[1:])

    def execute_if_command(self, params):
        if len(params) < 4:
            self.return_error('ValueError', 'Invalid if command. Usage: /execute if variable1 operator variable2 command')
            return

        variable1 = params[0]
        operator = params[1]
        variable2 = params[2]
        command = " ".join(params[3:])

        if variable1 in self.variables:
            value1 = self.variables[variable1]
        else:
            self.return_error('ValueError', f'Variable "{variable1}" not defined')
            return

        if variable2 in self.variables:
            value2 = self.variables[variable2]
        else:
            value2 = variable2

        if self.evaluate_condition(value1, operator, value2):
            self.run_command(command)

    def evaluate_condition(self, value1, operator, value2):
        try:
            value1 = float(value1)
            value2 = float(value2)
        except ValueError:
            return False

        if operator == '==':
            return value1 == value2
        elif operator == '!=':
            return value1 != value2
        else:
            return False

    def run_command(self, command):
        command_parts = command.split(' ')
        if command_parts[0] in self.commands:
            self.handle_command(command_parts[0], command_parts[1:])
        else:
            self.return_error('ValueError', f'Command "{command_parts[0]}" is not defined')

    def return_error(self, error_type, message):
        print(f'{Fore.RED}[CodeWave] {error_type}: {message}{Style.RESET_ALL}')

    def return_log(self, message):
        print(f'{Fore.LIGHTGREEN_EX}[CodeWave] {message}{Style.RESET_ALL}')


def load_prompt():
    print(f'{Fore.LIGHTMAGENTA_EX}CodeWave Prompt')
    print(f'{Fore.LIGHTCYAN_EX}Version: 1.0 | celes | 1')
    print('Channel: Stable') # this thing is inspired by chromebook build details, since coding this project. i used a samsung chromebook 3 lol
    print(Style.RESET_ALL)

    comm_handler = CommandHandler()
    run = True
    while run:
        v = input('Command: ')
        if v == 'stop':
            run = False
        comm_handler.run_command(v)


load_prompt()
