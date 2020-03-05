import pyglet
from math import sin
from timeit import default_timer

window = pyglet.window.Window(fullscreen=True, vsync=1)

whd2 = window.height//2
verts = [0, whd2 - 50, 100, whd2 - 50, 100, whd2 + 50, 0, whd2 + 50]
vlist = pyglet.graphics.vertex_list_indexed(4, (0, 1, 2, 0, 2, 3), ('v2i', verts), ('c3B', [0]*12))

@window.event
def on_key_press(symbol, modifiers):
    global should_close
    if symbol == pyglet.window.key.ESCAPE:
        should_close = True

if __name__ == '__main__':
    counter = 0
    should_close = False
    t0 = default_timer()
    times = []
    while not should_close:
        window.dispatch_events()
        counter += 1
        col = int(255*(sin((counter/10)+1)/2) + 127)
        vlist.colors[:] = [col]*12
        vlist.draw(pyglet.gl.GL_TRIANGLES)
        window.flip()
        window.clear()
        t1 = default_timer()
        dt = t1 - t0
        t0 = t1
        times.append(dt)
        
    window.close()
    times = times[5:]
    mean = sum(times)/len(times)
    print('mean %f, min %f, max %f' % (mean, min(times), max(times)))


