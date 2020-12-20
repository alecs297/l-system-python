from time import localtime
from time import strftime
from inspect import getsource
from turtle import *


default_jump = 5
default_angle = 45
default_speed = 0
default_input = "+a[a]++[a]*a"
default_file = "output.py"

points = []
output = default_file

axiom = "a-a-a-a"
rules = [
     "a=a+a*a+a+aa*aa+a+a*a+a"
]
angle = 90
level = 3

def custom_log(type, message):
    print("{} [{}] {}".format(strftime("%H:%M:%S", localtime()), type.upper(), message))

def a():
    pd()
    fd(default_jump)
    return ("pd;fd({})\n".format(default_jump))

def b():
    pu()
    fd(default_jump)
    return ("pu;fd({})\n".format(default_jump))

def plus():
    right(angle)
    return ("right({})\n".format(angle))

def minus():
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
        exit(1)
    return r

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
                exit(1)
    return axiom

def treat_axiom(axiom, m, output):
    r = "from turtle import *;speed({});onkey(lambda: tracer(0), 'space');listen();title('Press SPACE to skip preview')\n".format(default_speed)
    f = open(output, "w")
    for c in axiom:
        if (c in m):
            r += (m[c]())
        else:
            custom_log("error", "Unrecognized character in axiom: " + c)
            exit(1)
    f.write(r + "tracer(1);title('Click anywhere to close');exitonclick()")
    f.close()
    print("Sctipt generated to {} . It can be launched using python {}".format(output, output))

movement = {
    "a": a,
    "b": b,
    "+": plus,
    "-": minus,
    "*": snap,
    "[": lambda: save_point(points),
    "]": lambda: rewind_to_point(points)
}

onkey(lambda: tracer(0), "space")
listen()
title("Press SPACE to skip preview")
speed(default_speed)
treat_axiom(parse_levels(axiom, level, rules), movement, output)
tracer(1)
title("Click anywhere to close")
exitonclick()