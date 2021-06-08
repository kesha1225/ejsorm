import typing

EJData = typing.List[typing.Dict[str, typing.Any]]
EJObject = typing.Dict[str, typing.Any]
EJTable = typing.Dict[
    str, typing.Union[str, typing.List[typing.Dict[str, typing.Any]]]
]
EJTableData = typing.List[typing.Dict[str, typing.Any]]
EJSchema = typing.Dict[
    str, typing.Union[typing.Dict[str, typing.Union[str, typing.Dict]], str]
]
