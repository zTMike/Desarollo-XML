"""
Configuración del Procesador de Facturas XML
==========================================

Este archivo contiene todas las configuraciones de la aplicación,
incluyendo límites, rutas y configuraciones del servidor.
"""

import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración del servidor
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_12345')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5051))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Límites de archivos
    MAX_FILES = float('inf')  # Sin límite de archivos
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB por archivo
    MAX_TOTAL_SIZE = float('inf')  # Sin límite de espacio total
    ALLOWED_EXTENSIONS = {'.zip', '.xml'}
    
    # Configuración de archivos temporales
    TEMP_FILE_AGE = timedelta(hours=24)
    TEMP_DIR = os.environ.get('TEMP_DIR', None)  # None = usar directorio temporal del sistema
    
    # Configuración de procesamiento
    PROCESSING_TIMEOUT = 300  # 5 minutos
    BATCH_SIZE = 100  # Procesar archivos en lotes de 100
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Configuración de Excel
    EXCEL_SHEET_NAME = 'Facturas'
    EXCEL_MAX_ROWS = 1000000  # Máximo 1 millón de filas
    
    # Configuración de nombrespaces XML
    XML_NAMESPACES = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    }
    
    # Configuración de impuestos
    TAX_CLASSIFICATIONS = {
        'GRAVADO': 'Impuesto con porcentaje > 0 y valor > 0',
        'EXENTO': 'Impuesto con porcentaje > 0 pero valor = 0, o porcentaje = 0 con base > 0',
        'EXCLUIDO': 'Sin base gravable',
        'INDEFINIDO': 'Casos no clasificables'
    }
    
    # Configuración de columnas Excel
    EXCEL_COLUMNS = [
        'Cuenta',
        'Comprobante',
        'Fecha',
        'Documento',
        'Documento_Ref',
        'Nit',
        'Detalle',
        'Tipo',
        'Valor',
        'Base',
        'Centro_Costo',
        'Trans_Ext',
        'Plazo',
        'Docto_Electronico'
    ]

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Debe estar definida en producción

class TestingConfig(Config):
    """Configuración para pruebas"""
    DEBUG = True
    TESTING = True
    MAX_FILES = 5
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB para pruebas

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Obtiene la configuración según el entorno"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
