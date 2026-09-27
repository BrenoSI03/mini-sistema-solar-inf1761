import time
from pathlib import Path
from typing import cast

import wgpu
from rendercanvas.glfw import RenderCanvas, loop

from cena_grafos.camera2d import Camera2D
from cena_grafos.engine import Engine
from cena_grafos.node import Node
from cena_grafos.pipeline import Pipeline
from cena_grafos.renderer import Renderer
from cena_grafos.sampler import Sampler
from cena_grafos.scene import Scene
from cena_grafos.shader import Shader
from cena_grafos.square import Square
from cena_grafos.texture import Texture
from cena_grafos.textureset import TextureSet
from cena_grafos.transform import Transform
from disk import Disk


PROJECT_DIR = Path(__file__).resolve().parent


class SolarSystemAnimation(Engine):
    """Atualiza as órbitas e o giro próprio da Terra."""

    def __init__(self, earth_orbit, earth_spin, moon_orbit, mercury_orbit):
        """Guarda as transformações e inicia os ângulos da animação."""
        self.earth_orbit = earth_orbit
        self.earth_spin = earth_spin
        self.moon_orbit = moon_orbit
        self.mercury_orbit = mercury_orbit
        self.earth_angle = 0.0
        self.earth_spin_angle = 0.0
        self.moon_angle = 0.0
        self.mercury_angle = 0.0

    def update_orbit(self, transform, angle, radius):
        """Compõe uma órbita circular com o raio informado."""
        transform.load_identity()
        # A rotação orbital é aplicada antes da translação radial.
        transform.rotate(angle, 0.0, 0.0, 1.0)
        transform.translate(radius, 0.0, 0.0)

    def update(self, dt):
        """Avança os ângulos de acordo com o tempo decorrido."""
        self.earth_angle = (self.earth_angle + 25.0 * dt) % 360.0
        self.earth_spin_angle = (self.earth_spin_angle + 90.0 * dt) % 360.0
        self.moon_angle = (self.moon_angle + 110.0 * dt) % 360.0
        self.mercury_angle = (self.mercury_angle + 60.0 * dt) % 360.0

        self.update_orbit(self.earth_orbit, self.earth_angle, 5.5)
        self.update_orbit(self.moon_orbit, self.moon_angle, 1.5)
        self.update_orbit(self.mercury_orbit, self.mercury_angle, 3.2)

        self.earth_spin.load_identity()
        self.earth_spin.rotate(self.earth_spin_angle, 0.0, 0.0, 1.0)


def scale_transform(value):
    """Cria uma transformação de escala uniforme em 2D."""
    transform = Transform()
    transform.scale(value, value, 1.0)
    return transform


def load_texture(device, shader, sampler, filename):
    """Carrega uma imagem e registra seu conjunto de textura no shader."""
    path = PROJECT_DIR / "imagens" / filename
    texture_set = TextureSet([
        Texture(device, "image_texture", str(path)),
        sampler,
    ])
    shader.add_texture_set(texture_set)
    return texture_set


def create_pipeline(device, target_format):
    """Cria o shader e o pipeline usados por todos os objetos."""
    shader = Shader(device, str(PROJECT_DIR / "textured_2d.wgsl"))
    shader.set_vertex_buffers([
        {
            "array_stride": 8,
            "step_mode": "vertex",
            "attributes": [
                {"format": "float32x2", "offset": 0, "var_name": "position"},
            ],
        },
        {
            "array_stride": 8,
            "step_mode": "vertex",
            "attributes": [
                {"format": "float32x2", "offset": 0, "var_name": "texcoord"},
            ],
        },
    ])

    alpha_blend = {
        "color": {
            "src_factor": "src-alpha",
            "dst_factor": "one-minus-src-alpha",
            "operation": "add",
        },
        "alpha": {
            "src_factor": "one",
            "dst_factor": "one-minus-src-alpha",
            "operation": "add",
        },
    }
    return Pipeline(
        shader,
        target_format,
        depth_stencil=None,
        blend=alpha_blend,
    ), shader


def create_body(size, texture, disk):
    """Cria um nó de astro com escala, textura e disco."""
    return Node(trf=scale_transform(size), apps=[texture], shps=[disk])


def create_scene(device, target_format):
    """Cria os recursos e monta a hierarquia do sistema solar."""
    pipeline, shader = create_pipeline(device, target_format)
    sampler = Sampler(device, "image_sampler")

    # As imagens e os recursos GPU são carregados somente no setup.
    sun_texture = load_texture(device, shader, sampler, "sun.png")
    earth_texture = load_texture(device, shader, sampler, "earth.png")
    moon_texture = load_texture(device, shader, sampler, "moon.png")
    mercury_texture = load_texture(device, shader, sampler, "mercury.png")
    space_texture = load_texture(device, shader, sampler, "space.jpg")

    disk = Disk(device)
    sun = create_body(2.0, sun_texture, disk)
    earth = create_body(0.8, earth_texture, disk)
    moon = create_body(0.35, moon_texture, disk)
    mercury = create_body(0.45, mercury_texture, disk)
    background = Node(
        trf=scale_transform(10.0),
        apps=[space_texture],
        shps=[Square(device)],
    )

    earth_orbit = Transform()
    earth_spin = Transform()
    moon_orbit = Transform()
    mercury_orbit = Transform()

    mercury_orbit_node = Node(trf=mercury_orbit, nodes=[mercury])
    earth_spin_node = Node(trf=earth_spin, nodes=[earth])
    moon_orbit_node = Node(trf=moon_orbit, nodes=[moon])
    # A Lua herda a órbita da Terra, mas não seu giro próprio.
    earth_orbit_node = Node(
        trf=earth_orbit,
        nodes=[earth_spin_node, moon_orbit_node],
    )

    root = Node(
        pipeline=pipeline,
        nodes=[background, sun, mercury_orbit_node, earth_orbit_node],
    )
    scene = Scene(root)
    animation = SolarSystemAnimation(
        earth_orbit,
        earth_spin,
        moon_orbit,
        mercury_orbit,
    )
    animation.update(0.0)
    scene.add_engine(animation)
    return scene


canvas = RenderCanvas(
    size=(800, 800),
    title="Projeto 1 - Mini-sistema solar 2D",
    update_mode="continuous",
    max_fps=60,
)
context = cast(wgpu.GPUCanvasContext, canvas.get_context("wgpu"))
adapter = wgpu.gpu.request_adapter_sync(
    power_preference="high-performance",
    canvas=context,
)
device = adapter.request_device_sync()
target_format = context.get_preferred_format(adapter)
context.configure(device=device, format=target_format, alpha_mode="opaque")

camera = Camera2D(-10.0, 10.0, -10.0, 10.0)
renderer = Renderer(device, clear_value=(0.0, 0.0, 0.0, 1.0))
scene = create_scene(device, target_format)
last_time = time.perf_counter()


def draw_frame():
    """Atualiza a animação e renderiza um quadro."""
    global last_time
    current_time = time.perf_counter()
    scene.update(current_time - last_time)
    last_time = current_time
    renderer.render(context.get_current_texture(), scene, camera)


canvas.request_draw(draw_frame)

if __name__ == "__main__":
    loop.run()
