# Informe — Parte 1: Diagnóstico de Java-ismos

## 1. Tabla resumen de los 8 Java-ismos de diseño

| # | Ubicación | Antipatrón / Java-ismo detectado | Solución idiomática en Python | Inversión conceptual |
|:--|:---|:---|:---|:---|
| **1** | `Figura.getNombre`, `Figura.getColor` | Getters preventivos vacíos sin lógica. | Acceso directo a atributos (`self.nombre`, `self.color`). | Principio de acceso uniforme: no se encapsula preventivamente por miedo al compilador; si se requiere lógica futura se usa `@property` sin alterar la interfaz pública. |
| **2** | `Lado.getLongitud`, `Lado.setLongitud` | Getter y Setter explícitos estilo JavaBean para validar invariantes. | `@property` y `@longitud.setter`. | Se preserva la sintaxis limpia de acceso a atributos (`lado.longitud = 5`) ejecutando validaciones subyacentes mediante descriptores. |
| **3** | `Poligono.catalogo = []` | Atributo mutable de clase usado como variable `static` compartida. | Eliminar el atributo de clase; gestionar colecciones en un repositorio externo explícito. | Evitar estado global mutable oculto y efectos secundarios en la instanciación de entidades de dominio. |
| **4** | `Poligono.__init__(..., lados=[], observaciones=[])` | Argumentos por defecto mutables en funciones. | Valor centinela `None`: `lados=None, observaciones=None`. | En Python los valores por defecto se evalúan al definir la función, no al invocarla; si son mutables, todas las instancias comparten la misma lista en memoria. |
| **5** | `Poligono.__init__` | Omisión deliberada de `super().__init__()` y duplicación manual de atributos. | Llamada explícita a `super().__init__(nombre, color)`. | Respeta el MRO (Method Resolution Order) y asegura la inicialización cooperativa completa de la jerarquía (e.g. `_construida = True`). |
| **6** | `Poligono.perimetro` | Bucle acumulador procedural manual (`for` con acumulador `total`). | Expresión generadora con `sum()`: `sum(l.longitud for l in self._lados)`. | Estilo declarativo/funcional de alto nivel, más conciso, legible y optimizado en C. |
| **7** | `Triangulo.__init__` y `Cuadrado.__init__` | Simulación artesanal de sobrecarga de constructores con `*args`, `len` e `isinstance`. | Parámetros con valores por defecto o Factory Methods con `@classmethod`. | En Python no existe la sobrecarga estática en compilación; la flexibilidad se logra con argumentos opcionales claros o fábricas semánticas. |
| **8** | `Poligono.getLados` y `self._lados = lados` | Fuga de encapsulamiento por aliasing de colección interna (el octavo oculto). | Copia defensiva al recibir (`list(lados)`) y retorno inmutable (`tuple(self._lados)`). | Proteger el estado interno del objeto impidiendo que mutaciones externas rompan las invariantes de la clase. |

## 2. Limpieza de ruido sintáctico

Se eliminaron del código los siguientes vicios sintácticos que no constituyen problemas de diseño OO pero no son idiomáticos en Python:

* **Punto y coma (`;`):** Se removieron los puntos y coma al final de las sentencias.
* **Comparación explícita con booleanos:** Se reemplazó `if activo == True:` por la evaluación veritativa directa `if activo:`.
* **Concatenación con `+`:** Se cambiaron las concatenaciones manuales de strings y `str(...)` por f-strings (`f"Perímetro: {t.perimetro()}"`).
* **Type hint inconsistente:** Se corrigió la firma `def area(self) -> int` que retornaba un string `"area sin calcular"`.


## 3. Parte 2 — Pregunta obligatoria (Agregación vs. Composición vs. Asociación)

En rigor, en este código la sintaxis **no es idéntica** en los tres casos: la
composición y la asociación se ven como una asignación directa
(`self._algo = algo`), mientras que la agregación se ve como una operación
sobre una colección (`self._algo.append(algo)`), porque `Taller` administra
varios `Poligono`, no uno solo. Aun así, la diferencia de fondo que importa
—y que se sostiene en los tres casos— no está en la sintaxis de guardar la
referencia, sino en **quién construye el objeto y quién controla su ciclo de
vida**:

- **Poligono — Lado (composición):** en `Poligono.__init__`, la línea
  `self._lados: List[Lado] = [Lado(l.longitud, l.etiqueta) for l in lados]`
  no guarda los objetos recibidos por parámetro: **crea copias nuevas**,
  invocando el constructor `Lado(...)` adentro del propio `__init__` de
  `Poligono`. El `Poligono` es dueño exclusivo de sus `Lado`; si el polígono
  se destruye, esos lados no sobreviven en ningún otro lado del programa.

- **Taller — Poligono (agregación):** en `Taller.recibir`, la línea
  `self._poligonos.append(poligono)` guarda una **referencia a un objeto que
  ya existía antes**, construido afuera del `Taller` (llega como parámetro
  `poligono`; el `Taller` nunca escribe `Poligono(...)`). Si el `Taller` se
  destruye, los polígonos siguen vivos donde fueron creados.

