#!/usr/bin/env python3
"""
Script de diagnóstico para el procesador de facturas
"""

import sys
import os
import subprocess
import requests
import time

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ❌ Se requiere Python 3.7 o superior")
        return False
    else:
        print("   ✅ Versión de Python compatible")
        return True

def check_dependencies():
    """Verifica las dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        'flask',
        'pandas', 
        'lxml',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   Instala las dependencias faltantes con:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    else:
        print("   ✅ Todas las dependencias están instaladas")
        return True

def check_port_availability(port=5051):
    """Verifica si el puerto está disponible"""
    print(f"\n🔌 Verificando disponibilidad del puerto {port}...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  El puerto {port} está en uso")
            return False
        else:
            print(f"   ✅ El puerto {port} está disponible")
            return True
    except Exception as e:
        print(f"   ❌ Error verificando puerto: {e}")
        return False

def start_server():
    """Inicia el servidor Flask"""
    print("\n🚀 Iniciando servidor Flask...")
    
    try:
        # Verificar que app.py existe
        if not os.path.exists('app.py'):
            print("   ❌ No se encuentra app.py")
            return None
        
        # Iniciar el servidor en segundo plano
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que el servidor inicie
        time.sleep(3)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("   ✅ Servidor iniciado correctamente")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ Error iniciando servidor:")
            print(f"   STDOUT: {stdout.decode()}")
            print(f"   STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_server_connection():
    """Prueba la conexión al servidor"""
    print("\n🌐 Probando conexión al servidor...")
    
    try:
        # Probar la ruta de test
        response = requests.get('http://localhost:5051/test', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Conexión exitosa: {data['message']}")
            return True
        else:
            print(f"   ❌ Error del servidor: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Tiempo de espera agotado")
        return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def test_main_page():
    """Prueba la página principal"""
    print("\n📄 Probando página principal...")
    
    try:
        response = requests.get('http://localhost:5051/', timeout=10)
        
        if response.status_code == 200:
            if 'Procesador de Facturas' in response.text:
                print("   ✅ Página principal cargada correctamente")
                return True
            else:
                print("   ⚠️  Página cargada pero contenido inesperado")
                return False
        else:
            print(f"   ❌ Error del servidor: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔧 DIAGNÓSTICO DEL PROCESADOR DE FACTURAS")
    print("=" * 50)
    
    # Verificaciones básicas
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    if not check_port_availability():
        print("   💡 Intenta cambiar el puerto en app.py o detén otros servicios")
        return
    
    # Iniciar servidor
    server_process = start_server()
    if not server_process:
        return
    
    try:
        # Probar conexión
        if not test_server_connection():
            return
        
        if not test_main_page():
            return
        
        print("\n✅ DIAGNÓSTICO COMPLETADO - TODO FUNCIONA CORRECTAMENTE")
        print("\n🌐 El servidor está ejecutándose en: http://localhost:5051")
        print("📄 Abre tu navegador y ve a esa dirección")
        print("🔧 Para detener el servidor, presiona Ctrl+C")
        
        # Mantener el servidor ejecutándose
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servidor...")
            server_process.terminate()
            server_process.wait()
            print("✅ Servidor detenido")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        server_process.terminate()
        server_process.wait()
        print("✅ Servidor detenido")

if __name__ == "__main__":
    main()
