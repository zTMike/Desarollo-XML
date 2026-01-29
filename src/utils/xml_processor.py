"""
Procesador de Archivos XML - Módulo de Utilidades
================================================

Este módulo contiene toda la lógica para procesar archivos XML de facturas
electrónicas, incluyendo extracción de datos, parsing de estructuras UBL
y manejo de archivos ZIP.

Funcionalidades principales:
- Extracción de XMLs desde archivos ZIP
- Parsing de facturas UBL (Universal Business Language)
- Detección automática de tipos de documento
- Extracción de información básica de facturas
- Extracción detallada de información fiscal
- Manejo de XMLs anidados en CDATA

Clases principales:
- XMLProcessor: Clase principal para procesamiento de XMLs

Ejemplo de uso:
    processor = XMLProcessor()
    rows = processor.process_zip_file(zip_file)
    # rows contiene lista de diccionarios con datos extraídos

Autor: Sistema de Procesamiento XML
Versión: 2.0.0
"""

import zipfile
from lxml import etree
import logging
from typing import List, Dict, Any, Optional
import re
from io import BytesIO

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XMLProcessor:
    """
    Procesador principal para archivos XML de facturas electrónicas
    
    Esta clase encapsula toda la lógica necesaria para:
    - Extraer archivos XML desde archivos ZIP
    - Parsear estructuras UBL (Universal Business Language)
    - Extraer información fiscal y comercial
    - Manejar diferentes formatos de facturación
    
    Atributos:
        namespaces (dict): Mapeo de namespaces XML utilizados en facturas UBL
        document_types (dict): Mapeo de códigos de documento a descripciones
    
    Ejemplo de uso:
        processor = XMLProcessor()
        
        # Procesar archivo ZIP
        with open('facturas.zip', 'rb') as f:
            rows = processor.process_zip_file(f)
        
        # Procesar XML directo
        xml_content = b'<?xml version="1.0"?><Invoice>...</Invoice>'
        invoice_xml = processor.extract_invoice_from_xml(xml_content)
    """
    
    def __init__(self):
        """
        Inicializa el procesador XML con configuraciones necesarias
        
        Configura los namespaces XML utilizados en facturas UBL y los
        tipos de documento soportados por el sistema.
        """
        # Namespaces XML utilizados en facturas UBL
        self.namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ccts': 'urn:un:unece:uncefact:documentation:2',
            'ds': 'http://www.w3.org/2000/09/xmldsig#',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
            'udt': 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Mapeo de tipos de documento a descripciones legibles
        self.document_types = {
            '01': 'FACTURA',
            '02': 'NOTA DE CRÉDITO',
            '03': 'NOTA DE DÉBITO',
            '04': 'GUÍA DE REMISIÓN',
            '05': 'COMPROBANTE DE RETENCIÓN',
            '06': 'FACTURA DE EXPORTACIÓN',
            '07': 'FACTURA DE CONTRIBUYENTE ESPECIAL',
            '08': 'FACTURA DE VENTA A CONSUMIDOR FINAL',
            '09': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA',
            '10': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA',
            '11': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA - MICROEMPRESAS',
            '12': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA - MICROEMPRESAS',
            '13': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA - REGIMEN RIMPE',
            '14': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA - REGIMEN RIMPE',
            '15': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA - NEGOCIO POPULAR',
            '16': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA - NEGOCIO POPULAR',
            '17': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA - ARTESANOS',
            '18': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA - ARTESANOS',
            '19': 'FACTURA DE VENTA A CONSUMIDOR FINAL - ELECTRÓNICA - RÉGIMEN FISCAL PRIVATIVO',
            '20': 'FACTURA DE VENTA A CONSUMIDOR FINAL - IMPRESA - RÉGIMEN FISCAL PRIVATIVO'
        }
        
        logger.info("XMLProcessor inicializado con namespaces y tipos de documento configurados")

    def extract_xml_from_zip(self, zip_file) -> List[Dict[str, Any]]:
        """
        Extrae archivos XML desde un archivo ZIP
        
        Lee un archivo ZIP y extrae todos los archivos XML contenidos,
        procesando cada uno para obtener datos de facturas.
        
        Args:
            zip_file: Archivo ZIP (FileStorage de Flask o similar)
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con datos extraídos
                                 de cada factura encontrada en el ZIP
                                 
        Ejemplo de uso:
            with open('facturas.zip', 'rb') as f:
                rows = processor.extract_xml_from_zip(f)
                # rows = [
                #     {
                #         'ID_Factura': '001-001-000000001',
                #         'Fecha': '2024-01-15',
                #         'Cliente': 'EMPRESA ABC S.A.',
                #         'Proveedor': 'PROVEEDOR XYZ LTDA.',
                #         'Tipo': 'GRAVADO',
                #         'Porcentaje': '12.00',
                #         'Base_Imponible': '100.00',
                #         'Impuesto': '12.00',
                #         'Total': '112.00'
                #     },
                #     ...
                # ]
        
        Raises:
            zipfile.BadZipFile: Si el archivo no es un ZIP válido
            etree.XMLSyntaxError: Si algún XML dentro del ZIP es inválido
        """
        all_rows = []
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Obtener lista de archivos en el ZIP
                file_list = zip_ref.namelist()
                logger.info(f"Archivo ZIP contiene {len(file_list)} archivos")
                
                # Procesar cada archivo en el ZIP
                for filename in file_list:
                    # Solo procesar archivos XML
                    if filename.lower().endswith('.xml'):
                        try:
                            # Leer contenido del archivo XML
                            xml_content = zip_ref.read(filename)
                            logger.info(f"Procesando archivo XML: {filename}")
                            
                            # Extraer factura del XML
                            invoice_xml = self.extract_invoice_from_xml(xml_content)
                            
                            if invoice_xml:
                                # Parsear la factura para obtener estructura de datos
                                zip_filename = getattr(zip_file, 'filename', 'archivo_desconocido.zip')
                                rows = self.parse_invoice_for_structure(
                                    invoice_xml, filename, zip_filename
                                )
                                all_rows.extend(rows)
                                logger.info(f"Extraídas {len(rows)} líneas de {filename}")
                            else:
                                logger.warning(f"No se encontró factura válida en {filename}")
                                
                        except Exception as e:
                            logger.error(f"Error procesando {filename}: {str(e)}")
                            continue
                            
        except zipfile.BadZipFile:
            logger.error("El archivo no es un ZIP válido")
            raise
        except Exception as e:
            logger.error(f"Error general procesando ZIP: {str(e)}")
            raise
            
        logger.info(f"Total de líneas extraídas: {len(all_rows)}")
        return all_rows

    def extract_invoice_from_xml(self, xml_content: bytes) -> Optional[str]:
        """
        Extrae la factura XML desde el contenido del archivo
        
        Analiza el contenido XML para encontrar y extraer la factura,
        manejando casos donde el XML puede estar anidado en CDATA
        o tener estructuras complejas.
        
        Args:
            xml_content (bytes): Contenido del archivo XML en bytes
            
        Returns:
            Optional[str]: XML de la factura como string, o None si no se encuentra
            
        Ejemplo de uso:
            xml_content = b'<?xml version="1.0"?><Invoice>...</Invoice>'
            invoice_xml = processor.extract_invoice_from_xml(xml_content)
            if invoice_xml:
                # Procesar la factura
                pass
                
        Ejemplo de XML de entrada:
            <?xml version="1.0" encoding="UTF-8"?>
            <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
                <cbc:ID>001-001-000000001</cbc:ID>
                <cbc:IssueDate>2024-01-15</cbc:IssueDate>
                ...
            </Invoice>
        """
        try:
            # Decodificar contenido XML
            xml_string = xml_content.decode('utf-8', errors='ignore')
            
            # Buscar patrones de CDATA que puedan contener XML anidado
            cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
            cdata_matches = re.findall(cdata_pattern, xml_string, re.DOTALL)
            
            if cdata_matches:
                # Si hay CDATA, buscar XML válido dentro
                for cdata_content in cdata_matches:
                    if '<Invoice' in cdata_content or '<Factura' in cdata_content:
                        logger.info("Encontrada factura en CDATA")
                        return cdata_content.strip()
            
            # Si no hay CDATA o no se encontró factura, buscar directamente
            if '<Invoice' in xml_string or '<Factura' in xml_string:
                logger.info("Encontrada factura en XML principal")
                return xml_string
                
            logger.warning("No se encontró factura válida en el XML")
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo factura del XML: {str(e)}")
            return None

    def detect_document_type(self, root: etree._Element) -> str:
        """
        Detecta el tipo de documento basado en el elemento raíz
        
        Analiza el elemento raíz del XML para determinar si es una
        factura, nota de crédito, nota de débito, etc.
        
        Args:
            root (etree._Element): Elemento raíz del XML parseado
            
        Returns:
            str: Descripción del tipo de documento
            
        Ejemplo de uso:
            root = etree.fromstring(xml_content)
            doc_type = processor.detect_document_type(root)
            # doc_type = "FACTURA"
            
        Ejemplo de tipos de documento:
            - "FACTURA" para elementos <Invoice>
            - "NOTA DE CRÉDITO" para elementos <CreditNote>
            - "NOTA DE DÉBITO" para elementos <DebitNote>
        """
        tag = root.tag
        
        # Mapear tags XML a tipos de documento
        type_mapping = {
            'Invoice': 'FACTURA',
            'Factura': 'FACTURA',
            'CreditNote': 'NOTA DE CRÉDITO',
            'NotaCredito': 'NOTA DE CRÉDITO',
            'DebitNote': 'NOTA DE DÉBITO',
            'NotaDebito': 'NOTA DE DÉBITO',
            'DespatchAdvice': 'GUÍA DE REMISIÓN',
            'GuiaRemision': 'GUÍA DE REMISIÓN'
        }
        
        # Extraer nombre del tag sin namespace
        tag_name = tag.split('}')[-1] if '}' in tag else tag
        
        return type_mapping.get(tag_name, 'DOCUMENTO DESCONOCIDO')

    def extract_basic_info(self, root: etree._Element) -> Dict[str, str]:
        """
        Extrae información básica de la factura
        
        Obtiene datos fundamentales como ID, fecha, cliente, proveedor,
        moneda y totales de la factura.
        
        Args:
            root (etree._Element): Elemento raíz del XML parseado
            
        Returns:
            Dict[str, str]: Diccionario con información básica de la factura
            
        Ejemplo de uso:
            root = etree.fromstring(xml_content)
            basic_info = processor.extract_basic_info(root)
            # basic_info = {
            #     'ID_Factura': '001-001-000000001',
            #     'Fecha': '2024-01-15',
            #     'Cliente': 'EMPRESA ABC S.A.',
            #     'Proveedor': 'PROVEEDOR XYZ LTDA.',
            #     'Moneda': 'USD',
            #     'Total_Sin_Impuestos': '1000.00',
            #     'Total_Impuestos': '120.00',
            #     'Total': '1120.00'
            # }
        """
        basic_info = {
            'ID_Factura': '',
            'Fecha': '',
            'Cliente': '',
            'Proveedor': '',
            'Moneda': '',
            'NIT_Cliente': '',
            'NIT_Proveedor': '',
            'Fecha_Vencimiento': '',
            'ID_Documento_Electronico': '',
            'Total_Sin_Impuestos': '0.00',
            'Total_Impuestos': '0.00',
            'Total': '0.00'
        }
        
        try:
            # Extraer ID de la factura
            id_elem = root.find('.//cbc:ID', namespaces=self.namespaces)
            if id_elem is not None:
                basic_info['ID_Factura'] = id_elem.text or ''
            
            # Extraer fecha de emisión
            date_elem = root.find('.//cbc:IssueDate', namespaces=self.namespaces)
            if date_elem is not None:
                basic_info['Fecha'] = date_elem.text or ''
            
            # Extraer información del cliente (AccountingCustomerParty)
            customer_party = root.find('.//cac:AccountingCustomerParty', namespaces=self.namespaces)
            if customer_party is not None:
                customer_name = customer_party.find('.//cac:PartyName//cbc:Name', namespaces=self.namespaces)
                if customer_name is not None:
                    basic_info['Cliente'] = customer_name.text or ''
                
                # Extraer NIT del cliente
                customer_tax_id = customer_party.find('.//cac:PartyTaxScheme//cbc:CompanyID', namespaces=self.namespaces)
                if customer_tax_id is not None:
                    basic_info['NIT_Cliente'] = customer_tax_id.text or ''
            
            # Extraer información del proveedor (AccountingSupplierParty)
            supplier_party = root.find('.//cac:AccountingSupplierParty', namespaces=self.namespaces)
            if supplier_party is not None:
                supplier_name = supplier_party.find('.//cac:PartyName//cbc:Name', namespaces=self.namespaces)
                if supplier_name is not None:
                    basic_info['Proveedor'] = supplier_name.text or ''
                
                # Extraer NIT del proveedor
                supplier_tax_id = supplier_party.find('.//cac:PartyTaxScheme//cbc:CompanyID', namespaces=self.namespaces)
                if supplier_tax_id is not None:
                    basic_info['NIT_Proveedor'] = supplier_tax_id.text or ''
            
            # Extraer moneda
            currency_elem = root.find('.//cbc:DocumentCurrencyCode', namespaces=self.namespaces)
            if currency_elem is not None:
                basic_info['Moneda'] = currency_elem.text or ''
            
            # Extraer totales
            tax_exclusive_amount = root.find('.//cbc:TaxExclusiveAmount', namespaces=self.namespaces)
            if tax_exclusive_amount is not None:
                basic_info['Total_Sin_Impuestos'] = tax_exclusive_amount.text or '0.00'
            
            tax_inclusive_amount = root.find('.//cbc:TaxInclusiveAmount', namespaces=self.namespaces)
            if tax_inclusive_amount is not None:
                basic_info['Total'] = tax_inclusive_amount.text or '0.00'
            
            # Extraer fecha de vencimiento
            due_date = root.find('.//cbc:DueDate', namespaces=self.namespaces)
            if due_date is not None:
                basic_info['Fecha_Vencimiento'] = due_date.text or ''
            
            # Extraer ID del documento electrónico
            electronic_id = root.find('.//cbc:UUID', namespaces=self.namespaces)
            if electronic_id is not None:
                basic_info['ID_Documento_Electronico'] = electronic_id.text or ''
            
            # Calcular total de impuestos si no está disponible
            if basic_info['Total'] != '0.00' and basic_info['Total_Sin_Impuestos'] != '0.00':
                try:
                    total = float(basic_info['Total'])
                    sin_impuestos = float(basic_info['Total_Sin_Impuestos'])
                    basic_info['Total_Impuestos'] = f"{total - sin_impuestos:.2f}"
                except ValueError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error extrayendo información básica: {str(e)}")
            
        return basic_info

    def extract_tax_information(self, root: etree._Element) -> List[Dict[str, Any]]:
        """
        Extrae información detallada de impuestos de la factura
        
        Analiza los impuestos a nivel de documento, incluyendo TaxTotal y TaxSubtotal
        para capturar todos los tipos de impuesto sin duplicación.
        
        Args:
            root (etree._Element): Elemento raíz del XML parseado
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con información fiscal
                                 de cada impuesto encontrado
                                 
        Ejemplo de uso:
            root = etree.fromstring(xml_content)
            tax_info = processor.extract_tax_information(root)
            # tax_info = [
            #     {
            #         'LineNumber': 'DOC',
            #         'ItemName': 'Impuesto a nivel documento',
            #         'TaxSchemeID': '01',
            #         'TaxSchemeName': 'IVA',
            #         'Percent': '19.00',
            #         'TaxAmount': '180125.00',
            #         'TaxableAmount': '948026.00'
            #     },
            #     ...
            # ]
        """
        tax_information = []
        
        try:
            # Buscar SOLO los TaxTotal a nivel de documento (no dentro de InvoiceLine)
            document_tax_totals = root.findall('.//cac:TaxTotal', namespaces=self.namespaces)
            
            for tax_total in document_tax_totals:
                # Verificar que NO esté dentro de una línea de factura
                parent = tax_total.getparent()
                if parent is not None and 'InvoiceLine' in parent.tag:
                    continue  # Saltar impuestos de línea individual
                
                # Buscar TaxSubtotal dentro de este TaxTotal
                tax_subtotals = tax_total.findall('.//cac:TaxSubtotal', namespaces=self.namespaces)
                
                if tax_subtotals:
                    # Si hay TaxSubtotal, procesar cada uno
                    for tax_subtotal in tax_subtotals:
                        tax_data = {}
                        
                        # Extraer esquema de impuesto
                        tax_scheme = tax_subtotal.find('.//cac:TaxScheme', namespaces=self.namespaces)
                        if tax_scheme is not None:
                            scheme_id = tax_scheme.find('.//cbc:ID', namespaces=self.namespaces)
                            scheme_name = tax_scheme.find('.//cbc:Name', namespaces=self.namespaces)
                            
                            if scheme_id is not None:
                                tax_data['TaxSchemeID'] = scheme_id.text or ''
                            if scheme_name is not None:
                                tax_data['TaxSchemeName'] = scheme_name.text or ''
                        
                        # Extraer porcentaje de impuesto
                        percent = tax_subtotal.find('.//cbc:Percent', namespaces=self.namespaces)
                        if percent is not None:
                            tax_data['Percent'] = percent.text or '0.00'
                        else:
                            tax_data['Percent'] = '0.00'
                        
                        # Extraer monto de impuesto
                        tax_amount = tax_subtotal.find('.//cbc:TaxAmount', namespaces=self.namespaces)
                        if tax_amount is not None:
                            tax_data['TaxAmount'] = tax_amount.text or '0.00'
                        else:
                            tax_data['TaxAmount'] = '0.00'
                        
                        # Extraer base imponible
                        taxable_amount = tax_subtotal.find('.//cbc:TaxableAmount', namespaces=self.namespaces)
                        if taxable_amount is not None:
                            tax_data['TaxableAmount'] = taxable_amount.text or '0.00'
                        else:
                            tax_data['TaxableAmount'] = '0.00'
                        
                        # Agregar datos básicos para impuestos de documento
                        tax_data['LineNumber'] = 'DOC'
                        tax_data['ItemName'] = 'Impuesto a nivel documento'
                        tax_data['Quantity'] = '1'
                        tax_data['UnitPrice'] = '0.00'
                        
                        # Para impuestos específicos como IBUA/ICL, no hay base imponible
                        if scheme_name in ['IBUA', 'ICL', 'ADV']:
                            tax_data['LineExtensionAmount'] = '0.00'
                        else:
                            tax_data['LineExtensionAmount'] = tax_data.get('TaxableAmount', '0.00')
                        
                        tax_information.append(tax_data)
                else:
                    # Si no hay TaxSubtotal, procesar el TaxTotal directamente
                    tax_data = {}
                    
                    # Extraer esquema de impuesto
                    tax_scheme = tax_total.find('.//cac:TaxScheme', namespaces=self.namespaces)
                    if tax_scheme is not None:
                        scheme_id = tax_scheme.find('.//cbc:ID', namespaces=self.namespaces)
                        scheme_name = tax_scheme.find('.//cbc:Name', namespaces=self.namespaces)
                        
                        if scheme_id is not None:
                            tax_data['TaxSchemeID'] = scheme_id.text or ''
                        if scheme_name is not None:
                            tax_data['TaxSchemeName'] = scheme_name.text or ''
                    
                    # Extraer porcentaje de impuesto
                    percent = tax_total.find('.//cbc:Percent', namespaces=self.namespaces)
                    if percent is not None:
                        tax_data['Percent'] = percent.text or '0.00'
                    else:
                        tax_data['Percent'] = '0.00'
                    
                    # Extraer monto de impuesto
                    tax_amount = tax_total.find('.//cbc:TaxAmount', namespaces=self.namespaces)
                    if tax_amount is not None:
                        tax_data['TaxAmount'] = tax_amount.text or '0.00'
                    else:
                        tax_data['TaxAmount'] = '0.00'
                    
                    # Extraer base imponible
                    taxable_amount = tax_total.find('.//cbc:TaxableAmount', namespaces=self.namespaces)
                    if taxable_amount is not None:
                        tax_data['TaxableAmount'] = taxable_amount.text or '0.00'
                    else:
                        tax_data['TaxableAmount'] = '0.00'
                    
                    # Agregar datos básicos para impuestos de documento
                    tax_data['LineNumber'] = 'DOC'
                    tax_data['ItemName'] = 'Impuesto a nivel documento'
                    tax_data['Quantity'] = '1'
                    tax_data['UnitPrice'] = '0.00'
                    
                    # Para impuestos específicos como IBUA/ICL, no hay base imponible
                    if scheme_name in ['IBUA', 'ICL', 'ADV']:
                        tax_data['LineExtensionAmount'] = '0.00'
                    else:
                        tax_data['LineExtensionAmount'] = tax_data.get('TaxableAmount', '0.00')
                    
                    tax_information.append(tax_data)
                    
        except Exception as e:
            logger.error(f"Error extrayendo impuestos: {str(e)}")
            
        return tax_information

    def parse_invoice_for_structure(self, invoice_xml: str, filename: str, zip_name: str) -> List[Dict[str, Any]]:
        """
        Parsea una factura XML para obtener estructura de datos completa
        
        Combina información básica y fiscal para crear una estructura
        de datos completa para cada línea de la factura.
        
        Args:
            invoice_xml (str): XML de la factura como string
            filename (str): Nombre del archivo XML
            zip_name (str): Nombre del archivo ZIP contenedor
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con datos completos
                                 de cada línea de la factura
                                 
        Ejemplo de uso:
            invoice_xml = '<Invoice>...</Invoice>'
            rows = processor.parse_invoice_for_structure(
                invoice_xml, 'factura.xml', 'archivo.zip'
            )
            # rows = [
            #     {
            #         'ID_Factura': '001-001-000000001',
            #         'Fecha': '2024-01-15',
            #         'Cliente': 'EMPRESA ABC S.A.',
            #         'Proveedor': 'PROVEEDOR XYZ LTDA.',
            #         'Moneda': 'USD',
            #         'Tipo': 'GRAVADO',
            #         'Porcentaje': '12.00',
            #         'Base_Imponible': '1000.00',
            #         'Impuesto': '120.00',
            #         'Total': '1120.00',
            #         'Archivo_Origen': 'factura.xml',
            #         'ZIP_Origen': 'archivo.zip'
            #     },
            #     ...
            # ]
        """
        rows = []
        
        try:
            # Parsear XML
            root = etree.fromstring(invoice_xml.encode('utf-8'))
            
            # Detectar tipo de documento
            document_type = self.detect_document_type(root)
            
            # Extraer información básica
            basic_info = self.extract_basic_info(root)
            
            # Extraer información fiscal
            tax_info = self.extract_tax_information(root)
            
            # Separar impuestos por tipo para cada factura
            separated_taxes = self.separate_taxes_by_type(tax_info)
            
            # Crear filas separadas según la estructura requerida
            for tax_separated in separated_taxes:
                # Clasificar el tipo de impuesto
                tax_type = self.classify_tax_type(tax_separated)
                
                # Crear descripción del impuesto separado
                tax_description = self.create_separated_tax_description(tax_separated)
                
                # Extraer solo los últimos 5 dígitos del ID de factura
                invoice_id = basic_info['ID_Factura']
                last_five_digits = invoice_id[-5:] if len(invoice_id) >= 5 else invoice_id
                
                row = {
                    'Cuenta': document_type,
                    'Comprobante': '',  # Vacío según la imagen
                    'Fecha': basic_info['Fecha'],
                    'Documento': last_five_digits,
                    'Documento_Ref': zip_name,
                    'Nit': basic_info['NIT_Proveedor'],
                    'Detalle': tax_description,
                    'Tipo': tax_type,
                    'Estado_Fiscal': tax_type,  # Nueva columna con clasificación fiscal
                    'Valor': tax_separated.get('consolidated_tax_amount', '0.00'),
                    'Base': tax_separated.get('consolidated_base_amount', '0.00'),
                    'Centro_Costo': '',  # Vacío según la imagen
                    'Trans_Ext': '',  # Vacío según la imagen
                    'Plazo': basic_info['Fecha_Vencimiento'],
                    'Docto_Electronico': basic_info['ID_Documento_Electronico']
                }
                
                rows.append(row)
                
        except Exception as e:
            logger.error(f"Error parseando factura {filename}: {str(e)}")
            
        return rows

    def classify_tax_type(self, tax_line: Dict[str, Any]) -> str:
        """
        Clasifica el tipo de impuesto según las reglas fiscales ecuatorianas mejoradas
        
        Args:
            tax_line (Dict[str, Any]): Información de la línea de impuesto
            
        Returns:
            str: Clasificación del impuesto (GRAVADO, EXENTO, EXCLUIDO, INDEFINIDO)
            
        Reglas de clasificación fiscal ecuatoriana:
        - GRAVADO: Tiene monto de impuesto > 0 (independientemente del porcentaje)
        - EXENTO: Tiene base imponible > 0 pero monto de impuesto = 0
        - EXCLUIDO: Base imponible = 0 y monto de impuesto = 0
        - INDEFINIDO: Datos inconsistentes o faltantes
        """
        try:
            # Obtener valores del impuesto consolidado
            percent = tax_line.get('Percent', '0')
            tax_amount = float(tax_line.get('consolidated_tax_amount', '0'))
            base_amount = float(tax_line.get('consolidated_base_amount', '0'))
            scheme_name = tax_line.get('TaxSchemeName', '')
            
            # Validar datos de entrada
            if tax_amount < 0 or base_amount < 0:
                logger.warning(f"Datos negativos en clasificación: {scheme_name} - {percent}% - ${tax_amount} - ${base_amount}")
                return 'INDEFINIDO'
            
            # Reglas de clasificación fiscal ecuatoriana mejoradas
            if tax_amount > 0:
                # Hay monto de impuesto aplicado - GRAVADO
                return 'GRAVADO'
            elif base_amount > 0:
                # Hay base imponible pero no hay impuesto - EXENTO
                return 'EXENTO'
            elif base_amount == 0 and tax_amount == 0:
                # No hay base imponible ni impuesto - EXCLUIDO
                return 'EXCLUIDO'
            else:
                # Caso especial o datos inconsistentes
                return 'INDEFINIDO'
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error clasificando tipo de impuesto: {str(e)}")
            return 'INDEFINIDO'

    def create_tax_description(self, tax_line: Dict[str, Any]) -> str:
        """
        Crea la descripción del impuesto según el formato requerido
        
        Args:
            tax_line (Dict[str, Any]): Información de la línea de impuesto
            
        Returns:
            str: Descripción formateada del impuesto
        """
        try:
            scheme_name = tax_line.get('TaxSchemeName', '')
            percent = tax_line.get('Percent', '0.00')
            
            if scheme_name and percent != '0.00':
                return f"{scheme_name} - Impuesto al Valor Agregado ({percent}%)"
            elif scheme_name:
                return f"{scheme_name} - Impuesto al Valor Agregado (0.00%)"
            else:
                return "Sin Impuestos"
                
        except Exception:
            return "Sin Impuestos"

    def separate_taxes_by_type(self, tax_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Separa los impuestos por tipo y porcentaje para cada factura
        
        Crea líneas individuales para cada tipo de impuesto y porcentaje específico,
        EXCEPTO para ADV que se consolida por tipo únicamente.
        
        Args:
            tax_info (List[Dict[str, Any]]): Lista de información fiscal de las líneas
            
        Returns:
            List[Dict[str, Any]]: Lista de impuestos separados por tipo y porcentaje
            
        Ejemplo de uso:
            separated = processor.separate_taxes_by_type(tax_info)
            # separated = [
            #     {
            #         'TaxSchemeName': 'IVA',
            #         'Percent': '5.00',
            #         'consolidated_tax_amount': '243560.00',
            #         'consolidated_base_amount': '4871199.00',
            #         'line_count': 16
            #     },
            #     {
            #         'TaxSchemeName': 'ADV',
            #         'Percent': 'MIXTO',
            #         'consolidated_tax_amount': '1430343.00',
            #         'consolidated_base_amount': '5873814.00',
            #         'line_count': 2
            #     }
            # ]
        """
        # Agrupar por tipo de impuesto Y porcentaje (excepto ADV que se consolida)
        taxes_by_scheme_and_percent = {}
        
        try:
            for tax_line in tax_info:
                scheme_name = tax_line.get('TaxSchemeName', 'Sin Impuesto')
                percent = tax_line.get('Percent', '0.00')
                
                # Obtener montos de la línea
                tax_amount = float(tax_line.get('TaxAmount', '0'))
                base_amount = float(tax_line.get('TaxableAmount', tax_line.get('LineExtensionAmount', '0')))
                
                # Para ADV, consolidar por tipo únicamente
                if scheme_name == 'ADV':
                    consolidation_key = scheme_name  # Solo por tipo
                    percent = 'MIXTO'  # Indicar múltiples porcentajes
                else:
                    # Para otros impuestos, separar por tipo y porcentaje
                    consolidation_key = f"{scheme_name}_{percent}"
                
                if consolidation_key not in taxes_by_scheme_and_percent:
                    # Crear nueva entrada
                    taxes_by_scheme_and_percent[consolidation_key] = {
                        'TaxSchemeName': scheme_name,
                        'Percent': percent,
                        'consolidated_tax_amount': tax_amount,
                        'consolidated_base_amount': base_amount,
                        'line_count': 1
                    }
                else:
                    # Acumular montos
                    taxes_by_scheme_and_percent[consolidation_key]['consolidated_tax_amount'] += tax_amount
                    taxes_by_scheme_and_percent[consolidation_key]['consolidated_base_amount'] += base_amount
                    taxes_by_scheme_and_percent[consolidation_key]['line_count'] += 1
            
            # Convertir a lista y formatear montos
            result = []
            for tax_item in taxes_by_scheme_and_percent.values():
                tax_item['consolidated_tax_amount'] = f"{tax_item['consolidated_tax_amount']:.2f}"
                tax_item['consolidated_base_amount'] = f"{tax_item['consolidated_base_amount']:.2f}"
                result.append(tax_item)
            
            # Ordenar por tipo de impuesto y porcentaje para mejor legibilidad
            result.sort(key=lambda x: (x['TaxSchemeName'], x['Percent']))
            
            logger.info(f"Separados {len(tax_info)} líneas en {len(result)} tipos de impuesto")
            return result
            
        except Exception as e:
            logger.error(f"Error separando impuestos: {str(e)}")
            return []

    def create_separated_tax_description(self, tax_separated: Dict[str, Any]) -> str:
        """
        Crea la descripción del impuesto separado por tipo incluyendo clasificación fiscal detallada
        
        Args:
            tax_separated (Dict[str, Any]): Información del impuesto separado
            
        Returns:
            str: Descripción formateada del impuesto separado con clasificación fiscal
            
        Ejemplo de descripciones generadas:
            - "IVA - Impuesto (12.00%) - GRAVADO"
            - "IVA - Impuesto (0.00%) - EXENTO"
            - "ICE - Impuesto (300.00%) - GRAVADO - Consolidado (2 líneas)"
        """
        try:
            scheme_name = tax_separated.get('TaxSchemeName', '')
            percent = tax_separated.get('Percent', '0.00')
            line_count = tax_separated.get('line_count', 1)
            tax_amount = tax_separated.get('consolidated_tax_amount', '0.00')
            base_amount = tax_separated.get('consolidated_base_amount', '0.00')
            
            # Clasificar el tipo de impuesto
            tax_type = self.classify_tax_type(tax_separated)
            
            # Crear descripción dinámica para cualquier tipo de impuesto
            if scheme_name:
                # Formatear porcentaje
                try:
                    percent_float = float(percent)
                    formatted_percent = f"{percent_float:.2f}"
                except (ValueError, TypeError):
                    formatted_percent = percent
                
                # Crear descripción base con clasificación fiscal
                base_description = f"{scheme_name} - Impuesto ({formatted_percent}%) - {tax_type}"
                
                # Agregar información de consolidación si aplica
                if line_count > 1:
                    return f"{base_description} - Consolidado ({line_count} líneas)"
                else:
                    return base_description
            else:
                return f"Sin Impuestos - {tax_type}"
                
        except Exception as e:
            logger.error(f"Error creando descripción de impuesto separado: {str(e)}")
            return "Sin Impuestos - INDEFINIDO"

    def process_zip_file(self, file) -> List[Dict[str, Any]]:
        """
        Procesa un archivo ZIP completo
        
        Método principal para procesar un archivo ZIP que contiene
        facturas XML. Coordina todo el proceso de extracción y parsing.
        
        Args:
            file: Archivo ZIP (FileStorage de Flask o similar)
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con datos extraídos
                                 de todas las facturas en el ZIP
                                 
        Ejemplo de uso:
            with open('facturas.zip', 'rb') as f:
                rows = processor.process_zip_file(f)
                print(f"Se procesaron {len(rows)} líneas de factura")
                
        Ejemplo de estructura de datos retornada:
            [
                {
                    'ID_Factura': '001-001-000000001',
                    'Fecha': '2024-01-15',
                    'Cliente': 'EMPRESA ABC S.A.',
                    'Proveedor': 'PROVEEDOR XYZ LTDA.',
                    'Moneda': 'USD',
                    'Tipo_Documento': 'FACTURA',
                    'Numero_Linea': '1',
                    'Descripcion': 'Producto A',
                    'Cantidad': '10',
                    'Precio_Unitario': '100.00',
                    'Base_Imponible': '1000.00',
                    'Porcentaje': '12.00',
                    'Impuesto': '120.00',
                    'Total_Sin_Impuestos': '1000.00',
                    'Total_Impuestos': '120.00',
                    'Total': '1120.00',
                    'Archivo_Origen': 'factura1.xml',
                    'ZIP_Origen': 'facturas.zip'
                },
                ...
            ]
        """
        filename = getattr(file, 'filename', 'archivo_desconocido.zip')
        logger.info(f"Iniciando procesamiento del archivo: {filename}")
        
        try:
            # Extraer XMLs del archivo ZIP
            rows = self.extract_xml_from_zip(file)
            
            logger.info(f"Procesamiento completado. {len(rows)} líneas extraídas")
            return rows
            
        except Exception as e:
            logger.error(f"Error procesando archivo {filename}: {str(e)}")
            raise
