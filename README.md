# 📄 Procesador de Facturas XML v2.0.0

Una aplicación web moderna para procesar archivos ZIP que contienen facturas electrónicas XML y generar reportes en formato Excel con la estructura específica requerida para análisis fiscal.

## 🚀 Características

- **Procesamiento masivo**: Hasta 100 archivos ZIP simultáneamente
- **Formato UBL**: Compatible con facturas electrónicas colombianas
- **Clasificación automática**: Identifica IVA GRAVADO, EXENTO y EXCLUIDO
- **Agrupación inteligente**: IVAs del mismo porcentaje se agrupan automáticamente
- **Interfaz moderna**: Diseño responsivo con drag & drop
- **Reportes detallados**: Estadísticas completas del procesamiento
- **Gestión de archivos**: Limpieza automática de archivos temporales

## 📋 Estructura del Proyecto

```
procesador-facturas-xml/
├── src/
│   ├── app.py                 # Aplicación principal Flask
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── xml_processor.py   # Procesamiento de archivos XML
│   │   ├── tax_classifier.py  # Clasificación de impuestos
│   │   ├── excel_generator.py # Generación de archivos Excel
│   │   └── file_manager.py    # Gestión de archivos
│   ├── templates/
│   │   └── index.html         # Interfaz de usuario
│   └── static/
│       ├── css/
│       │   └── style.css      # Estilos CSS
│       └── js/
│           └── app.js         # JavaScript del frontend
├── docs/                      # Documentación adicional
├── examples/                  # Ejemplos de uso
├── tests/                     # Pruebas unitarias
├── requirements.txt           # Dependencias Python
└── README.md                 # Este archivo
```

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd procesador-facturas-xml
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   cd src
   python app.py
   ```

5. **Acceder a la aplicación**
   Abrir el navegador en: `http://localhost:5051`

## 📖 Uso

### Interfaz Web

1. **Cargar archivos**: Arrastra archivos ZIP o haz clic para seleccionar
2. **Procesar**: Haz clic en "Procesar Facturas"
3. **Descargar**: Descarga el archivo Excel generado
4. **Ver estadísticas**: Revisa las estadísticas del procesamiento

### Estructura de Archivos ZIP

Los archivos ZIP deben contener:
- Archivos XML con facturas electrónicas en formato UBL
- Estructura estándar de facturación electrónica colombiana

### Estructura del Excel Generado

El archivo Excel contiene las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| Cuenta | Campo para clasificación contable |
| Comprobante | Tipo de documento (FACTURA, NOTA CRÉDITO, etc.) |
| Fecha(mm/dd/yyyy) | Fecha de la factura |
| Documento | Número de factura (últimos 5 dígitos) |
| Documento Ref. | Nombre del archivo ZIP original |
| Nit | NIT del proveedor |
| Detalle | Descripción del impuesto con porcentaje |
| Tipo | Clasificación: GRAVADO, EXENTO, EXCLUIDO |
| Valor | Monto del impuesto |
| Base | Base gravable |
| Centro de Costo | Campo para centro de costos |
| Trans. Ext | Campo para transacciones externas |
| Plazo | Fecha de vencimiento |
| Docto Electrónico | UUID del documento |

## 🔧 Configuración

### Variables de Entorno

```bash
# Configuración del servidor
DEBUG=True                    # Modo debug (True/False)
PORT=5051                     # Puerto del servidor
HOST=0.0.0.0                  # Host del servidor
SECRET_KEY=tu_clave_secreta   # Clave secreta para Flask
```

### Límites de Configuración

- **Archivos máximos**: 100 archivos ZIP
- **Tamaño máximo por archivo**: 100MB
- **Tamaño total máximo**: 500MB
- **Tiempo de procesamiento**: 5 minutos máximo
- **Archivos temporales**: Expiran en 24 horas

## 📊 Ejemplos de Uso

### Ejemplo 1: Procesamiento Básico

