/// How to deal with hit miss
/// * Miss to black
pub const MISS_NONE: u8 = 0;
/// How to deal with hit miss
/// * Miss to envmap
pub const MISS_ENVMAP: u8 = 1;

/// The normal used for reflection model
/// * Use face normal
pub const REFLECTION_NORMAL_FACE: u8 = 0;
/// The normal used for reflection model
/// * Use vertex normal
pub const REFLECTION_NORMAL_VERTEX: u8 = 1;
/// The normal used for reflection model
/// * Use texture normal
pub const REFLECTION_NORMAL_TEXTURE: u8 = 2;

/// The reflection model used for diffuse reflection
/// * No diffuse reflection
pub const REFLECTION_DIFFUSE_NONE: u8 = 0;
/// The reflection model used for diffuse reflection
/// * Lambertian diffuse reflection
pub const REFLECTION_DIFFUSE_LAMBERTIAN: u8 = 1;

/// The reflection model used for specular reflection
/// * No specular reflection
pub const REFLECTION_SPECULAR_NONE: u8 = 0;
/// The reflection model used for specular reflection
/// * Phong specular reflection
pub const REFLECTION_SPECULAR_PHONG: u8 = 1;
/// The reflection model used for specular reflection
/// * Blinn-Phong specular reflection
pub const REFLECTION_SPECULAR_BLINN_PHONG: u8 = 2;
/// The reflection model used for specular reflection
/// * Torrance-Sparrow specular reflection with Phong as D
pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_PHONG: u8 = 3;
/// The reflection model used for specular reflection
/// * Torrance-Sparrow specular reflection with Blinn-Phong as D
pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_BLINN_PHONG: u8 = 4;
/// The reflection model used for specular reflection
/// * Torrance-Sparrow specular reflection with Beckmann as D
pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_BECKMANN: u8 = 5;
