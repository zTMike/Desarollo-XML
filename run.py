#!/usr/bin/env python3
"""
Script de inicio rápido para el Procesador de Facturas XML
=======================================================

Este script permite ejecutar la aplicación de forma rápida
sin necesidad de cambiar al directorio src.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Cambiar al directorio src
os.chdir(src_path)

# Importar y ejecutar la aplicación
if __name__ == '__main__':
    from app import app
    
    print("🚀 Iniciando Procesador de Facturas XML v2.0.0")
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print(f"🌐 URL: http://localhost:5051")
    print("=" * 50)
    
    app.run(debug=True, port=5051, host='0.0.0.0')
