from ejsorm import EJModel

REF = "$ref"


class Reference:
    def __init__(self, model: EJModel, field_title: str):
        self.model = model
        self.field_title = field_title

    def __str__(self) -> str:
        return f"Reference({self.model=}, {self.field_title=})"
