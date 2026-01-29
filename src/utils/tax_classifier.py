"""
Clasificador de Impuestos - Módulo de Utilidades
===============================================

Este módulo contiene la lógica para clasificar y categorizar impuestos
según las reglas fiscales ecuatorianas y estándares UBL.

Funcionalidades principales:
- Mapeo de códigos de impuesto a descripciones legibles
- Clasificación automática de líneas (GRAVADO, EXENTO, EXCLUIDO)
- Cálculo de resúmenes fiscales
- Validación de porcentajes y montos de impuestos

Clases principales:
- TaxClassifier: Clase principal para clasificación de impuestos

Ejemplo de uso:
    classifier = TaxClassifier()
    tax_status = classifier.classify_tax_status('IVA', '12.00', '120.00', '1000.00')
    # tax_status = 'GRAVADO'

Autor: Sistema de Procesamiento XML
Versión: 2.0.0
"""

import logging
from typing import Dict, List, Any

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxClassifier:
    """
    Clasificador de impuestos para facturas electrónicas
    
    Esta clase maneja la clasificación y categorización de impuestos
    según las reglas fiscales ecuatorianas y estándares UBL.
    
    Funcionalidades:
    - Mapeo de códigos de impuesto a descripciones
    - Clasificación automática de líneas fiscales
    - Cálculo de resúmenes y totales
    - Validación de datos fiscales
    
    Atributos:
        tax_descriptions (dict): Mapeo de códigos de impuesto a descripciones
        tax_classifications (dict): Reglas de clasificación por tipo de impuesto
    
    Ejemplo de uso:
        classifier = TaxClassifier()
        
        # Clasificar una línea de impuesto
        status = classifier.classify_tax_status('IVA', '12.00', '120.00', '1000.00')
        
        # Obtener descripción de impuesto
        description = classifier.get_tax_description('2', 'IVA', '12.00')
        
        # Generar resumen fiscal
        summary = classifier.get_tax_summary(tax_data_list)
    """
    
    def __init__(self):
        """
        Inicializa el clasificador de impuestos con configuraciones necesarias
        
        Configura los mapeos de códigos de impuesto a descripciones y
        las reglas de clasificación según la normativa fiscal ecuatoriana.
        """
        # Mapeo de códigos de impuesto a descripciones legibles
        self.tax_descriptions = {
            '2': 'IVA',
            '3': 'ICE',
            '5': 'IRBPNR',
            '6': 'ISD',
            '7': 'IVA RETENIDO',
            '8': 'ICE RETENIDO',
            '9': 'IRBPNR RETENIDO',
            '10': 'ISD RETENIDO',
            '11': 'IVA DIFERIDO',
            '12': 'IVA DIFERIDO RETENIDO',
            '13': 'IVA DIFERIDO PAGADO',
            '14': 'IVA DIFERIDO PAGADO RETENIDO',
            '15': 'IVA DIFERIDO PAGADO PAGADO',
            '16': 'IVA DIFERIDO PAGADO PAGADO RETENIDO',
            '17': 'IVA DIFERIDO PAGADO PAGADO PAGADO',
            '18': 'IVA DIFERIDO PAGADO PAGADO PAGADO RETENIDO',
            '19': 'IVA DIFERIDO PAGADO PAGADO PAGADO PAGADO',
            '20': 'IVA DIFERIDO PAGADO PAGADO PAGADO PAGADO RETENIDO'
        }
        
        # Reglas de clasificación por tipo de impuesto
        self.tax_classifications = {
            'IVA': {
                'gravado_threshold': 0.01,  # Porcentaje mínimo para considerar gravado
                'exento_codes': ['2'],      # Códigos que indican exención
                'excluido_codes': ['6']     # Códigos que indican exclusión
            },
            'ICE': {
                'gravado_threshold': 0.01,
                'exento_codes': ['3'],
                'excluido_codes': []
            },
            'IRBPNR': {
                'gravado_threshold': 0.01,
                'exento_codes': ['5'],
                'excluido_codes': []
            }
        }
        
        logger.info("TaxClassifier inicializado con mapeos y reglas de clasificación")

    def classify_iva_specifically(self, percent: str, tax_amount: str, taxable_amount: str, tax_scheme_id: str = None) -> Dict[str, str]:
        """
        Clasifica específicamente el IVA según reglas fiscales ecuatorianas detalladas
        
        Aplica reglas específicas para IVA considerando códigos de impuesto,
        porcentajes y montos para determinar la clasificación fiscal exacta.
        Mejora la discriminación entre EXENTO y EXCLUIDO.
        
        Args:
            percent (str): Porcentaje del IVA
            tax_amount (str): Monto del IVA
            taxable_amount (str): Base imponible
            tax_scheme_id (str): Código del esquema de impuesto (opcional)
            
        Returns:
            Dict[str, str]: Diccionario con clasificación y descripción detallada
            {
                'classification': 'GRAVADO|EXENTO|EXCLUIDO|INDEFINIDO',
                'description': 'Descripción detallada del estado fiscal',
                'reason': 'Razón de la clasificación',
                'subtype': 'Subtipo específico (opcional)'
            }
            
        Ejemplo de uso:
            result = classifier.classify_iva_specifically('0.00', '0.00', '1000.00')
            # result = {
            #     'classification': 'EXENTO',
            #     'description': 'IVA Exento - Productos de Primera Necesidad',
            #     'reason': 'Productos exentos por ley',
            #     'subtype': 'PRIMERA_NECESIDAD'
            # }
        """
        try:
            # Convertir valores a float
            percent_float = float(percent) if percent else 0.0
            tax_amount_float = float(tax_amount) if tax_amount else 0.0
            taxable_amount_float = float(taxable_amount) if taxable_amount else 0.0
            
            # Validar datos de entrada
            if percent_float < 0 or tax_amount_float < 0 or taxable_amount_float < 0:
                return {
                    'classification': 'INDEFINIDO',
                    'description': 'IVA con datos negativos',
                    'reason': 'Valores negativos no permitidos',
                    'subtype': 'ERROR_DATOS'
                }
            
            # Reglas específicas para IVA con mejor discriminación
            if tax_amount_float > 0:
                # IVA GRAVADO - Hay monto de impuesto aplicado
                if percent_float == 12.0:
                    return {
                        'classification': 'GRAVADO',
                        'description': 'IVA Gravado 12% - Tasa General',
                        'reason': 'IVA estándar con monto aplicado',
                        'subtype': 'TASA_GENERAL'
                    }
                elif percent_float == 14.0:
                    return {
                        'classification': 'GRAVADO',
                        'description': 'IVA Gravado 14% - Tasa Especial',
                        'reason': 'IVA con tasa especial aplicada',
                        'subtype': 'TASA_ESPECIAL'
                    }
                elif percent_float == 15.0:
                    return {
                        'classification': 'GRAVADO',
                        'description': 'IVA Gravado 15% - Tasa Adicional',
                        'reason': 'IVA con tasa adicional aplicada',
                        'subtype': 'TASA_ADICIONAL'
                    }
                elif percent_float == 0.0:
                    return {
                        'classification': 'GRAVADO',
                        'description': 'IVA Gravado 0% - Con Monto',
                        'reason': 'IVA con tasa 0% pero con monto aplicado (inconsistencia)',
                        'subtype': 'INCONSISTENTE'
                    }
                else:
                    return {
                        'classification': 'GRAVADO',
                        'description': f'IVA Gravado {percent_float}% - Tasa No Estándar',
                        'reason': f'IVA con tasa {percent_float}% aplicada',
                        'subtype': 'TASA_NO_ESTANDAR'
                    }
                    
            elif taxable_amount_float > 0:
                # IVA EXENTO - Hay base imponible pero NO hay impuesto
                if percent_float == 0.0:
                    return {
                        'classification': 'EXENTO',
                        'description': 'IVA Exento 0% - Productos de Primera Necesidad',
                        'reason': 'Productos exentos de IVA por ley',
                        'subtype': 'PRIMERA_NECESIDAD'
                    }
                elif percent_float == 12.0:
                    return {
                        'classification': 'EXENTO',
                        'description': 'IVA Exento 12% - Exención Específica',
                        'reason': 'Producto con tasa 12% pero exento por normativa especial',
                        'subtype': 'EXENCION_ESPECIAL'
                    }
                elif percent_float == 14.0:
                    return {
                        'classification': 'EXENTO',
                        'description': 'IVA Exento 14% - Exención Especial',
                        'reason': 'Producto con tasa 14% pero exento por normativa especial',
                        'subtype': 'EXENCION_ESPECIAL'
                    }
                elif percent_float > 0:
                    return {
                        'classification': 'EXENTO',
                        'description': f'IVA Exento {percent_float}% - Exención por Normativa',
                        'reason': 'Base imponible presente pero exento por normativa',
                        'subtype': 'EXENCION_NORMATIVA'
                    }
                else:
                    return {
                        'classification': 'EXENTO',
                        'description': 'IVA Exento - Sin Porcentaje Específico',
                        'reason': 'Base imponible sin impuesto aplicado',
                        'subtype': 'EXENCION_GENERAL'
                    }
                    
            elif taxable_amount_float == 0 and tax_amount_float == 0:
                # IVA EXCLUIDO - NO hay base imponible NI impuesto
                if percent_float == 12.0:
                    return {
                        'classification': 'EXCLUIDO',
                        'description': 'IVA Excluido 12% - Exportaciones',
                        'reason': 'Exportaciones fuera del alcance del IVA',
                        'subtype': 'EXPORTACIONES'
                    }
                elif percent_float == 14.0:
                    return {
                        'classification': 'EXCLUIDO',
                        'description': 'IVA Excluido 14% - Servicios Excluidos',
                        'reason': 'Servicios específicos fuera del alcance del IVA',
                        'subtype': 'SERVICIOS_EXCLUIDOS'
                    }
                elif percent_float > 0:
                    return {
                        'classification': 'EXCLUIDO',
                        'description': f'IVA Excluido {percent_float}% - Fuera del Alcance',
                        'reason': 'Producto/servicio fuera del alcance del IVA',
                        'subtype': 'FUERA_ALCANCE'
                    }
                else:
                    # Caso general: porcentaje 0.0, base 0.0, monto 0.0
                    return {
                        'classification': 'EXCLUIDO',
                        'description': 'IVA Excluido - Sin Base Imponible',
                        'reason': 'Producto/servicio excluido del IVA',
                        'subtype': 'EXCLUSION_GENERAL'
                    }
                
            else:
                # Caso especial o datos inconsistentes
                return {
                    'classification': 'INDEFINIDO',
                    'description': 'IVA Indefinido - Datos Inconsistentes',
                    'reason': 'No se puede determinar la clasificación fiscal',
                    'subtype': 'DATOS_INCONSISTENTES'
                }
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error clasificando IVA específicamente: {str(e)}")
            return {
                'classification': 'INDEFINIDO',
                'description': 'IVA con error de datos',
                'reason': f'Error en procesamiento: {str(e)}',
                'subtype': 'ERROR_PROCESAMIENTO'
            }

    def get_tax_description(self, tax_scheme_id: str, tax_scheme_name: str, percent: str, tax_amount: str = '0', taxable_amount: str = '0') -> str:
        """
        Obtiene la descripción completa de un impuesto con clasificación fiscal
        
        Combina el código del impuesto, nombre, porcentaje y clasificación fiscal
        para crear una descripción legible y completa.
        
        Args:
            tax_scheme_id (str): Código del esquema de impuesto
            tax_scheme_name (str): Nombre del esquema de impuesto
            percent (str): Porcentaje del impuesto
            tax_amount (str): Monto del impuesto (opcional)
            taxable_amount (str): Base imponible (opcional)
            
        Returns:
            str: Descripción completa del impuesto con clasificación
            
        Ejemplo de uso:
            description = classifier.get_tax_description('2', 'IVA', '12.00', '120.00', '1000.00')
            # description = 'IVA 12.00% - GRAVADO'
            
        Ejemplo de descripciones generadas:
            - 'IVA 12.00% - GRAVADO' para IVA estándar
            - 'IVA 0.00% - EXENTO' para IVA exento
            - 'ICE 300.00% - GRAVADO' para ICE
            - 'IRBPNR 1.00% - GRAVADO' para IRBPNR
        """
        try:
            # Obtener descripción base del código
            base_description = self.tax_descriptions.get(tax_scheme_id, tax_scheme_name)
            
            # Formatear porcentaje
            try:
                percent_float = float(percent)
                formatted_percent = f"{percent_float:.2f}"
            except (ValueError, TypeError):
                formatted_percent = percent
            
            # Clasificar el impuesto si se proporcionan los montos
            classification = ""
            if tax_amount and taxable_amount:
                if tax_scheme_name.upper() == 'IVA':
                    # Usar clasificación específica para IVA con descripción mejorada
                    iva_result = self.classify_iva_specifically(percent, tax_amount, taxable_amount, tax_scheme_id)
                    # Usar la descripción detallada en lugar de solo la clasificación
                    description = iva_result['description']
                    return description
                else:
                    # Usar clasificación general para otros impuestos
                    general_classification = self.classify_tax_status(tax_scheme_name, percent, tax_amount, taxable_amount)
                    classification = f" - {general_classification}"
            
            # Construir descripción completa para impuestos no-IVA
            description = f"{base_description} {formatted_percent}%{classification}"
            
            logger.debug(f"Descripción generada: {description}")
            return description
            
        except Exception as e:
            logger.error(f"Error generando descripción de impuesto: {str(e)}")
            return f"{tax_scheme_name} {percent}%"

    def classify_tax_status(self, tax_type: str, percent: str, tax_amount: str, taxable_amount: str) -> str:
        """
        Clasifica el estado fiscal de una línea de factura según reglas fiscales ecuatorianas
        
        Determina si una línea es GRAVADO, EXENTO o EXCLUIDO basándose
        en el tipo de impuesto, porcentaje y montos, aplicando reglas específicas
        para cada tipo de impuesto según la normativa ecuatoriana.
        
        Args:
            tax_type (str): Tipo de impuesto (IVA, ICE, etc.)
            percent (str): Porcentaje del impuesto
            tax_amount (str): Monto del impuesto
            taxable_amount (str): Base imponible
            
        Returns:
            str: Clasificación fiscal ('GRAVADO', 'EXENTO', 'EXCLUIDO', 'INDEFINIDO')
            
        Ejemplo de uso:
            status = classifier.classify_tax_status('IVA', '12.00', '120.00', '1000.00')
            # status = 'GRAVADO'
            
            status = classifier.classify_tax_status('IVA', '0.00', '0.00', '1000.00')
            # status = 'EXENTO'
            
        Reglas de clasificación fiscal ecuatoriana:
            - GRAVADO: Tiene monto de impuesto > 0 (independientemente del porcentaje)
            - EXENTO: Tiene base imponible > 0 pero monto de impuesto = 0
            - EXCLUIDO: Base imponible = 0 y monto de impuesto = 0
            - INDEFINIDO: Datos inconsistentes o faltantes
        """
        try:
            # Convertir valores a float para comparaciones
            percent_float = float(percent) if percent else 0.0
            tax_amount_float = float(tax_amount) if tax_amount else 0.0
            taxable_amount_float = float(taxable_amount) if taxable_amount else 0.0
            
            # Validar datos de entrada
            if percent_float < 0 or tax_amount_float < 0 or taxable_amount_float < 0:
                logger.warning(f"Datos negativos detectados: {tax_type} - {percent}% - ${tax_amount} - ${taxable_amount}")
                return 'INDEFINIDO'
            
            # Reglas de clasificación fiscal ecuatoriana mejoradas
            if tax_amount_float > 0:
                # Hay monto de impuesto aplicado - GRAVADO
                classification = 'GRAVADO'
                logger.debug(f"Línea clasificada como GRAVADO: {tax_type} {percent_float}% - ${tax_amount_float}")
                
            elif taxable_amount_float > 0:
                # Hay base imponible pero no hay impuesto - EXENTO
                classification = 'EXENTO'
                logger.debug(f"Línea clasificada como EXENTO: {tax_type} {percent_float}% - Base: ${taxable_amount_float}")
                
            elif taxable_amount_float == 0 and tax_amount_float == 0:
                # No hay base imponible ni impuesto - EXCLUIDO
                classification = 'EXCLUIDO'
                logger.debug(f"Línea clasificada como EXCLUIDO: {tax_type} - Sin base ni impuesto")
                
            else:
                # Caso especial o datos inconsistentes
                classification = 'INDEFINIDO'
                logger.warning(f"Clasificación INDEFINIDA: {tax_type} - {percent}% - ${tax_amount} - ${taxable_amount}")
            
            return classification
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error clasificando estado fiscal: {str(e)}")
            # Por defecto, clasificar como INDEFINIDO en caso de error
            return 'INDEFINIDO'

    def get_tax_summary(self, tax_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un resumen fiscal de los datos procesados
        
        Calcula totales y estadísticas por tipo de clasificación fiscal
        y tipo de impuesto.
        
        Args:
            tax_data (List[Dict[str, Any]]): Lista de datos fiscales procesados
            
        Returns:
            Dict[str, Any]: Resumen con totales y estadísticas fiscales
            
        Ejemplo de uso:
            summary = classifier.get_tax_summary(tax_data_list)
            # summary = {
            #     'total_gravado': 5000.00,
            #     'total_exento': 2000.00,
            #     'total_excluido': 500.00,
            #     'total_iva': 600.00,
            #     'total_ice': 150.00,
            #     'count_gravado': 25,
            #     'count_exento': 10,
            #     'count_excluido': 5
            # }
            
        Estructura del resumen:
            - totales por clasificación fiscal
            - totales por tipo de impuesto
            - conteos por clasificación
            - estadísticas generales
        """
        summary = {
            'total_gravado': 0.0,
            'total_exento': 0.0,
            'total_excluido': 0.0,
            'total_iva': 0.0,
            'total_ice': 0.0,
            'total_irbpnr': 0.0,
            'total_isd': 0.0,
            'count_gravado': 0,
            'count_exento': 0,
            'count_excluido': 0,
            'total_facturas': 0,
            'total_lineas': len(tax_data)
        }
        
        try:
            # Conjunto para contar facturas únicas
            facturas_unicas = set()
            
            for row in tax_data:
                # Extraer valores de la fila
                base_imponible = float(row.get('Base', 0))
                impuesto = float(row.get('Valor', 0))
                tipo_impuesto = row.get('Detalle', '')
                id_factura = row.get('Documento', '')
                
                # Contar factura única
                if id_factura:
                    facturas_unicas.add(id_factura)
                
                # Clasificar la línea
                status = self.classify_tax_status(
                    tipo_impuesto,
                    row.get('Porcentaje', '0'),
                    str(impuesto),
                    str(base_imponible)
                )
                
                # Acumular totales por clasificación
                if status == 'GRAVADO':
                    summary['total_gravado'] += base_imponible
                    summary['count_gravado'] += 1
                elif status == 'EXENTO':
                    summary['total_exento'] += base_imponible
                    summary['count_exento'] += 1
                elif status == 'EXCLUIDO':
                    summary['total_excluido'] += base_imponible
                    summary['count_excluido'] += 1
                
                # Acumular totales por tipo de impuesto
                tipo_impuesto_upper = tipo_impuesto.upper()
                if 'IVA' in tipo_impuesto_upper:
                    summary['total_iva'] += impuesto
                elif 'ICE' in tipo_impuesto_upper:
                    summary['total_ice'] += impuesto
                elif 'IRBPNR' in tipo_impuesto_upper:
                    summary['total_irbpnr'] += impuesto
                elif 'ISD' in tipo_impuesto_upper:
                    summary['total_isd'] += impuesto
            
            # Actualizar conteo de facturas únicas
            summary['total_facturas'] = len(facturas_unicas)
            
            # Redondear todos los valores a 2 decimales
            for key in summary:
                if isinstance(summary[key], float):
                    summary[key] = round(summary[key], 2)
            
            logger.info(f"Resumen fiscal generado: {summary['total_lineas']} líneas, "
                       f"{summary['total_facturas']} facturas")
            
        except Exception as e:
            logger.error(f"Error generando resumen fiscal: {str(e)}")
            
        return summary

    def validate_tax_data(self, tax_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida la consistencia de los datos fiscales
        
        Verifica que los datos fiscales sean consistentes y cumplan
        con las reglas básicas de validación.
        
        Args:
            tax_data (List[Dict[str, Any]]): Lista de datos fiscales a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación con errores encontrados
            
        Ejemplo de uso:
            validation = classifier.validate_tax_data(tax_data_list)
            # validation = {
            #     'valid': True,
            #     'errors': [],
            #     'warnings': ['Línea 5: Porcentaje de IVA inusual (15%)']
            # }
            
        Validaciones realizadas:
            - Consistencia entre porcentaje y monto de impuesto
            - Valores numéricos válidos
            - Tipos de impuesto reconocidos
            - Porcentajes dentro de rangos esperados
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            for i, row in enumerate(tax_data):
                line_number = i + 1
                
                # Validar que los campos numéricos sean válidos
                try:
                    base_imponible = float(row.get('Base', 0))
                    impuesto = float(row.get('Valor', 0))
                    porcentaje = float(row.get('Porcentaje', 0))
                except (ValueError, TypeError):
                    validation_result['errors'].append(
                        f"Línea {line_number}: Valores numéricos inválidos"
                    )
                    validation_result['valid'] = False
                    continue
                
                # Validar consistencia entre porcentaje y monto de impuesto
                if porcentaje > 0 and base_imponible > 0:
                    expected_tax = base_imponible * (porcentaje / 100)
                    tolerance = 0.01  # Tolerancia de 1 centavo
                    
                    if abs(expected_tax - impuesto) > tolerance:
                        validation_result['warnings'].append(
                            f"Línea {line_number}: Inconsistencia entre porcentaje "
                            f"({porcentaje}%) y monto de impuesto (${impuesto:.2f})"
                        )
                
                # Validar porcentajes de IVA comunes
                tipo_impuesto = row.get('Detalle', '').upper()
                if 'IVA' in tipo_impuesto:
                    if porcentaje not in [0, 12, 14, 15]:
                        validation_result['warnings'].append(
                            f"Línea {line_number}: Porcentaje de IVA inusual ({porcentaje}%)"
                        )
                
                # Validar que no haya valores negativos
                if base_imponible < 0 or impuesto < 0 or porcentaje < 0:
                    validation_result['errors'].append(
                        f"Línea {line_number}: Valores negativos no permitidos"
                    )
                    validation_result['valid'] = False
            
            logger.info(f"Validación completada: {len(validation_result['errors'])} errores, "
                       f"{len(validation_result['warnings'])} advertencias")
            
        except Exception as e:
            logger.error(f"Error en validación de datos fiscales: {str(e)}")
            validation_result['valid'] = False
            validation_result['errors'].append(f"Error de validación: {str(e)}")
            
        return validation_result

    def get_tax_statistics(self, tax_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera estadísticas detalladas de los datos fiscales
        
        Calcula estadísticas descriptivas como promedios, máximos,
        mínimos y distribuciones por tipo de impuesto.
        
        Args:
            tax_data (List[Dict[str, Any]]): Lista de datos fiscales
            
        Returns:
            Dict[str, Any]: Estadísticas detalladas de los datos
            
        Ejemplo de uso:
            stats = classifier.get_tax_statistics(tax_data_list)
            # stats = {
            #     'promedio_base_imponible': 500.00,
            #     'max_impuesto': 1200.00,
            #     'min_impuesto': 12.00,
            #     'distribucion_porcentajes': {'12.00': 150, '0.00': 25},
            #     'tipos_impuesto_encontrados': ['IVA', 'ICE']
            # }
        """
        stats = {
            'promedio_base_imponible': 0.0,
            'max_impuesto': 0.0,
            'min_impuesto': float('inf'),
            'total_base_imponible': 0.0,
            'total_impuestos': 0.0,
            'distribucion_porcentajes': {},
            'tipos_impuesto_encontrados': set(),
            'facturas_por_cliente': {},
            'proveedores_encontrados': set()
        }
        
        try:
            for row in tax_data:
                # Extraer valores
                base_imponible = float(row.get('Base', 0))
                impuesto = float(row.get('Valor', 0))
                porcentaje = row.get('Porcentaje', '0.00')
                tipo_impuesto = row.get('Detalle', '')
                cliente = row.get('Nit', '')  # Usar NIT como identificador del cliente
                proveedor = ''  # No tenemos proveedor en la nueva estructura
                
                # Acumular totales
                stats['total_base_imponible'] += base_imponible
                stats['total_impuestos'] += impuesto
                
                # Actualizar máximos y mínimos
                if impuesto > stats['max_impuesto']:
                    stats['max_impuesto'] = impuesto
                if impuesto < stats['min_impuesto'] and impuesto > 0:
                    stats['min_impuesto'] = impuesto
                
                # Contar distribución de porcentajes
                stats['distribucion_porcentajes'][porcentaje] = \
                    stats['distribucion_porcentajes'].get(porcentaje, 0) + 1
                
                # Registrar tipos de impuesto
                if tipo_impuesto:
                    stats['tipos_impuesto_encontrados'].add(tipo_impuesto)
                
                # Contar facturas por cliente
                if cliente:
                    if cliente not in stats['facturas_por_cliente']:
                        stats['facturas_por_cliente'][cliente] = set()
                    stats['facturas_por_cliente'][cliente].add(row.get('Documento', ''))
                
                # Registrar proveedores
                if proveedor:
                    stats['proveedores_encontrados'].add(proveedor)
            
            # Calcular promedio
            if tax_data:
                stats['promedio_base_imponible'] = stats['total_base_imponible'] / len(tax_data)
            
            # Convertir sets a listas para serialización JSON
            stats['tipos_impuesto_encontrados'] = list(stats['tipos_impuesto_encontrados'])
            stats['proveedores_encontrados'] = list(stats['proveedores_encontrados'])
            
            # Convertir facturas por cliente a conteos
            stats['facturas_por_cliente'] = {
                cliente: len(facturas) 
                for cliente, facturas in stats['facturas_por_cliente'].items()
            }
            
            # Redondear valores numéricos
            for key in ['promedio_base_imponible', 'total_base_imponible', 'total_impuestos']:
                if key in stats:
                    stats[key] = round(stats[key], 2)
            
            # Manejar caso donde no hay impuestos
            if stats['min_impuesto'] == float('inf'):
                stats['min_impuesto'] = 0.0
            
            logger.info(f"Estadísticas generadas: {len(tax_data)} líneas procesadas")
            
        except Exception as e:
            logger.error(f"Error generando estadísticas: {str(e)}")
            
        return stats

    def validate_iva_rules(self, percent: str, tax_amount: str, taxable_amount: str, tax_scheme_id: str = None) -> Dict[str, Any]:
        """
        Valida reglas específicas para IVA según normativa ecuatoriana
        
        Aplica validaciones específicas para IVA considerando:
        - Porcentajes permitidos por ley
        - Consistencia entre porcentaje y monto
        - Reglas de exención y exclusión
        - Códigos de impuesto válidos
        
        Args:
            percent (str): Porcentaje del IVA
            tax_amount (str): Monto del IVA
            taxable_amount (str): Base imponible
            tax_scheme_id (str): Código del esquema de impuesto (opcional)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'classification': str,
                'recommendations': List[str]
            }
            
        Ejemplo de uso:
            result = classifier.validate_iva_rules('12.00', '120.00', '1000.00')
            # result = {
            #     'valid': True,
            #     'errors': [],
            #     'warnings': [],
            #     'classification': 'GRAVADO',
            #     'recommendations': []
            # }
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'classification': 'INDEFINIDO',
            'recommendations': []
        }
        
        try:
            # Convertir valores a float
            percent_float = float(percent) if percent else 0.0
            tax_amount_float = float(tax_amount) if tax_amount else 0.0
            taxable_amount_float = float(taxable_amount) if taxable_amount else 0.0
            
            # Validar datos de entrada
            if percent_float < 0 or tax_amount_float < 0 or taxable_amount_float < 0:
                validation_result['errors'].append("Valores negativos no permitidos en IVA")
                validation_result['valid'] = False
                return validation_result
            
            # Validar porcentajes de IVA permitidos por ley ecuatoriana
            valid_percentages = [0.0, 12.0, 14.0, 15.0]
            if percent_float not in valid_percentages and percent_float > 0:
                validation_result['warnings'].append(f"Porcentaje de IVA inusual: {percent_float}%")
                validation_result['recommendations'].append("Verificar si el porcentaje es correcto según normativa vigente")
            
            # Validar consistencia entre porcentaje y monto
            if percent_float > 0 and taxable_amount_float > 0:
                expected_tax = taxable_amount_float * (percent_float / 100)
                tolerance = 0.01  # Tolerancia de 1 centavo
                
                if abs(expected_tax - tax_amount_float) > tolerance:
                    validation_result['warnings'].append(
                        f"Inconsistencia entre porcentaje ({percent_float}%) y monto de IVA (${tax_amount_float:.2f})"
                    )
                    validation_result['recommendations'].append("Verificar cálculo del IVA")
            
            # Validar reglas específicas de IVA con mejor discriminación
            if tax_amount_float > 0:
                # IVA GRAVADO
                validation_result['classification'] = 'GRAVADO'
                
                if percent_float == 0.0 and tax_amount_float > 0:
                    validation_result['warnings'].append("IVA con porcentaje 0% pero con monto aplicado")
                    validation_result['recommendations'].append("Verificar si debe ser IVA exento o gravado - posible inconsistencia")
                elif percent_float not in [12.0, 14.0, 15.0]:
                    validation_result['warnings'].append(f"IVA con porcentaje no estándar: {percent_float}%")
                    validation_result['recommendations'].append("Verificar si el porcentaje es correcto según normativa vigente")
                    
            elif taxable_amount_float > 0:
                # IVA EXENTO - Validaciones específicas para exentos
                validation_result['classification'] = 'EXENTO'
                
                if percent_float == 0.0:
                    validation_result['recommendations'].append("Verificar que el producto esté en la lista de exenciones de primera necesidad")
                elif percent_float == 12.0:
                    validation_result['warnings'].append("IVA con porcentaje 12% pero sin monto aplicado")
                    validation_result['recommendations'].append("Verificar si el producto tiene exención específica por normativa")
                elif percent_float == 14.0:
                    validation_result['warnings'].append("IVA con porcentaje 14% pero sin monto aplicado")
                    validation_result['recommendations'].append("Verificar si el producto tiene exención especial por normativa")
                elif percent_float > 0:
                    validation_result['warnings'].append(f"IVA con porcentaje {percent_float}% pero sin monto aplicado")
                    validation_result['recommendations'].append("Verificar si el producto está correctamente exento por normativa")
                    
            elif taxable_amount_float == 0 and tax_amount_float == 0:
                # IVA EXCLUIDO - Validaciones específicas para excluidos
                validation_result['classification'] = 'EXCLUIDO'
                
                if percent_float == 0.0:
                    validation_result['recommendations'].append("Confirmar que se trate de servicios financieros o similares excluidos")
                elif percent_float == 12.0:
                    validation_result['recommendations'].append("Verificar si se trata de exportaciones o servicios excluidos")
                elif percent_float > 0:
                    validation_result['warnings'].append(f"IVA con porcentaje {percent_float}% pero sin base imponible")
                    validation_result['recommendations'].append("Verificar si el producto/servicio está correctamente excluido del IVA")
                else:
                    validation_result['recommendations'].append("Confirmar que el producto/servicio esté fuera del alcance del IVA")
                    
            else:
                # Caso especial
                validation_result['classification'] = 'INDEFINIDO'
                validation_result['errors'].append("No se puede determinar la clasificación del IVA")
                validation_result['valid'] = False
            
            # Validar códigos de impuesto si se proporcionan
            if tax_scheme_id:
                valid_codes = ['2', '7', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
                if tax_scheme_id not in valid_codes:
                    validation_result['warnings'].append(f"Código de IVA no reconocido: {tax_scheme_id}")
                    validation_result['recommendations'].append("Verificar código de impuesto según normativa")
            
            # Recomendaciones generales
            if validation_result['classification'] == 'GRAVADO':
                validation_result['recommendations'].append("Asegurar que el IVA se declare correctamente en la contabilidad")
            elif validation_result['classification'] == 'EXENTO':
                validation_result['recommendations'].append("Verificar que el producto esté en la lista de exenciones")
            elif validation_result['classification'] == 'EXCLUIDO':
                validation_result['recommendations'].append("Confirmar que el producto esté fuera del alcance del IVA")
            
            logger.info(f"Validación de IVA completada: {validation_result['classification']}")
            
        except (ValueError, TypeError) as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Error en validación de IVA: {str(e)}")
            logger.error(f"Error validando reglas de IVA: {str(e)}")
            
        return validation_result
