"""
Draws and generates a lsystem from a specified file, for more details use the "-h" flag
For the supported file syntax, check the examples folder

:author: Moldovan Alexandru
:author: Bouillon Quentin
:author: Poupon Thomas
"""

from sys import argv
from time import localtime
from time import strftime
from turtle import *

def custom_log(type, message):
    """
    Prints a custom message and in case of error, stops the program

    :param type: Type of the message
    :param message: Message
    """

    print("{} [{}] {}".format(strftime("%H:%M:%S", localtime()), type.upper(), message))
    if (type == "error"): exit(1)

def print_help():
    """
    Prints the help message
    """

    print("\nUsage: {} -i INPUT [-o OUTPUT] [-rgb] [-h]\n".format(argv[0]))
    print("Required Arguments:\n")
    print("\t-i <path>\t\tSpecifies the path of the lsystem\n")
    print("Optional Arguments:\n")
    print("\t-o <path>\t\tSpecifies the path of output file")
    print("\t-rgb\t\t\tEnables Fancy preview mode")
    print("\t-h  \t\t\tShows help\n")
    print("Example: {} -i arbre.txt -o sortie.py -rgb\n".format(argv[0]))
    exit(0)

def a(size):
    """
    Draws forward and returns the executed instruction as text

    :param size: Chosen length per action
    :return: Executed action as an instruction
    """

    pd()
    fd(size)
    return ("pd;fd({})\n".format(size))

def b(size):
    """
    Moves forward and returns the executed instruction as text

    :param size: Chosen length per action
    :return: Executed action as an instruction
    """

    pu()
    fd(size)
    return ("pu;fd({})\n".format(size))

def plus(angle):
    """
    Turns the turtle right by a provided angle

    :param angle: Chosen angle
    :return: Executed action as an instruction
    """

    right(angle)
    return ("right({})\n".format(angle))

def minus(angle):
    """
    Turns the turtle left by a provided angle

    :param angle: Chosen angle
    :return: Executed action as an instruction
    """

    left(angle)
    return ("left({})\n".format(angle))

def snap():
    """
    Turns the turtle by 180°

    :return: Executed action as an instruction
    """

    right(180)
    return ("right(180)\n")

def save_point(points):
    """
    Saves current turtle position to provided list

    :param points: Points list
    :return: Executed action as an instruction (nothing)
    """

    points.append({"linear": pos(), "rotational": heading()})
    return ("")

def jump_to(pos):
    """
    Teleports turtle to provided coordinates

    :param pos: Coordinates [(x, y)], [angle]
    :return: Executed action as an instruction
    """

    goto(pos["linear"])
    setheading(pos["rotational"])
    return("goto({});setheading({})\n".format(pos["linear"], pos["rotational"]))

def rewind_to_point(points):
    """
    Rewinds the turtle to the previous saved position and updates position list

    :param points: List of points
    :return: Executed action as an instruction
    """

    r = -1
    if (len(points)):
        r = jump_to(points[-1])
        points.pop()
    else:
        custom_log("error", "Tried rewinding to non-existing point, please check your axiom")
    return r

def get_moves(size, angle, points):
    """
    Returns a dictionnary assigning an action per character

    :param size: Chosen size
    :param angle: Chosen angle
    :param points: List of points
    :return: Dictionnary
    """

    return {
        "a": lambda: a(size),
        "b": lambda: b(size),
        "+": lambda: plus(angle),
        "-": lambda: minus(angle),
        "*": snap,
        "[": lambda: save_point(points),
        "]": lambda: rewind_to_point(points)
    }

def update_rgb(rgb):
    """
    Gets the next RGB value for a color shading effect

    :param rgb: Current RGB state (r, g, b)
    :return: Next RGB state (r, g, b)
    """

    r, g, b = 0, 1, 2
    if (rgb[r] > 0 and rgb[b] == 0):
        rgb[r] -= 1
        rgb[g] += 1
    elif (rgb[g] > 0 and rgb[r] == 0):
        rgb[g] -= 1
        rgb[b] += 1
    else:
        rgb[b] -= 1
        rgb[r] += 1
    return tuple(rgb)

def check_line(line):
    """
    Checks if a line respects the required format

    :param line: Line
    :return: The presence of '=' in the line
    """

    return ("=" in line)

def trim_spaces(text):
    """
    Removes white space characters (" ", "\n", "\t"...)

    :param text: Chosen string
    :return: String without white space
    """

    return "".join(text.split())

def sanitize_line(line):
    """
    Removes every " from a string

    :param line: Chosen line
    :return: Line without "
    """

    return line.replace('"', "")

