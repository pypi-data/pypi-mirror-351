from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel
from rmediator.decorators import request
from rmediator.mediator import Request

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.business.dtos import CreateOrderDto
from ed_core.application.features.common.dtos import OrderDto


class CreateOrdersDto(BaseModel):
    orders: list[CreateOrderDto]


@request(BaseResponse[list[OrderDto]])
@dataclass
class CreateOrdersCommand(Request):
    business_id: UUID
    dto: CreateOrdersDto