- **Lado — Etiqueta (asociación):** en `Lado.__init__`, la línea
  `self._etiqueta: Optional[Etiqueta] = etiqueta` también recibe un objeto ya
  construido afuera, igual que en la agregación. Lo que la diferencia de la
  agregación es la **multiplicidad opcional (0..1)**: puede valer `None`
  (el valor por defecto del parámetro), no representa "parte de" ni
  "conjunto de", solo una referencia cruzada entre dos objetos independientes.

**Conclusión:** lo que delata la relación no es la forma de la sintaxis, sino
si el código, en ese mismo método, **instancia el objeto con `NombreClase(...)`**
(composición) o **lo recibe ya armado desde afuera** (agregación/asociación);
y dentro de este segundo grupo, si la relación es obligatoria y plural
(agregación) u opcional y singular (asociación).


## 4. Parte 3 — Decisión sobre PoligonoRegular

**Problema en el código de partida:** `PoligonoRegular` heredaba de `Poligono`
únicamente para poder guardarse en la misma lista/colección que `Triangulo` y
`Cuadrado`, y ser recorrida con un tipo común. Esa es una necesidad propia de
un compilador con tipado estático como Java (`List<Poligono>` exige que todo
lo que entre ahí sea, formalmente, un `Poligono`). En Python las listas son
dinámicas y el duck typing permite mezclar cualquier objeto que cumpla el
comportamiento esperado (`perimetro()`, `lados_esperados()`, `area()`), sin
que exista un tipo declarado en la colección que lo exija.

**Decisión tomada:** se descartó la herencia y se reemplazó por una
**Factory Method** (`FactoriaPoligonoRegular.crear(nombre, color, medida,
cantidad)`), que no crea un tipo nuevo: internamente decide, según la
`cantidad` de lados, cuál subclase concreta corresponde (`Triangulo`,
`Cuadrado`, `Pentagono` o `Hexagono`) y devuelve una instancia de esa clase
ya existente.

**Justificación con el criterio de la unidad:** el dominio no afirma que "un
polígono regular ES-UN tipo aparte de figura" — afirma que "un polígono
regular ES uno de estos polígonos concretos, con todos sus lados iguales".
La jerarquía que ya existía (`Triangulo`, `Cuadrado`, `Pentagono`,
`Hexagono`), cada una con su propio `area()`, ya expresa ese "ES-UN" de forma
correcta. Agregar una clase más solo para representar "regularidad" hubiera
sido ceremonia sin necesidad real de dominio: la regularidad no es un tipo,
es una restricción sobre los datos de construcción (todos los lados con la
misma medida), y por eso se resuelve mejor en una función que arma el objeto
correcto, no en una clase que hereda para "encajar" en una lista.


**Falla temprana verificada:** como `Poligono` es una `ABC` con `area()` y
`lados_esperados()` como `@abstractmethod`, intentar instanciarla
directamente (`Poligono("x", "y", [...])`) lanza, en el momento de
construir el objeto, el siguiente error:

> `TypeError: Can't instantiate abstract class Poligono without an implementation for abstract methods 'area', 'lados_esperados'`

No se rompe al usar el objeto, sino al intentar crearlo. Esto se demuestra
en `main.py`.

**Alcance de la fábrica:** `FactoriaPoligonoRegular` solo mapea 3, 4, 5 y 6
lados (las subclases concretas que existen en el dominio). Pedir un polígono
regular con otra cantidad de lados lanza un `ValueError` explícito — no es
una falla, sino el límite consciente del catálogo de figuras implementado.

## 5. Parte 4 — ABC vs. Protocol

**Por qué una ABC no hubiera servido para PlanoCAD:** una ABC (`abc.ABC`)
exige **herencia explícita**: para que `PlanoCAD` cumpliera el contrato
`Exportable` como ABC, tendría que declarar `class PlanoCAD(Exportable)`
en su propia definición. Pero `PlanoCAD` está en `libreria_externa.py`,
un archivo de un tercero que **no se puede modificar**. Como no se puede
editar esa clase, jamás podría heredar de una ABC nuestra, aunque ya tenga
el método `exportar() -> str` implementado. Con `typing.Protocol` el
cumplimiento es **estructural**: no importa de dónde venga la clase ni si
conoce el contrato — alcanza con que tenga el método con esa firma. Por eso
`isinstance(plano, Exportable)` da `True` sin que `PlanoCAD` sepa que
`Exportable` existe, algo imposible de lograr con una ABC pura sin tocar
el archivo externo.

**Pregunta que cierra la unidad — ¿lo decide el lenguaje o el dominio?**
Depende del contrato en cuestión, y por eso conviene compararlo con la
decisión de la Parte 3:

- Para **`Poligono`** (Parte 3), la elección de `ABC` la impone el
  **dominio**: queremos forzar que toda figura poligonal declare cuántos
  lados espera (`lados_esperados()`), porque esa regla es parte de lo que
  significa "ser un polígono" en este sistema. Acá sí tiene sentido que
  el compilador (Python, en este caso, en tiempo de instanciación) impida
  crear un objeto que viole esa regla del dominio.

