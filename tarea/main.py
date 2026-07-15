from pathlib import Path
import typer
from datetime import date

# Importamos los componentes necesarios de Rich para la tabla
from rich.console import Console
from rich.table import Table

home = Path.home()
tareas = home / ".tareas"
tareas.mkdir(exist_ok=True)
config = tareas / "config.txt"

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
    tarea: str,
    fecha: str = typer.Argument("2099-12-31"),
    estado: int = typer.Argument(0),
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
    tabla.add_column("Tarea", style="cyan", justify="left")
    tabla.add_column("Fecha Límite", style="magenta", justify="center")
    tabla.add_column("Estado", justify="center")

    # 4. Agregamos las filas parseando los datos
    for linea in lineas:
        if not linea.strip():
            continue
        partes = linea.split("|")
        # Aseguramos que la línea tenga el formato correcto (tarea|fecha|estado)
        if len(partes) == 3:
            nom_tarea, fecha_tarea, est = partes

            # Formateamos visualmente el estado
            if est == "1":
                status_formatted = "[green]✔ Completada[/green]"
            else:
                status_formatted = "[red]❌ Pendiente[/red]"

            tabla.add_row(nom_tarea, fecha_tarea, status_formatted)

    # 5. Imprimimos la tabla en la consola
    console.print(tabla)


if __name__ == "__main__":
    app()
