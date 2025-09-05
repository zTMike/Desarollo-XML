# Consolidación de IVAs por Factura y Tipo ✅

## Problema Identificado

Las facturas XML contienen múltiples líneas de impuestos del mismo tipo (IVA, ICE, etc.) con diferentes porcentajes. Para un mejor análisis fiscal, se requiere consolidar estos impuestos por tipo y porcentaje dentro de cada factura.

## Objetivo

Consolidar los impuestos de cada factura según su tipo, agrupando líneas con el mismo tipo de impuesto y porcentaje, sumando los montos correspondientes.

## Funcionalidad Implementada

### **Método `consolidate_taxes_by_type()`**

Este método agrupa las líneas de impuestos por:
- **Tipo de impuesto** (IVA, ICE, IRBPNR, etc.)
- **Porcentaje** (12%, 0%, 300%, etc.)

Y suma los montos correspondientes:
- **Monto del impuesto** (`TaxAmount`)
- **Base imponible** (`TaxableAmount`)

### **Ejemplo de Consolidación**

#### **Antes de la consolidación:**
```python
# Líneas individuales de una factura
tax_info = [
    {
        'TaxSchemeName': 'IVA',
        'Percent': '12.00',
        'TaxAmount': '120.00',
        'TaxableAmount': '1000.00'
    },
    {
        'TaxSchemeName': 'IVA',
        'Percent': '12.00',
        'TaxAmount': '60.00',
        'TaxableAmount': '500.00'
    },
    {
        'TaxSchemeName': 'ICE',
        'Percent': '300.00',
        'TaxAmount': '300.00',
        'TaxableAmount': '100.00'
    },
    {
        'TaxSchemeName': 'IVA',
        'Percent': '0.00',
        'TaxAmount': '0.00',
        'TaxableAmount': '200.00'
    }
]
```

#### **Después de la consolidación:**
```python
# Impuestos consolidados por tipo y porcentaje
consolidated_taxes = [
    {
        'TaxSchemeName': 'IVA',
        'Percent': '12.00',
        'consolidated_tax_amount': '180.00',  # 120.00 + 60.00
        'consolidated_base_amount': '1500.00',  # 1000.00 + 500.00
        'line_count': 2
    },
    {
        'TaxSchemeName': 'ICE',
        'Percent': '300.00',
        'consolidated_tax_amount': '300.00',
        'consolidated_base_amount': '100.00',
        'line_count': 1
    },
    {
        'TaxSchemeName': 'IVA',
        'Percent': '0.00',
        'consolidated_tax_amount': '0.00',
        'consolidated_base_amount': '200.00',
        'line_count': 1
    }
]
```

## Estructura de Datos Consolidada

### **Campos de la consolidación:**
- **`TaxSchemeName`**: Nombre del tipo de impuesto (IVA, ICE, etc.)
- **`Percent`**: Porcentaje del impuesto
- **`consolidated_tax_amount`**: Suma total del monto del impuesto
- **`consolidated_base_amount`**: Suma total de la base imponible
- **`line_count`**: Número de líneas consolidadas

### **Clave de consolidación:**
```python
consolidation_key = f"{scheme_name}_{percent}"
# Ejemplo: "IVA_12.00", "ICE_300.00", "IVA_0.00"
```

## Descripción de Impuestos Consolidados

### **Método `create_consolidated_tax_description()`**

Genera descripciones que indican cuando un impuesto ha sido consolidado:

#### **Ejemplos de descripciones:**
- **IVA consolidado**: `"IVA - Impuesto al Valor Agregado (12.00%) - Consolidado (3 líneas)"`
- **ICE único**: `"ICE - Impuesto al Valor Agregado (300.00%)"`
- **IVA exento**: `"IVA - Impuesto al Valor Agregado (0.00%) - Consolidado (2 líneas)"`

## Beneficios de la Consolidación

### ✅ **Análisis Fiscal Simplificado**
- Una sola línea por tipo de impuesto y porcentaje
- Facilita el análisis de totales por factura
- Reduce la complejidad del reporte Excel

### ✅ **Mejor Legibilidad**
- Descripciones claras que indican consolidación
- Conteo de líneas consolidadas
- Estructura más limpia en el Excel

### ✅ **Precisión en Totales**
- Sumas exactas por tipo de impuesto
- Eliminación de duplicados
- Cálculos más precisos

### ✅ **Eficiencia en Procesamiento**
- Menos filas en el Excel final
- Procesamiento más rápido
- Menor uso de memoria

## Implementación Técnica

### **Flujo de Procesamiento:**

1. **Extracción de datos fiscales** → `extract_tax_information()`
2. **Consolidación por tipo** → `consolidate_taxes_by_type()`
3. **Clasificación fiscal** → `classify_tax_type()`
4. **Creación de descripción** → `create_consolidated_tax_description()`
5. **Generación de filas** → Estructura final para Excel

### **Validaciones:**
- Manejo de errores en conversión de tipos
- Validación de montos numéricos
- Logging detallado del proceso

## Ejemplo de Resultado en Excel

### **Antes (sin consolidación):**
| Documento | Detalle | Tipo | Valor | Base |
|-----------|---------|------|-------|------|
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) | GRAVADO | 120.00 | 1000.00 |
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) | GRAVADO | 60.00 | 500.00 |
| 001-001-001 | ICE - Impuesto al Valor Agregado (300.00%) | GRAVADO | 300.00 | 100.00 |

### **Después (con consolidación):**
| Documento | Detalle | Tipo | Valor | Base |
|-----------|---------|------|-------|------|
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) - Consolidado (2 líneas) | GRAVADO | 180.00 | 1500.00 |
| 001-001-001 | ICE - Impuesto al Valor Agregado (300.00%) | GRAVADO | 300.00 | 100.00 |

## Configuración y Personalización

### **Tipos de Impuesto Soportados:**
- **IVA**: Impuesto al Valor Agregado
- **ICE**: Impuesto al Consumo Especial
- **IRBPNR**: Impuesto a la Renta de Bienes Personales
- **ISD**: Impuesto a la Salida de Divisas
- **Otros**: Cualquier tipo definido en el XML

### **Porcentajes Comunes:**
- **IVA**: 0%, 12%, 14%, 15%
- **ICE**: 100%, 200%, 300%, etc.
- **IRBPNR**: 1%, 2%, etc.

## Estado Actual

✅ **Consolidación implementada**: Los IVAs se consolidan por tipo y porcentaje
✅ **Descripciones mejoradas**: Indican cuando hay consolidación
✅ **Totales precisos**: Sumas exactas por tipo de impuesto
✅ **Estructura optimizada**: Menos filas, mejor legibilidad
✅ **Logging detallado**: Seguimiento del proceso de consolidación

---

**🎉 ¡Consolidación de IVAs implementada exitosamente!**

Ahora cada factura mostrará una línea consolidada por cada tipo de impuesto y porcentaje, facilitando el análisis fiscal y mejorando la legibilidad del reporte Excel.
