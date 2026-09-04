"""demo_sintomas.py — Evidencia empírica de los síntomas de Java-ismos antes de corregir.

Se demuestran:
1. El argumento por defecto mutable compartido entre instancias (ANTES del arreglo).
2. La fuga de encapsulamiento por aliasing de listas internas (ANTES del arreglo).
3. El uso transparente de @property sin alterar el código cliente (DESPUÉS del arreglo).
"""

# Importamos las clases defectuosas originales para reproducir el síntoma real
import parte1_diagnostico_Original as original
# Importamos la versión limpia corregida
import parte1_diagnostico as limpio


def demo_sintoma_default_mutable():
    print("=== SÍNTOMA 1: Argumento mutable por defecto compartido ===")
    # Instanciamos dos triángulos usando la clase ORIGINAL con def __init__(..., observaciones=[])
    t1_orig = original.Triangulo("T1", "rojo", [original.Lado(3), original.Lado(4), original.Lado(5)])
    t2_orig = original.Triangulo("T2", "azul", [original.Lado(3), original.Lado(4), original.Lado(5)])

    comparten_memoria = t1_orig._observaciones is t2_orig._observaciones
    print(f"ANTES: ¿t1 y t2 comparten la misma lista de observaciones en memoria? -> {comparten_memoria}")

    t1_orig.agregar_observacion("Observación confidencial de T1")
    print(f"ANTES: Observaciones de t1: {t1_orig._observaciones}")
    print(f"ANTES: Observaciones de t2 (contaminada por efecto secundario): {t2_orig._observaciones}")

    # Demostración en la versión limpia
    t1_limp = limpio.Triangulo("T1", "rojo", [limpio.Lado(3), limpio.Lado(4), limpio.Lado(5)])
    t2_limp = limpio.Triangulo("T2", "azul", [limpio.Lado(3), limpio.Lado(4), limpio.Lado(5)])
    print(f"DESPUÉS: ¿Comparten memoria en la versión corregida? -> {t1_limp._observaciones is t2_limp._observaciones}\n")


def demo_sintoma_aliasing():
    print("=== SÍNTOMA 2: Fuga de encapsulamiento por aliasing ===")
    lados_externos = [original.Lado(2), original.Lado(2), original.Lado(2)]
    p_orig = original.Poligono("Triángulo", "verde", lados_externos)

    print(f"ANTES: Perímetro inicial del polígono: {p_orig.perimetro()}")
    # Un cliente externo muta la lista original que le pasó al constructor
    lados_externos.clear()
    print(f"ANTES: Se ejecutó 'lados_externos.clear()' por fuera.")
    print(f"ANTES: Perímetro tras mutar la lista externa: {p_orig.perimetro()} (¡se rompieron sus invariantes!)")

    # Demostración en la versión limpia
    lados_limpios = [limpio.Lado(2), limpio.Lado(2), limpio.Lado(2)]
    p_limp = limpio.Poligono("Triángulo", "verde", lados_limpios)
    lados_limpios.clear()
    print(f"DESPUÉS: Se limpia la lista externa en la versión corregida.")
    print(f"DESPUÉS: Perímetro del polígono limpio: {p_limp.perimetro()} (estado interno protegido mediante copia defensiva)\n")


def demo_property_transparente():
    print("=== SÍNTOMA 3: @property transparente para el cliente ===")
    lado = limpio.Lado(10.0)
    print(f"Lectura directa de propiedad: lado.longitud = {lado.longitud}")
    lado.longitud = 15.0
    print(f"Asignación directa: lado.longitud = {lado.longitud}")
    try:
        lado.longitud = -5.0
    except ValueError as e:
        print(f"Validación interceptada correctamente con @property.setter: {e}\n")


if __name__ == "__main__":
    demo_sintoma_default_mutable()
    demo_sintoma_aliasing()
    demo_property_transparente()