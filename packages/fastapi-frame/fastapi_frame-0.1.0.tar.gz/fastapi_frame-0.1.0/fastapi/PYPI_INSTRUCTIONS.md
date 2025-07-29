# Instrucciones para subir a PyPI

## Paso 1: Crear cuenta en PyPI
1. Ve a https://pypi.org/account/register/
2. Crea tu cuenta con un nombre de usuario y contraseña
3. Verifica tu email

## Paso 2: Crear cuenta en TestPyPI (opcional pero recomendado)
1. Ve a https://test.pypi.org/account/register/
2. Crea tu cuenta (puede ser la misma información)

## Paso 3: Crear tokens de API
### Para TestPyPI:
1. Ve a https://test.pypi.org/manage/account/#api-tokens
2. Crea un nuevo token API con alcance para todo el proyecto
3. Copia el token (empieza con `pypi-`)

### Para PyPI:
1. Ve a https://pypi.org/manage/account/#api-tokens
2. Crea un nuevo token API
3. Copia el token

## Paso 4: Subir a TestPyPI (recomendado primero)
```bash
cd "c:\Users\jordi\Documents\UNI\fastapi"
python -m twine upload --repository testpypi dist/*
```
- Username: `__token__`
- Password: tu token de TestPyPI

## Paso 5: Probar la instalación desde TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ fastapi-templates-framework
```

## Paso 6: Subir a PyPI real
```bash
cd "c:\Users\jordi\Documents\UNI\fastapi"
python -m twine upload dist/*
```
- Username: `__token__`
- Password: tu token de PyPI

## Paso 7: Verificar la instalación
```bash
pip install fastapi-templates-framework
```

## Notas importantes:
- Una vez subido a PyPI, no puedes eliminar o modificar esa versión
- Para actualizaciones, necesitas incrementar el número de versión en pyproject.toml
- El nombre del paquete debe ser único en PyPI

## Estructura del paquete creado:
- **Nombre**: fastapi-templates-framework
- **Versión**: 0.1.0
- **Descripción**: FastAPI framework templates and utilities for rapid API development
- **Autor**: Jordi
- **Licencia**: MIT

## Uso después de la instalación:
```python
from fastapi_templates_framework.dependencies import FrameworkRegistry
from fastapi_templates_framework.dependencies.entities import Framework, Endpoint

# Crear un framework
framework = Framework(name="FastAPI", type=FrameworkTypes.API_FRAMEWORK)

# Crear un endpoint
endpoint = Endpoint(name="/users", method="GET", framework_id=1)
```
