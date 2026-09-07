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