# Diagrama de clases final — TPI POO Unidad 3

Este diagrama refleja las decisiones tomadas en las Partes 3 y 4, no el
punto de partida. Para verlo renderizado, copiá el bloque de abajo y
pegalo en https://mermaid.live

​```mermaid
classDiagram
    class Exportable {
        <<Protocol>>
        +exportar() str
    }
    class Figura {
        <<abstract>>
        #_nombre str
        #_color str
        +area()* float
    }
    class Poligono {
        <<abstract>>
        #_lados list~Lado~
        +lados_esperados()* int
        +perimetro() float
        +lados() tuple~Lado~
        +exportar() str
    }
    class Lado {
        #_longitud float
        #_etiqueta Etiqueta
        +longitud float
        +etiqueta Etiqueta
        +escalar(factor)
    }
    class Etiqueta {
        <<frozen dataclass>>
        +texto str
    }
    class Taller {
        #_poligonos list~Poligono~
        +recibir(poligono)
        +restaurar(poligono)
        +inventario() tuple~Poligono~
    }
    class Triangulo
    class Cuadrado
    class Pentagono
    class Hexagono
    class FactoriaPoligonoRegular {
        <<factory>>
        +crear(nombre, color, medida, cantidad) Poligono
    }
    class PlanoCAD {
        <<librería externa>>
        +exportar() str
    }

    Figura <|-- Poligono : herencia
    Poligono <|-- Triangulo
    Poligono <|-- Cuadrado
    Poligono <|-- Pentagono
    Poligono <|-- Hexagono
    Poligono "1" *-- "3..*" Lado : composición
    Lado "1" --> "0..1" Etiqueta : asociación
    Taller "1" o-- "0..*" Poligono : agregación
    Poligono ..|> Exportable : cumple
    PlanoCAD ..|> Exportable : cumple sin saberlo
    FactoriaPoligonoRegular ..> Triangulo : crea
    FactoriaPoligonoRegular ..> Cuadrado : crea
    FactoriaPoligonoRegular ..> Pentagono : crea
    FactoriaPoligonoRegular ..> Hexagono : crea
​```

## Diferencias respecto al diagrama "destino" del PDF

- **`PoligonoRegular` no aparece como clase heredada.** Se decidió (Parte 3)
  que la regularidad no es un tipo nuevo del dominio, sino una restricción
  sobre los datos de construcción. Se reemplazó por
  `FactoriaPoligonoRegular`, que no hereda de `Poligono` ni de `Figura`:
  solo **crea** instancias de las subclases concretas ya existentes,
  relación que se representa con una flecha punteada de dependencia
  (`..>`), no de herencia.
- **`Exportable` se cumple de dos formas distintas**: `Poligono` lo cumple
  explícitamente (implementa `exportar()` sabiendo que existe el
  contrato), mientras que `PlanoCAD` lo cumple "sin saberlo" — nunca
  declaró ni conoce `Exportable`, pero como tiene el método con la firma
  correcta, `typing.Protocol` lo reconoce en tiempo de ejecución.