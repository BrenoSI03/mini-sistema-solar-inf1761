import math
from array import array

import wgpu
from cena_grafos.shape import Shape


class Disk(Shape):
    """Disco unitário texturizado formado por triângulos indexados."""

    def __init__(self, device, segments=64):
        """Cria os vértices, coordenadas de textura e buffers do disco."""
        # O primeiro vértice fica no centro do disco e da textura.
        coordinates = [0.0, 0.0]
        texcoords = [0.5, 0.5]

        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            x = math.cos(angle)
            y = math.sin(angle)
            coordinates += [x, y]
            texcoords += [0.5 + 0.5 * x, 0.5 - 0.5 * y]

        indices = []
        # Cada segmento forma um triângulo com o centro.
        for index in range(segments):
            first = index + 1
            second = (index + 1) % segments + 1
            indices += [0, first, second]

        self.index_count = len(indices)
        self.coordinate_buffer = device.create_buffer_with_data(
            data=array("f", coordinates),
            usage=wgpu.BufferUsage.VERTEX,
        )
        self.texcoord_buffer = device.create_buffer_with_data(
            data=array("f", texcoords),
            usage=wgpu.BufferUsage.VERTEX,
        )
        self.index_buffer = device.create_buffer_with_data(
            data=array("I", indices),
            usage=wgpu.BufferUsage.INDEX,
        )

    def draw(self, st):
        """Liga os buffers e desenha os triângulos indexados."""
        first_instance = st.get_shader().commit_matrix(st)
        st.render_pass.set_vertex_buffer(0, self.coordinate_buffer)
        st.render_pass.set_vertex_buffer(1, self.texcoord_buffer)
        st.render_pass.set_index_buffer(self.index_buffer, wgpu.IndexFormat.uint32)
        st.render_pass.draw_indexed(
            self.index_count, 1, 0, 0, first_instance
        )
