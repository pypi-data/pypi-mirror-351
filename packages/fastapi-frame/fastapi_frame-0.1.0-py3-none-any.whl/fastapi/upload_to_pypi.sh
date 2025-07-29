#!/bin/bash

# Script para subir el paquete fastapi-templates-framework a PyPI

echo "=== FastAPI Templates Framework - Subida a PyPI ==="
echo

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "Error: No se encuentra pyproject.toml. Asegúrate de estar en el directorio correcto."
    exit 1
fi

echo "1. Limpiando builds anteriores..."
rm -rf dist/ build/ *.egg-info/

echo "2. Construyendo el paquete..."
python -m build

if [ $? -ne 0 ]; then
    echo "Error: Falló la construcción del paquete."
    exit 1
fi

echo "3. Verificando el paquete..."
python -m twine check dist/*

if [ $? -ne 0 ]; then
    echo "Error: El paquete no pasó las verificaciones."
    exit 1
fi

echo
echo "=== Opciones de subida ==="
echo "1. Subir a TestPyPI (recomendado para pruebas)"
echo "2. Subir a PyPI oficial"
echo "3. Solo mostrar archivos generados"
echo

read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo "Subiendo a TestPyPI..."
        echo "Usa '__token__' como username y tu token de TestPyPI como password"
        python -m twine upload --repository testpypi dist/*
        echo
        echo "Para probar la instalación:"
        echo "pip install --index-url https://test.pypi.org/simple/ fastapi-templates-framework"
        ;;
    2)
        echo "Subiendo a PyPI oficial..."
        echo "Usa '__token__' como username y tu token de PyPI como password"
        python -m twine upload dist/*
        echo
        echo "Para instalar:"
        echo "pip install fastapi-templates-framework"
        ;;
    3)
        echo "Archivos generados en dist/:"
        ls -la dist/
        ;;
    *)
        echo "Opción no válida."
        exit 1
        ;;
esac

echo
echo "¡Proceso completado!"
