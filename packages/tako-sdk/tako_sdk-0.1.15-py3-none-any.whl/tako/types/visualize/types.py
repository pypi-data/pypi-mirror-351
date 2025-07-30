from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel, Field

class TakoDataFormatValueType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    FLOAT = "float"
    NULL = "null"
    ANY = "any"


class TakoDataFormatCellValue(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        description="The value of the variable",
        examples=["Apple", 1000000],
    )


class TakoDataFormatRowValues(BaseModel):
    cell_values: list[TakoDataFormatCellValue] = Field(
        description="Each cell contains a single aspect (variable + value)",
        examples=[
            [
                {"variable_name": "Company", "value": "Apple"},
                {"variable_name": "Revenue", "value": 1000000},
            ]
        ],
    )


class TakoDataFormatTimeseriesVariableType(str, Enum):
    SERIES = "series"
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"

class TakoDataFormatCategoryVariableType(str, Enum):
    CATEGORY = "category"
    VALUE = "value"


class TakoDataFormatVariable(BaseModel):
    # Variable contains rich metadata about the variables for each observation
    name: str = Field(
        description="The human friendly name of the column variable",
        examples=["Company", "Revenue"],
    )
    type: TakoDataFormatValueType = Field(
        description="The type of the column variable",
        examples=[TakoDataFormatValueType.STRING, TakoDataFormatValueType.NUMBER],
    )
    units: Optional[str] = Field(
        description="The units of the variable in the data",
        examples=["USD", "EUR"],
    )
    is_sortable: Optional[bool] = Field(
        description="Whether the data is sortable by this variable",
    )
    is_higher_better: Optional[bool] = Field(
        description="Whether a higher value of this variable is better",
    )
    timeseries_variable_type: Optional[TakoDataFormatTimeseriesVariableType] = Field(
        description="The type of the variable in the timeseries visualization. "
        "SERIES: The variable should be a series in the timeseries visualization. "
        "X_AXIS: The variable should be the x-axis of the timeseries visualization. This "
        "must be in ISO 8601 format (YYYY-MM-DD). "
        "Y_AXIS: The variable should be the y-axis of the timeseries visualization. "
        "This is typically a numeric column.",
        examples=[
            TakoDataFormatTimeseriesVariableType.SERIES,
            TakoDataFormatTimeseriesVariableType.X_AXIS,
            TakoDataFormatTimeseriesVariableType.Y_AXIS,
        ],
    )
    category_variable_type: TakoDataFormatCategoryVariableType | None = Field(
        description="The type of the category variable",
        examples=[
            TakoDataFormatCategoryVariableType.CATEGORY,
            TakoDataFormatCategoryVariableType.VALUE,
        ],
    )


class TakoDataFormatDataset(BaseModel):
    # A single dataset contains all column variables and all the rows of data
    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: Optional[str] = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    variables: list[TakoDataFormatVariable] = Field(
        description="Details about all variables in the dataset",
        examples=[
            [
                {
                    "name": "Company",
                    "type": TakoDataFormatValueType.STRING,
                    "units": None,
                    "is_sortable": True,
                    "is_higher_better": True,
                },
            ]
        ],
    )
    rows: list[TakoDataFormatRowValues] = Field(
        description="Each row contains a single coherent set of values with each "
        "cell having different aspects (variable + value)",
        examples=[
            [
                {
                    "values": [
                        {"variable_name": "Company", "value": "Apple"},
                        {"variable_name": "Revenue", "value": 1000000},
                    ]
                },
            ]
        ],
    )


class SimpleDataPoint(BaseModel):
    variable_name: str = Field(
        description="The name of the variable",
        examples=["Company", "Revenue"],
    )
    value: Optional[Union[str, int, float, bool]] = Field(
        description="The value of the variable",
        examples=["Apple", 1000000],
    )


class SimpleDataset(BaseModel):
    title: str = Field(
        description="The title of the dataset",
        examples=["Walmart vs Verizon Total Revenue"],
    )
    description: Optional[str] = Field(
        description="The description of the dataset",
        examples=["Comparison of Walmart and Verizon's Total Revenue (fiscal years)"],
    )
    data_points: list[SimpleDataPoint] = Field(
        description="The data points to visualize",
        examples=[
            {"variable_name": "Company", "value": "Apple"},
            {"variable_name": "Revenue", "value": 1000000},
        ],
    )


class VisualizeRequest(BaseModel):
    simple_dataset: Optional[SimpleDataset] = Field(
        description="The simple dataset to visualize", default=None
    )
    tako_formatted_dataset: Optional[TakoDataFormatDataset] = Field(
        description="The tako formatted dataset to visualize", default=None
    )