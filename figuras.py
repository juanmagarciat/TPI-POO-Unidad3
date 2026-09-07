"""figuras.py — Dominio completo de Figuras, Polígonos, Taller y Contratos Estructurales.

Resuelve:
- Parte 2: Relaciones estructurales (Composición, Agregación, Asociación 0..1, Copia defensiva).
- Parte 3: Clases abstractas (ABC), subclases por dominio y rediseño de PoligonoRegular.
- Parte 4: Contrato estructural typing.Protocol (Exportable) y función polimórfica.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple, Protocol, runtime_checkable
import math
from libreria_externa import PlanoCAD


# ==============================================================================
# PARTE 4: Contrato estructural (Protocol)
# ==============================================================================
@runtime_checkable
class Exportable(Protocol):
    """Contrato estructural. Cualquier clase con exportar() -> str lo cumple."""
    def exportar(self) -> str:
        ...


# ==============================================================================
# PARTE 2: Value Object Etiqueta (frozen dataclass)
# ==============================================================================
@dataclass(frozen=True)
class Etiqueta:
    """Identifica un Lado con un texto inmutable."""
    texto: str


# ==============================================================================
# Elemento Lado (Asociación 0..1 con Etiqueta)
# ==============================================================================
class Lado:
    def __init__(self, longitud: float, etiqueta: Optional[Etiqueta] = None) -> None:
        self.longitud = longitud
        self._etiqueta: Optional[Etiqueta] = etiqueta

    @property
    def longitud(self) -> float:
        return self._longitud

    @longitud.setter
    def longitud(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("La longitud debe ser un número positivo.")
        self._longitud = float(valor)

    @property
    def etiqueta(self) -> Optional[Etiqueta]:
        return self._etiqueta

    @etiqueta.setter
    def etiqueta(self, nueva_etiqueta: Optional[Etiqueta]) -> None:
        self._etiqueta = nueva_etiqueta

    def escalar(self, factor: float) -> None:
        if factor <= 0:
            raise ValueError("El factor de escala debe ser positivo.")
        self._longitud *= factor

    def __repr__(self) -> str:
        tag = f" [{self._etiqueta.texto}]" if self._etiqueta else ""
        return f"Lado({self._longitud}{tag})"


# ==============================================================================
# Jerarquía Figura / Polígono (ABC y validación de invariantes)
# ==============================================================================
class Figura(ABC):
    def __init__(self, nombre: str, color: str) -> None:
        self._nombre = nombre
        self._color = color

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def color(self) -> str:
        return self._color

    @abstractmethod
    def area(self) -> float:
        """Cálculo polimórfico del área."""
        pass


class Poligono(Figura):
    def __init__(self, nombre: str, color: str, lados: List[Lado]) -> None:
        super().__init__(nombre, color)
        # Composición: copia defensiva interna al construir
        self._lados: List[Lado] = [Lado(l.longitud, l.etiqueta) for l in lados]

        if len(self._lados) < 3:
            raise ValueError(f"Un polígono debe tener al menos 3 lados (recibidos: {len(self._lados)}).")

        # Falla temprana: valida contra lados_esperados()
        esperados = self.lados_esperados()
        if esperados != 0 and len(self._lados) != esperados:
            raise ValueError(
                f"Inconsistencia en {self.__class__.__name__}: "
                f"esperaba {esperados} lados y recibió {len(self._lados)}."
            )

    @abstractmethod
    def lados_esperados(self) -> int:
        pass

    def perimetro(self) -> float:
        return sum(l.longitud for l in self._lados)

    def lados(self) -> Tuple[Lado, ...]:
        """Copia defensiva: tupla inmutable hacia el exterior."""
        return tuple(self._lados)

    def exportar(self) -> str:
        """Implementa el método requerido por el Protocol Exportable."""
        return f"Poligono[{self.nombre}, color={self.color}, lados={len(self._lados)}, perimetro={self.perimetro():.2f}]"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nombre='{self.nombre}', color='{self.color}', lados={len(self._lados)})"


class Triangulo(Poligono):
    def __init__(self, nombre: str = "Triángulo", color: str = "Negro", lados: Optional[List[Lado]] = None) -> None:
        if lados is None:
            lados = [Lado(1.0), Lado(1.0), Lado(1.0)]
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 3

    def area(self) -> float:
        a, b, c = (l.longitud for l in self._lados)
        s = (a + b + c) / 2.0
        radicando = s * (s - a) * (s - b) * (s - c)
        return math.sqrt(max(0.0, radicando))


class Cuadrado(Poligono):
    def __init__(self, nombre: str = "Cuadrado", color: str = "Negro", lados: Optional[List[Lado]] = None) -> None:
        if lados is None:
            lados = [Lado(1.0) for _ in range(4)]
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 4

    def area(self) -> float:
        return self._lados[0].longitud ** 2


class Pentagono(Poligono):
    def __init__(self, nombre: str = "Pentágono", color: str = "Negro", lados: Optional[List[Lado]] = None) -> None:
        if lados is None:
            lados = [Lado(1.0) for _ in range(5)]
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 5

    def area(self) -> float:
        lado = self._lados[0].longitud
        return (5 * lado ** 2) / (4 * math.tan(math.pi / 5))


class Hexagono(Poligono):
    def __init__(self, nombre: str = "Hexágono", color: str = "Negro", lados: Optional[List[Lado]] = None) -> None:
        if lados is None:
            lados = [Lado(1.0) for _ in range(6)]
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 6

    def area(self) -> float:
        lado = self._lados[0].longitud
        return (3 * math.sqrt(3) * (lado ** 2)) / 2.0


# ==============================================================================
# PARTE 3: Decisión de diseño sobre PoligonoRegular
# Se reemplaza la herencia artificial por una Factory Method
# ==============================================================================
class FactoriaPoligonoRegular:
    """Fábrica para instanciar polígonos regulares del tipo concreto correspondiente."""
    @staticmethod
    def crear(nombre: str, color: str, medida_lado: float, cantidad_lados: int) -> Poligono:
        lados = [Lado(medida_lado) for _ in range(cantidad_lados)]
        mapa = {
            3: Triangulo,
            4: Cuadrado,
            5: Pentagono,
            6: Hexagono,
        }
        clase_destino = mapa.get(cantidad_lados)
        if clase_destino is None:
            raise ValueError(f"No hay polígono concreto registrado para {cantidad_lados} lados.")
        return clase_destino(nombre, color, lados)


# ==============================================================================
# PARTE 2: Taller (Agregación)
# ==============================================================================
class Taller:
    """Mantiene relación de AGREGACIÓN con Poligono:
    los recibe ya construidos; si el taller se destruye, los polígonos sobreviven.
    """
    def __init__(self) -> None:
        self._poligonos: List[Poligono] = []

    def recibir(self, poligono: Poligono) -> None:
        if not isinstance(poligono, Poligono):
            raise TypeError("El taller solo admite instancias de Poligono.")
        self._poligonos.append(poligono)

    def restaurar(self, poligono: Poligono, factor_escala: float = 1.1) -> None:
        if poligono not in self._poligonos:
            raise ValueError("El polígono no pertenece a este taller.")
        for lado in poligono._lados:
            lado.escalar(factor_escala)

    def inventario(self) -> Tuple[Poligono, ...]:
        """Copia defensiva: tupla de polígonos agregados."""
        return tuple(self._poligonos)


# ==============================================================================
# PARTE 4: Función polimórfica estructural
# ==============================================================================
def exportar_todo(items: List[Exportable]) -> List[str]:
    """Exporta cualquier objeto que cumpla estructuralmente con el Protocol Exportable."""
    return [item.exportar() for item in items]

# ==============================================================================
# Verificación: PlanoCAD (librería externa) cumple Exportable SIN heredar
# ==============================================================================
if __name__ == "__main__":
    plano = PlanoCAD("PLANO-01", "1:50")
    triangulo = Triangulo(lados=[Lado(3), Lado(4), Lado(5)])

    # isinstance funciona por duck typing estructural (gracias a @runtime_checkable),
    # aunque PlanoCAD no conoce ni hereda de Exportable.
    print(f"¿PlanoCAD cumple Exportable? -> {isinstance(plano, Exportable)}")
    print(f"¿Triangulo cumple Exportable? -> {isinstance(triangulo, Exportable)}")

    resultados = exportar_todo([triangulo, plano])
    for linea in resultados:
        print(linea)