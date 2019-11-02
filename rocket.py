# rocket.py

import wadze  # Web Assembly Decoder
module = wadze.parse_module(open('program.wasm', 'rb').read())


# Build imported functions
import math

# These functions are imported by Wasm.  Must be implemented in the host
# environment (Python).  These are listed in the required order.

def imp_Math_atan(x):
    return float64(math.atan(x))

def imp_cos(x):
    return float64(math.cos(x))

def imp_sin(x):
    return float64(math.sin(x))

import pygame

pygame.init()

size = width, height = (800, 600)
screen = pygame.display.set_mode(size)

def imp_clear_screen():
    screen.fill((0,0,0))

def imp_draw_bullet(x, y):
    pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 2)

def imp_draw_enemy(x, y):
    pygame.draw.circle(screen, (255, 0, 255), (int(x), int(y)), 10, 2)

def imp_draw_particle(x, y, z):
    pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 5)

def imp_draw_player(x, y, z):
    pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 10)

def imp_draw_score(s):
    #print('draw_score', s)
    pass


import vm

# Declare as imported functions for our "machine"
imported_functions = [
    vm.ImportFunction(1, 1, imp_Math_atan),
    vm.ImportFunction(0, 0, imp_clear_screen),
    vm.ImportFunction(1, 1, imp_cos),
    vm.ImportFunction(2, 0, imp_draw_bullet),
    vm.ImportFunction(2, 0, imp_draw_enemy),
    vm.ImportFunction(3, 0, imp_draw_particle),
    vm.ImportFunction(3, 0, imp_draw_player),
    vm.ImportFunction(1, 0, imp_draw_score),
    vm.ImportFunction(1, 1, imp_sin),
]

# Declare "defined" functions
defined_functions = [ ]

for typeidx, code in zip(module['func'], module['code']):
    functype = module['type'][typeidx]  # Signature
    func = vm.Function(nparams=len(functype.params),
                            returns=bool(functype.returns),
                            code=wadze.parse_code(code).instructions)
    defined_functions.append(func)

functions = imported_functions + defined_functions

# Declare "exported" functions
exports = {exp.name: functions[exp.ref] for exp in module['export']
           if isinstance(exp, wadze.ExportFunction)}

m = vm.Machine(functions, 20*65536)     # Hack on memory

# Initialize memory
for data in module['data']:
    m.execute(data.offset, None)
    offset = m.pop()
    m.memory[offset:offset+len(data.values)] = data.values

from vm import float64, int32

# Call something
width = float64(800.0)
height = float64(600.0)

m.call(exports['resize'], width, height)

# Game loop
import time

last = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit()
        elif event.type == pygame.KEYUP:
            if event.key == 32:
                m.call(exports['toggle_shoot'], int32(0))
            elif event.key == 275:
                m.call(exports['toggle_turn_right'], int32(0))
            elif event.key == 276:
                m.call(exports['toggle_turn_left'], int32(0))
            elif event.key == 277:
                m.call(exports['toggle_boost'], int32(0))

        elif event.type == pygame.KEYDOWN:
            if event.key == 32:
                m.call(exports['toggle_shoot'], int32(1))
            elif event.key == 275:
                m.call(exports['toggle_turn_right'], int32(1))
            elif event.key == 276:
                m.call(exports['toggle_turn_left'], int32(1))
            elif event.key == 277:
                m.call(exports['toggle_boost'], int32(1))

    now = time.time()
    dt = now - last
    last = now
    m.call(exports['update'], float64(dt))
    m.call(exports['draw'])
    pygame.display.flip()


