# Separación de Impuestos por Tipo ✅

## Problema Identificado

Las facturas XML contienen múltiples tipos de impuestos (IVA, ICE, IRBPNR, ISD, etc.) que necesitan ser separados y mostrados en líneas individuales para un mejor análisis fiscal y contable.

## Objetivo

Separar los diferentes tipos de impuestos en líneas individuales, manteniendo la consolidación por tipo y porcentaje, pero creando descripciones específicas para cada tipo de impuesto.

## Funcionalidad Implementada

### **Método `separate_taxes_by_type()`**

Este método:
- **Agrupa por tipo de impuesto** (cualquier tipo encontrado en el XML)
- **Consolida por porcentaje** dentro de cada tipo
- **Crea líneas separadas** para cada tipo de impuesto
- **Ordena por tipo** para mejor legibilidad

### **Método `create_separated_tax_description()`**

Genera descripciones dinámicas para cualquier tipo de impuesto encontrado:

#### **Tipos de Impuesto Capturados:**

- **Todos los tipos** que aparezcan en el XML de la factura
- **Impuestos por línea** de producto/servicio
- **Impuestos a nivel documento** (totales generales)
- **Cualquier esquema fiscal** definido en el XML

## Ejemplo de Separación

### **Antes (todos los impuestos mezclados):**
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
        'TaxSchemeName': 'ICE',
        'Percent': '300.00',
        'TaxAmount': '300.00',
        'TaxableAmount': '100.00'
    },
    {
        'TaxSchemeName': 'IVA',
        'Percent': '12.00',
        'TaxAmount': '60.00',
        'TaxableAmount': '500.00'
    },
    {
        'TaxSchemeName': 'IRBPNR',
        'Percent': '1.00',
        'TaxAmount': '15.00',
        'TaxableAmount': '1500.00'
    }
]
```

### **Después (impuestos separados por tipo):**
```python
# Impuestos separados por tipo
separated_taxes = [
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
        'TaxSchemeName': 'IRBPNR',
        'Percent': '1.00',
        'consolidated_tax_amount': '15.00',
        'consolidated_base_amount': '1500.00',
        'line_count': 1
    }
]
```

## Descripciones Dinámicas por Tipo

### **Formato General:**
- `"NOMBRE_IMPUESTO - Impuesto (PORCENTAJE%)"`
- `"NOMBRE_IMPUESTO - Impuesto (PORCENTAJE%) - Consolidado (N líneas)"`

### **Ejemplos de Descripciones:**
- `"IVA - Impuesto (12.00%)"`
- `"ICE - Impuesto (300.00%) - Consolidado (2 líneas)"`
- `"IRBPNR - Impuesto (1.00%)"`
- `"ISD - Impuesto (5.00%)"`
- `"CUALQUIER_OTRO_IMPUESTO - Impuesto (10.00%) - Consolidado (3 líneas)"`

### **Características:**
- **Dinámico**: Se adapta a cualquier nombre de impuesto encontrado
- **Flexible**: Captura cualquier tipo de esquema fiscal
- **Consolidado**: Indica cuando hay múltiples líneas del mismo tipo
- **Porcentaje**: Muestra el porcentaje específico del impuesto

## Ejemplo de Resultado en Excel

### **Antes (sin separación):**
| Documento | Detalle | Tipo | Valor | Base |
|-----------|---------|------|-------|------|
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) | GRAVADO | 120.00 | 1000.00 |
| 001-001-001 | ICE - Impuesto al Valor Agregado (300.00%) | GRAVADO | 300.00 | 100.00 |
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) | GRAVADO | 60.00 | 500.00 |

### **Después (con separación):**
| Documento | Detalle | Tipo | Valor | Base |
|-----------|---------|------|-------|------|
| 001-001-001 | IVA - Impuesto al Valor Agregado (12.00%) - Consolidado (2 líneas) | GRAVADO | 180.00 | 1500.00 |
| 001-001-001 | ICE - Impuesto al Consumo Especial (300.00%) | GRAVADO | 300.00 | 100.00 |
| 001-001-001 | IRBPNR - Impuesto a la Renta de Bienes Personales (1.00%) | GRAVADO | 15.00 | 1500.00 |

## Beneficios de la Separación

### ✅ **Análisis Fiscal Detallado**
- Cada tipo de impuesto en línea separada
- Facilita el análisis por tipo de impuesto
- Mejor control contable

### ✅ **Descripciones Específicas**
- Nombres correctos para cada tipo de impuesto
- Información clara sobre el tipo de impuesto
- Mejor comprensión del reporte

### ✅ **Ordenamiento Lógico**
- Impuestos ordenados por tipo
- Mejor legibilidad del Excel
- Facilita la búsqueda y filtrado

### ✅ **Cumplimiento Fiscal**
- Separación clara de obligaciones fiscales
- Facilita la declaración de impuestos
- Mejor auditoría fiscal

## Configuración y Personalización

### **Tipos de Impuesto Capturados:**
- **Todos los tipos** que aparezcan en el XML de la factura
- **Impuestos por línea** de producto/servicio
- **Impuestos a nivel documento** (totales generales)
- **Cualquier esquema fiscal** definido en el XML

### **Extracción Completa:**
- **Por líneas**: Cada línea de producto/servicio puede tener múltiples impuestos
- **Por documento**: Impuestos aplicados a nivel de factura completa
- **Dinámico**: Se adapta automáticamente a cualquier estructura de impuestos
- **Flexible**: Captura cualquier nombre o esquema de impuesto

## Estado Actual

✅ **Separación implementada**: Los impuestos se separan por tipo
✅ **Descripciones dinámicas**: Se adapta a cualquier tipo de impuesto encontrado
✅ **Consolidación mantenida**: Se mantiene la consolidación por porcentaje
✅ **Ordenamiento**: Los impuestos se ordenan por tipo
✅ **Extracción completa**: Captura impuestos por línea y por documento
✅ **Flexibilidad total**: Procesa cualquier esquema fiscal del XML
✅ **Logging detallado**: Seguimiento del proceso de separación

---

**🎉 ¡Separación completa de impuestos implementada exitosamente!**

Ahora el sistema captura y procesa **todos los tipos de impuestos** que aparezcan en los XML de facturas, sin limitaciones. Cada tipo de impuesto aparecerá en líneas separadas con descripciones dinámicas, facilitando el análisis fiscal completo y mejorando la claridad del reporte Excel.
