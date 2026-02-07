from enum import StrEnum


class OrderStatus(StrEnum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    COOKING = "COOKING"
    COURIER_ASSIGNED = "COURIER_ASSIGNED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


STATUS_LABEL = {
    OrderStatus.NEW: "Принят",
    OrderStatus.CONFIRMED: "Подтвержден",
    OrderStatus.COOKING: "Готовится",
    OrderStatus.COURIER_ASSIGNED: "Курьер назначен",
    OrderStatus.OUT_FOR_DELIVERY: "Передан курьеру",
    OrderStatus.DELIVERED: "Доставлен",
    OrderStatus.CANCELED: "Отменен",
}