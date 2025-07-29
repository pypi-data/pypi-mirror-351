"""Pydantic Models for Resource Definitions, used to define default resources for a node or workcell."""

from typing import Annotated, Any, Literal, Optional, Union

from madsci.common.types.auth_types import OwnershipInfo
from madsci.common.types.base_types import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    PositiveNumber,
)
from madsci.common.types.event_types import EventClientConfig
from madsci.common.types.lab_types import ManagerDefinition, ManagerType
from madsci.common.types.resource_types.resource_enums import ResourceTypeEnum
from madsci.common.utils import new_name_str
from pydantic import AfterValidator
from pydantic.functional_validators import field_validator
from pydantic.types import Discriminator, Tag
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field


def single_letter_or_digit_validator(value: str) -> str:
    """Validate that the value is a single letter or digit."""
    if not (value.isalpha() and len(value) == 1) or value.isdigit():
        raise ValueError("Value must be a single letter or digit.")
    return value


GridIndex = Union[
    int,
    Annotated[str, AfterValidator(single_letter_or_digit_validator)],
]
GridIndex2D = tuple[GridIndex, GridIndex]
GridIndex3D = tuple[GridIndex, GridIndex, GridIndex]


class ResourceManagerDefinition(ManagerDefinition):
    """Definition for a Resource Manager's Configuration"""

    manager_type: Literal[ManagerType.RESOURCE_MANAGER] = Field(
        title="Manager Type",
        description="The type of the resource manager",
        default=ManagerType.RESOURCE_MANAGER,
    )
    host: str = Field(
        default="127.0.0.1",
        title="Server Host",
        description="The hostname or IP address of the Resource Manager server.",
    )
    port: int = Field(
        default=8003,
        title="Server Port",
        description="The port number of the Resource Manager server.",
    )
    db_url: str = Field(
        default="postgresql://rpl:rpl@localhost:5432/resources",
        title="Database URL",
        description="The URL of the database used by the Resource Manager.",
    )
    event_client_config: Optional[EventClientConfig] = Field(
        default=None,
        title="Event Client Configuration",
        description="Configuration for the event client.",
    )
    custom_types: dict[str, "ResourceDefinitions"] = Field(
        default_factory=dict,
        title="Custom Types",
        description="Custom Types for this resource manager",
    )


class CustomResourceAttributeDefinition(BaseModel, extra="allow"):
    """Definition for a MADSci Custom Resource Attribute."""

    attribute_name: str = Field(
        title="Attribute Name",
        description="The name of the attribute.",
    )
    attribute_description: Optional[str] = Field(
        default=None,
        title="Attribute Description",
        description="A description of the attribute.",
    )
    optional: bool = Field(
        default=False,
        title="Optional",
        description="Whether the attribute is optional.",
    )
    default_value: Any = Field(
        default=None,
        title="Default Value",
        description="The default value of the attribute.",
        sa_type=JSON,
    )


class ResourceDefinition(BaseModel, table=False, extra="allow"):
    """Definition for a MADSci Resource."""

    model_config = ConfigDict(extra="allow")
    resource_name: str = Field(
        title="Resource Name",
        description="The name of the resource.",
        default_factory=new_name_str,
    )

    resource_name_prefix: Optional[str] = Field(
        title="Resource Name Prefix",
        description="A prefix to append the key of the object to for machine instanciated resources",
        default=None,
    )
    resource_class: str = Field(
        title="Resource Class",
        description="The class of the resource. Must match a class defined in the resource manager.",
        default="",
        nullable=False,
    )
    base_type: Literal[ResourceTypeEnum.resource] = Field(
        default=ResourceTypeEnum.resource,
        title="Resource Base Type",
        description="The base type of the resource.",
    )
    resource_description: Optional[str] = Field(
        default=None,
        title="Resource Description",
        description="A description of the resource.",
    )
    owner: OwnershipInfo = Field(
        default_factory=OwnershipInfo,
        title="Ownership Info",
        description="The owner of this resource",
        sa_type=JSON,
    )
    custom_attributes: Optional[list["CustomResourceAttributeDefinition"]] = Field(
        default=None,
        title="Custom Attributes",
        description="Custom attributes used by resources of this type.",
        sa_type=JSON,
    )

    @classmethod
    def discriminate(cls, resource: dict) -> "ResourceDefinition":
        """Discriminate the resource definition based on its base type."""
        from madsci.common.types.resource_types import RESOURCE_TYPE_MAP

        if isinstance(resource, dict):
            resource_type = resource.get("base_type")
        else:
            resource_type = resource.base_type
        return RESOURCE_TYPE_MAP[resource_type]["definition"].model_validate(resource)


class AssetResourceDefinition(ResourceDefinition, table=False):
    """Definition for an asset resource."""

    base_type: Literal[ResourceTypeEnum.asset] = Field(
        default=ResourceTypeEnum.asset,
        title="Resource Base Type",
        description="The base type of the asset.",
    )


