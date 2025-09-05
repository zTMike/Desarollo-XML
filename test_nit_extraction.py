#!/usr/bin/env python3
"""
Script para verificar la extracción del NIT del cliente
"""

import sys
import os
sys.path.append('src')

from utils.xml_processor import XMLProcessor
from lxml import etree

def test_nit_extraction():
    """Prueba la extracción del NIT del cliente"""
    
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
        
        print("=== EXTRACCIÓN DE INFORMACIÓN BÁSICA ===\n")
        
        # Extraer información básica
        basic_info = processor.extract_basic_info(root)
        
        print("Información extraída:")
        print(f"ID_Factura: {basic_info.get('ID_Factura', 'N/A')}")
        print(f"Fecha: {basic_info.get('Fecha', 'N/A')}")
        print(f"Cliente: {basic_info.get('Cliente', 'N/A')}")
        print(f"Proveedor: {basic_info.get('Proveedor', 'N/A')}")
        print(f"NIT_Cliente: {basic_info.get('NIT_Cliente', 'N/A')}")
        print(f"Moneda: {basic_info.get('Moneda', 'N/A')}")
        print(f"Fecha_Vencimiento: {basic_info.get('Fecha_Vencimiento', 'N/A')}")
        print(f"ID_Documento_Electronico: {basic_info.get('ID_Documento_Electronico', 'N/A')}")
        
        print("\n=== VERIFICACIÓN MANUAL DEL XML ===\n")
        
        # Buscar manualmente el NIT del cliente
        customer_party = root.find('.//cac:AccountingCustomerParty', namespaces=processor.namespaces)
        if customer_party is not None:
            print("✅ Se encontró AccountingCustomerParty")
            
            # Buscar nombre del cliente
            customer_name = customer_party.find('.//cac:PartyName//cbc:Name', namespaces=processor.namespaces)
            if customer_name is not None:
                print(f"Nombre del cliente: {customer_name.text}")
            else:
                print("❌ No se encontró nombre del cliente")
            
            # Buscar NIT del cliente
            customer_tax_id = customer_party.find('.//cac:PartyTaxScheme//cbc:CompanyID', namespaces=processor.namespaces)
            if customer_tax_id is not None:
                print(f"NIT del cliente: {customer_tax_id.text}")
            else:
                print("❌ No se encontró NIT del cliente")
        else:
            print("❌ No se encontró AccountingCustomerParty")
        
        # Buscar manualmente el NIT del proveedor
        supplier_party = root.find('.//cac:AccountingSupplierParty', namespaces=processor.namespaces)
        if supplier_party is not None:
            print("\n✅ Se encontró AccountingSupplierParty")
            
            # Buscar nombre del proveedor
            supplier_name = supplier_party.find('.//cac:PartyName//cbc:Name', namespaces=processor.namespaces)
            if supplier_name is not None:
                print(f"Nombre del proveedor: {supplier_name.text}")
            else:
                print("❌ No se encontró nombre del proveedor")
            
            # Buscar NIT del proveedor
            supplier_tax_id = supplier_party.find('.//cac:PartyTaxScheme//cbc:CompanyID', namespaces=processor.namespaces)
            if supplier_tax_id is not None:
                print(f"NIT del proveedor: {supplier_tax_id.text}")
            else:
                print("❌ No se encontró NIT del proveedor")
        else:
            print("❌ No se encontró AccountingSupplierParty")
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nit_extraction()

