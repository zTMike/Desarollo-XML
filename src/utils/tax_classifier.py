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

    def get_tax_description(self, tax_scheme_id: str, tax_scheme_name: str, percent: str) -> str:
        """
        Obtiene la descripción completa de un impuesto
        
        Combina el código del impuesto, nombre y porcentaje para crear
        una descripción legible y completa.
        
        Args:
            tax_scheme_id (str): Código del esquema de impuesto
            tax_scheme_name (str): Nombre del esquema de impuesto
            percent (str): Porcentaje del impuesto
            
        Returns:
            str: Descripción completa del impuesto
            
        Ejemplo de uso:
            description = classifier.get_tax_description('2', 'IVA', '12.00')
            # description = 'IVA 12.00%'
            
        Ejemplo de descripciones generadas:
            - 'IVA 12.00%' para IVA estándar
            - 'ICE 300.00%' para ICE
            - 'IRBPNR 1.00%' para IRBPNR
            - 'ISD 5.00%' para ISD
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
            
            # Construir descripción completa
            description = f"{base_description} {formatted_percent}%"
            
            logger.debug(f"Descripción generada: {description}")
            return description
            
        except Exception as e:
            logger.error(f"Error generando descripción de impuesto: {str(e)}")
            return f"{tax_scheme_name} {percent}%"

    def classify_tax_status(self, tax_type: str, percent: str, tax_amount: str, taxable_amount: str) -> str:
        """
        Clasifica el estado fiscal de una línea de factura
        
        Determina si una línea es GRAVADO, EXENTO o EXCLUIDO basándose
        en el tipo de impuesto, porcentaje y montos.
        
        Args:
            tax_type (str): Tipo de impuesto (IVA, ICE, etc.)
            percent (str): Porcentaje del impuesto
            tax_amount (str): Monto del impuesto
            taxable_amount (str): Base imponible
            
        Returns:
            str: Clasificación fiscal ('GRAVADO', 'EXENTO', 'EXCLUIDO')
            
        Ejemplo de uso:
            status = classifier.classify_tax_status('IVA', '12.00', '120.00', '1000.00')
            # status = 'GRAVADO'
            
            status = classifier.classify_tax_status('IVA', '0.00', '0.00', '1000.00')
            # status = 'EXENTO'
            
        Lógica de clasificación:
            - GRAVADO: Cuando hay impuesto aplicado (porcentaje > 0 y monto > 0)
            - EXENTO: Cuando no hay impuesto pero hay base imponible
            - EXCLUIDO: Cuando no hay impuesto ni base imponible
        """
        try:
            # Convertir valores a float para comparaciones
            percent_float = float(percent) if percent else 0.0
            tax_amount_float = float(tax_amount) if tax_amount else 0.0
            taxable_amount_float = float(taxable_amount) if taxable_amount else 0.0
            
            # Obtener reglas de clasificación para el tipo de impuesto
            rules = self.tax_classifications.get(tax_type, {})
            gravado_threshold = rules.get('gravado_threshold', 0.01)
            
            # Clasificar según las reglas
            if percent_float > gravado_threshold and tax_amount_float > 0:
                # Hay impuesto aplicado
                classification = 'GRAVADO'
                logger.debug(f"Línea clasificada como GRAVADO: {tax_type} {percent_float}%")
                
            elif taxable_amount_float > 0:
                # Hay base imponible pero no hay impuesto
                classification = 'EXENTO'
                logger.debug(f"Línea clasificada como EXENTO: {tax_type} sin impuesto")
                
            else:
                # No hay base imponible ni impuesto
                classification = 'EXCLUIDO'
                logger.debug(f"Línea clasificada como EXCLUIDO: {tax_type} sin base")
            
            return classification
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error clasificando estado fiscal: {str(e)}")
            # Por defecto, clasificar como EXCLUIDO en caso de error
            return 'EXCLUIDO'

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
