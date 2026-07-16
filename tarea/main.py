from pathlib import Path
import typer
from datetime import date
from enum import IntEnum

# Importamos los componentes necesarios de Rich para la tabla
from rich.console import Console
from rich.table import Table

home = Path.home()
tareas = home / ".tareas"
tareas.mkdir(exist_ok=True)
config = tareas / "config.txt"


# definimos el enum para los estado
class EstadoTarea(IntEnum):
    PENDIENTE = 0
    COMPLETADA = 1
    URGENTE = 2
    MEGAURGENTE = 3


# Corregimos la lógica de inicialización para asegurar que 'datos' apunte a datos.txt
if not config.exists():
    config.write_text(str(tareas))
    datos = tareas / "datos.txt"
else:
    ruta_datos = Path(config.read_text().strip())
    datos = ruta_datos / "datos.txt"

if not datos.exists():
    datos.touch()

app = typer.Typer()
console = Console()  # Instanciamos la consola de Rich para imprimir la tabla


@app.command()
def add(
    tarea: str = typer.Argument(..., help="La tarea que deseas añadir"),
    fecha: str = typer.Option(
        "2099-12-31", "--fecha", "-f", help="La fecha de finalización de la tarea"
    ),
    estado: EstadoTarea = typer.Option(
        EstadoTarea.PENDIENTE, "--estado", "-e", help="Estado para la tarea"
    ),
):
    try:
        # Validamos la fecha
        fecha_validada = date.fromisoformat(fecha)
    except ValueError:
        typer.secho(
            f"❌ Error: La fecha '{fecha}' no es válida. Debe tener el formato AAAA-MM-DD (ej. 2026-07-15).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    # Escribimos con un salto de línea (\n) al final para separar las tareas
    with datos.open("a", encoding="utf-8") as f:
        f.write(f"{tarea}|{fecha_validada}|{estado}\n")

    # Añadimos la 'f' al string para que reemplace correctamente la variable
    typer.secho(f"✅ Se creó exitosamente la tarea: '{tarea}'.", fg=typer.colors.GREEN)


@app.command()
def list():
    # 1. Leemos las tareas del archivo
    lineas = datos.read_text(encoding="utf-8").strip().split("\n")

    # Si el archivo está vacío o solo contiene una línea vacía
    if not lineas or lineas == [""]:
        typer.secho("📭 No hay tareas registradas.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    # 2. Creamos la tabla de Rich
    # 'row_styles' define los estilos alternos para las filas (ej: una oscura, una más clara)
    tabla = Table(
        title="📋 LISTADO DE TAREAS",
        box=None,  # Quita los bordes pesados para que se vea más minimalista y limpia
        row_styles=["none", "dim"],  # Alterna entre estilo normal y opaco/atenuado
    )

    # 3. Definimos las columnas y sus estilos
    tabla.add_column("Id", style="white", justify="left")
    tabla.add_column("Tarea", style="cyan", justify="left")
    tabla.add_column("Fecha Límite", style="magenta", justify="center")
    tabla.add_column("Estado", justify="center")

    # 4. Agregamos las filas parseando los datos
    i = 0
    for linea in lineas:
        if not linea.strip():
            continue
        partes = linea.split("|")
        i = i + 1
        # Aseguramos que la línea tenga el formato correcto (tarea|fecha|estado)
        if len(partes) == 3:
            nom_tarea, fecha_tarea, est = partes

            try:
                estado_enum = EstadoTarea(int(est))
            except ValueError:
                estado_enum = EstadoTarea.PENDIENTE
            # Formateamos visualmente el estado
            if estado_enum == EstadoTarea.COMPLETADA:
                status_formatted = "[green]✔ Completada[/green]"
            elif estado_enum == EstadoTarea.PENDIENTE:
                status_formatted = "[red]❌ Pendiente[/red]"
            elif estado_enum == EstadoTarea.URGENTE:
                status_formatted = "[red]❌ Urgente[/red]"
            else:
                status_formatted = "[red]❌ MegaUrgente[/red]"

            tabla.add_row(str(i), nom_tarea, fecha_tarea, status_formatted)

    # 5. Imprimimos la tabla en la consola
    console.print(tabla)


@app.command()
def update(
    id: int = typer.Argument(
        ..., help="El Id (número de línea) de la tarea a modificar."
    ),
    tarea: str = typer.Option(
        None, "--tarea", "-t", help="Nueva descripción para la tarea."
    ),
    fecha: str = typer.Option(
        None, "--fecha", "-f", help="Nueva fecha límite (AAAA-MM-DD)."
    ),
    estado: EstadoTarea = typer.Option(
        None, "--estado", "-e", help="Nuevo estado para la tarea."
    ),
):
    # 1. Leemos todas las líneas del archivo
    lineas = datos.read_text(encoding="utf-8").strip().split("\n")

    if not lineas or lineas == [""]:
        typer.secho(
            "📭 No hay tareas registradas para modificar.", fg=typer.colors.YELLOW
        )
        raise typer.Exit(code=1)

    # 2. Validamos que el ID exista dentro del rango del archivo
    # Como tu lista es base 1, el índice de la lista será id - 1
    if id < 1 or id > len(lineas):
        typer.secho(
            f"❌ Error: El Id '{id}' no existe. Ingresa un número entre 1 y {len(lineas)}.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    # 3. Extraemos los valores actuales de la tarea que queremos modificar
    indice = id - 1
    partes = lineas[indice].split("|")

    if len(partes) != 3:
        typer.secho(
            "❌ Error: Los datos de esa tarea están corruptos.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    t_actual, f_actual, e_actual = partes

    # 4. Modificamos solo los parámetros que el usuario haya enviado
    if tarea is not None:
        t_actual = tarea

    if fecha is not None:
        try:
            # Validamos que la nueva fecha sea un formato ISO real
            f_actual = str(date.fromisoformat(fecha))
        except ValueError:
            typer.secho(
                f"❌ Error: La fecha '{fecha}' no es válida. Debe ser AAAA-MM-DD.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)

    if estado is not None:
        # Guardamos el valor numérico del Enum (0, 1, 2 o 3)
        e_actual = str(estado.value)

    # 5. Reconstruimos la línea modificada en nuestro array de líneas
    lineas[indice] = f"{t_actual}|{f_actual}|{e_actual}"

    # 6. Escribimos todo de vuelta al archivo datos.txt (uniendo con saltos de línea)
    datos.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    typer.secho(f"✨ Tarea #{id} modificada con éxito.", fg=typer.colors.GREEN)


@app.command()
def delete(id: int = typer.Argument(..., help="El ID de la tarea a eliminar")):
    lineas = datos.read_text(encoding="utf-8").strip().split("\n")
    if not lineas or lineas == [""]:
        typer.secho("No hay tareas registradas para eliminar", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    if id > len(lineas):
        typer.secho(f"No existe la tarea con el id:{id}", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    print("\n¿Seguro que deseas eliminar el elemento?")
    eleccion = str.upper(str(input("Si/No(S/N):")))
    if not (eleccion == "SI" or eleccion == "S"):
        typer.secho("Se ha cancelado la eliminación", fg=typer.colors.YELLOW)
    indice = id - 1
    lineas.pop(indice)
    datos.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    typer.secho("Se ha eliminado correctamente la tarea", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()
