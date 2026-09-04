"""parte1_diagnostico_Original.py — Dominio Figura / Polígono / Lado refactorizado a Python idiomático."""

from typing import List, Optional, Tuple


class Figura:
    def __init__(self, nombre: str, color: str) -> None:
        # Atributos públicos directos (Principio de acceso uniforme)
        self.nombre = nombre
        self.color = color
        self._construida = True

    def area(self) -> float:
        return 0.0


class Lado:
    def __init__(self, longitud: float) -> None:
        self.longitud = longitud  # Dispara la validación del setter

    @property
    def longitud(self) -> float:
        return self._longitud

    @longitud.setter
    def longitud(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("La longitud debe ser positiva")
        self._longitud = valor


class Poligono(Figura):
    def __init__(
        self,
        nombre: str,
        color: str,
        lados: Optional[List[Lado]] = None,
        observaciones: Optional[List[str]] = None,
    ) -> None:
        # super().__init__ explícito para respetar MRO
        super().__init__(nombre, color)
        # Centinela None para evitar mutables por defecto y copia defensiva contra aliasing
        self._lados: List[Lado] = list(lados) if lados is not None else []
        self._observaciones: List[str] = list(observaciones) if observaciones is not None else []

    @property
    def lados(self) -> Tuple[Lado, ...]:
        # Expone tupla inmutable hacia el exterior
        return tuple(self._lados)

    def lados_esperados(self) -> int:
        return 0

    def perimetro(self) -> float:
        # Expresión generadora limpia con sum()
        return sum(l.longitud for l in self._lados)

    def area(self) -> float:
        return 0.0

    def agregar_observacion(self, texto: str) -> None:
        self._observaciones.append(texto)


class Triangulo(Poligono):
    def __init__(
        self,
        nombre: str = "triángulo",
        color: str = "negro",
        lados: Optional[List[Lado]] = None,
    ) -> None:
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 3


class Cuadrado(Poligono):
    def __init__(
        self,
        nombre: str = "cuadrado",
        color: str = "negro",
        lados: Optional[List[Lado]] = None,
    ) -> None:
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 4


class PoligonoRegular(Poligono):
    """Polígono de N lados de igual longitud.

    Objeto de análisis para la Parte 3.
    """

    def __init__(self, nombre: str, color: str, medida: float, cantidad: int) -> None:
        super().__init__(nombre, color, [Lado(medida) for _ in range(cantidad)])
        self._cantidad = cantidad

    def lados_esperados(self) -> int:
        return self._cantidad


if __name__ == "__main__":
    activo = True
    if activo:
        t = Triangulo("Triángulo", "rojo", [Lado(3), Lado(4), Lado(5)])
        c = Cuadrado("Cuadrado", "azul", [Lado(2), Lado(2), Lado(2), Lado(2)])

        print(f"Perímetro del triángulo: {t.perimetro()}")
        print(f"Perímetro del cuadrado: {c.perimetro()}")

        t.agregar_observacion("revisar el vértice A")
        print(f"Nombre: {t.nombre}")

        r = PoligonoRegular("Pentágono", "verde", 4, 5)
        print(f"Perímetro del pentágono: {r.perimetro()}")