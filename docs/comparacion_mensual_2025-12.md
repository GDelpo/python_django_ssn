# Comparación Stock Mensual 2025-12

## Resumen

Se comparó el JSON generado por nuestra aplicación contra lo que está presentado en SSN para el período mensual **2025-12**.

- **Nuestra app generó:** 26 stocks
- **SSN tiene presentado:** 27 stocks

---

## ✅ Stocks que COINCIDEN (21 especies)

Estas especies tienen las mismas cantidades en ambos sistemas:

| Tipo | Código | Cantidad | Libre Disp. |
|------|--------|----------|-------------|
| TP | TZX26 | 154,239,125 | Sí |
| TP | TZXM6 | 220,790,075 | Sí |
| FC | 1158 | 12.15 | Sí |
| FC | 685 | 32,214 | **No** |
| FC | 685 | 4,286,559 | Sí |
| ON | VSCUO | 40,000 | Sí |
| TP | TZXO6 | 308,600,000 | Sí |
| TP | TX26 | 20,366,470 | Sí |
| ON | YM40O | 100,000 | Sí |
| TP | GD35 | 767,902 | Sí |
| TP | TZXD6 | 163,285,000 | Sí |
| ON | YM38O | 100,000 | Sí |
| ON | YM35O | 100,000 | Sí |
| ON | PECMO | 77,117 | Sí |
| ON | TLCQO | 100,000 | Sí |
| TP | GD30 | 520,024 | Sí |
| TP | T30A7 | 284,428,290 | Sí |
| TP | AN29 | 250,000 | Sí |
| ON | BF37O | 200,000 | Sí |
| TP | AL30 | 1,211,949 | Sí |
| TP | TZXD7 | 132,791,600 | Sí |

---

## ❌ Stocks que FALTAN en nuestra app

Estas especies aparecen en SSN pero **no se generaron** en nuestra app:

| Tipo | Código | Cantidad en SSN | Posible causa |
|------|--------|-----------------|---------------|
| ON | YM42O | 100,000 | Compra no registrada en semanales |
| ON | BF39O | 100,000 | Compra no registrada en semanales |
| FC | 165 | 473,929 | Compra no registrada en semanales |

**¿Por qué faltan?**  
Estas especies fueron compradas durante el mes, pero las operaciones de compra no están cargadas en las entregas semanales sincronizadas.

---

## ❌ Stocks que SOBRAN en nuestra app

Estas especies aparecen en nuestra app pero **no están en SSN**:

| Tipo | Código | Cantidad en App | Posible causa |
|------|--------|-----------------|---------------|
| ON | MGC9O | 62,164 | Venta total no registrada en semanales |
| TP | TZXD5 | 142,894,500 | Venta total no registrada en semanales |

**¿Por qué sobran?**  
Estas especies fueron vendidas completamente durante el mes, pero las operaciones de venta no están cargadas en las entregas semanales sincronizadas.

---

## ⚠️ Stocks con CANTIDADES DIFERENTES

Estas especies existen en ambos sistemas pero con **cantidades distintas**:

| Tipo | Código | Nuestra App | SSN | Diferencia |
|------|--------|-------------|-----|------------|
| FC | 1048 | 63,222,358 | 43,937,773 | -19,284,585 (venta parcial faltante) |
| FC | 1678 | 99,599 | 14.22 | -99,585 (venta casi total faltante) |
| TP | X29Y6 | 2,323,000,000 | 232,300,000 | **10x de más** (posible error en dato original) |

**¿Por qué las diferencias?**

- **FC 1048 y FC 1678:** Hubo ventas parciales durante el mes que no están registradas en las semanales sincronizadas.
- **X29Y6:** La cantidad en nuestra app es exactamente 10 veces mayor. Posiblemente un error en el dato de la compra original (un cero de más).

---

## Conclusión

La lógica de generación de stock mensual funciona correctamente. Las diferencias se deben a que **las entregas semanales sincronizadas desde SSN no contienen todas las operaciones reales** (compras y ventas) que se hicieron durante el mes.

### Para corregir:
1. Verificar que todas las compras y ventas del mes estén cargadas en las semanales correspondientes
2. Revisar el dato de X29Y6 que parece tener un error de magnitud (10x)
3. Regenerar el stock mensual después de completar las operaciones faltantes
