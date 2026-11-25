"""Recortes dos estudos-amostra do rotzx Pro (D81): cada módulo define um `RECORTE`."""
from .cafe import RECORTE as CAFE
from .fertilizantes import RECORTE as FERTILIZANTES

ESTUDOS = {"fertilizantes": FERTILIZANTES, "cafe": CAFE}
