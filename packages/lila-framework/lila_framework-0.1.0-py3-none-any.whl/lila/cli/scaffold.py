# lila/cli/scaffold.py
import shutil
import os
from importlib import resources
from pathlib import Path

SCAFFOLD_ITEMS = {
    "app.py": "app.py",
    "admin": "admin",
    "database": "database",
    "locales": "locales",
    "logs": "logs",
    "middlewares": "middlewares",
    "models": "models",
    "routes": "routes",
    "security": "security",
    "static": "static",
    "templates": "templates",
    "uploads": "uploads",
    "env_example": "env_example",
}


def copy_item(
    source_package_name, item_name_in_package, destination_base_path, item_name_in_dest
):
    try:
        with resources.path(source_package_name, item_name_in_package) as source_path:
            destination_path = Path(destination_base_path) / item_name_in_dest

            if not source_path.exists():
                print(
                    f"  ⚠️ Advertencia: El origen '{source_path}' no existe. Omitiendo. / "
                    f"Warning: Source '{source_path}' does not exist. Skipping."
                )
                return

            if source_path.is_dir():
                shutil.copytree(source_path, destination_path)
                print(
                    f"  📂 Directorio '{item_name_in_package}' copiado a '{destination_path}'. / "
                    f"Directory '{item_name_in_package}' copied to '{destination_path}'."
                )
            else:
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, destination_path)
                print(
                    f"  📄 Archivo '{item_name_in_package}' copiado a '{destination_path}'. / "
                    f"File '{item_name_in_package}' copied to '{destination_path}'."
                )

    except FileNotFoundError:
        print(
            f"  ⚠️ Advertencia: Recurso '{source_package_name}/{item_name_in_package}' no encontrado. Omitiendo. / "
            f"Warning: Resource '{source_package_name}/{item_name_in_package}' not found. Skipping."
        )
    except Exception as e:
        print(
            f"  ❌ Error al copiar '{item_name_in_package}': {e}. / "
            f"Error copying '{item_name_in_package}': {e}."
        )


