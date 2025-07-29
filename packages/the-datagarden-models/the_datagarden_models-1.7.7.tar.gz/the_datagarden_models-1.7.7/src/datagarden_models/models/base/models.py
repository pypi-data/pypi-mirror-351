from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .legend import DataGardenModelLegends, Legend
from .metadata import MetadataModel, MetadataModelKeys


class DataGardenSubModel(BaseModel):
    """
    Base model class for DataGarden models that provides common functionality for data validation
    and manipulation.

    This class extends Pydantic's BaseModel and adds specialized methods for:
    - Checking if the model contains non-default values (has_values method)
    - Converting model data to a cleaned dictionary format with ounly (sub) models/attributes
      that have values (data_dump method)
    - Handling model legends/documentation (legends method)
    - Boolean evaluation of model state (is_empty and __bool__ properties)

    Attributes:
        Meta: Inner class for configuration, containing:
            exclude_fields_in_has_values_check (list[str]): Fields to exclude when checking if model
            has values

    Example:
        ```python
        class MySubModel(DataGardenSubModel):
            field1: str
            field2: Optional[int] = None

        model = MySubModel(field1="test")
        if model.has_values():
            print("Model contains data")
        ```
    """

    class Meta:
        exclude_fields_in_has_values_check: list[str] = []
        fields_to_include_in_data_dump: list[str] = ["datagarden_model_version", "metadata"]

    def has_values(self, data: BaseModel | None = None) -> bool:
        # Recursively check if any field has a non-default or non-empty value
        data = data or self
        for field, value in data:
            if field in ["datagarden_model_version", "metadata"]:
                continue
            if field in self.Meta.exclude_fields_in_has_values_check:
                continue

            if isinstance(value, DataGardenSubModel):
                if value.has_values():
                    return True
            elif value or value == 0 or value is False:  # This will check for truthy values (non-empty)
                return True
        return False

    @classmethod
    def legends(cls) -> Legend:
        return Legend(model=cls)

    @property
    def is_empty(self) -> bool:
        return not self.has_values()

    def __bool__(self) -> bool:
        return not self.is_empty

    def data_dump(self) -> dict:
        result = {}
        for field, value in self:
            if field in self.Meta.fields_to_include_in_data_dump:
                result[field] = value
            elif isinstance(value, DataGardenSubModel):
                if value.has_values():
                    result[field] = value.data_dump()
            elif value or value == 0 or value is False:  # This will check for truthy values (non-empty)
                result[field] = value
        return result


class DataGardenModelKeys(MetadataModelKeys):
    DATAGARDEN_MODEL_VERSION = "datagarden_model_version"
    LOCAL_REGIONAL_DATA = "local_regional_data"
    METADATA = "metadata"


class DataGardenModel(DataGardenSubModel):
    datagarden_model_version: str = Field(
        "v1.0",
        frozen=True,
        description=DataGardenModelLegends.DATAGARDEN_MODEL_VERSION,
    )
    local_regional_data: Optional[dict] = Field(
        default=None, description=DataGardenModelLegends.LOCAL_REGIONAL_DATA
    )
    metadata: MetadataModel = Field(default=MetadataModel(), description=DataGardenModelLegends.METADATA)

    @model_validator(mode="before")
    def check_datagarden_model_version(cls, values):
        if (
            "datagarden_model_version" in values
            and values["datagarden_model_version"] != cls.model_fields["datagarden_model_version"].default
        ):
            raise ValueError("The field 'datagarden_model_version' is immutable.")
        return values
