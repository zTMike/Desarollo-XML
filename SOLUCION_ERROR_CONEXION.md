# 🔧 Solución al Error "Failed to fetch"

## 📋 Diagnóstico del Problema

El error "Failed to fetch" indica que hay un problema de comunicación entre el navegador y el servidor Flask. Esto puede ocurrir por varias razones:

### 🔍 Posibles Causas:

1. **Servidor no está ejecutándose**
2. **Puerto bloqueado o en uso**
3. **Dependencias faltantes**
4. **Error en el código del servidor**
5. **Problemas de red/firewall**

## 🛠️ Pasos para Solucionar

### Paso 1: Ejecutar el Diagnóstico Automático

```bash
# Instalar dependencias adicionales para diagnóstico
pip install requests

# Ejecutar el script de diagnóstico
python diagnostico.py
```

### Paso 2: Verificación Manual

Si el diagnóstico automático no funciona, sigue estos pasos:

#### 2.1 Verificar Dependencias
```bash
pip install -r requirements.txt
```

#### 2.2 Verificar que el Servidor se Inicia
```bash
python app.py
```

Deberías ver algo como:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5051
```

#### 2.3 Probar Conexión Manual
Abre tu navegador y ve a:
- `http://localhost:5051/test` - Debería mostrar un JSON
- `http://localhost:5051/` - Debería mostrar la página principal

### Paso 3: Soluciones Específicas

#### Si el puerto 5051 está en uso:
Cambia el puerto en `app.py`:
```python
app.run(debug=True, port=5052, host='0.0.0.0')  # Cambia 5051 por 5052
```

#### Si hay errores de dependencias:
```bash
pip install --upgrade flask pandas lxml openpyxl
```

#### Si el servidor no inicia:
Verifica que no haya errores de sintaxis en `app.py`:
```bash
python -m py_compile app.py
```

### Paso 4: Verificar el Navegador

1. **Abrir las herramientas de desarrollador** (F12)
2. **Ir a la pestaña Console**
3. **Intentar procesar archivos** y ver si hay errores específicos
4. **Verificar la pestaña Network** para ver las peticiones HTTP

## 🚨 Errores Comunes y Soluciones

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
```bash
# En Windows
netstat -ano | findstr :5051
taskkill /PID <PID> /F

# En Linux/Mac
lsof -i :5051
kill -9 <PID>
```

### Error: "Permission denied"
Ejecuta como administrador o cambia el puerto a uno superior a 1024.

### Error: "Connection refused"
Verifica que el servidor esté ejecutándose y que no haya firewall bloqueando.

## 📞 Información de Depuración

### Logs del Servidor
Cuando ejecutes `python app.py`, verás logs como:
```
Archivos recibidos: 2
Iniciando procesamiento de archivos...
Registros procesados: 15
Generando archivo Excel...
Archivo Excel generado: /tmp/tmpxxx.xlsx
```

### Logs del Navegador
En las herramientas de desarrollador (F12), verás:
```
Enviando 2 archivos al servidor...
Respuesta recibida: 200 OK
Contenido HTML recibido, longitud: 15420
```

## ✅ Verificación Final

Después de seguir estos pasos:

1. ✅ El servidor inicia sin errores
2. ✅ Puedes acceder a `http://localhost:5051/`
3. ✅ Puedes seleccionar archivos ZIP
4. ✅ Al hacer clic en "Procesar Facturas" no aparece "Failed to fetch"
5. ✅ Se genera el archivo Excel y puedes descargarlo

## 🆘 Si el Problema Persiste

Si después de seguir todos estos pasos el problema persiste:

1. **Comparte los logs del servidor** (lo que aparece en la terminal)
2. **Comparte los errores de la consola del navegador** (F12 → Console)
3. **Verifica la versión de Python**: `python --version`
4. **Verifica las dependencias**: `pip list`

## 📱 Contacto

Si necesitas ayuda adicional, proporciona:
- Sistema operativo
- Versión de Python
- Logs de error completos
- Pasos exactos que seguiste
