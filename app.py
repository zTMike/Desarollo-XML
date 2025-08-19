from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import zipfile
from lxml import etree
from collections import defaultdict
import os
import tempfile

app = Flask(__name__)

def extract_xml_from_zip(zip_file):
    """Extrae todos los archivos XML de un ZIP"""
    xml_files = []
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.lower().endswith('.xml'):
                    xml_content = zip_ref.read(file_info.filename)
                    xml_files.append({
                        'filename': file_info.filename,
                        'content': xml_content
                    })
    except Exception as e:
        print(f"Error procesando ZIP: {e}")
        return []
    
    return xml_files

def extract_invoice_from_xml(xml_content):
    """Extrae la factura XML anidada si existe"""
    try:
        root = etree.fromstring(xml_content)
        # Buscar factura en el contenido CDATA
        for elem in root.iter():
            if elem.text and '<?xml' in elem.text and 'Invoice' in elem.text:
                # Extraer el XML de la factura del CDATA
                start = elem.text.find('<?xml')
                end = elem.text.rfind('</Invoice>') + len('</Invoice>')
                if start != -1 and end != -1:
                    invoice_xml = elem.text[start:end]
                    return invoice_xml
        # Si no encuentra factura anidada, usar el XML directamente
        return xml_content.decode('utf-8') if isinstance(xml_content, bytes) else xml_content
    except Exception as e:
        print(f"Error extrayendo factura XML: {e}")
        return None

def classify_tax_status(tax_type, percent, tax_amount, taxable_amount):
    """Clasifica el estado fiscal del impuesto"""
    percent = float(percent) if percent else 0.0
    tax_amount = float(tax_amount) if tax_amount else 0.0
    taxable_amount = float(taxable_amount) if taxable_amount else 0.0
    
    if percent == 0.0 and taxable_amount > 0:
        return 'EXENTO'
    elif percent > 0.0 and tax_amount > 0:
        return 'GRAVADO'
    elif percent > 0.0 and tax_amount == 0:
        return 'EXENTO'
    elif taxable_amount == 0:
        return 'EXCLUIDO'
    else:
        return 'INDEFINIDO'