- Para **`Exportable`/`PlanoCAD`** (Parte 4), la elección de `Protocol` la
  impone una **restricción del lenguaje/entorno**: no se puede modificar
  una clase de terceros para que herede de algo. No es que el dominio
  prefiera duck typing por sobre herencia — es que la herencia explícita
  es, directamente, inviable en ese caso.

**Conclusión:** no existe una regla única ("ABC siempre" o "Protocol
siempre"). La unidad se cierra entendiendo que **el dominio decide cuándo
una regla debe forzarse con herencia** (como en `Poligono`), y **el
lenguaje/la situación técnica decide cuándo la herencia no es una opción**
y hay que recurrir a un contrato estructural (como con `PlanoCAD`). Ambas
decisiones — la de la Parte 3 y la de la Parte 4 — se justifican con el
mismo criterio: usar herencia solo cuando el dominio la necesita, y
duck typing/contratos estructurales cuando alcanza con el comportamiento.


## 6. Tabla de equivalencias Java ↔ Python (sobre mi propio código)

| Elemento en Java | Cómo quedó en mi código Python | ¿Traducción directa o rediseño? | Por qué |
|:---|:---|:---|:---|
| Getters/Setters (`getNombre()`, `getColor()`) | Atributos expuestos como `@property` en `Figura` y `Poligono` | Rediseño | Python no necesita un método para leer un atributo; `@property` solo se usa donde hay lógica real (validación en `Lado.longitud`), no como ceremonia preventiva. |
| Modificador `private` | Prefijo `_` (`_nombre`, `_lados`, `_etiqueta`) | Rediseño | Python no tiene protección real de acceso; el guion bajo es un acuerdo entre programadores ("no lo toques desde afuera"), no una barrera del compilador. |
| `List<Poligono>` como tipo común para guardar subtipos | Listas dinámicas (`List[Poligono]`, `self._poligonos`) sin necesidad de un ancestro artificial | Rediseño | El tipado estático de Java exige un tipo declarado para la colección; en Python el duck typing permite mezclar objetos por comportamiento, sin forzar una jerarquía (por eso se eliminó la herencia de `PoligonoRegular`). |
| Sobrecarga de constructores (`Triangulo(String, String)`, `Triangulo(List<Lado>)`, etc.) | Un único `__init__` con parámetros opcionales (`lados: Optional[List[Lado]] = None`) | Rediseño | Python no soporta sobrecarga de métodos por firma; se resuelve con valores por defecto o `Optional`, evitando las ramas `isinstance` artesanales del código original. |
| Interfaz (`interface Exportable { String exportar(); }`) | `class Exportable(Protocol)` con `exportar() -> str` | Rediseño | Una interfaz Java exige `implements` explícito. `Protocol` logra el mismo contrato sin que la clase lo declare, indispensable para que `PlanoCAD` (código de terceros) lo cumpla. |
| Clase abstracta con método abstracto (`abstract class Poligono { abstract int ladosEsperados(); }`) | `class Poligono(ABC)` con `@abstractmethod` en `lados_esperados()` | Traducción directa | El concepto de clase abstracta con métodos obligatorios existe igual en Python vía `abc.ABC`; acá sí el dominio exige forzar la regla en tiempo de construcción. |
| Atributo `static` compartido (`static List<Poligono> catalogo`) | Eliminado por completo | Rediseño | Un atributo de clase mutable en Python se comparte igual que un `static` de Java, pero acá generaba estado global oculto; se descartó en vez de traducirse. |
| `toString()` | `__repr__` en `Poligono` | Traducción directa | Ambos cumplen el mismo rol (representación legible del objeto), Python solo cambia el nombre del método especial. |


## 7. Cierre: qué cambió y qué se mantuvo igual

**Lo que cambió al pasar de Java a Python** fue, sobre todo, **el criterio para
usar herencia**. En el código de partida, `PoligonoRegular` heredaba de
`Poligono` solo para resolver un problema que en Python no existe (tener un
tipo común para una colección). También cambió la forma de proteger el
estado interno: en vez de getters/setters ceremoniales, se usó `@property`
únicamente donde había lógica real, y copia defensiva explícita para evitar
aliasing entre objetos. Y cambió el mecanismo de contrato: donde Java
hubiera usado una interfaz con `implements` obligatorio, acá se usó
`typing.Protocol`, porque había una restricción real (no poder modificar
`libreria_externa.py`) que una interfaz clásica no podría resolver.

**Lo que se mantuvo idéntico** fue el **diseño conceptual del dominio**: la
relación "un polígono tiene lados", "un taller agrupa polígonos sin ser
dueño de ellos", "un lado puede tener una etiqueta opcional" no cambiaron en
absoluto — son decisiones de modelado que no dependen del lenguaje. Lo que
se demostró en este TP es que la **sintaxis y las herramientas para expresar
esas relaciones sí cambian con el lenguaje**, pero el diseño de qué relación
corresponde a cada par de clases (composición, agregación, asociación,
herencia) es un problema de dominio, independiente de si el lenguaje es
Java o Python.