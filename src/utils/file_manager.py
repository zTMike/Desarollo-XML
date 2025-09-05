"""
Gestor de Archivos - Módulo de Utilidades
========================================

Este módulo contiene la lógica para gestionar archivos temporales,
validar archivos subidos y realizar operaciones de limpieza automática.

Funcionalidades principales:
- Creación y gestión de archivos temporales
- Validación de archivos subidos (tamaño, extensión, contenido)
- Limpieza automática de archivos expirados
- Control de espacio en disco
- Seguimiento de archivos temporales

Clases principales:
- FileManager: Clase principal para gestión de archivos

Ejemplo de uso:
    manager = FileManager()
    file_id = manager.create_temp_file(file_content, '.xlsx')
    file_path = manager.get_temp_file_path(file_id)
    manager.cleanup_file(file_id)

Autor: Sistema de Procesamiento XML
Versión: 2.0.0
"""

import os
import tempfile
import uuid
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileManager:
    """
    Gestor de archivos temporales y validaciones
    
    Esta clase maneja todas las operaciones relacionadas con archivos:
    - Creación y gestión de archivos temporales
    - Validación de archivos subidos
    - Limpieza automática de archivos expirados
    - Control de espacio en disco
    
    Funcionalidades:
    - Gestión de archivos temporales con IDs únicos
    - Validación de tipos de archivo y tamaños
    - Limpieza automática de archivos antiguos
    - Seguimiento de uso de espacio
    
    Atributos:
        temp_files (dict): Diccionario de archivos temporales gestionados
        max_file_age (timedelta): Tiempo máximo de vida de archivos
        max_file_size (int): Tamaño máximo de archivo en bytes
        allowed_extensions (set): Extensiones de archivo permitidas
    
    Ejemplo de uso:
        manager = FileManager()
        
        # Crear archivo temporal
        file_id = manager.create_temp_file(content, '.xlsx')
        
        # Validar archivo subido
        validation = manager.validate_file(uploaded_file)
        
        # Limpiar archivos expirados
        removed_count = manager.cleanup_expired_files()
    """
    
    def __init__(self):
        """
        Inicializa el gestor de archivos con configuraciones necesarias
        
        Configura límites de tamaño, extensiones permitidas, tiempo
        de expiración y directorio temporal para archivos.
        """
        # Diccionario para almacenar información de archivos temporales
        self.temp_files: Dict[str, Dict] = {}
        
        # Configuración de límites y tiempos
        self.max_file_age = timedelta(hours=24)  # Archivos expiran en 24 horas
        self.max_file_size = 100 * 1024 * 1024  # 100MB máximo por archivo
        self.max_total_files = float('inf')  # Sin límite de archivos temporales
        self.max_total_size = float('inf')  # Sin límite de espacio total
        
        # Extensiones de archivo permitidas
        self.allowed_extensions = {'.zip', '.xml', '.xlsx', '.xls'}
        
        # Directorio temporal personalizado
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'xml_processor')
        
        # Crear directorio temporal si no existe
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.info(f"FileManager inicializado con directorio temporal: {self.temp_dir}")

    def create_temp_file(self, file_content: bytes, extension: str = '.xlsx') -> str:
        """
        Crea un archivo temporal con contenido específico
        
        Genera un archivo temporal único con el contenido proporcionado
        y lo registra en el sistema de gestión de archivos.
        
        Args:
            file_content (bytes): Contenido del archivo en bytes
            extension (str): Extensión del archivo (por defecto '.xlsx')
            
        Returns:
            str: ID único del archivo temporal creado
            
        Ejemplo de uso:
            file_id = manager.create_temp_file(excel_content, '.xlsx')
            # file_id = 'abc123-def456-ghi789'
            
        Ejemplo de archivo creado:
            /tmp/xml_processor/abc123-def456-ghi789.xlsx
            
        Características:
            - ID único generado con UUID
            - Registro automático en sistema de gestión
            - Control de tiempo de creación
            - Validación de tamaño de contenido
        """
        try:
            # Generar ID único para el archivo
            file_id = str(uuid.uuid4())
            
            # Validar tamaño del contenido
            content_size = len(file_content)
            if content_size > self.max_file_size:
                raise ValueError(f"Contenido demasiado grande: {content_size} bytes")
            
            # Crear nombre de archivo con extensión
            filename = f"{file_id}{extension}"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Escribir contenido al archivo
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Registrar archivo en el sistema
            self.temp_files[file_id] = {
                'path': file_path,
                'filename': filename,
                'size': content_size,
                'created': datetime.now(),
                'extension': extension
            }
            
            logger.info(f"Archivo temporal creado: {file_id} ({content_size} bytes)")
            return file_id
            
        except Exception as e:
            logger.error(f"Error creando archivo temporal: {str(e)}")
            raise

    def get_temp_file_path(self, file_id: str) -> Optional[str]:
        """
        Obtiene la ruta del archivo temporal por su ID
        
        Busca y retorna la ruta del archivo temporal correspondiente
        al ID proporcionado, verificando que el archivo exista.
        
        Args:
            file_id (str): ID único del archivo temporal
            
        Returns:
            Optional[str]: Ruta del archivo si existe, None en caso contrario
            
        Ejemplo de uso:
            file_path = manager.get_temp_file_path('abc123-def456-ghi789')
            # file_path = '/tmp/xml_processor/abc123-def456-ghi789.xlsx'
            
        Validaciones:
            - Verifica que el ID exista en el registro
            - Confirma que el archivo físico existe
            - Verifica que no haya expirado
        """
        try:
            if file_id not in self.temp_files:
                logger.warning(f"ID de archivo no encontrado: {file_id}")
                return None
            
            file_info = self.temp_files[file_id]
            file_path = file_info['path']
            
            # Verificar que el archivo físico existe
            if not os.path.exists(file_path):
                logger.warning(f"Archivo físico no encontrado: {file_path}")
                self.cleanup_file(file_id)
                return None
            
            # Verificar si el archivo ha expirado
            if datetime.now() - file_info['created'] > self.max_file_age:
                logger.info(f"Archivo expirado, limpiando: {file_id}")
                self.cleanup_file(file_id)
                return None
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error obteniendo ruta de archivo {file_id}: {str(e)}")
            return None

    def cleanup_file(self, file_id: str) -> bool:
        """
        Elimina un archivo temporal específico
        
        Elimina el archivo físico y lo remueve del registro de archivos
        temporales gestionados.
        
        Args:
            file_id (str): ID único del archivo a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
            
        Ejemplo de uso:
            success = manager.cleanup_file('abc123-def456-ghi789')
            if success:
                print("Archivo eliminado exitosamente")
                
        Proceso de limpieza:
            - Elimina archivo físico del sistema
            - Remueve entrada del registro
            - Maneja errores de archivo no encontrado
        """
        try:
            if file_id not in self.temp_files:
                logger.warning(f"ID de archivo no encontrado para limpieza: {file_id}")
                return False
            
            file_info = self.temp_files[file_id]
            file_path = file_info['path']
            
            # Eliminar archivo físico
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo físico eliminado: {file_path}")
            
            # Remover del registro
            del self.temp_files[file_id]
            logger.info(f"Archivo removido del registro: {file_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando archivo {file_id}: {str(e)}")
            return False

    def cleanup_expired_files(self) -> int:
        """
        Limpia automáticamente todos los archivos expirados
        
        Recorre todos los archivos temporales y elimina aquellos que
        han superado el tiempo máximo de vida configurado.
        
        Returns:
            int: Número de archivos eliminados
            
        Ejemplo de uso:
            removed_count = manager.cleanup_expired_files()
            print(f"Se eliminaron {removed_count} archivos expirados")
            
        Criterios de limpieza:
            - Archivos más antiguos que max_file_age
            - Archivos físicos que no existen
            - Archivos huérfanos en el registro
        """
        try:
            current_time = datetime.now()
            expired_files = []
            
            # Identificar archivos expirados
            for file_id, file_info in self.temp_files.items():
                file_age = current_time - file_info['created']
                
                # Verificar si ha expirado
                if file_age > self.max_file_age:
                    expired_files.append(file_id)
                    continue
                
                # Verificar si el archivo físico existe
                if not os.path.exists(file_info['path']):
                    expired_files.append(file_id)
                    continue
            
            # Eliminar archivos expirados
            removed_count = 0
            for file_id in expired_files:
                if self.cleanup_file(file_id):
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Limpieza automática completada: {removed_count} archivos eliminados")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error en limpieza automática: {str(e)}")
            return 0

    def validate_file(self, file) -> Dict[str, Any]:
        """
        Valida un archivo subido según las reglas configuradas
        
        Verifica que el archivo cumpla con los requisitos de tamaño,
        extensión y contenido antes de procesarlo.
        
        Args:
            file: Archivo subido (FileStorage de Flask o similar)
            
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
            
        Ejemplo de uso:
            validation = manager.validate_file(uploaded_file)
            if validation['valid']:
                # Procesar archivo
                pass
            else:
                print(f"Error: {validation['message']}")
                
        Validaciones realizadas:
            - Verificación de nombre de archivo
            - Validación de extensión permitida
            - Control de tamaño máximo
            - Verificación de contenido no vacío
        """
        validation_result = {
            'valid': False,
            'message': '',
            'filename': '',
            'size': 0,
            'extension': ''
        }
        
        try:
            # Verificar que el archivo existe
            if not file or not file.filename:
                validation_result['message'] = 'No se proporcionó archivo'
                return validation_result
            
            filename = file.filename
            validation_result['filename'] = filename
            
            # Validar extensión
            file_extension = os.path.splitext(filename)[1].lower()
            validation_result['extension'] = file_extension
            
            if file_extension not in self.allowed_extensions:
                validation_result['message'] = f'Extensión no permitida: {file_extension}'
                return validation_result
            
            # Obtener tamaño del archivo
            file.seek(0, 2)  # Ir al final del archivo
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            validation_result['size'] = file_size
            
            # Validar tamaño
            if file_size > self.max_file_size:
                validation_result['message'] = f'Archivo demasiado grande: {file_size} bytes'
                return validation_result
            
            if file_size == 0:
                validation_result['message'] = 'El archivo está vacío'
                return validation_result
            
            # Verificar límites del sistema (solo si están configurados)
            if self.max_total_files != float('inf') and len(self.temp_files) >= self.max_total_files:
                validation_result['message'] = 'Se ha alcanzado el límite máximo de archivos'
                return validation_result
            
            total_size = sum(info['size'] for info in self.temp_files.values())
            if self.max_total_size != float('inf') and total_size + file_size > self.max_total_size:
                validation_result['message'] = 'Se ha alcanzado el límite máximo de espacio'
                return validation_result
            
            # Archivo válido
            validation_result['valid'] = True
            validation_result['message'] = 'Archivo válido'
            
            logger.info(f"Archivo validado: {filename} ({file_size} bytes)")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validando archivo: {str(e)}")
            validation_result['message'] = f'Error de validación: {str(e)}'
            return validation_result

    def validate_multiple_files(self, files: List) -> Dict[str, Any]:
        """
        Valida múltiples archivos subidos simultáneamente
        
        Aplica validaciones a una lista de archivos y retorna un
        resultado consolidado de la validación.
        
        Args:
            files (List): Lista de archivos a validar
            
        Returns:
            Dict[str, Any]: Resultado consolidado de la validación
            
        Ejemplo de uso:
            validation = manager.validate_multiple_files(file_list)
            if validation['valid']:
                # Procesar todos los archivos
                pass
            else:
                print(f"Errores: {validation['errors']}")
                
        Validaciones adicionales:
            - Límite de cantidad de archivos
            - Tamaño total combinado
            - Duplicados por nombre
        """
        validation_result = {
            'valid': True,
            'message': 'Todos los archivos son válidos',
            'errors': [],
            'warnings': [],
            'valid_files': [],
            'total_size': 0
        }
        
        try:
            if not files:
                validation_result['valid'] = False
                validation_result['message'] = 'No se proporcionaron archivos'
                return validation_result
            
            # Validar límite de archivos (solo si está configurado)
            max_files_per_batch = 100  # Aumentado de 10 a 100 archivos por lote
            if len(files) > max_files_per_batch:
                validation_result['valid'] = False
                validation_result['message'] = f'Demasiados archivos (máximo {max_files_per_batch})'
                return validation_result
            
            # Validar cada archivo individualmente
            filenames = set()
            total_size = 0
            
            for file in files:
                individual_validation = self.validate_file(file)
                
                if not individual_validation['valid']:
                    validation_result['errors'].append(
                        f"{file.filename}: {individual_validation['message']}"
                    )
                    validation_result['valid'] = False
                else:
                    validation_result['valid_files'].append(file)
                    total_size += individual_validation['size']
                    
                    # Verificar duplicados
                    if file.filename in filenames:
                        validation_result['warnings'].append(
                            f"Archivo duplicado: {file.filename}"
                        )
                    else:
                        filenames.add(file.filename)
            
            validation_result['total_size'] = total_size
            
            # Actualizar mensaje según resultado
            if not validation_result['valid']:
                validation_result['message'] = f"Errores en {len(validation_result['errors'])} archivos"
            elif validation_result['warnings']:
                validation_result['message'] = f"Archivos válidos con {len(validation_result['warnings'])} advertencias"
            
            logger.info(f"Validación múltiple: {len(validation_result['valid_files'])} archivos válidos")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error en validación múltiple: {str(e)}")
            validation_result['valid'] = False
            validation_result['message'] = f'Error de validación: {str(e)}'
            return validation_result

    def get_file_path(self, file_id: str) -> Optional[str]:
        """
        Obtiene la ruta completa de un archivo temporal
        
        Args:
            file_id (str): ID único del archivo
            
        Returns:
            Optional[str]: Ruta completa del archivo si existe, None en caso contrario
            
        Ejemplo de uso:
            file_path = manager.get_file_path('abc123-def456-ghi789')
            if file_path:
                print(f"Ruta del archivo: {file_path}")
        """
        try:
            if file_id not in self.temp_files:
                return None
            
            return self.temp_files[file_id]['path']
            
        except Exception as e:
            logger.error(f"Error obteniendo ruta de archivo {file_id}: {str(e)}")
            return None

    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Obtiene información detallada de un archivo temporal
        
        Args:
            file_id (str): ID único del archivo
            
        Returns:
            Optional[Dict]: Información del archivo si existe, None en caso contrario
            
        Ejemplo de uso:
            file_info = manager.get_file_info('abc123-def456-ghi789')
            if file_info:
                print(f"Archivo: {file_info['filename']}")
                print(f"Tamaño: {file_info['size']} bytes")
                print(f"Creado: {file_info['created']}")
        """
        try:
            if file_id not in self.temp_files:
                return None
            
            file_info = self.temp_files[file_id].copy()
            
            # Agregar información adicional
            file_info['exists'] = os.path.exists(file_info['path'])
            file_info['age_hours'] = (datetime.now() - file_info['created']).total_seconds() / 3600
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error obteniendo información de archivo {file_id}: {str(e)}")
            return None

    def get_temp_files_count(self) -> int:
        """
        Obtiene el número total de archivos temporales gestionados
        
        Returns:
            int: Número de archivos en el registro
            
        Ejemplo de uso:
            count = manager.get_temp_files_count()
            print(f"Archivos temporales activos: {count}")
        """
        return len(self.temp_files)

    def get_temp_files_size(self) -> int:
        """
        Obtiene el tamaño total de todos los archivos temporales
        
        Returns:
            int: Tamaño total en bytes
            
        Ejemplo de uso:
            total_size = manager.get_temp_files_size()
            size_mb = total_size / (1024 * 1024)
            print(f"Espacio utilizado: {size_mb:.2f} MB")
        """
        try:
            total_size = sum(file_info['size'] for file_info in self.temp_files.values())
            return total_size
        except Exception as e:
            logger.error(f"Error calculando tamaño total: {str(e)}")
            return 0

    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado general del sistema de archivos
        
        Returns:
            Dict[str, Any]: Información del estado del sistema
            
        Ejemplo de uso:
            status = manager.get_system_status()
            print(f"Archivos: {status['file_count']}")
            print(f"Espacio: {status['total_size_mb']:.2f} MB")
            print(f"Última limpieza: {status['last_cleanup']}")
        """
        try:
            total_size = self.get_temp_files_size()
            
            status = {
                'file_count': self.get_temp_files_count(),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'max_files': 'Sin límite' if self.max_total_files == float('inf') else self.max_total_files,
                'max_size_gb': 'Sin límite' if self.max_total_size == float('inf') else round(self.max_total_size / (1024 * 1024 * 1024), 2),
                'temp_directory': self.temp_dir,
                'allowed_extensions': list(self.allowed_extensions),
                'max_file_age_hours': self.max_file_age.total_seconds() / 3600
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del sistema: {str(e)}")
            return {}
