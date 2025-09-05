"""
Procesador de Facturas XML - Aplicación Principal
================================================

Este módulo contiene la aplicación Flask principal que coordina el procesamiento
de archivos XML de facturas electrónicas y la generación de reportes Excel.

Funcionalidades principales:
- Carga de archivos ZIP/XML mediante interfaz web
- Procesamiento de facturas UBL (Universal Business Language)
- Clasificación automática de impuestos (GRAVADO, EXENTO, EXCLUIDO)
- Generación de reportes Excel con formato profesional
- Gestión de archivos temporales y limpieza automática

Ejemplo de uso:
    python run.py
    # Acceder a http://localhost:5051

Autor: Sistema de Procesamiento XML
Versión: 2.0.0
"""

from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import os
import tempfile
import uuid
from datetime import datetime

# Importar módulos de utilidades
from utils.xml_processor import XMLProcessor
from utils.excel_generator import ExcelGenerator
from utils.tax_classifier import TaxClassifier
from utils.file_manager import FileManager

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_12345')

# Configuración de límites de archivos
TEMP_FILES = {}  # Diccionario para almacenar archivos temporales (legacy)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB máximo por archivo
MAX_FILES = float('inf')  # Sin límite de archivos por sesión

# Inicializar instancias de las clases de utilidades
xml_processor = XMLProcessor()      # Procesador de archivos XML
excel_generator = ExcelGenerator()  # Generador de archivos Excel
tax_classifier = TaxClassifier()    # Clasificador de impuestos
file_manager = FileManager()        # Gestor de archivos temporales


@app.route('/')
def index():
    """
    Ruta principal - Página de inicio
    
    Renderiza la interfaz web principal donde los usuarios pueden:
    - Arrastrar y soltar archivos ZIP/XML
    - Ver el progreso del procesamiento
    - Descargar el reporte Excel generado
    
    Returns:
        str: HTML de la página principal
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Endpoint para procesar archivos subidos
    
    Procesa archivos ZIP que contienen facturas XML y genera un reporte Excel
    con la información extraída y clasificada.
    
    Flujo de procesamiento:
    1. Validar archivos subidos (tamaño, extensión, cantidad)
    2. Extraer XMLs de los archivos ZIP
    3. Parsear cada factura XML para extraer datos
    4. Clasificar impuestos según reglas fiscales
    5. Generar reporte Excel con formato profesional
    6. Almacenar archivo temporal para descarga
    
    Returns:
        JSON con información del procesamiento:
        - success: bool - Indica si el procesamiento fue exitoso
        - message: str - Mensaje descriptivo del resultado
        - file_id: str - ID del archivo Excel generado (si es exitoso)
        - stats: dict - Estadísticas del procesamiento (filas procesadas, etc.)
    
    Ejemplo de respuesta exitosa:
        {
            "success": true,
            "message": "Procesamiento completado exitosamente",
            "file_id": "abc123-def456",
            "stats": {
                "archivos_procesados": 2,
                "facturas_extraidas": 15,
                "filas_totales": 45
            }
        }
    
    Ejemplo de respuesta con error:
        {
            "success": false,
            "message": "Error: No se encontraron archivos XML válidos",
            "file_id": null,
            "stats": {}
        }
    """
    try:
        # Verificar si se subieron archivos
        if 'zip_files' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se seleccionaron archivos',
                'file_id': None,
                'stats': {}
            })

        files = request.files.getlist('zip_files')
        
        # Validar archivos usando el FileManager
        validation_result = file_manager.validate_multiple_files(files)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message'],
                'file_id': None,
                'stats': {}
            })

        all_rows = []  # Lista para almacenar todas las filas de datos
        processed_files = 0  # Contador de archivos procesados exitosamente

        # Procesar cada archivo subido
        for file in files:
            try:
                # Procesar archivo ZIP usando XMLProcessor
                rows = xml_processor.process_zip_file(file)
                if rows:
                    all_rows.extend(rows)
                    processed_files += 1
                    
            except Exception as e:
                # Continuar con el siguiente archivo si hay error en uno
                print(f"Error procesando archivo {file.filename}: {str(e)}")
                continue

        # Verificar si se extrajeron datos
        if not all_rows:
            return jsonify({
                'success': False,
                'message': 'No se encontraron archivos XML válidos en los ZIPs',
                'file_id': None,
                'stats': {}
            })

        # Generar archivo Excel usando ExcelGenerator
        excel_file = excel_generator.generate_excel(all_rows)
        
        # Crear archivo temporal para descarga usando FileManager
        file_id = file_manager.create_temp_file(excel_file.getvalue(), '.xlsx')
        
        # Almacenar información del archivo temporal
        TEMP_FILES[file_id] = {
            'path': file_manager.get_file_path(file_id),
            'created': datetime.now(),
            'filename': f'reporte_facturas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        }

        # Calcular estadísticas del procesamiento
        stats = {
            'archivos_procesados': processed_files,
            'facturas_extraidas': len(set(row['Documento'] for row in all_rows)),
            'filas_totales': len(all_rows),
            'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify({
            'success': True,
            'message': f'Procesamiento completado exitosamente. {len(all_rows)} líneas procesadas.',
            'file_id': file_id,
            'stats': stats
        })

    except Exception as e:
        # Manejar errores inesperados
        print(f"Error en upload_files: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'file_id': None,
            'stats': {}
        })