class ConsumableResourceDefinition(ResourceDefinition):
    """Definition for a consumable resource."""

    base_type: Literal[ResourceTypeEnum.consumable] = Field(
        default=ResourceTypeEnum.consumable,
        title="Resource Base Type",
        description="The base type of the consumable.",
    )
    unit: Optional[str] = Field(
        default=None,
        title="Resource Unit",
        description="The unit used to measure the quantity of the consumable.",
    )
    quantity: PositiveNumber = Field(
        default=0.0,
        title="Default Resource Quantity",
        description="The initial quantity of the consumable.",
    )
    capacity: Optional[PositiveNumber] = Field(
        default=None,
        title="Resource Capacity",
        description="The initial capacity of the consumable.",
    )


class DiscreteConsumableResourceDefinition(ConsumableResourceDefinition):
    """Definition for a discrete consumable resource."""

    base_type: Literal[ResourceTypeEnum.discrete_consumable] = Field(
        default=ResourceTypeEnum.discrete_consumable,
        title="Resource Base Type",
        description="The base type of the consumable.",
    )
    quantity: PositiveInt = Field(
        default=0,
        title="Default Resource Quantity",
        description="The initial quantity of the consumable.",
    )
    capacity: Optional[PositiveInt] = Field(
        default=None,
        title="Resource Capacity",
        description="The initial capacity of the consumable.",
    )


class ContinuousConsumableResourceDefinition(ConsumableResourceDefinition):
    """Definition for a continuous consumable resource."""

    base_type: Literal[ResourceTypeEnum.continuous_consumable] = Field(
        default=ResourceTypeEnum.continuous_consumable,
        title="Resource Base Type",
        description="The base type of the continuous consumable.",
    )


class ContainerResourceDefinition(ResourceDefinition):
    """Definition for a container resource."""

    base_type: Literal[ResourceTypeEnum.container] = Field(
        default=ResourceTypeEnum.container,
        title="Resource Base Type",
        description="The base type of the container.",
    )
    capacity: Optional[Union[int, float]] = Field(
        default=None,
        title="Container Capacity",
        description="The capacity of the container. If None, uses the type's default_capacity.",
    )
    default_children: Optional[
        Union[list[ResourceDefinition], dict[str, ResourceDefinition]]
    ] = Field(
        default=None,
        title="Default Children",
        description="The default children to create when initializing the container. If None, use the type's default_children.",
    )
    default_child_template: Optional["ResourceDefinitions"] = Field(
        default=None,
        title="Default Child Template",
        description="Template for creating child resources, supporting variable substitution. If None, use the type's default_child_template.",
    )


class CollectionResourceDefinition(ContainerResourceDefinition):
    """Definition for a collection resource. Collections are used for resources that have a number of children, each with a unique key, which can be randomly accessed."""

    base_type: Literal[ResourceTypeEnum.collection] = Field(
        default=ResourceTypeEnum.collection,
        title="Resource Base Type",
        description="The base type of the collection.",
    )
    keys: Optional[Union[int, list[str]]] = Field(
        default=None,
        title="Collection Keys",
        description="The keys for the collection. Can be an integer (converted to 1-based range) or explicit list.",
    )
    default_children: Optional[
        Union[list[ResourceDefinition], dict[str, ResourceDefinition]]
    ] = Field(
        default=None,
        title="Default Children",
        description="The default children to create when initializing the collection. If None, use the type's default_children.",
    )

    @field_validator("keys", mode="before")
    @classmethod
    def validate_keys(cls, v: Union[int, list[str], None]) -> Optional[list[str]]:
        """Convert integer keys to 1-based range if needed."""
        if isinstance(v, int):
            return [str(i) for i in range(1, v + 1)]
        return v


class RowResourceDefinition(ContainerResourceDefinition):
    """Definition for a row resource. Rows are 1D collections of resources. They are treated as single collections (i.e. Collection[Resource])."""

    base_type: Literal[ResourceTypeEnum.row] = Field(
        default=ResourceTypeEnum.row,
        title="Resource Base Type",
        description="The base type of the row.",
    )
    default_children: Optional[dict[str, ResourceDefinition]] = Field(
        default=None,
        title="Default Children",
        description="The default children to create when initializing the collection. If None, use the type's default_children.",
    )
    fill: bool = Field(
        default=False,
        title="Fill",
        description="Whether to populate every empty key with a default child",
    )
    columns: int = Field(
        title="Number of Columns",
        description="The number of columns in the row.",
        ge=0,
    )
    is_one_indexed: bool = Field(
        title="One Indexed",
        description="Whether the numeric index of the object start at 0 or 1",
        default=True,
    )


