import sys
import re
import os.path
import time
from traceback import format_exc as error_stack
from types import CodeType, FunctionType

try:
    from types import TypeType
except ImportError:
    # Python 3 compatibility
    TypeType = type
    
from renardo.lib.Utils import modulo_index
from renardo.settings_manager import settings

"""
Live Object
===========

Base for any self-scheduling objects
"""

# Player RegEx - used to match player definitions in code
re_player = re.compile(r"(\s*?)(\w+)\s*?>>\s*?\w+")

# Macro RegEx - used to match scheduling macro definitions
re_macro = re.compile(r"^\s*#\s*\{(.+?)\}\s*$")

class LiveObject(object):
    """ Base class for any self-scheduling objects """
    foxdot_object = True
    isAlive = True
    
    metro = None  # Reference to the metronome/clock
    step  = None  # Time between executions
    n     = 0     # Number of times executed
    
    def kill(self):
        """ Stop this object from scheduling itself """
        self.isAlive = False
        return self

    def __call__(self):
        """ Schedule this object to execute again """
        self.metro.schedule(self, self.metro.now() + float(modulo_index(self.step, self.n)))
        self.n += 1
        return self

"""
FoxCode
=======
Handles the execution of FoxDot code
"""

class CodeString:
    """ Wrapper for string that can be executed line by line """
    def __init__(self, raw):
        self.raw = raw
        self.iter = -1
        self.lines = [s + "\n" for s in self.raw.split("\n")] + ['']
    def readline(self):
        """ Return next line, used in compilation """
        self.iter += 1
        return self.lines[self.iter]
    def __str__(self):
        return self.raw

if sys.version_info[0] > 2:
    def clean(string):
        """ Cleans string by replacing unicode lambda symbol """
        string = string.replace("\u03BB", "lambda")
        return string
else:
    def clean(string):
        """ Removes non-ascii characters from a string for Python 2 """
        string = string.replace(u"\u03BB", "lambda")
        return string.encode("ascii", "replace")

class _StartupFile:
    """ Manages loading of startup file code """
    def __init__(self, path=None):
        self.path = None
        if path is not None:
            self.set_path(path)
    
    def set_path(self, path):
        """ Set the path to the startup file """
        if path is None:
            self.path = None
        else:
            self.path = os.path.realpath(path)
        return self

    def load(self):
        """ Load and return the content of the startup file """
        if self.path is not None:
            try:
                file = open(self.path)
                code = file.read()
                file.close()
                return code
            except (IOError, OSError):
                WarningMsg(f"'{self.path}' startup file not found.")
        return ""

# Initialize startup file - will be replaced by runtime.startup_files module
FOXDOT_STARTUP = _StartupFile()
        
