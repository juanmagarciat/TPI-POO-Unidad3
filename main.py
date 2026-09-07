"""main.py — Demo integrador: Partes 1 a 4 funcionando en conjunto."""

from figuras import (
    Triangulo, Cuadrado, Pentagono, Hexagono,
    Lado, Etiqueta, Taller, Poligono, Exportable, exportar_todo,
)
from libreria_externa import PlanoCAD


def main() -> None:
    print("=" * 70)
    print("1. Construcción de polígonos (uno de cada subclase concreta)")
    print("=" * 70)
    t = Triangulo("Triángulo A", "rojo", [Lado(3), Lado(4), Lado(5)])
    c = Cuadrado("Cuadrado B", "azul", [Lado(2), Lado(2), Lado(2), Lado(2)])
    p = Pentagono("Pentágono C", "verde", [Lado(4)] * 5)
    h = Hexagono("Hexágono D", "amarillo", [Lado(3)] * 6)

    for poligono in (t, c, p, h):
        print(f"  {poligono!r}  ->  perímetro={poligono.perimetro():.2f}  área={poligono.area():.2f}")

    print("\n" + "=" * 70)
    print("2. Etiquetar al menos 2 lados (asociación Lado—Etiqueta)")
    print("=" * 70)
    t.lados()[0].etiqueta = Etiqueta("lado más largo del triángulo")
    c.lados()[0].etiqueta = Etiqueta("lado de referencia del cuadrado")
    for lado in (t.lados()[0], c.lados()[0]):
        print(f"  {lado!r}")

    print("\n" + "=" * 70)
    print("3. Taller: agregación — recibe polígonos ya construidos")
    print("=" * 70)
    taller = Taller()
    for poligono in (t, c, p, h):
        taller.recibir(poligono)
    print(f"  Inventario del taller: {len(taller.inventario())} polígonos")
    for poligono in taller.inventario():
        print(f"    - {poligono!r}")

    print("\n" + "=" * 70)
    print("4. Evidencia: Polígono SOBREVIVE al Taller (agregación)")
    print("=" * 70)
    # El taller solo referencia polígonos que existen afuera; si el taller
    # desaparece, los polígonos siguen vivos porque otra variable los sostiene.
    referencia_externa = t
    del taller
    print(f"  Taller eliminado. ¿Sigue existiendo el Triángulo afuera? -> {referencia_externa!r}")

    print("\n" + "=" * 70)
    print("5. Evidencia: Lado NO sobrevive independiente de su Polígono (composición)")
    print("=" * 70)
    # Poligono.__init__ hace copia defensiva: crea SUS PROPIOS Lado internos.
    # El objeto Lado que el usuario pasó por fuera NO es el mismo que quedó
    # adentro del polígono: son copias distintas en memoria.
    lado_externo = Lado(3)
    triangulo_2 = Triangulo("Triángulo E", "negro", [lado_externo, Lado(4), Lado(5)])
    mismo_objeto = lado_externo is triangulo_2.lados()[0]
    print(f"  ¿El Lado externo es el mismo objeto que el interno del polígono? -> {mismo_objeto}")
    print("  (False confirma la composición: el polígono es dueño de copias propias,")
    print("   no de referencias a lados que puedan seguir existiendo por su cuenta)")

    print("\n" + "=" * 70)
    print("6. Falla temprana: instanciar Poligono abstracto sin lados_esperados()")
    print("=" * 70)
    try:
        Poligono("figura inválida", "gris", [Lado(1), Lado(1), Lado(1)])
        print("  ERROR: no debería poder instanciarse")
    except TypeError as e:
        print(f"  Falló al CONSTRUIR (no al usar), como se esperaba:\n  {e}")

    print("\n" + "=" * 70)
    print("7. Exportable (Protocol): Polígonos + PlanoCAD en la misma lista")
    print("=" * 70)
    plano = PlanoCAD("PLANO-FINAL", "1:100")
    items: list[Exportable] = [t, c, p, h, plano]
    for linea in exportar_todo(items):
        print(f"  {linea}")


if __name__ == "__main__":
    main()