"""
Ejemplo de Uso Programático - Procesador de Facturas XML
======================================================

Este script demuestra cómo usar la aplicación de forma programática
sin necesidad de la interfaz web.
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path

# Agregar el directorio src al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.xml_processor import XMLProcessor
from utils.excel_generator import ExcelGenerator
from utils.tax_classifier import TaxClassifier

def crear_archivo_zip_ejemplo():
    """Crea un archivo ZIP de ejemplo con XML de factura"""
    
    # XML de ejemplo (factura simple)
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>FAC001</cbc:ID>
    <cbc:IssueDate>2024-01-15</cbc:IssueDate>
    <cbc:UUID>12345678-1234-1234-1234-123456789012</cbc:UUID>
    
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>EMPRESA EJEMPLO S.A.S.</cbc:Name>
            </cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>900123456-7</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>CLIENTE EJEMPLO LTDA.</cbc:Name>
            </cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>800987654-3</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>
    
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="COP">100000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:Percent>19</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>01</cbc:ID>
                    <cbc:Name>IVA</cbc:Name>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    
    <cbc:PayableAmount currencyID="COP">119000.00</cbc:PayableAmount>
</Invoice>'''
    
    # Crear archivo ZIP temporal
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
        zip_file.writestr('factura_ejemplo.xml', xml_content)
    
    return temp_zip.name

def procesar_archivo_ejemplo():
    """Procesa un archivo ZIP de ejemplo"""
    
    print("🚀 Iniciando procesamiento de ejemplo...")
    
    # Crear archivo ZIP de ejemplo
    zip_path = crear_archivo_zip_ejemplo()
    print(f"📦 Archivo ZIP creado: {zip_path}")
    
    try:
        # Inicializar componentes
        xml_processor = XMLProcessor()
        excel_generator = ExcelGenerator()
        tax_classifier = TaxClassifier()
        
        # Simular archivo subido
        class MockFile:
            def __init__(self, path):
                self.path = path
                self.filename = os.path.basename(path)
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        mock_file = MockFile(zip_path)
        
        # Procesar archivo
        print("📄 Procesando archivo XML...")
        rows = xml_processor.process_zip_file(mock_file)
        
        if rows:
            print(f"✅ Procesamiento exitoso: {len(rows)} registros generados")
            
            # Mostrar datos procesados
            print("\n📊 Datos procesados:")
            for i, row in enumerate(rows, 1):
                print(f"  Registro {i}:")
                print(f"    Documento: {row['Documento']}")
                print(f"    Fecha: {row['Fecha(mm/dd/yyyy)']}")
                print(f"    NIT: {row['Nit']}")
                print(f"    Detalle: {row['Detalle']}")
                print(f"    Tipo: {row['Tipo']}")
                print(f"    Valor: ${row['Valor']:,.2f}")
                print(f"    Base: ${row['Base']:,.2f}")
                print()
            
            # Generar Excel
            print("📈 Generando archivo Excel...")
            excel_output = excel_generator.generate_excel(rows)
            
            if excel_output:
                # Guardar Excel
                excel_path = "facturas_procesadas_ejemplo.xlsx"
                with open(excel_path, 'wb') as f:
                    f.write(excel_output.getvalue())
                
                print(f"✅ Archivo Excel generado: {excel_path}")
                
                # Mostrar estadísticas
                stats = tax_classifier.get_tax_summary(rows)
                print("\n📈 Estadísticas del procesamiento:")
                print(f"  Total registros: {stats['total_gravado'] + stats['total_exento'] + stats['total_excluido']}")
                print(f"  IVA Gravado: {stats['total_gravado']}")
                print(f"  IVA Exento: {stats['total_exento']}")
                print(f"  IVA Excluido: {stats['total_excluido']}")
                print(f"  Total valor impuestos: ${stats['total_amount']:,.2f}")
                print(f"  Total base gravable: ${stats['total_base']:,.2f}")
            else:
                print("❌ Error generando archivo Excel")
        else:
            print("❌ No se encontraron datos válidos en el archivo")
    
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(zip_path)
            print(f"🧹 Archivo temporal eliminado: {zip_path}")
        except:
            pass

def ejemplo_clasificacion_impuestos():
    """Ejemplo de clasificación de impuestos"""
    
    print("\n🔍 Ejemplo de Clasificación de Impuestos:")
    
    tax_classifier = TaxClassifier()
    
    # Ejemplos de diferentes tipos de impuestos
    ejemplos = [
        {
            'tax_scheme_id': '01',
            'tax_scheme_name': 'IVA',
            'percent': '19',
            'description': 'IVA - Impuesto al Valor Agregado (19%)'
        },
        {
            'tax_scheme_id': '32',
            'tax_scheme_name': 'ICL',
            'percent': '15',
            'description': 'ICL - Impuesto al Consumo de Licores (15%)'
        },
        {
            'tax_scheme_id': '36',
            'tax_scheme_name': 'ADV',
            'percent': '8',
            'description': 'ADV - Impuesto al Consumo de Licores, Vinos, Cervezas y Cigarrillos (8%)'
        }
    ]
    
    for ejemplo in ejemplos:
        descripcion = tax_classifier.get_tax_description(
            ejemplo['tax_scheme_id'],
            ejemplo['tax_scheme_name'],
            ejemplo['percent']
        )
        print(f"  {ejemplo['description']} -> {descripcion}")

if __name__ == '__main__':
    print("=" * 60)
    print("PROCESADOR DE FACTURAS XML - EJEMPLO DE USO")
    print("=" * 60)
    
    # Ejemplo de clasificación de impuestos
    ejemplo_clasificacion_impuestos()
    
    # Ejemplo de procesamiento completo
    procesar_archivo_ejemplo()
    
    print("\n" + "=" * 60)
    print("EJEMPLO COMPLETADO")
    print("=" * 60)
