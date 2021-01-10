from time import localtime
from time import strftime
from turtle import *

def get_moves(size, angle, points):
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

def custom_log(type, message):
    print("{} [{}] {}".format(strftime("%H:%M:%S", localtime()), type.upper(), message))
    if (type == "error"): exit(1)

def a(size):
    pd()
    fd(size)
    return ("pd;fd({})\n".format(size))

def b(size):
    pu()
    fd(size)
    return ("pu;fd({})\n".format(size))

def plus(angle):
    right(angle)
    return ("right({})\n".format(angle))

def minus(angle):
    left(angle)
    return ("left({})\n".format(angle))

def snap():
    right(180)
    return ("right(180)\n")

def save_point(points):
    points.append({"linear": pos(), "rotational": heading()})
    return ("")

def jump_to(pos):
    goto(pos["linear"])
    setheading(pos["rotational"])
    return("goto({});setheading({})\n".format(pos["linear"], pos["rotational"]))

def rewind_to_point(points):
    r = -1
    if (len(points)):
        r = jump_to(points[-1])
        points.pop()
    else:
        custom_log("error", "Tried rewinding to non-existing point, please check your axiom")
    return r

def check_line(line):
    return ("=" in line)

def trim_spaces(text):
    return "".join(text.split())

def sanitize_line(line):
    return line.replace('"', "")

def parse_file(file):
    options = {"regles": []}
    f = open(file, 'r')
    lines = f.readlines()
    reading_rules = 0
    for line in lines:
        line = trim_spaces(line)
        if (check_line(line)):
            r = line.split("=")
            if (r[0] == "regles"):
                reading_rules = 1
            elif (reading_rules and line[0] == '"'):
                options["regles"].append(sanitize_line(line))
            else:
                reading_rules = 0
                options[r[0]] = sanitize_line(r[1])
        else:
            custom_log("error", "Provided file is not following the correct syntax")
    f.close()
    return options

def inject_rule(axiom, character, rule):
    return rule.join(axiom.split(character))

def parse_levels(axiom, levels, rules):
    for level in range(0, levels):
        for rule in rules:
            character, _, parsed_rule = rule.partition("=")
            if (character and parsed_rule):
                axiom = inject_rule(axiom, character, parsed_rule)
            else:
                custom_log("error", "Invalid rule: " + rule)
    return axiom

def treat_axiom(axiom, m, output, rgb):
    f = open(output, "w")
    f.write("from turtle import *;speed(0);onkey(lambda: tracer(0), 'space');listen();title('Press SPACE to skip preview')\n")
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
    f.write("tracer(1);exitonclick();title('Click anywhere to close')")
    f.close()
    custom_log("success", "Sctipt generated to {} . It can be launched using python {}".format(output, output))


if __name__ == "__main__":
    points = []
    output = "output.py"

    try:
        options = parse_file("text.txt")
    except:
        custom_log("error", "Couldn't open the specified file")

    movement = get_moves(int(options["taille"]), int(options["angle"]), points)
    rgb = ("rgb" in options and options["rgb"] == 1)
    onkey(lambda: tracer(0), "space")
    listen()
    title("Press SPACE to skip preview")
    speed(0)
    try:
        treat_axiom(parse_levels(options["axiome"], int(options["niveau"]), options["regles"]), movement, output, rgb)
    except:
        custom_log("error", "Couldn't write to the specified file")
    tracer(1)
    title("Click anywhere to close")
    exitonclick()