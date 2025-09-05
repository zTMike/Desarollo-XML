# 📋 Guía de Instalación - Procesador de Facturas XML

## 🎯 Objetivo

Esta guía te ayudará a instalar y configurar el Procesador de Facturas XML en tu sistema de forma rápida y sencilla.

## 📋 Prerrequisitos

### Sistema Operativo
- **Windows**: 10 o superior
- **macOS**: 10.14 o superior
- **Linux**: Ubuntu 18.04+, CentOS 7+, o distribución similar

### Software Requerido
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python (incluido con Python)
- **Git**: Para clonar el repositorio (opcional)

### Verificar Python
```bash
# Verificar versión de Python
python --version
# o
python3 --version

# Verificar pip
pip --version
# o
pip3 --version
```

## 🚀 Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

#### Opción A: Usando Git
```bash
git clone <url-del-repositorio>
cd procesador-facturas-xml
```

#### Opción B: Descarga Directa
1. Descarga el archivo ZIP del proyecto
2. Extrae el contenido en tu directorio de trabajo
3. Abre una terminal en el directorio extraído

### 2. Crear Entorno Virtual

#### Windows
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

#### macOS/Linux
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

### 4. Verificar Instalación

```bash
# Verificar que Flask esté instalado
python -c "import flask; print('Flask instalado correctamente')"

# Verificar que pandas esté instalado
python -c "import pandas; print('Pandas instalado correctamente')"

# Verificar que lxml esté instalado
python -c "import lxml; print('LXML instalado correctamente')"
```

## 🏃‍♂️ Ejecutar la Aplicación

### Método 1: Script de Inicio Rápido
```bash
# Desde el directorio raíz del proyecto
python run.py
```

### Método 2: Ejecución Manual
```bash
# Cambiar al directorio src
cd src

# Ejecutar la aplicación
python app.py
```

### Método 3: Usando Flask Directamente
```bash
# Configurar variables de entorno
set FLASK_APP=src/app.py  # Windows
export FLASK_APP=src/app.py  # macOS/Linux

# Ejecutar Flask
flask run --host=0.0.0.0 --port=5051
```

## 🌐 Acceder a la Aplicación

Una vez ejecutada la aplicación:

1. Abre tu navegador web
2. Ve a: `http://localhost:5051`
3. Deberías ver la interfaz del Procesador de Facturas XML

## ⚙️ Configuración Adicional

### Variables de Entorno (Opcional)

Crea un archivo `.env` en el directorio raíz:

```bash
# Configuración del servidor
DEBUG=True
PORT=5051
HOST=0.0.0.0
SECRET_KEY=tu_clave_secreta_aqui

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Configuración de archivos temporales
TEMP_DIR=temp/
```

### Configuración de Firewall

Si tienes problemas de conexión:

#### Windows
1. Abrir "Firewall de Windows Defender"
2. Permitir Python en redes privadas y públicas
3. Crear regla para el puerto 5051

#### macOS
```bash
# Permitir conexiones al puerto 5051
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

#### Linux
```bash
# Abrir puerto 5051 (Ubuntu/Debian)
sudo ufw allow 5051

# Abrir puerto 5051 (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=5051/tcp
sudo firewall-cmd --reload
```

## 🧪 Probar la Instalación

### 1. Verificar Estado del Servidor
```bash
curl http://localhost:5051/test
```

Respuesta esperada:
```json
{
  "status": "ok",
  "message": "Servidor funcionando correctamente",
  "timestamp": "2024-01-15T10:30:00",
  "version": "2.0.0"
}
```

### 2. Verificar Salud del Sistema
```bash
curl http://localhost:5051/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "temp_files_count": 0,
  "version": "2.0.0"
}
```

### 3. Ejecutar Ejemplo de Uso
```bash
# Ejecutar ejemplo programático
python examples/ejemplo_uso.py
```

## 🐛 Solución de Problemas

### Error: "Python no se reconoce como comando"
- **Solución**: Instalar Python desde python.org
- **Alternativa**: Usar `python3` en lugar de `python`

### Error: "pip no se reconoce como comando"
- **Solución**: Reinstalar Python con pip incluido
- **Alternativa**: Usar `pip3` en lugar de `pip`

### Error: "Puerto 5051 ya está en uso"
- **Solución**: Cambiar el puerto en la configuración
- **Alternativa**: Terminar el proceso que usa el puerto

### Error: "Módulo no encontrado"
- **Solución**: Verificar que el entorno virtual esté activado
- **Alternativa**: Reinstalar dependencias con `pip install -r requirements.txt`

### Error: "Permiso denegado"
- **Solución**: Ejecutar como administrador (Windows) o con sudo (Linux/macOS)
- **Alternativa**: Cambiar permisos del directorio

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. **Revisar logs**: Verificar mensajes de error en la consola
2. **Verificar versiones**: Asegurar que Python sea 3.8+
3. **Reinstalar**: Eliminar entorno virtual y crear uno nuevo
4. **Contactar soporte**: Enviar detalles del error y configuración del sistema

## ✅ Verificación Final

Para verificar que todo esté funcionando correctamente:

1. ✅ Python 3.8+ instalado
2. ✅ Entorno virtual creado y activado
3. ✅ Dependencias instaladas
4. ✅ Aplicación ejecutándose en puerto 5051
5. ✅ Interfaz web accesible
6. ✅ Endpoints de prueba respondiendo
7. ✅ Ejemplo de uso ejecutándose

¡Felicitaciones! 🎉 El Procesador de Facturas XML está listo para usar.
