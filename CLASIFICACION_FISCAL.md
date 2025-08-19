# Clasificación Fiscal de Items en Facturación Electrónica Colombiana

## Diferenciación entre Items Exentos y Excluidos

### **Items Exentos**
Los items **exentos** son aquellos que:
- ✅ **Sí aparecen** en las secciones de impuestos del XML
- ✅ Tienen una **base gravable** (`TaxableAmount`)
- ✅ Tienen un **porcentaje de 0%** o no generan impuesto
- ✅ Se incluyen en el cálculo de la base gravable total
- ✅ Aparecen en reportes fiscales

**Ejemplo en XML:**
```xml
<cac:TaxTotal>
    <cbc:TaxableAmount currencyID="COP">100000.00</cbc:TaxableAmount>
    <cbc:TaxAmount currencyID="COP">0.00</cbc:TaxAmount>
    <cac:TaxCategory>
        <cbc:Percent>0.00</cbc:Percent>
        <cac:TaxScheme>
            <cbc:ID>01</cbc:ID>
            <cbc:Name>IVA</cbc:Name>
        </cac:TaxScheme>
    </cac:TaxCategory>
</cac:TaxTotal>
```

### **Items Excluidos**
Los items **excluidos** son aquellos que:
- ❌ **No aparecen** en las secciones de impuestos del XML
- ❌ No tienen elementos `<cac:TaxTotal>` asociados
- ❌ No se incluyen en la base gravable para ningún impuesto
- ❌ No aparecen en reportes fiscales
- ❌ No están sujetos a ningún tipo de impuesto

**Ejemplo:** Un item sin sección de impuestos en el XML.

## Códigos de Impuestos DIAN

| Código | Impuesto | Descripción |
|--------|----------|-------------|
| 01 | IVA | Impuesto al Valor Agregado |
| 02 | ICA | Impuesto de Industria y Comercio |
| 06 | ReteRenta | Retención de Renta |
| 07-34 | ReteIVA | Retención de IVA (varios códigos) |
| 35 | ICUI | Impuesto de Consumo de Industria y Comercio |
| 36-50 | INC | Impuestos Nacionales de Consumo |

## Lógica de Clasificación en el Código

### Función `classify_tax_status()`

```python
def classify_tax_status(tax_type, percent, tax_amount, taxable_amount):
    """
    Clasifica el estado fiscal de un item
    """
    if percent == 0.0 and taxable_amount > 0:
        return 'EXENTO'  # Item exento
    elif percent > 0.0 and tax_amount > 0:
        return 'GRAVADO'  # Item gravado
    elif percent > 0.0 and tax_amount == 0:
        return 'EXENTO'  # Item exento (porcentaje aplicado pero sin impuesto)
    elif taxable_amount == 0:
        return 'EXCLUIDO'  # Item excluido
    else:
        return 'INDEFINIDO'  # Estado no determinado
```

### Estados Fiscales

1. **GRAVADO**: Item que genera impuesto
   - Porcentaje > 0% y monto de impuesto > 0

2. **EXENTO**: Item que no genera impuesto pero está en base gravable
   - Porcentaje = 0% o monto de impuesto = 0
   - Aparece en secciones de impuestos

3. **EXCLUIDO**: Item que no está sujeto a impuestos
   - No aparece en secciones de impuestos
   - No tiene base gravable

## Columnas Agregadas al Reporte

El sistema ahora incluye las siguientes columnas adicionales:

- **Estado Fiscal**: Clasificación principal del item (GRAVADO/EXENTO/EXCLUIDO)
- **Descripción Fiscal**: Descripción detallada del estado fiscal
- **Estado [Impuesto]**: Estado específico para cada tipo de impuesto
- **Descripción [Impuesto]**: Descripción específica para cada tipo de impuesto

## Ejemplos Prácticos

### Item Gravado (IVA 19%)
```xml
<cac:TaxTotal>
    <cbc:TaxableAmount>100000.00</cbc:TaxableAmount>
    <cbc:TaxAmount>19000.00</cbc:TaxAmount>
    <cbc:Percent>19.00</cbc:Percent>
</cac:TaxTotal>
```
**Resultado:** GRAVADO - IVA Gravado (19%)

### Item Exento (IVA 0%)
```xml
<cac:TaxTotal>
    <cbc:TaxableAmount>100000.00</cbc:TaxableAmount>
    <cbc:TaxAmount>0.00</cbc:TaxAmount>
    <cbc:Percent>0.00</cbc:Percent>
</cac:TaxTotal>
```
**Resultado:** EXENTO - IVA Exento (0%)

### Item Excluido
```xml
<!-- Sin sección de impuestos -->
<cac:Item>
    <cbc:Description>Producto excluido</cbc:Description>
    <!-- No hay TaxTotal -->
</cac:Item>
```
**Resultado:** EXCLUIDO - Item excluido (sin impuestos)

## Validaciones Importantes

1. **Consistencia**: La suma de bases gravables debe coincidir con el total de la factura
2. **Completitud**: Todos los items deben tener una clasificación fiscal válida
3. **Normativa**: Los códigos de impuestos deben cumplir con la normativa DIAN
4. **Reportes**: Los items exentos y excluidos se reportan de manera diferente en declaraciones fiscales


