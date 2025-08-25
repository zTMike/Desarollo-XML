#!/usr/bin/env python3
"""
Script para validar los totales de impuestos del XML
"""

from lxml import etree
import sys

def validar_totales_xml(xml_file):
    """Valida los totales de impuestos del XML"""
    
    try:
        with open(xml_file, 'rb') as f:
            xml_content = f.read()

        root = etree.fromstring(xml_content)
        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        }

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

        print("\n🔍 VALIDACIÓN DE TOTALES DE IMPUESTOS")
        print("=" * 60)

        # Diccionario para agrupar impuestos
        tax_groups = {}

        # Buscar solo los TaxTotal del nivel documento (no de las líneas)
        tax_totals = root.findall('.//cac:TaxTotal', namespaces=ns)
        print(f"📊 Total de TaxTotal encontrados: {len(tax_totals)}")
        
        # Filtrar solo los TaxTotal del nivel documento (no dentro de InvoiceLine)
        doc_level_tax_totals = []
        for tax_total in tax_totals:
            # Verificar si el TaxTotal está dentro de una InvoiceLine
            parent = tax_total.getparent()
            while parent is not None:
                if parent.tag.endswith('InvoiceLine'):
                    break
                parent = parent.getparent()
            else:
                # No está dentro de InvoiceLine, es del nivel documento
                doc_level_tax_totals.append(tax_total)
        
        print(f"📊 TaxTotal del nivel documento: {len(doc_level_tax_totals)}")

        for i, tax_total in enumerate(doc_level_tax_totals, 1):
            tax_subs = tax_total.findall('.//cac:TaxSubtotal', namespaces=ns)
            
            for j, tax_subtotal in enumerate(tax_subs, 1):
                percent = tax_subtotal.findtext('.//cac:TaxCategory/cbc:Percent', namespaces=ns)
                taxable_amount = tax_subtotal.findtext('.//cbc:TaxableAmount', namespaces=ns)
                tax_amount = tax_subtotal.findtext('.//cbc:TaxAmount', namespaces=ns)
                
                # Obtener información del esquema de impuestos
                tax_scheme_id = tax_subtotal.findtext('.//cac:TaxScheme/cbc:ID', namespaces=ns)
                tax_scheme_name = tax_subtotal.findtext('.//cac:TaxScheme/cbc:Name', namespaces=ns)
                
                # Crear clave única para agrupar
                if tax_scheme_id == '01':  # IVA
                    key = f"IVA - Impuesto al Valor Agregado ({percent}%)"
                elif tax_scheme_id == '32':  # ICL
                    key = "ICL - Impuesto al Consumo de Licores"
                elif tax_scheme_id == '36':  # ADV
                    key = f"ADV - Impuesto al Consumo de Licores, Vinos, Cervezas y Cigarrillos ({percent}%)"
                else:
                    key = f"{tax_scheme_name} ({percent}%)" if percent else tax_scheme_name

                if key not in tax_groups:
                    tax_groups[key] = {
                        'tax_amount': 0.0,
                        'taxable_amount': 0.0,
                        'count': 0,
                        'details': []
                    }

                # Sumar valores
                tax_amount_val = float(tax_amount) if tax_amount else 0.0
                taxable_amount_val = float(taxable_amount) if taxable_amount else 0.0

                tax_groups[key]['tax_amount'] += tax_amount_val
                tax_groups[key]['taxable_amount'] += taxable_amount_val
                tax_groups[key]['count'] += 1
                tax_groups[key]['details'].append({
                    'tax_amount': tax_amount_val,
                    'taxable_amount': taxable_amount_val,
                    'percent': percent,
                    'scheme_id': tax_scheme_id,
                    'scheme_name': tax_scheme_name
                })

        # Mostrar resultados agrupados
        print("\n📋 TOTALES AGRUPADOS POR TIPO DE IMPUESTO:")
        print("-" * 60)
        
        total_general = 0.0
        for tax_description, values in tax_groups.items():
            print(f"\n🔸 {tax_description}")
            print(f"   💰 Total Impuesto: ${values['tax_amount']:,.2f}")
            print(f"   📊 Base Imponible: ${values['taxable_amount']:,.2f}")
            print(f"   📝 Registros: {values['count']}")
            total_general += values['tax_amount']

        print(f"\n💰 TOTAL GENERAL DE IMPUESTOS: ${total_general:,.2f}")

        # Verificar totales del documento
        print("\n🔍 VERIFICACIÓN DE TOTALES DEL DOCUMENTO:")
        print("-" * 60)
        
        # Total de impuestos del documento
        doc_tax_inclusive = root.findtext('.//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', namespaces=ns)
        doc_tax_exclusive = root.findtext('.//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount', namespaces=ns)
        doc_payable = root.findtext('.//cac:LegalMonetaryTotal/cbc:PayableAmount', namespaces=ns)
        
        print(f"📄 Total con Impuestos: ${float(doc_tax_inclusive):,.2f}" if doc_tax_inclusive else "❌ No encontrado")
        print(f"📄 Total sin Impuestos: ${float(doc_tax_exclusive):,.2f}" if doc_tax_exclusive else "❌ No encontrado")
        print(f"📄 Total a Pagar: ${float(doc_payable):,.2f}" if doc_payable else "❌ No encontrado")

        # Calcular diferencia
        if doc_tax_inclusive and doc_tax_exclusive:
            diferencia = float(doc_tax_inclusive) - float(doc_tax_exclusive)
            print(f"📊 Diferencia (Impuestos): ${diferencia:,.2f}")
            print(f"📊 Nuestro cálculo: ${total_general:,.2f}")
            print(f"📊 Diferencia: ${abs(diferencia - total_general):,.2f}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python validar_totales.py <archivo_xml>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    print(f"🔍 Validando archivo: {xml_file}")
    
    success = validar_totales_xml(xml_file)
    
    if success:
        print("\n✅ Validación completada exitosamente")
    else:
        print("\n❌ Validación falló")
        sys.exit(1)
