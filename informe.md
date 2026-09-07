# Informe — TP Integrador Unidad 3 (POO)

## 1. Los 8 java-ismos de diseño (Parte 1)

| # | Ubicación | Java-ismo | Solución Python | Inversión conceptual |
|:--|:---|:---|:---|:---|
| 1 | `Figura.getNombre/getColor` | Getters vacíos sin lógica | Atributos directos / `@property` | Acceso uniforme: no se encapsula por miedo, solo con lógica real |
| 2 | `Lado.getLongitud/setLongitud` | Getter/setter estilo JavaBean | `@property` + `@longitud.setter` | Sintaxis limpia con validación oculta detrás |
| 3 | `Poligono.catalogo = []` | Atributo de clase mutable ("static") | Se elimina | Evita estado global oculto |
| 4 | `__init__(lados=[], observaciones=[])` | Default mutable compartido | `lados=None` + centinela | Defaults se evalúan una sola vez al definir la función |
| 5 | `Poligono.__init__` | `super().__init__()` omitido | Llamada explícita a `super()` | Respeta el MRO e inicialización cooperativa |
| 6 | `Poligono.perimetro` | Bucle acumulador manual | `sum(l.longitud for l in ...)` | Estilo declarativo, más idiomático |
| 7 | `Triangulo/Cuadrado.__init__` | Sobrecarga simulada con `*args`+`isinstance` | Parámetros opcionales | Python no tiene sobrecarga estática; se resuelve con defaults |
| 8 | `Poligono.getLados`/`self._lados=lados` | Aliasing: fuga de encapsulamiento | Copia defensiva (`list(...)`/`tuple(...)`) | Protege invariantes de mutación externa |

**Ruido sintáctico limpiado** (no cuenta como java-ismo): `;` al final de línea, `== True`, concatenación con `+` reemplazada por f-strings, y el type hint `-> int` que devolvía un `str`.

## 2. Agregación vs. Composición vs. Asociación (Parte 2)

La sintaxis de guardar la referencia (`self._algo = algo`) es parecida en los tres casos, pero lo que distingue la relación es **quién construye el objeto**:
- **Composición** (`Poligono`—`Lado`): `self._lados = [Lado(...) for l in lados]` — el `Poligono` **crea copias nuevas**; si muere, sus `Lado` no sobreviven.
- **Agregación** (`Taller`—`Poligono`): `self._poligonos.append(poligono)` — recibe un objeto **ya construido afuera**; si el `Taller` muere, el `Poligono` sigue vivo.
- **Asociación** (`Lado`—`Etiqueta`): `self._etiqueta = etiqueta` — también recibe un objeto externo, pero es **opcional (0..1)**, no representa "parte de".

## 3. Decisión sobre PoligonoRegular (Parte 3)

En el original, `PoligonoRegular` heredaba de `Poligono` solo para compartir tipo en una lista — necesidad de Java, no de Python (acá el duck typing lo resuelve). **Se descartó la herencia** y se reemplazó por `FactoriaPoligonoRegular.crear(...)`, una Factory Method que devuelve una instancia de la subclase concreta correcta (`Triangulo`, `Cuadrado`, etc.) según la cantidad de lados. El dominio no dice "regular ES-UN tipo aparte"; dice "regular ES uno de los polígonos ya existentes, con lados iguales". Falla temprana verificada: `Poligono("x","y",[...])` lanza `TypeError` al construir, por ser `ABC`.

## 4. ABC vs. Protocol (Parte 4)

Una ABC exige herencia explícita; `PlanoCAD` no puede heredar de nada nuestro porque no se puede modificar `libreria_externa.py`. `Protocol` resuelve esto porque el cumplimiento es **estructural**: alcanza con tener el método `exportar() -> str`, sin conocer el contrato (`isinstance(plano, Exportable)` → `True` sin herencia).

**¿Lenguaje o dominio?** Depende del contrato: en `Poligono` (Parte 3) la elección de ABC la impone el **dominio** (queremos forzar `lados_esperados()` como regla propia de ser polígono). En `Exportable`/`PlanoCAD` (Parte 4) la elección de Protocol la impone el **lenguaje/entorno** (no se puede tocar código de terceros). No hay una regla única: se usa herencia cuando el dominio la exige, y contrato estructural cuando la herencia es inviable.

## 5. Tabla de equivalencias sobre mi código (Parte 5)

| Elemento en Java | Cómo quedó en Python | ¿Directa o rediseño? | Por qué |
|:---|:---|:---|:---|
| Getters/Setters | `@property` | Rediseño | Solo se usa donde hay lógica real |
| `private` | Prefijo `_` | Rediseño | Convención, no protección del compilador |
| `List<Poligono>` con tipo común | Duck typing, sin ancestro artificial | Rediseño | No hace falta tipo declarado para mezclar objetos |
| Sobrecarga de constructores | Un solo `__init__` con `Optional` | Rediseño | Python no soporta sobrecarga por firma |
| `interface Exportable` | `Protocol` | Rediseño | Cumplimiento estructural, sin `implements` |
| Clase abstracta con método abstracto | `ABC` + `@abstractmethod` | Directa | El concepto existe igual en ambos lenguajes |
| `toString()` | `__repr__` | Directa | Mismo rol, distinto nombre |

## 6. Cierre

**Cambió** el criterio para usar herencia (se abandonó cuando era solo ceremonia de compilador, como en `PoligonoRegular`) y el mecanismo de contratos (`Protocol` en vez de interfaces obligatorias, por la restricción de no poder tocar `libreria_externa.py`). **Se mantuvo igual** el diseño conceptual del dominio: qué relación corresponde a cada par de clases (composición, agregación, asociación, herencia) es una decisión de modelado independiente del lenguaje usado para expresarla.