def main():
    project_dir_name_input = input(
        "🚀 Ingresa el nombre del directorio para tu nuevo proyecto (ej: mi_app_lila): / "
        "Enter the directory name for your new project (e.g., my_lila_app): "
    )
    if not project_dir_name_input:
        print(
            "❌ El nombre del directorio no puede estar vacío. Abortando. / "
            "Directory name cannot be empty. Aborting."
        )
        return

    project_dir_name = "".join(
        c if c.isalnum() or c in ("_", "-") else "_" for c in project_dir_name_input
    )
    if project_dir_name != project_dir_name_input:
        print(
            f"ℹ️ Nombre del directorio sanitizado a: '{project_dir_name}'. / "
            f"Directory name sanitized to: '{project_dir_name}'."
        )

    destination_base_path = Path(os.getcwd()) / project_dir_name

    if destination_base_path.exists():
        print(
            f"❌ Error: El directorio '{destination_base_path}' ya existe. Abortando. / "
            f"Error: Directory '{destination_base_path}' already exists. Aborting."
        )
        return

    try:
        destination_base_path.mkdir(parents=True, exist_ok=False)
        print(
            f"✅ Directorio del proyecto creado: {destination_base_path}. / "
            f"Project directory created: {destination_base_path}."
        )

        print(
            f"\n🛠️  Construyendo el esqueleto del proyecto '{project_dir_name}' usando Lila Framework... / "
            f"Scaffolding project '{project_dir_name}' using Lila Framework..."
        )

        for item_pkg_name, item_dest_name in SCAFFOLD_ITEMS.items():
            copy_item("lila", item_pkg_name, destination_base_path, item_dest_name)

        scaffolded_env_example_name = SCAFFOLD_ITEMS.get("env_example", "env_example")
        env_example_in_project_path = (
            destination_base_path / scaffolded_env_example_name
        )
        env_path = destination_base_path / ".env"

        if env_example_in_project_path.exists() and not env_path.exists():
            shutil.copy2(env_example_in_project_path, env_path)
            print(
                f"\n✨ '{scaffolded_env_example_name}' copiado a '.env'. ¡No olvides configurarlo! / "
                f"'{scaffolded_env_example_name}' copied to '.env'. Don't forget to configure it!"
            )
        elif env_example_in_project_path.exists() and env_path.exists():
            print(
                f"\nℹ️ Ya existe un archivo '.env'. Se copió igualmente '{scaffolded_env_example_name}'. / "
                f"An '.env' file already exists. '{scaffolded_env_example_name}' was also copied."
            )
        elif not env_example_in_project_path.exists():
            print(
                f"\n⚠️ Advertencia: '{scaffolded_env_example_name}' no se encontró en el proyecto scaffolded, no se pudo crear '.env' automáticamente. / "
                f"Warning: '{scaffolded_env_example_name}' not found in the scaffolded project, '.env' could not be created automatically."
            )

        readme_content = f"""
# {project_dir_name.replace('_', ' ').title()}

Este proyecto fue generado con Lila Framework.

## Primeros Pasos

1.  **Navega al directorio de tu proyecto:**
    ```bash
    cd {project_dir_name}
    ```

2.  **(Recomendado) Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    # Linux/macOS:
    source venv/bin/activate
    # Windows:
    # .\\venv\\Scripts\\activate
    ```

3.  **Instala las dependencias (incluyendo `lila-framework` si no está global):**
    ```bash
    pip install lila-framework
    # Si tienes un requirements.txt específico del proyecto:
    # pip install -r requirements.txt
    ```

4.  **Configura tu entorno:**
    Edita el archivo `.env` con tu configuración (base de datos, claves secretas, etc.).

5.  **Ejecuta las migraciones de base de datos (si aplica):**
    ```bash
    lila-migrate # (o el comando específico que tu framework use)
    ```

6.  **Inicia el servidor de desarrollo:**
    Generalmente, si `app.py` define una instancia de Starlette llamada `app`:
    ```bash
    uvicorn app:app --reload
    ```

¡Feliz desarrollo! 🚀
"""
        with open(destination_base_path / "README.md", "w",encoding="utf-8") as f:
            f.write(readme_content)
        print(
            f"📄 README.md básico creado en tu nuevo proyecto. / "
            f"Basic README.md created in your new project."
        )

        print(
            "\n🎉 ¡Proyecto Lila inicializado exitosamente! / "
            "Lila project initialized successfully!"
        )
        print(
            f"\n➡️  Ahora, ve a tu proyecto: cd {project_dir_name}. / "
            f"Now, navigate to your project: cd {project_dir_name}."
        )
        print(
            "   Sigue las instrucciones en el README.md generado. / "
            "Follow the instructions in the generated README.md."
        )

    except Exception as e:
        print(
            f"\n❌ Ocurrió un error durante la creación del proyecto: {e}. / "
            f"An error occurred during project creation: {e}."
        )
        if destination_base_path.exists():
            try:
                shutil.rmtree(destination_base_path)
                print(
                    f"🧹 Directorio del proyecto incompleto eliminado: {destination_base_path}. / "
                    f"Incomplete project directory deleted: {destination_base_path}."
                )
            except Exception as cleanup_e:
                print(
                    f"⚠️ No se pudo eliminar automáticamente el directorio '{destination_base_path}': {cleanup_e}. Por favor, elimínalo manually. / "
                    f"Could not automatically delete directory '{destination_base_path}': {cleanup_e}. Please delete it manually."
                )


if __name__ == "__main__":
    print(
        "Este script está pensado para ejecutarse como 'lila-init' después de instalar 'lila-framework'. / "
        "This script is intended to be run as 'lila-init' after installing 'lila-framework'."
    )
