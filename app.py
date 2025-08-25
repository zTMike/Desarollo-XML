from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import zipfile
from lxml import etree
from collections import defaultdict
import os
import tempfile
import uuid

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_12345'  # Necesario para usar session

# Diccionario para almacenar archivos temporales
temp_files = {}

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

def get_tax_type_description(tax_scheme_id, tax_scheme_name, percent):
    """Obtiene la descripción del tipo de impuesto basado en el ID del esquema"""
    tax_descriptions = {
        '01': 'IVA - Impuesto al Valor Agregado',
        '02': 'IC - Impuesto al Consumo',
        '03': 'ICA - Impuesto de Industria y Comercio',
        '04': 'INC - Impuesto Nacional al Consumo',
        '05': 'INC - Impuesto Nacional al Consumo',
        '06': 'INC - Impuesto Nacional al Consumo',
        '07': 'INC - Impuesto Nacional al Consumo',
        '08': 'INC - Impuesto Nacional al Consumo',
        '09': 'INC - Impuesto Nacional al Consumo',
        '10': 'INC - Impuesto Nacional al Consumo',
        '11': 'INC - Impuesto Nacional al Consumo',
        '12': 'INC - Impuesto Nacional al Consumo',
        '13': 'INC - Impuesto Nacional al Consumo',
        '14': 'INC - Impuesto Nacional al Consumo',
        '15': 'INC - Impuesto Nacional al Consumo',
        '16': 'INC - Impuesto Nacional al Consumo',
        '17': 'INC - Impuesto Nacional al Consumo',
        '18': 'INC - Impuesto Nacional al Consumo',
        '19': 'INC - Impuesto Nacional al Consumo',
        '20': 'INC - Impuesto Nacional al Consumo',
        '21': 'INC - Impuesto Nacional al Consumo',
        '22': 'INC - Impuesto Nacional al Consumo',
        '23': 'INC - Impuesto Nacional al Consumo',
        '24': 'INC - Impuesto Nacional al Consumo',
        '25': 'INC - Impuesto Nacional al Consumo',
        '26': 'INC - Impuesto Nacional al Consumo',
        '27': 'INC - Impuesto Nacional al Consumo',
        '28': 'INC - Impuesto Nacional al Consumo',
        '29': 'INC - Impuesto Nacional al Consumo',
        '30': 'INC - Impuesto Nacional al Consumo',
        '31': 'INC - Impuesto Nacional al Consumo',
        '32': 'ICL - Impuesto al Consumo de Licores',
        '33': 'INC - Impuesto Nacional al Consumo',
        '34': 'INC - Impuesto Nacional al Consumo',
        '35': 'INC - Impuesto Nacional al Consumo',
        '36': 'ADV - Impuesto al Consumo de Licores, Vinos, Cervezas y Cigarrillos',
        '37': 'INC - Impuesto Nacional al Consumo',
        '38': 'INC - Impuesto Nacional al Consumo',
        '39': 'INC - Impuesto Nacional al Consumo',
        '40': 'INC - Impuesto Nacional al Consumo',
        '41': 'INC - Impuesto Nacional al Consumo',
        '42': 'INC - Impuesto Nacional al Consumo',
        '43': 'INC - Impuesto Nacional al Consumo',
        '44': 'INC - Impuesto Nacional al Consumo',
        '45': 'INC - Impuesto Nacional al Consumo',
        '46': 'INC - Impuesto Nacional al Consumo',
        '47': 'INC - Impuesto Nacional al Consumo',
        '48': 'INC - Impuesto Nacional al Consumo',
        '49': 'INC - Impuesto Nacional al Consumo',
        '50': 'INC - Impuesto Nacional al Consumo',
        '51': 'INC - Impuesto Nacional al Consumo',
        '52': 'INC - Impuesto Nacional al Consumo',
        '53': 'INC - Impuesto Nacional al Consumo',
        '54': 'INC - Impuesto Nacional al Consumo',
        '55': 'INC - Impuesto Nacional al Consumo',
        '56': 'INC - Impuesto Nacional al Consumo',
        '57': 'INC - Impuesto Nacional al Consumo',
        '58': 'INC - Impuesto Nacional al Consumo',
        '59': 'INC - Impuesto Nacional al Consumo',
        '60': 'INC - Impuesto Nacional al Consumo',
        '61': 'INC - Impuesto Nacional al Consumo',
        '62': 'INC - Impuesto Nacional al Consumo',
        '63': 'INC - Impuesto Nacional al Consumo',
        '64': 'INC - Impuesto Nacional al Consumo',
        '65': 'INC - Impuesto Nacional al Consumo',
        '66': 'INC - Impuesto Nacional al Consumo',
        '67': 'INC - Impuesto Nacional al Consumo',
        '68': 'INC - Impuesto Nacional al Consumo',
        '69': 'INC - Impuesto Nacional al Consumo',
        '70': 'INC - Impuesto Nacional al Consumo',
        '71': 'INC - Impuesto Nacional al Consumo',
        '72': 'INC - Impuesto Nacional al Consumo',
        '73': 'INC - Impuesto Nacional al Consumo',
        '74': 'INC - Impuesto Nacional al Consumo',
        '75': 'INC - Impuesto Nacional al Consumo',
        '76': 'INC - Impuesto Nacional al Consumo',
        '77': 'INC - Impuesto Nacional al Consumo',
        '78': 'INC - Impuesto Nacional al Consumo',
        '79': 'INC - Impuesto Nacional al Consumo',
        '80': 'INC - Impuesto Nacional al Consumo',
        '81': 'INC - Impuesto Nacional al Consumo',
        '82': 'INC - Impuesto Nacional al Consumo',
        '83': 'INC - Impuesto Nacional al Consumo',
        '84': 'INC - Impuesto Nacional al Consumo',
        '85': 'INC - Impuesto Nacional al Consumo',
        '86': 'INC - Impuesto Nacional al Consumo',
        '87': 'INC - Impuesto Nacional al Consumo',
        '88': 'INC - Impuesto Nacional al Consumo',
        '89': 'INC - Impuesto Nacional al Consumo',
        '90': 'INC - Impuesto Nacional al Consumo',
        '91': 'INC - Impuesto Nacional al Consumo',
        '92': 'INC - Impuesto Nacional al Consumo',
        '93': 'INC - Impuesto Nacional al Consumo',
        '94': 'INC - Impuesto Nacional al Consumo',
        '95': 'INC - Impuesto Nacional al Consumo',
        '96': 'INC - Impuesto Nacional al Consumo',
        '97': 'INC - Impuesto Nacional al Consumo',
        '98': 'INC - Impuesto Nacional al Consumo',
        '99': 'INC - Impuesto Nacional al Consumo'
    }
    
    # Obtener descripción base
    base_description = tax_descriptions.get(tax_scheme_id, f'{tax_scheme_name or "Impuesto"}')
    
    # Agregar porcentaje si existe
    if percent and percent != 'None':
        return f"{base_description} ({percent}%)"
    else:
        return base_description

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
        
        # Detectar tipo de documento
        document_type = "FACTURA"
        if root.tag.endswith('CreditNote'):
            document_type = "NOTA CRÉDITO"
            print(f"⚠️  NOTA CRÉDITO DETECTADA en {filename}")
        elif root.tag.endswith('DebitNote'):
            document_type = "NOTA DÉBITO"
            print(f"⚠️  NOTA DÉBITO DETECTADA en {filename}")
        elif root.tag.endswith('Invoice'):
            document_type = "FACTURA"
        else:
            document_type = "DOCUMENTO DESCONOCIDO"
            print(f"❓ TIPO DE DOCUMENTO DESCONOCIDO en {filename}: {root.tag}")
        
        print(f"📄 Tipo de documento: {document_type}")
        
        # Información básica de la factura
        numero_factura_completo = root.findtext('.//cbc:ID', namespaces=ns) or ''
        # Tomar solo los últimos 5 dígitos del documento
        numero_factura = numero_factura_completo[-5:] if len(numero_factura_completo) >= 5 else numero_factura_completo
        fecha = root.findtext('.//cbc:IssueDate', namespaces=ns) or ''
        cliente = root.findtext('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name', namespaces=ns) or ''
        proveedor = root.findtext('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name', namespaces=ns) or ''
        nit_cliente = root.findtext('.//cac:AccountingCustomerParty//cbc:CompanyID', namespaces=ns) or ''
        nit_proveedor = root.findtext('.//cac:AccountingSupplierParty//cbc:CompanyID', namespaces=ns) or ''
        total = root.findtext('.//cbc:PayableAmount', namespaces=ns) or ''
        
        print(f"Factura: {numero_factura_completo} -> {numero_factura} (últimos 5 dígitos), Fecha: {fecha}, Proveedor: {proveedor}, NIT: {nit_proveedor}")
        
        # Dirección del cliente (solo dirección, sin observaciones)
        direccion = root.findtext('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line', namespaces=ns) or ''
        if not direccion:
            direccion = root.findtext('.//cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line', namespaces=ns) or ''
        
        # Plazo de pago
        plazo = root.findtext('.//cac:PaymentMeans/cbc:PaymentDueDate', namespaces=ns) or ''
        
        # UUID del documento electrónico
        uuid = root.findtext('.//cbc:UUID', namespaces=ns) or ''
        
        print(f"Factura: {numero_factura}, Fecha: {fecha}, Proveedor: {proveedor}, NIT: {nit_proveedor}")
        
        # Crear filas agrupadas por tipo de impuesto
        rows = []
        tax_groups = {}  # Diccionario para agrupar impuestos por tipo y porcentaje
        
        # Buscar solo los TaxTotal del nivel documento (no de las líneas)
        tax_totals = root.findall('.//cac:TaxTotal', namespaces=ns)
        print(f"Encontrados {len(tax_totals)} TaxTotal en {filename}")
        
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
        
        print(f"TaxTotal del nivel documento: {len(doc_level_tax_totals)}")
        
        for tax_total in doc_level_tax_totals:
            tax_subs = tax_total.findall('.//cac:TaxSubtotal', namespaces=ns)
            print(f"Encontrados {len(tax_subs)} TaxSubtotal")
            
            for tax_subtotal in tax_subs:
                percent = tax_subtotal.findtext('.//cac:TaxCategory/cbc:Percent', namespaces=ns)
                taxable_amount = tax_subtotal.findtext('.//cbc:TaxableAmount', namespaces=ns)
                tax_amount = tax_subtotal.findtext('.//cbc:TaxAmount', namespaces=ns)
                
                # Obtener información del esquema de impuestos
                tax_scheme_id = tax_subtotal.findtext('.//cac:TaxScheme/cbc:ID', namespaces=ns)
                tax_scheme_name = tax_subtotal.findtext('.//cac:TaxScheme/cbc:Name', namespaces=ns)
                
                # Obtener descripción del tipo de impuesto
                tax_description = get_tax_type_description(tax_scheme_id, tax_scheme_name, percent)
                
                print(f"Impuesto encontrado: {tax_description}, Valor: {tax_amount}, Base: {taxable_amount}")
                
                if tax_amount:  # Procesar si hay valor de impuesto
                    # Usar la descripción como clave para agrupar
                    key = tax_description
                    
                    if key not in tax_groups:
                        tax_groups[key] = {
                            'tax_amount': 0.0,
                            'taxable_amount': 0.0,
                            'count': 0
                        }
                    
                    # Sumar valores
                    tax_groups[key]['tax_amount'] += float(tax_amount)
                    if taxable_amount:
                        tax_groups[key]['taxable_amount'] += float(taxable_amount)
                    tax_groups[key]['count'] += 1
        
        # Crear una fila por cada tipo de impuesto agrupado
        for tax_description, values in tax_groups.items():
            # Extraer el porcentaje de la descripción del impuesto
            percent_from_description = '0'
            if '(' in tax_description and '%)' in tax_description:
                # Extraer el porcentaje de la descripción (ej: "IVA - Impuesto al Valor Agregado (19.00%)")
                percent_start = tax_description.find('(') + 1
                percent_end = tax_description.find('%)')
                if percent_start > 0 and percent_end > percent_start:
                    percent_from_description = tax_description[percent_start:percent_end]
            
            # Clasificar estado fiscal con el porcentaje correcto
            estado = classify_tax_status('Impuesto', percent_from_description, values['tax_amount'], values['taxable_amount'])
            
            row = {
                'Cuenta': '',  # Campo a llenar según requerimientos
                'Comprobante': document_type,  # Tipo de documento (FACTURA, NOTA CRÉDITO, NOTA DÉBITO)
                'Fecha(mm/dd/yyyy)': fecha,
                'Documento': numero_factura,
                'Documento Ref.': zip_name,  # Nombre del archivo ZIP
                'Nit': nit_proveedor,
                'Detalle': tax_description,  # Descripción completa del impuesto
                'Tipo': estado,  # Estado fiscal: GRAVADO, EXENTO, EXCLUIDO
                'Valor': round(values['tax_amount'], 2),
                'Base': round(values['taxable_amount'], 2),
                'Centro de Costo': '',
                'Trans. Ext': '',
                'Plazo': plazo,
                'Docto Electrónico': uuid
            }
            rows.append(row)
            print(f"Fila agrupada: {tax_description} - Total: {values['tax_amount']}, Base: {values['taxable_amount']}, Registros: {values['count']}")
        
        # Si no hay impuestos, crear una fila con información básica
        if not rows:
            print(f"No se encontraron impuestos en {filename}, creando fila sin impuestos")
            row = {
                'Cuenta': '',  # Campo a llenar según requerimientos
                'Comprobante': document_type,  # Tipo de documento (FACTURA, NOTA CRÉDITO, NOTA DÉBITO)
                'Fecha(mm/dd/yyyy)': fecha,
                'Documento': numero_factura,
                'Documento Ref.': zip_name,  # Nombre del archivo ZIP
                'Nit': nit_proveedor,
                'Detalle': 'Sin Impuestos',
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
        import traceback
        traceback.print_exc()
        return []

def process_files_for_excel(files):
    """Procesa archivos para generar la estructura Excel requerida"""
    all_rows = []
    
    for file in files:
        filename = file.filename
        if filename.lower().endswith('.zip'):
            try:
                print(f"Procesando ZIP: {filename}")
                
                # Procesar el ZIP
                xml_files = extract_xml_from_zip(file)
                print(f"Encontrados {len(xml_files)} archivos XML en {filename}")
                
                # Procesar cada XML
                for xml_file in xml_files:
                    print(f"Procesando XML: {xml_file['filename']}")
                    invoice_xml = extract_invoice_from_xml(xml_file['content'])
                    if invoice_xml:
                        rows = parse_invoice_for_structure(invoice_xml, xml_file['filename'], filename)
                        for row in rows:
                            row['Archivo'] = filename
                            all_rows.append(row)
                        print(f"Factura procesada: {len(rows)} filas generadas")
                    else:
                        print(f"No se pudo extraer factura de {xml_file['filename']}")
            except Exception as e:
                print(f"Error procesando ZIP {filename}: {e}")
        elif filename.lower().endswith('.xml'):
            try:
                xml_bytes = file.read()
                invoice_xml = extract_invoice_from_xml(xml_bytes)
                if invoice_xml:
                    rows = parse_invoice_for_structure(invoice_xml, filename, filename)
                    for row in rows:
                        row['Archivo'] = filename
                        all_rows.append(row)
                else:
                    print(f"No se pudo extraer factura de {filename}")
            except Exception as e:
                print(f"Error procesando XML {filename}: {e}")
    
    return all_rows

def generate_excel(all_rows):
    """Genera el archivo Excel con la estructura requerida"""
    if not all_rows:
        return None
    
    # Definir las columnas en el orden exacto requerido
    columns = [
        'Cuenta',
        'Comprobante',
        'Fecha(mm/dd/yyyy)',
        'Documento',
        'Documento Ref.',
        'Nit',
        'Detalle',
        'Tipo',
        'Valor',
        'Base',
        'Centro de Costo',
        'Trans. Ext',
        'Plazo',
        'Docto Electrónico'
    ]

    # Crear el DataFrame con las columnas definidas
    df = pd.DataFrame(all_rows, columns=columns)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Facturas')
        
        # Obtener la hoja de trabajo para formatear
        worksheet = writer.sheets['Facturas']
        
        # Ajustar el ancho de las columnas automáticamente
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

@app.route('/test')
def test():
    """Ruta de prueba para verificar que el servidor esté funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'timestamp': pd.Timestamp.now().isoformat()
    })

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            print("Iniciando procesamiento POST")
            
            if 'zip_files' not in request.files:
                print("No se encontraron archivos en la request")
                return render_template('index.html', results=None, error="No se seleccionaron archivos")
            
            zip_files = request.files.getlist('zip_files')
            print(f"Archivos recibidos: {len(zip_files)}")
            
            if not zip_files or all(f.filename == '' for f in zip_files):
                print("No hay archivos válidos")
                return render_template('index.html', results=None, error="No se seleccionaron archivos")
            
            # Verificar que todos los archivos sean ZIP
            for file in zip_files:
                if not file.filename.lower().endswith('.zip'):
                    print(f"Archivo no válido: {file.filename}")
                    return render_template('index.html', results=None, error=f"El archivo {file.filename} no es un archivo ZIP válido")
            
            print("Iniciando procesamiento de archivos...")
            
            # Procesar archivos para Excel
            all_rows = process_files_for_excel(zip_files)
            
            print(f"Registros procesados: {len(all_rows)}")
            
            if not all_rows:
                print("No se encontraron datos válidos")
                return render_template('index.html', results=None, error="No se encontraron datos válidos en los archivos")
            
            # Generar Excel
            print("Generando archivo Excel...")
            excel_output = generate_excel(all_rows)
            
            if excel_output:
                # Generar ID único para el archivo
                file_id = str(uuid.uuid4())
                
                # Guardar archivo temporal
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                temp_file.write(excel_output.getvalue())
                temp_file.close()
                
                # Almacenar referencia al archivo temporal
                temp_files[file_id] = temp_file.name
                
                print(f"Archivo Excel generado: {temp_file.name}")
                print(f"ID del archivo: {file_id}")
                
                # Mostrar resultados en HTML con botón de descarga
                return render_template('index.html', 
                                     results=all_rows, 
                                     excel_file_id=file_id,
                                     success=True)
            else:
                print("Error generando Excel")
                return render_template('index.html', results=None, error="Error generando el archivo Excel")
                
        except Exception as e:
            print(f"Error en el procesamiento: {str(e)}")
            import traceback
            traceback.print_exc()
            return render_template('index.html', results=None, error=f"Error en el procesamiento: {str(e)}")
    
    return render_template('index.html', results=None)

@app.route('/download_excel/<file_id>')
def download_excel(file_id):
    """Descarga el archivo Excel generado"""
    try:
        if file_id in temp_files:
            file_path = temp_files[file_id]
            if os.path.exists(file_path):
                return send_file(file_path, 
                                as_attachment=True, 
                                download_name='facturas_procesadas.xlsx',
                                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            else:
                # Limpiar referencia si el archivo no existe
                del temp_files[file_id]
                return jsonify({'error': 'Archivo no encontrado'}), 404
        else:
            return jsonify({'error': 'ID de archivo inválido'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/cleanup/<file_id>')
def cleanup_file(file_id):
    """Limpia archivos temporales después de la descarga"""
    try:
        if file_id in temp_files:
            file_path = temp_files[file_id]
            if os.path.exists(file_path):
                os.unlink(file_path)
            del temp_files[file_id]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5051, host='0.0.0.0')
