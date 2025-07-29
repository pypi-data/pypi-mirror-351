import json
from typing import Dict, Any, NamedTuple, Optional, Type
from copy import deepcopy


def check_required(env: Dict[str, str], required: list[str]):
    """Check if required environment variables are set.

    Parameters
    ----------
    env : Dict[str, str]
        The environment variables.
    required : list[str]
        A list of required environment variables.

    Raises
    ------
    ValueError
        If any required environment variables are missing.

    """
    missing = [var for var in required if not env.get(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")


class ParamConfig(NamedTuple):
    """Configuration for a single parameter."""

    env_var: str
    key: str
    is_json: bool
    allow_empty: bool
    type_val: Type


class EnvVarBuilder:
    """A builder class for constructing a dictionary of parameters from environment variables.

    This class provides a fluent interface for parsing and transforming environment variables
    into a structured dictionary, with support for JSON parsing and type conversion.

    Attributes
    ----------
    env : Dict[str, str]
        The environment variables.
    params : dict
        The dictionary of parsed parameters.

    Parameters
    ----------
    env: Dict[str, str]
        The environment variables.

    Examples
    --------
    >>> env = {"MY_VAR": "123", "JSON_VAR": '{"key": "value"}'}
    >>> builder = EnvVarBuilder(env)
    >>> result = (builder
    ...     .with_var("MY_VAR", "my_key", type_hint=int)
    ...     .with_var("JSON_VAR", "json_key", is_json=True)
    ...     .build())
    >>> # result = {"my_key": 123, "json_key": {"key": "value"}}

    Notes
    -----
    - The builder creates deep copies of values to prevent mutation
    - JSON parsing is performed before type conversion
    - Empty strings are ignored by default unless allow_empty is True

    """

    def __init__(self, env: Dict[str, str]):
        self.env = env
        self._params = {}

    def _parse_value(
        self, value: str, is_json: bool, type_hint: Optional[Type]
    ) -> Any:
        """Parse the value based on the configuration.

        Parameters
        ----------
        value : str
            The value to parse
        is_json : bool, optional
            If True, parse the value as JSON, by default False
        allow_empty : bool, optional
            If True, include empty strings in the result, by default False
        type_hint : Type, optional
            Type to convert the value to (if not JSON), by default str

        Returns
        -------
        Any
            The parsed value as the specified type or JSON object

        Notes
        -----
        - JSON parsing is performed before type conversion if is_json is True

        """
        if is_json:
            return json.loads(value)
        if type_hint is not None:
            return type_hint(value)

    def _parse_single_param(self, config: ParamConfig):
        """Parse a single parameter from the environment variables."""
        value = self.env.get(config.env_var)
        if value is not None and (config.allow_empty or value.strip()):
            parsed_value = self._parse_value(
                value, config.is_json, config.type_val
            )
            self._update_params(config.key, parsed_value)

    def _update_params(self, key: str, value: Any):
        self._params = deepcopy(self._params)
        self._params[key] = deepcopy(value)

    def update_state(
        self,
        var_name: str,
        key: str,
        is_json: bool = False,
        allow_empty: bool = False,
        type_hint: Type = str,
    ) -> "EnvVarBuilder":
        """Update the state of the builder with a single parameter.

        Returns
        -------
        EnvVarBuilder
            Returns self for method chaining

        Raises
        ------
        ValueError
            If any configured environment variable parsing fails

        Notes
        -----
        - Empty strings are ignored by default unless allow_empty is True
        - JSON parsing is performed before type conversion if is_json is True

        """
        config = ParamConfig(var_name, key, is_json, allow_empty, type_hint)

        self._parse_single_param(config)
        return self

    @property
    def params(self) -> dict:
        """Returns a copyt of the dictionary of parsed parameters."""
        return deepcopy(self._params)
