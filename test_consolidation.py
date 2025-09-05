#!/usr/bin/env python3
"""
Script simple para probar la consolidación de impuestos
"""

import sys
import os
sys.path.append('src')

from utils.xml_processor import XMLProcessor

def test_consolidation():
    """Prueba solo la consolidación de impuestos"""
    
    processor = XMLProcessor()
    
    # Datos de prueba basados en el XML
    tax_info = [
        {'TaxSchemeName': 'IVA', 'Percent': '19.00', 'TaxAmount': '423685.00', 'TaxableAmount': '948026.00'},
        {'TaxSchemeName': 'ICL', 'Percent': '0.00', 'TaxAmount': '1239236.00', 'TaxableAmount': '0.00'},
        {'TaxSchemeName': 'ADV', 'Percent': '25.00', 'TaxAmount': '1430343.00', 'TaxableAmount': '5111604.00'},
        {'TaxSchemeName': 'IVA', 'Percent': '5.00', 'TaxAmount': '243560.00', 'TaxableAmount': '4871199.00'},
    ]
    
    print("=== PRUEBA DE CONSOLIDACIÓN ===\n")
    
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
    print("ADV: $1.430.343 (Base: $5.111.604, Tasa: MIXTO)")
    print("ICL: $1.239.236 (Base: $0, Tasa: MIXTO)")
    print("IVA: $667.245 (Base: $5.818.225, Tasa: MIXTO)")
    
    print("\nOBTENIDO:")
    for tax in separated_taxes:
        scheme = tax.get('TaxSchemeName', 'N/A')
        percent = tax.get('Percent', 'N/A')
        amount = tax.get('consolidated_tax_amount', 'N/A')
        base = tax.get('consolidated_base_amount', 'N/A')
        print(f"{scheme} {percent}: ${amount} (Base: ${base})")

if __name__ == "__main__":
    test_consolidation()
