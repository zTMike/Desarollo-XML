#!/usr/bin/env python3
"""
Script para probar los XPath y verificar la extracción de información
"""

from lxml import etree
import sys

def test_xpath_extraction(xml_file):
    """Prueba la extracción de información usando XPath"""
    
    try:
        # Leer el archivo XML
        with open(xml_file, 'rb') as f:
            xml_content = f.read()
        
        # Parsear el XML
        root = etree.fromstring(xml_content)
        
        # Definir namespaces
        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        }
        
        print("🔍 PRUEBA DE EXTRACCIÓN DE INFORMACIÓN")
        print("=" * 50)
        
        # Verificar si es un AttachedDocument
        if root.tag.endswith('AttachedDocument'):
            print("📋 Detectado AttachedDocument - Buscando factura anidada...")
            
            # Buscar la factura XML en el CDATA
            invoice_xml = None
            for elem in root.iter():
                if elem.text and '<?xml' in elem.text and 'Invoice' in elem.text:
                    # Extraer el XML de la factura del CDATA
                    start = elem.text.find('<?xml')
                    end = elem.text.rfind('</Invoice>') + len('</Invoice>')
                    if start != -1 and end != -1:
                        invoice_xml = elem.text[start:end]
                        print("✅ Factura XML encontrada en CDATA")
                        break
            
            if invoice_xml:
                # Parsear la factura extraída
                invoice_root = etree.fromstring(invoice_xml.encode('utf-8'))
                root = invoice_root
                print("✅ Factura XML parseada correctamente")
            else:
                print("❌ No se encontró factura XML en el CDATA")
                return False
        
        # 1. Información básica de la factura
        print("\n📄 INFORMACIÓN BÁSICA:")
        numero_factura = root.findtext('.//cbc:ID', namespaces=ns)
        fecha = root.findtext('.//cbc:IssueDate', namespaces=ns)
        uuid = root.findtext('.//cbc:UUID', namespaces=ns)
        
        print(f"   Número de Factura: {numero_factura}")
        print(f"   Fecha: {fecha}")
        print(f"   UUID: {uuid}")
        
        # 2. Información del proveedor
        print("\n🏢 INFORMACIÓN DEL PROVEEDOR:")
        proveedor = root.findtext('.//cac:AccountingSupplierParty//cac:PartyName/cbc:Name', namespaces=ns)
        nit_proveedor = root.findtext('.//cac:AccountingSupplierParty//cac:PartyTaxScheme/cbc:CompanyID', namespaces=ns)
        
        print(f"   Nombre: {proveedor}")
        print(f"   NIT: {nit_proveedor}")
        
        # 3. Información del cliente
        print("\n👤 INFORMACIÓN DEL CLIENTE:")
        cliente = root.findtext('.//cac:AccountingCustomerParty//cac:PartyName/cbc:Name', namespaces=ns)
        nit_cliente = root.findtext('.//cac:AccountingCustomerParty//cac:PartyTaxScheme/cbc:CompanyID', namespaces=ns)
        direccion_cliente = root.findtext('.//cac:AccountingCustomerParty//cac:Party//cac:PhysicalLocation//cac:AddressLine/cbc:Line', namespaces=ns)
        
        print(f"   Nombre: {cliente}")
        print(f"   NIT: {nit_cliente}")
        print(f"   Dirección: {direccion_cliente}")
        
        # 4. Plazo de pago
        print("\n📅 PLAZO DE PAGO:")
        plazo = root.findtext('.//cac:PaymentMeans/cbc:PaymentDueDate', namespaces=ns)
        print(f"   Fecha de vencimiento: {plazo}")
        
        # 5. Impuestos del nivel documento (simplificado)
        print("\n💰 IMPUESTOS DEL NIVEL DOCUMENTO:")
        document_tax_totals = root.findall('.//cac:TaxTotal', namespaces=ns)
        print(f"   Total de TaxTotal encontrados: {len(document_tax_totals)}")
        
        # Filtrar TaxTotal que no están dentro de InvoiceLine
        doc_level_taxes = []
        for tax_total in document_tax_totals:
            # Verificar si el TaxTotal está dentro de una InvoiceLine
            parent = tax_total.getparent()
            while parent is not None:
                if parent.tag.endswith('InvoiceLine'):
                    break
                parent = parent.getparent()
            else:
                # No está dentro de InvoiceLine, es del nivel documento
                doc_level_taxes.append(tax_total)
        
        print(f"   TaxTotal del nivel documento: {len(doc_level_taxes)}")
        
        for i, tax_total in enumerate(doc_level_taxes, 1):
            print(f"\n   TaxTotal #{i}:")
            tax_subs = tax_total.findall('.//cac:TaxSubtotal', namespaces=ns)
            for j, tax_subtotal in enumerate(tax_subs, 1):
                percent = tax_subtotal.findtext('.//cac:TaxCategory/cbc:Percent', namespaces=ns)
                taxable_amount = tax_subtotal.findtext('.//cbc:TaxableAmount', namespaces=ns)
                tax_amount = tax_subtotal.findtext('.//cbc:TaxAmount', namespaces=ns)
                tax_scheme_name = tax_subtotal.findtext('.//cac:TaxScheme/cbc:Name', namespaces=ns)
                
                print(f"     Subtotal #{j}:")
                print(f"       Tipo: {tax_scheme_name}")
                print(f"       Porcentaje: {percent}")
                print(f"       Base: {taxable_amount}")
                print(f"       Total: {tax_amount}")
        
        # 6. Impuestos del nivel línea
        print("\n📋 IMPUESTOS DEL NIVEL LÍNEA:")
        invoice_lines = root.findall('.//cac:InvoiceLine', namespaces=ns)
        print(f"   Total de líneas de factura: {len(invoice_lines)}")
        
        line_tax_count = 0
        for i, line in enumerate(invoice_lines[:3], 1):  # Solo mostrar las primeras 3 líneas
            line_tax_totals = line.findall('.//cac:TaxTotal', namespaces=ns)
            if line_tax_totals:
                print(f"\n   Línea #{i}:")
                for j, tax_total in enumerate(line_tax_totals, 1):
                    line_tax_count += 1
                    tax_subs = tax_total.findall('.//cac:TaxSubtotal', namespaces=ns)
                    for k, tax_subtotal in enumerate(tax_subs, 1):
                        percent = tax_subtotal.findtext('.//cac:TaxCategory/cbc:Percent', namespaces=ns)
                        taxable_amount = tax_subtotal.findtext('.//cbc:TaxableAmount', namespaces=ns)
                        tax_amount = tax_subtotal.findtext('.//cbc:TaxAmount', namespaces=ns)
                        tax_scheme_name = tax_subtotal.findtext('.//cac:TaxScheme/cbc:Name', namespaces=ns)
                        
                        print(f"     TaxTotal #{j}, Subtotal #{k}:")
                        print(f"       Tipo: {tax_scheme_name}")
                        print(f"       Porcentaje: {percent}")
                        print(f"       Base: {taxable_amount}")
                        print(f"       Total: {tax_amount}")
        
        print(f"\n   Total de TaxTotal en líneas: {line_tax_count}")
        
        # 7. Resumen
        print("\n📊 RESUMEN:")
        total_tax_totals = len(doc_level_taxes) + line_tax_count
        print(f"   Total de TaxTotal encontrados: {total_tax_totals}")
        print(f"   - Nivel documento: {len(doc_level_taxes)}")
        print(f"   - Nivel línea: {line_tax_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python test_xpath.py <archivo_xml>")
        return
    
    xml_file = sys.argv[1]
    
    if not xml_file.endswith('.xml'):
        print("❌ El archivo debe ser un XML")
        return
    
    print(f"🔍 Probando archivo: {xml_file}")
    success = test_xpath_extraction(xml_file)
    
    if success:
        print("\n✅ Prueba completada exitosamente")
    else:
        print("\n❌ Prueba falló")

if __name__ == "__main__":
    main()