def parse_file(options):
    """
    Extracts parameters from settings and updates settings

    :param options: Chosen parameters
    """

    f = open(options["i"], 'r')
    lines = f.readlines()
    reading_rules = 0
    for line in lines:
        if (not (line.startswith("#") or line.startswith("\n"))):
            line = trim_spaces(line)
            if (check_line(line)):
                r = line.split("=")
                if (r[0] == "regles"):
                    reading_rules = 1
                elif (reading_rules and line[0] == '"'):
                    if (not ("regles" in options)):
                        options["regles"] = []
                    options["regles"].append(sanitize_line(line))
                else:
                    reading_rules = 0
                    if (r[0] in options):
                        custom_log("warning", "'{}' parameter was specified twice, keeping first assignment".format(r[0]))
                    else:
                        options[r[0]] = sanitize_line(r[1])
            else:
                custom_log("error", "Provided file is not following the correct syntax")
    f.close()
    return options

def inject_rule(axiom, character, rule):
    """
    Injects rule in an axiom by replacing the attached character

    :param axiom: Current axiom
    :param character: Assigned character
    :param rule: Assigned rule
    :return: New axiom
    """

    return rule.join(axiom.split(character))

def parse_levels(axiom, levels, rules):
    """
    Injects all rules into an axiom the specified number of times

    :param axiom: Current axiom
    :param levels: Number of injections
    :param rules: Set of rules
    :return: New axiom
    """

    for level in range(0, levels):
        for rule in rules:
            character, _, parsed_rule = rule.partition("=")
            if (character and parsed_rule):
                axiom = inject_rule(axiom, character, parsed_rule)
            else:
                custom_log("error", "Invalid rule: " + rule)
    return axiom

def treat_axiom(axiom, m, output, rgb):
    """
    Draws a lsystem and converts the executed instructions into text, then write them into output file

    :param axiom: Current axiom
    :param m: Movement dictionnary
    :param output: Output path
    :param rgb: RGB option (1=yes, 0=no)
    """

    f = open(output, "w")
    f.write("from turtle import *;speed(0);onkey(lambda: tracer(0), 'space');screensize(2000, 2000);listen();title('Press SPACE to skip preview')\n")
    colormode(255)
    bgcolor("black")
    pencolor("white")
    screensize(2000, 2000)
    if (rgb): rgb = [255, 0, 0]
    for c in axiom:
        if (c in m):
            if (rgb): pencolor(update_rgb(rgb))
            f.write(m[c]())
        else:
            custom_log("error", "Unrecognized character in axiom: " + c)
    f.write("tracer(1);title('Click anywhere to close');exitonclick()")
    f.close()
    custom_log("success", "Sctipt generated to {} . It can be launched using command 'python {}'".format(output, output))

def test_requirements(options):
    """
    Test for every required option, if not met, exits

    :param options: lsystem settings
    """

    req = ["axiome", "regles", "taille", "angle", "niveau"]
    for r in req:
        if (not(r in options)):
            custom_log("error", "Missing {} parameter in chosen file: {}".format(r, options["i"]))

def get_arguments():
    """
    Command line arguments getter, because the argparse library is overrated

    :return: Parsed arguments, in a dictionnary
    """

    i = 1
    options = {}
    while(i < len(argv)):
        if (argv[i].startswith("-")):
            user_input = ""
            flag = argv[i][1:]
            i = i + 1
            while(i < len(argv) and not (argv[i].startswith("-"))):
                user_input += " {}".format(argv[i])
                i = i + 1
            options[flag] = user_input[1:]
        else:
            i = i + 1
    return options

def parse_options(options):
    """
    Check arguments requirements and shows help if asked. Loads lsystem file if everything is ok, exits if not

    :return: lsystem settings
    """

    if ("h" in options or "help" in options):
        print_help()
    if ("i" in options):
        if (not ("o" in options)):
            options["o"] = "./output.py"
        try:
            parse_file(options)
        except:
            custom_log("error", "Couldn't open the specified file")
        test_requirements(options)
        return options
    else:
        custom_log("error", "Please specify your lsystem file using the '-i /path/to your/lsystem.txt' argument\nFor additional help use the '-h' argument")


if __name__ == "__main__":
    """
    'Main' function of the program, treats arguments, settings, draws lsystem and writes instructions to file
    """

    points = []
    options = parse_options(get_arguments())

    onkey(lambda: tracer(0), "space")
    listen()

    title("Press SPACE to skip preview")
    speed(0)

    movement = get_moves(int(options["taille"]), int(options["angle"]), points)
    rgb = ("rgb" in options)
    custom_log("info", "Starting drawing...")
    try:
        treat_axiom(parse_levels(options["axiome"], int(options["niveau"]), options["regles"]), movement, options["o"], rgb)
        custom_log("info", "Finished drawing.")
    except:
        custom_log("error", "Couldn't write to the specified file")
        
    tracer(1)
    title("Click anywhere to close")
    exitonclick()