@app.route('/download/<file_id>')
def download_file(file_id):
    """
    Endpoint para descargar archivos Excel generados
    
    Permite a los usuarios descargar el reporte Excel generado después
    del procesamiento de archivos XML.
    
    Args:
        file_id (str): ID único del archivo temporal a descargar
        
    Returns:
        Flask response: Archivo Excel para descarga o error 404
        
    Ejemplo de uso:
        GET /download/abc123-def456
        # Descarga el archivo Excel correspondiente al ID
        
    Ejemplo de respuesta con error:
        HTTP 404 - Archivo no encontrado
    """
    try:
        # Verificar si el archivo existe en el registro temporal
        if file_id not in TEMP_FILES:
            return "Archivo no encontrado", 404
        
        file_info = TEMP_FILES[file_id]
        file_path = file_info['path']
        
        # Verificar si el archivo físico existe
        if not os.path.exists(file_path):
            # Limpiar entrada del registro si el archivo no existe
            del TEMP_FILES[file_id]
            return "Archivo no encontrado", 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error en download_file: {str(e)}")
        return "Error interno del servidor", 500


@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """
    Endpoint para limpiar archivos temporales
    
    Elimina archivos temporales antiguos para liberar espacio en disco.
    Útil para mantenimiento del sistema.
    
    Returns:
        JSON con información de la limpieza:
        - success: bool - Indica si la limpieza fue exitosa
        - message: str - Mensaje descriptivo del resultado
        - files_removed: int - Número de archivos eliminados
        
    Ejemplo de respuesta:
        {
            "success": true,
            "message": "Limpieza completada",
            "files_removed": 5
        }
    """
    try:
        # Usar FileManager para limpiar archivos expirados
        files_removed = file_manager.cleanup_expired_files()
        
        return jsonify({
            'success': True,
            'message': 'Limpieza completada',
            'files_removed': files_removed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en limpieza: {str(e)}',
            'files_removed': 0
        })


@app.route('/health')
def health_check():
    """
    Endpoint de verificación de salud del sistema
    
    Proporciona información sobre el estado del sistema, incluyendo:
    - Estado general del servicio
    - Número de archivos temporales
    - Espacio utilizado
    - Versión de la aplicación
    
    Returns:
        JSON con información del estado del sistema
        
    Ejemplo de respuesta:
        {
            "status": "healthy",
            "version": "2.0.0",
            "temp_files_count": 3,
            "temp_files_size_mb": 2.5,
            "timestamp": "2024-01-15T10:30:00"
        }
    """
    try:
        temp_files_count = file_manager.get_temp_files_count()
        temp_files_size = file_manager.get_temp_files_size()
        
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'temp_files_count': temp_files_count,
            'temp_files_size_mb': round(temp_files_size / (1024 * 1024), 2),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Configuración para ejecución directa
if __name__ == '__main__':
    """
    Punto de entrada principal para ejecución directa
    
    Configura y ejecuta la aplicación Flask en modo desarrollo.
    Útil para pruebas locales y desarrollo.
    
    Ejemplo de uso:
        python app.py
        # La aplicación estará disponible en http://localhost:5051
    """
    port = int(os.environ.get('PORT', 5051))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Procesador de Facturas XML v2.0.0")
    print(f"📡 Servidor disponible en: http://{host}:{port}")
    print(f"🔧 Modo debug: {debug}")
    print(f"📁 Archivos temporales: {file_manager.get_temp_files_count()}")
    
    app.run(debug=debug, port=port, host=host)
