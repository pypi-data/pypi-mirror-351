from typing import Any, Dict, cast

from pydantic import BaseModel, Field

from pipelex.tools.typing.pydantic_utils import ExtraFieldAttribute, serialize_model


class ChildModel(BaseModel):
    child_name: str
    child_secret: str = Field(
        ...,
        json_schema_extra={ExtraFieldAttribute.IS_HIDDEN: True},  # This field should be hidden
    )


class ParentModel(BaseModel):
    parent_name: str
    child: ChildModel


def test_serialize_model_with_hidden_fields():
    # Create nested models
    child = ChildModel(child_name="foo", child_secret="secret_foo")
    parent = ParentModel(parent_name="bar", child=child)

    # Test default model_dump() shows everything
    model_dump_result: Dict[str, Any] = parent.model_dump()
    child_dict = cast(Dict[str, Any], model_dump_result["child"])
    assert "child_secret" in child_dict
    assert child_dict["child_secret"] == "secret_foo"

    # Test our custom serializer omits hidden fields (child_secret)
    serialized_result = cast(Dict[str, Any], serialize_model(parent))
    child_serialized = cast(Dict[str, Any], serialized_result["child"])
    assert "child_secret" not in child_serialized
    assert serialized_result == {"parent_name": "bar", "child": {"child_name": "foo"}}
