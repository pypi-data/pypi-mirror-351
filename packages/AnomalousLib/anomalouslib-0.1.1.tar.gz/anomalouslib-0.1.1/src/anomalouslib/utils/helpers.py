from pathlib import Path
import yaml
    
def load_param(paramType: str, keys_str: str):
    yaml_path = Path(f"../config/{paramType}s.yaml")
    if not yaml_path.exists():
        print(f"Directorio actual: {Path.cwd()}")
        raise FileNotFoundError(f"El archivo {yaml_path} no existe.")

    try:
        with yaml_path.open('r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ValueError(f"Error al cargar el archivo YAML: {e}")

    keys = keys_str.split('>')
    for i, key in enumerate(keys):
        if not isinstance(data, dict):
            raise ValueError(f"El dato {data} no es un diccionario, no se puede seguir navegando.")
        
        if i == len(keys) - 1:
            return data.get(key, None)  # O cualquier otro comportamiento que desees
        else: data = data.get(key)
    return data