def parse_invoice_for_structure(invoice_xml, filename, zip_name):
    """Extrae información de la factura para la estructura específica requerida"""
    try:
        root = etree.fromstring(invoice_xml.encode('utf-8') if isinstance(invoice_xml, str) else invoice_xml)
        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        }
        
        # Información básica de la factura
        numero_factura = root.findtext('.//cbc:ID', namespaces=ns) or ''
        fecha = root.findtext('.//cbc:IssueDate', namespaces=ns) or ''
        cliente = root.findtext('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name', namespaces=ns) or ''
        proveedor = root.findtext('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name', namespaces=ns) or ''
        nit_cliente = root.findtext('.//cac:AccountingCustomerParty//cbc:CompanyID', namespaces=ns) or ''
        nit_proveedor = root.findtext('.//cac:AccountingSupplierParty//cbc:CompanyID', namespaces=ns) or ''
        total = root.findtext('.//cbc:PayableAmount', namespaces=ns) or ''
        
        # Dirección del cliente (solo dirección, sin observaciones)
        direccion = root.findtext('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line', namespaces=ns) or ''
        if not direccion:
            direccion = root.findtext('.//cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line', namespaces=ns) or ''
        
        # Plazo de pago
        plazo = root.findtext('.//cac:PaymentMeans/cbc:PaymentDueDate', namespaces=ns) or ''
        
        # UUID del documento electrónico
        uuid = root.findtext('.//cbc:UUID', namespaces=ns) or ''
        
        # Crear filas separadas por cada IVA encontrado
        rows = []
        
        # Buscar todos los TaxTotal en la factura
        tax_totals = root.findall('.//cac:TaxTotal', namespaces=ns)
        print(f"Encontrados {len(tax_totals)} TaxTotal en {filename}")
        
        for tax_total in tax_totals:
            tax_subs = tax_total.findall('.//cac:TaxSubtotal', namespaces=ns)
            print(f"Encontrados {len(tax_subs)} TaxSubtotal")
            
            for tax_subtotal in tax_subs:
                percent = tax_subtotal.findtext('.//cac:TaxCategory/cbc:Percent', namespaces=ns)
                taxable_amount = tax_subtotal.findtext('.//cbc:TaxableAmount', namespaces=ns)
                tax_amount = tax_subtotal.findtext('.//cbc:TaxAmount', namespaces=ns)
                
                print(f"IVA encontrado: {percent}%, Valor: {tax_amount}, Base: {taxable_amount}")
                
                if percent and tax_amount:
                    # Clasificar estado fiscal
                    estado = classify_tax_status('IVA', percent, tax_amount, taxable_amount)
                    
                    row = {
                        'Obserad direccion de el fecha de acturacion': direccion,  # Solo dirección
                        'Documento': numero_factura,
                        'Documento Ref.': '',  # Vacío como solicitado
                        'Nit': nit_proveedor,
                        'IVA': f"IVA {percent}%",
                        'Tipo': estado,  # Estado fiscal: GRAVADO, EXENTO, EXCLUIDO
                        'Valor': round(float(tax_amount), 2),
                        'Base': round(float(taxable_amount), 2) if taxable_amount else 0.0,
                        'Centro de Costo': '',
                        'Trans. Ext': '',
                        'Plazo': plazo,
                        'Docto Electrónico': uuid
                    }
                    rows.append(row)
        
        # Si no hay IVAs, crear una fila con información básica
        if not rows:
            print(f"No se encontraron IVAs en {filename}, creando fila sin IVA")
            row = {
                'Obserad direccion de el fecha de acturacion': direccion,
                'Documento': numero_factura,
                'Documento Ref.': '',
                'Nit': nit_proveedor,
                'IVA': 'Sin IVA',
                'Tipo': 'EXCLUIDO',
                'Valor': 0.0,
                'Base': 0.0,
                'Centro de Costo': '',
                'Trans. Ext': '',
                'Plazo': plazo,
                'Docto Electrónico': uuid
            }
            rows.append(row)
        
        print(f"Generadas {len(rows)} filas para {filename}")
        return rows
        
    except Exception as e:
        print(f"Error parseando factura {filename}: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Iniciando procesamiento POST")
        
        if 'zip_files' not in request.files:
            print("No se encontraron archivos en la request")
            return jsonify({'error': 'No se seleccionaron archivos'})
        
        zip_files = request.files.getlist('zip_files')
        print(f"Archivos recibidos: {len(zip_files)}")
        
        if not zip_files or all(f.filename == '' for f in zip_files):
            print("No hay archivos válidos")
            return jsonify({'error': 'No se seleccionaron archivos'})
        
        # Verificar límite de archivos
        if len(zip_files) > 100:
            return jsonify({'error': 'Máximo 100 archivos ZIP permitidos'})
        
        # Procesar todos los ZIP
        all_rows = []
        processed_files = 0
        
        for zip_file in zip_files:
            if zip_file.filename and zip_file.filename.lower().endswith('.zip'):
                print(f"Procesando ZIP: {zip_file.filename}")
                
                # Procesar el ZIP
                xml_files = extract_xml_from_zip(zip_file)
                print(f"Encontrados {len(xml_files)} archivos XML en {zip_file.filename}")
                
                # Procesar cada XML
                for xml_file in xml_files:
                    print(f"Procesando XML: {xml_file['filename']}")
                    invoice_xml = extract_invoice_from_xml(xml_file['content'])
                    if invoice_xml:
                        rows = parse_invoice_for_structure(invoice_xml, xml_file['filename'], zip_file.filename)
                        all_rows.extend(rows)
                        processed_files += 1
                        print(f"Factura procesada: {len(rows)} filas generadas")
                    else:
                        print(f"No se pudo extraer factura de {xml_file['filename']}")
        
        print(f"Total de archivos procesados: {processed_files}")
        print(f"Total de filas generadas: {len(all_rows)}")
        
        if not all_rows:
            return jsonify({'error': 'No se pudieron procesar las facturas'})
        
        # Crear DataFrame con la estructura específica
        columns = [
            'Obserad direccion de el fecha de acturacion',
            'Documento',
            'Documento Ref.',
            'Nit',
            'IVA',
            'Tipo',
            'Valor',
            'Base',
            'Centro de Costo',
            'Trans. Ext',
            'Plazo',
            'Docto Electrónico'
        ]
        
        df = pd.DataFrame(all_rows, columns=columns)
        
        # Generar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Facturas', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='facturas_procesadas.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5051, host='0.0.0.0')

