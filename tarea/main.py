from pathlib import Path
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
import typer
from datetime import date
app = typer.Typer()
@app.command()
def add(tarea: str, fecha: str, estado: int ):
    fecha = date.fromisoformat(fecha)
    with datos.open("a", encoding="utf-8") as f:
        f.write(f"{tarea}|{fecha}|{estado}")

@app.command()
def list():
    print("Listando...")