class GridResourceDefinition(RowResourceDefinition):
    """Definition for a grid resource. Grids are 2D grids of resources. They are treated as nested collections (i.e. Collection[Collection[Resource]])."""

    base_type: Literal[ResourceTypeEnum.grid] = Field(
        default=ResourceTypeEnum.grid,
        title="Resource Base Type",
        description="The base type of the grid.",
    )
    default_children: Optional[dict[str, dict[str, ResourceDefinition]]] = Field(
        default=None,
        title="Default Children",
        description="The default children to create when initializing the collection. If None, use the type's default_children.",
    )
    rows: int = Field(
        default=None,
        title="Number of Rows",
        description="The number of rows in the grid. If None, use the type's rows.",
    )


class VoxelGridResourceDefinition(GridResourceDefinition):
    """Definition for a voxel grid resource. Voxel grids are 3D grids of resources. They are treated as nested collections (i.e. Collection[Collection[Collection[Resource]]])."""

    base_type: Literal[ResourceTypeEnum.voxel_grid] = Field(
        default=ResourceTypeEnum.voxel_grid,
        title="Resource Base Type",
        description="The base type of the voxel grid.",
    )
    default_children: Optional[dict[str, dict[str, dict[str, ResourceDefinition]]]] = (
        Field(
            default=None,
            title="Default Children",
            description="The default children to create when initializing the collection. If None, use the type's default_children.",
        )
    )
    layers: int = Field(
        title="Number of Layers",
        description="The number of layers in the voxel grid. If None, use the type's layers.",
    )

    def get_all_keys(self) -> list:
        """get all keys of this object"""
        return [
            GridIndex3D((i, j, k))
            for i in range(self.columns)
            for j in range(self.rows)
            for k in range(self.layers)
        ]


class SlotResourceDefinition(ContainerResourceDefinition):
    """Definition for a slot resource."""

    base_type: Literal[ResourceTypeEnum.slot] = Field(
        default=ResourceTypeEnum.slot,
        title="Resource Base Type",
        description="The base type of the slot.",
    )

    default_child_quantity: Optional[int] = Field(
        default=None,
        title="Default Child Quantity",
        description="The number of children to create by default. If None, use the type's default_child_quantity.",
        ge=0,
        le=1,
    )
    capacity: Literal[1] = Field(
        title="Capacity",
        description="The capacity of the slot.",
        default=1,
        const=1,
    )


class StackResourceDefinition(ContainerResourceDefinition):
    """Definition for a stack resource."""

    base_type: Literal[ResourceTypeEnum.stack] = Field(
        default=ResourceTypeEnum.stack,
        title="Resource Base Type",
        description="The base type of the stack.",
    )
    default_child_quantity: Optional[int] = Field(
        default=None,
        title="Default Child Quantity",
        description="The number of children to create by default. If None, use the type's default_child_quantity.",
    )


class QueueResourceDefinition(ContainerResourceDefinition):
    """Definition for a queue resource."""

    base_type: Literal[ResourceTypeEnum.queue] = Field(
        default=ResourceTypeEnum.queue,
        title="Resource Base Type",
        description="The base type of the queue.",
    )
    default_child_quantity: Optional[int] = Field(
        default=None,
        title="Default Child Quantity",
        description="The number of children to create by default. If None, use the type's default_child_quantity.",
    )


class PoolResourceDefinition(ContainerResourceDefinition):
    """Definition for a pool resource. Pool resources are collections of consumables with no structure (used for wells, reservoirs, etc.)."""

    base_type: Literal[ResourceTypeEnum.pool] = Field(
        default=ResourceTypeEnum.pool,
        title="Resource Base Type",
        description="The base type of the pool.",
    )
    capacity: Optional[PositiveNumber] = Field(
        title="Capacity",
        description="The default capacity of the pool as a whole.",
        default=None,
    )
    unit: Optional[str] = Field(
        default=None,
        title="Resource Unit",
        description="The unit used to measure the quantity of the pool.",
    )


ResourceDefinitions = Annotated[
    Union[
        Annotated[ResourceDefinition, Tag("resource")],
        Annotated[AssetResourceDefinition, Tag("asset")],
        Annotated[ContainerResourceDefinition, Tag("container")],
        Annotated[CollectionResourceDefinition, Tag("collection")],
        Annotated[RowResourceDefinition, Tag("row")],
        Annotated[GridResourceDefinition, Tag("grid")],
        Annotated[VoxelGridResourceDefinition, Tag("voxel_grid")],
        Annotated[StackResourceDefinition, Tag("stack")],
        Annotated[QueueResourceDefinition, Tag("queue")],
        Annotated[PoolResourceDefinition, Tag("pool")],
        Annotated[SlotResourceDefinition, Tag("slot")],
        Annotated[ConsumableResourceDefinition, Tag("consumable")],
        Annotated[DiscreteConsumableResourceDefinition, Tag("discrete_consumable")],
        Annotated[ContinuousConsumableResourceDefinition, Tag("continuous_consumable")],
    ],
    Discriminator("base_type"),
]