```python
# Ejecutar la aplicación
python src/app.py

# Acceder a la interfaz web
# http://localhost:5051
```

### Ejemplo 2: Verificar Estado del Servidor

```bash
# Verificar que el servidor esté funcionando
curl http://localhost:5051/test

# Respuesta esperada:
{
  "status": "ok",
  "message": "Servidor funcionando correctamente",
  "timestamp": "2024-01-15T10:30:00",
  "version": "2.0.0"
}
```

### Ejemplo 3: Verificar Salud del Sistema

```bash
# Verificar salud del sistema
curl http://localhost:5051/health

# Respuesta esperada:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "temp_files_count": 0,
  "version": "2.0.0"
}
```

## 🧪 Pruebas

### Ejecutar pruebas unitarias

```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-cov

# Ejecutar pruebas
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

### Pruebas manuales

1. **Prueba de carga de archivos**: Subir archivos ZIP de diferentes tamaños
2. **Prueba de procesamiento**: Verificar que se generen los Excel correctamente
3. **Prueba de errores**: Intentar subir archivos no válidos
4. **Prueba de límites**: Probar con el máximo de archivos permitidos

## 🔍 Clasificación de Impuestos

### Tipos de Impuestos Soportados

- **IVA (01)**: Impuesto al Valor Agregado
- **IC (02)**: Impuesto al Consumo
- **ICA (03)**: Impuesto de Industria y Comercio
- **INC (04-99)**: Impuesto Nacional al Consumo
- **ICL (32)**: Impuesto al Consumo de Licores
- **ADV (36)**: Impuesto al Consumo de Licores, Vinos, Cervezas y Cigarrillos

### Clasificación Fiscal

- **GRAVADO**: Impuesto con porcentaje > 0 y valor > 0
- **EXENTO**: Impuesto con porcentaje > 0 pero valor = 0, o porcentaje = 0 con base > 0
- **EXCLUIDO**: Sin base gravable
- **INDEFINIDO**: Casos no clasificables

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Error de conexión**
   - Verificar que el servidor esté ejecutándose
   - Comprobar el puerto 5051
   - Revisar firewall/antivirus

2. **Error de procesamiento**
   - Verificar formato de archivos ZIP
   - Comprobar que contengan XML válidos
   - Revisar logs del servidor

3. **Error de memoria**
   - Reducir número de archivos
   - Procesar archivos más pequeños
   - Reiniciar la aplicación

### Logs y Debugging

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Modo debug
export DEBUG=True
python src/app.py
```

## 📈 Estadísticas y Métricas

### Métricas Disponibles

- **Registros procesados**: Total de filas generadas
- **Archivos procesados**: Número de ZIP procesados
- **IVA Gravado**: Registros con IVA gravado
- **IVA Exento**: Registros con IVA exento
- **IVA Excluido**: Registros sin IVA

### Rendimiento

- **Tiempo promedio**: 2-5 segundos por archivo
- **Memoria**: ~50MB por 100 archivos
- **CPU**: Uso moderado durante procesamiento

## 🤝 Contribución

### Cómo contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

### Estándares de código

- Usar Python 3.8+
- Seguir PEP 8
- Documentar funciones y clases
- Agregar pruebas para nuevas funcionalidades

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Sistema de Procesamiento XML** - *Desarrollo inicial* - [TuNombre](https://github.com/tuusuario)

## 🙏 Agradecimientos

- Comunidad de desarrolladores Python
- Estándares UBL para facturación electrónica
- Contribuidores y usuarios del proyecto

## 📞 Soporte

Para soporte técnico o preguntas:

- 📧 Email: soporte@ejemplo.com
- 📱 Teléfono: +57 XXX XXX XXXX
- 🌐 Web: https://ejemplo.com/soporte

---

**Versión**: 2.0.0  
**Última actualización**: Enero 2024  
**Compatibilidad**: Python 3.8+, Flask 2.3+
