"""
Experimental module to create custom types that
we can reuse in our code to simplify the way we
declare our parameter types.
"""
from typing import Union


AudioType = Union[str, 'BinaryIO', 'BytesIO', 'np.ndarray']
"""
The type that we declare when using an audio
input.

- `Union[str, 'BinaryIO', 'BytesIO', 'np.ndarray']`

TODO: This is not including the moviepy audio
types.
"""

def validate_parameter_with_type(
    type: Union[AudioType, any],
    parameter_name: str,
    parameter_value: any,
    is_mandatory: bool = False
) -> None:
    """
    Validate the parameter with the given 'parameter_name'
    name and the 'parameter_value' value, according to the
    given 'type'.

    This method will raise an Exception if it is not valid.
    """
    # TODO: Maybe move this to top
    from yta_validation.parameter import ParameterValidator

    if type == AudioType:
        if is_mandatory:
            ParameterValidator.validate_mandatory_instance_of(parameter_name, parameter_value, [str, 'BinaryIO', 'BytesIO', 'np.ndarray'])
        else:
            ParameterValidator.validate_instance_of(parameter_name, parameter_value, [str, 'BinaryIO', 'BytesIO', 'np.ndarray'])