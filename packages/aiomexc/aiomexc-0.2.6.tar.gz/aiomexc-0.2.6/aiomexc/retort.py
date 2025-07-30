from adaptix import NameStyle, Retort, name_mapping

from aiomexc.methods import (
    MexcMethod,
    QueryOrder,
    CreateOrder,
    CreateListenKey,
    GetListenKeys,
    ExtendListenKey,
    DeleteListenKey,
)
from aiomexc.types import (
    Order,
    AccountInformation,
    TickerPrice,
    ListenKey,
    ListenKeys,
    CreateOrder as CreateOrderType,
)

type_recipes = [
    name_mapping(
        mexc_type,
        name_style=NameStyle.CAMEL,
    )
    for mexc_type in [
        Order,
        AccountInformation,
        TickerPrice,
        ListenKey,
        ListenKeys,
        CreateOrderType,
    ]
]

method_recipes = [
    name_mapping(
        mexc_method,
        name_style=NameStyle.CAMEL,
        omit_default=True,
    )
    for mexc_method in [
        MexcMethod,
        QueryOrder,
        CreateOrder,
        CreateListenKey,
        GetListenKeys,
        ExtendListenKey,
        DeleteListenKey,
    ]
]

_retort = Retort(
    recipe=method_recipes + type_recipes,
)

__all__ = ["_retort"]
