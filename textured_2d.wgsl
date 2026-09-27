struct Matrix {
  vertex: mat4x4<f32>,
}
@group(0) @binding(0) var<storage, read> matrix: array<Matrix>;

struct Global {
  projection: mat4x4<f32>,
}
@group(1) @binding(0) var<uniform> global: Global;

@group(2) @binding(0) var image_texture: texture_2d<f32>;
@group(2) @binding(1) var image_sampler: sampler;

struct VertexOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) texcoord: vec2<f32>,
}

@vertex
fn vs_main(
  @builtin(instance_index) instance_index: u32,
  @location(0) position: vec2<f32>,
  @location(1) texcoord: vec2<f32>,
) -> VertexOutput {
  var output: VertexOutput;
  output.position = global.projection *
    (matrix[instance_index].vertex * vec4<f32>(position, 0.0, 1.0));
  output.texcoord = texcoord;
  return output;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  return textureSample(image_texture, image_sampler, input.texcoord);
}
