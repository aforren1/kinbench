import atexit
import glfw
import moderngl as mgl
import glm
from array import array
from math import sin

def on_key(win, key, scancode, action, modifiers):
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(win, True)


vert_string = '''
#version 330
in vec2 in_vert;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
'''

frag_string = '''
#version 330
uniform float color;
out vec4 oc;

void main() {
    oc = vec4(color, color, color, 1.0);
}
'''

if __name__ == '__main__':
    if not glfw.init():
        raise ValueError('GLFW init went wrong.')

    atexit.register(glfw.terminate)

    screen = 0
    monitor = glfw.get_monitors()[screen]
    video_mode = glfw.get_video_mode(monitor)

    width, height = video_mode.size
    size = width, height

    # Configure the OpenGL context
    glfw.window_hint(glfw.CONTEXT_CREATION_API, glfw.NATIVE_CONTEXT_API)
    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, False)  # turn on for mac compat
    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.DOUBLEBUFFER, True)
    glfw.window_hint(glfw.DEPTH_BITS, 0)  # 2d only?
    glfw.window_hint(glfw.SAMPLES, 8)  # MSAA
    glfw.window_hint(glfw.STENCIL_BITS, 0)  # no need for stencil buffer
    glfw.window_hint(glfw.REFRESH_RATE, video_mode.refresh_rate)
    glfw.window_hint(glfw.DECORATED, 0)  # no decorations allowed
    glfw.window_hint(glfw.STEREO, 0)
    glfw.window_hint(glfw.RED_BITS, video_mode.bits[0])
    glfw.window_hint(glfw.GREEN_BITS, video_mode.bits[1])
    glfw.window_hint(glfw.BLUE_BITS, video_mode.bits[2])
    glfw.window_hint(glfw.AUTO_ICONIFY, 0)

    win = glfw.create_window(width=width, height=height,
                             title='', monitor=monitor, share=None)
    
    glfw.make_context_current(win)
    glfw.swap_interval(True) # vsync?
    glfw.set_input_mode(win, glfw.CURSOR, glfw.CURSOR_HIDDEN)

    glfw.set_key_callback(win, on_key)

    # set up moderngl context
    major = glfw.get_window_attrib(win, glfw.CONTEXT_VERSION_MAJOR)
    minor = glfw.get_window_attrib(win, glfw.CONTEXT_VERSION_MINOR)

    ctx = mgl.create_context(require=int('%i%i0' % (major, minor)))
    ctx.viewport = (0, 0, width, height)
    ctx.disable(mgl.DEPTH_TEST)

    # set up square
    # we want 100px by 100px square on edge of screen
    # origin is top left corner
    prog = ctx.program(vertex_shader=vert_string, fragment_shader=frag_string)
    proj = glm.ortho(0, width, height, 0)

    verts = [*(proj * glm.vec4(0, height//2 - 50, 0, 1)).to_list()[:2],
             *(proj * glm.vec4(0, height//2 + 50, 0, 1)).to_list()[:2],
             *(proj * glm.vec4(100, height//2 - 50, 0, 1)).to_list()[:2],
             *(proj * glm.vec4(0, height//2 + 50, 0, 1)).to_list()[:2],
             *(proj * glm.vec4(100, height//2 + 50, 0, 1)).to_list()[:2],
             *(proj * glm.vec4(100, height//2 - 50, 0, 1)).to_list()[:2],]
    
    verts = array('f', verts)

    buf = ctx.buffer(bytes(verts))
    vao = ctx.vertex_array(prog, buf, 'in_vert')
    color = prog['color']

    counter = 0
    
    while not glfw.window_should_close(win):
        # draw
        counter += 1
        color.value = (sin(counter/10) + 1)/2
        vao.render()
        glfw.swap_buffers(win)
        glfw.poll_events()
        ctx.clear(0, 0, 0, 1)

    glfw.terminate()
