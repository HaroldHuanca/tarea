from pathlib import Path
import typer
from datetime import date

home = Path.home()
tareas = home / ".tareas"
tareas.mkdir(exist_ok=True)
config = tareas / "config.txt"
ruta_datos = tareas
if not config.exists():
    config.write_text(str(tareas))
    datos = tareas
else:
    ruta_datos = Path(config.read_text().strip())
    datos = ruta_datos / "datos.txt"

if not datos.exists():
    datos.touch()

# Segundo necesitamos crear la lógica de adición de tareas
app = typer.Typer()


@app.command()
def add(tarea: str, fecha: str, estado: int):
    try:
        date.fromisoformat(fecha)
    except ValueError:
        typer.secho(
            f"❌ Error: La fecha '{fecha}' no es válida. Debe tener el formato AAAA-MM-DD (ej. 2026-07-15).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    with datos.open("a", encoding="utf-8") as f:
        f.write(f"{tarea}|{fecha}|{estado}")

    typer.secho("Se creo exitosamente la tarea:{tarea}.", fg=typer.colors.GREEN)


@app.command()
def list():
    print("Listando...")