class FoxDotCode:
    """ Handles execution of FoxDot code with namespace management """
    namespace={}  # Global namespace for executed code
    player_line_numbers={}  # Tracks line numbers of player definitions
    macro_counter = 0  # Counter for generating unique macro function names

    @staticmethod
    def _compile(string):
        """ Compiles a string of code to bytecode """
        return compile(str(CodeString(string)), "FoxDot", "exec")

    @classmethod
    def use_sample_directory(cls, directory):
        """ Forces FoxDot to look in `directory` instead of the default 
            directory when using audio samples. """
        return cls.namespace['symbolToDir'].set_root(directory)

    @classmethod
    def use_startup_file(cls, path):
        """ Set the path to a custom startup file """
        return cls.namespace['FOXDOT_STARTUP'].set_path(path)

    @classmethod
    def no_startup(cls):
        """ Disable the startup file """
        return cls.namespace["FOXDOT_STARTUP"].set_path(None)

    def load_startup_file(self): 
        """ Load and execute the startup file """
        code = self.namespace["FOXDOT_STARTUP"].load()
        return self.__call__(code, verbose=False)
    
    def parse_macros(self, code):
        """ Parse and extract scheduling macros from code """
        lines = code.split('\n')
        macros = []
        processed_lines = []
        current_macro = None
        current_block = []
        
        for line in lines:
            macro_match = re_macro.match(line)
            
            if macro_match:
                # Save previous macro if exists
                if current_macro is not None:
                    macros.append((current_macro, '\n'.join(current_block)))
                
                # Start new macro
                current_macro = macro_match.group(1).strip()
                current_block = []
                
            elif current_macro is not None:
                # We're inside a macro block
                if line.strip() == '':
                    # Empty line ends the macro block
                    macros.append((current_macro, '\n'.join(current_block)))
                    current_macro = None
                    current_block = []
                    processed_lines.append(line)  # Keep empty line in regular code
                else:
                    # Add line to current macro block
                    current_block.append(line)
            else:
                # Regular code line
                processed_lines.append(line)
        
        # Handle last macro if code doesn't end with empty line
        if current_macro is not None:
            macros.append((current_macro, '\n'.join(current_block)))
        
        return macros, '\n'.join(processed_lines)
    
    def create_macro_function(self, block_code):
        """ Create a dynamic function from a code block """
        self.macro_counter += 1
        func_name = f"_macro_func_{self.macro_counter}"
        
        # Indent the block code for function body
        indented_code = '\n'.join('    ' + line for line in block_code.split('\n') if line.strip())
        
        func_code = f"""def {func_name}():
{indented_code}
"""
        
        # Compile and execute the function definition
        exec(self._compile(func_code), self.namespace)
        
        # Return the function object
        return self.namespace[func_name]
    
    def schedule_macros(self, macros):
        """ Schedule all parsed macros """
        if not macros:
            return
            
        # Get Clock from namespace
        clock = self.namespace.get('Clock')
        if clock is None:
            print("Warning: Clock not available for macro scheduling")
            return
        
        for beat_expr, block_code in macros:
            if not block_code.strip():
                continue
                
            try:
                # Create function from block
                func = self.create_macro_function(block_code)
                
                # Evaluate beat expression in current namespace
                beat_value = eval(beat_expr, self.namespace)
                
                # Schedule using Clock.schedule which handles PointInTime correctly
                clock.schedule(func, beat_value)
                
            except Exception as e:
                print(f"Error scheduling macro '{beat_expr}': {e}")
                 
    def __call__(self, code, verbose=True, verbose_error=None):
        """ Takes a string of FoxDot code and executes as Python """

        # Check if clock is waiting for sync
        if self.namespace['_Clock'].waiting_for_sync:
            time.sleep(0.25)
            return self.__call__(code, verbose, verbose_error)

        if verbose_error is None:
            verbose_error = verbose

        if not code:
            return

        response = ""
        macros = []
        processed_code = code

        catching_exceptions_in_performance_code = settings.get("core.PERFORMANCE_EXCEPTIONS_CATCHING")

        if catching_exceptions_in_performance_code == True: 
            try:
                if type(code) != CodeType:
                    code = clean(code)
                    
                    # Parse macros before execution
                    macros, processed_code = self.parse_macros(code)
                    
                    response = stdout(processed_code)
                    if verbose is True:
                        print(response)

                # Execute the processed code (without macro lines)
                exec(self._compile(processed_code), self.namespace)
                
                # Schedule the macros
                self.schedule_macros(macros)

            # catch any exception in the executed code 
            except Exception as e:
                response = error_stack()
                if verbose_error is True:
                    print(response)

        else: # no exception catching 
            if type(code) != CodeType:
                code = clean(code)
                
                # Parse macros before execution
                macros, processed_code = self.parse_macros(code)
                
                response = stdout(processed_code)
                if verbose is True:
                    print(response)

            # Execute the processed code (without macro lines)
            exec(self._compile(processed_code), self.namespace)
            
            # Schedule the macros
            self.schedule_macros(macros)

        return response

    def update_line_numbers(self, text_widget, start="1.0", end="end", remove=0):
        """ Updates the line numbers of player objects in the editor """
        lines = text_widget.get(start, end).split("\n")[remove:]
        update = []
        offset = int(start.split(".")[0])

        for i, line in enumerate(lines):
            # Check line for a player and assign it a line number
            match = re_player.match(line)
            line_changed = False

            if match is not None:                
                whitespace = len(match.group(1))
                player     = match.group(2)
                line       = i + offset

                if player in self.player_line_numbers:
                    if (line, whitespace) != self.player_line_numbers[player]:
                        line_changed = True

                if line_changed or player not in self.player_line_numbers:
                    self.player_line_numbers[player] = (line, whitespace)
                    update.append("{}.id = '{}'".format(player, player))
                    update.append("{}.line_number = {}".format(player, line))
                    update.append("{}.whitespace  = {}".format(player, whitespace))

        # Execute updates if necessary
        if len(update) > 0:
            self.__call__("\n".join(update), verbose=False)
                
        return

# Main execution instance
execute = FoxDotCode()

def get_now(obj):
    """ Returns the value of objects if they are time-varying """
    return getattr(obj, 'now', lambda: obj).__call__()

def get_input():
    """ Similar to `input` but can handle multi-line input. Terminates on a final "\n" """
    line = " "; text = []
    
    while len(line) > 0:
        line = input("")
        text.append(line)

    return "\n".join(text)

def handle_stdin():
    """ When FoxDot is run with the --pipe flag, this function
        is called to continuously read from stdin """
    load_startup_file()

    while True:
        try:
            text = get_input()
            execute(text, verbose=False, verbose_error=True)
        except(EOFError, KeyboardInterrupt):
            sys.exit("Quitting")

def stdout(code):
    """ Format code for command line output """
    console_text = code.strip().split("\n")
    return ">>> {}".format("\n... ".join(console_text))

def debug_stdout(*args):
    """ Forces prints to server-side for debugging """
    sys.__stdout__.write(" ".join([str(s) for s in args]) + "\n")

def load_startup_file():
    """ Load and execute the startup file """
    return execute.load_startup_file()

def WarningMsg(*text):
    """ Print a warning message """
    print("Warning: {}".format(" ".join(str(s) for s in text)))

def write_to_file(fn, text):
    """ Write text to a file with proper encoding """
    try:
        with open(fn, "w") as f:
            f.write(clean(text))
    except IOError:
        print("Unable to write to {}".format(fn))
    return

# These functions return information about an imported module

def classes(module):
    """ Returns a list of class names defined in module """
    return [name for name, data in vars(module).items() if type(data) == TypeType]

def instances(module, cls):
    """ Returns a list of instances of cls from module """
    return [name for name, data in vars(module).items() if isinstance(data, cls)]

def functions(module):
    """ Returns a list of function names defined in module """
    return [name for name, data in vars(module).items() if type(data) == FunctionType]