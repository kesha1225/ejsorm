import typing

HeftyData = typing.List[typing.Dict[str, typing.Any]]
HeftyObject = typing.Dict[str, typing.Any]
HeftyTable = typing.Dict[
    str, typing.Union[str, typing.List[typing.Dict[str, typing.Any]]]
]
HeftyTableData = typing.List[typing.Dict[str, typing.Any]]
HeftySchema = typing.Dict[
    str, typing.Union[typing.Dict[str, typing.Union[str, typing.Dict]], str]
]
