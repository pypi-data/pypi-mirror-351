#![allow(non_camel_case_types)] // Again due to generation -> Might solve eventually
use num_derive::FromPrimitive;
impl From<u32> for Rules {
    fn from(i: u32) -> Rules {
        let element = num::FromPrimitive::from_u32(i);
        match element {
            Some(rule) => rule,
            None => panic!("Not a valid Rule"),
        }
    }
}
#[allow(dead_code)]
pub static RULES_SIZE: u32 = 41;
#[allow(clippy::upper_case_acronyms)] // Again due to generation -> Might solve eventually
#[derive(PartialEq, Eq, Hash, FromPrimitive, Clone, Copy, Debug, Ord, PartialOrd)]

pub enum Rules {
    Grammar,
    annotation,
    annotation_block,
    annotation_content,
    annotation_name,
    array,
    attribute,
    binary,
    close_bracket,
    comment,
    digits,
    enum_value,
    enumeration,
    exponent,
    file_path,
    float,
    fraction,
    hex,
    import_model,
    import_namespace,
    input_params,
    integer,
    interface,
    major,
    method,
    minor,
    multiline_comment,
    number,
    open_bracket,
    output_params,
    package,
    sign,
    structure,
    type_collection,
    type_dec,
    type_ref,
    typedef,
    variable_declaration,
    variable_name,
    version,
    wildcard,
}
