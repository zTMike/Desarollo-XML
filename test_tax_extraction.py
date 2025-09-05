#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de impuestos del XML
"""

import sys
import os
sys.path.append('src')

from utils.xml_processor import XMLProcessor
from lxml import etree

def test_tax_extraction():
    """Prueba la extracción de impuestos del XML"""
    
    # Inicializar el procesador
    processor = XMLProcessor()
    
    # Leer el archivo XML
    xml_file = 'fv08909165750152500772933.xml'
    
    if not os.path.exists(xml_file):
        print(f"Error: No se encontró el archivo {xml_file}")
        return
    
    try:
        with open(xml_file, 'rb') as f:
            xml_content = f.read()
        
        # Extraer la factura del XML
        invoice_xml = processor.extract_invoice_from_xml(xml_content)
        
        if not invoice_xml:
            print("Error: No se pudo extraer la factura del XML")
            return
        
        # Parsear el XML
        root = etree.fromstring(invoice_xml.encode('utf-8'))
        
        print("=== EXTRACCIÓN DE IMPUESTOS ===\n")
        
        # Extraer información fiscal
        tax_info = processor.extract_tax_information(root)
        print(f"Total de líneas de impuestos extraídas: {len(tax_info)}")
        
        # Mostrar cada línea de impuesto
        for i, tax in enumerate(tax_info):
            print(f"\n--- Línea {i+1} ---")
            print(f"TaxSchemeName: {tax.get('TaxSchemeName', 'N/A')}")
            print(f"Percent: {tax.get('Percent', 'N/A')}")
            print(f"TaxAmount: {tax.get('TaxAmount', 'N/A')}")
            print(f"TaxableAmount: {tax.get('TaxableAmount', 'N/A')}")
            print(f"LineExtensionAmount: {tax.get('LineExtensionAmount', 'N/A')}")
            print(f"LineNumber: {tax.get('LineNumber', 'N/A')}")
            print(f"ItemName: {tax.get('ItemName', 'N/A')}")
        
        print("\n=== SEPARACIÓN DE IMPUESTOS ===\n")
        
        # Separar impuestos por tipo
        separated_taxes = processor.separate_taxes_by_type(tax_info)
        print(f"Total de tipos de impuesto separados: {len(separated_taxes)}")
        
        # Mostrar cada tipo de impuesto separado
        for i, tax in enumerate(separated_taxes):
            print(f"\n--- Tipo {i+1} ---")
            print(f"TaxSchemeName: {tax.get('TaxSchemeName', 'N/A')}")
            print(f"Percent: {tax.get('Percent', 'N/A')}")
            print(f"consolidated_tax_amount: {tax.get('consolidated_tax_amount', 'N/A')}")
            print(f"consolidated_base_amount: {tax.get('consolidated_base_amount', 'N/A')}")
            print(f"line_count: {tax.get('line_count', 'N/A')}")
            
            # Clasificar el tipo
            tax_type = processor.classify_tax_type(tax)
            print(f"Clasificación: {tax_type}")
            
            # Crear descripción
            description = processor.create_separated_tax_description(tax)
            print(f"Descripción: {description}")
        
        print("\n=== VALORES ESPERADOS vs OBTENIDOS ===\n")
        print("ESPERADO:")
        print("ADV: $1.430.343 (Base: $0, Tasa: 0%)")
        print("ICL: $1.239.236 (Base: $0, Tasa: 0%)")
        print("IVA 5%: $243.560 (Base: $4.871.199, Tasa: 5%)")
        print("IVA 19%: $180.125 (Base: $948.026, Tasa: 19%)")
        
        print("\nOBTENIDO:")
        for tax in separated_taxes:
            scheme = tax.get('TaxSchemeName', 'N/A')
            percent = tax.get('Percent', 'N/A')
            amount = tax.get('consolidated_tax_amount', 'N/A')
            base = tax.get('consolidated_base_amount', 'N/A')
            print(f"{scheme} {percent}%: ${amount} (Base: ${base})")
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tax_extraction()
