import pandas as pd

CUENTAS_ACTIVO = ["Efectivo", "Clientes", "Inventario de materiales", "Inventario de productos terminados", "Terreno", "Planta y equipo"]
CUENTAS_PASIVO_CAPITAL = ["Proveedores", "Documentos por pagar", "ISR por pagar", "Préstamos bancarios", "Capital contribuido", "Capital ganado"]


def formato(valor):
    if valor is None:
        return ""
    valor = round(valor, 2)
    if valor == int(valor):
        return f"{valor:,.0f}"
    return f"{valor:,.2f}"


def mostrar_tabla(titulo, filas, columnas):
    tabla = {}
    for etiqueta, valores in filas.items():
        tabla[etiqueta] = []
        for valor in valores:
            tabla[etiqueta].append(formato(valor))
    print()
    print(titulo)
    print("-" * len(titulo))
    print(pd.DataFrame.from_dict(tabla, orient="index", columns=columnas).to_string())


def con_total(valores):
    return valores + [sum(valores)]


def en_columna(renglones):
    filas = {}
    for etiqueta, valor in renglones.items():
        filas[etiqueta] = [valor]
    return filas


def pedir_numero(mensaje, minimo=0):
    while True:
        texto = input(mensaje).replace(",", "")
        try:
            valor = float(texto)
        except ValueError:
            print("  Escribe un número válido.")
            continue
        if valor < minimo:
            print("  No puede ser menor que", minimo)
            continue
        return valor


def pedir_entero(mensaje, minimo=0):
    while True:
        valor = pedir_numero(mensaje, minimo)
        if valor == int(valor):
            return int(valor)
        print("  Escribe un número entero.")


def pedir_porcentaje(mensaje):
    while True:
        valor = pedir_numero(mensaje + " (0 a 100): ")
        if valor <= 100:
            return valor / 100
        print("  No puede ser mayor que 100.")


def pedir_texto(mensaje, nombres_usados=()):
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            print("  No puede quedar vacío.")
        elif texto in nombres_usados:
            print("  Ese nombre ya existe.")
        else:
            return texto


def pedir_si_no(mensaje):
    while True:
        respuesta = input(mensaje + " (s/n): ").strip().lower()
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        print("  Responde s o n.")


def pedir_por_periodo(mensaje, periodos):
    valores = []
    for periodo in periodos:
        valores.append(pedir_numero(f"{mensaje} ({periodo}): "))
    return valores


def capturar_materiales(periodos):
    materiales = {}
    cantidad = pedir_entero("\n¿Cuántos materiales usa la empresa? ", 1)
    for i in range(cantidad):
        nombre = pedir_texto(f"\nNombre del material {i + 1}: ", materiales)
        materiales[nombre] = {
            "inventario_inicial": pedir_numero("  Inventario inicial: "),
            "inventario_final": pedir_por_periodo("  Inventario final deseado", periodos),
            "costo": pedir_por_periodo("  Costo unitario", periodos),
        }
    return materiales


def capturar_productos(periodos, materiales):
    productos = {}
    cantidad = pedir_entero("\n¿Cuántos productos vende la empresa? ", 1)
    for i in range(cantidad):
        nombre = pedir_texto(f"\nNombre del producto {i + 1}: ", productos)
        precio = pedir_por_periodo("  Precio de venta", periodos)
        unidades_vender = pedir_por_periodo("  Unidades a vender", periodos)
        inventario_inicial = pedir_numero("  Inventario inicial: ")
        inventario_final = pedir_por_periodo("  Inventario final deseado", periodos)
        consumo = {}
        for material in materiales:
            consumo[material] = pedir_numero(f"  Material {material} por unidad: ")
        horas = pedir_numero("  Horas de mano de obra por unidad: ")
        productos[nombre] = {
            "precio": precio,
            "unidades_vender": unidades_vender,
            "inventario_inicial": inventario_inicial,
            "inventario_final": inventario_final,
            "consumo": consumo,
            "horas": horas,
        }
    return productos


def capturar_gastos(tipo, periodos):
    gastos = {}
    cantidad = pedir_entero(f"\n¿Cuántos conceptos de {tipo} hay? ")
    for i in range(cantidad):
        nombre = pedir_texto(f"\nConcepto {i + 1}: ", gastos)
        if pedir_si_no("  ¿El monto es anual?"):
            monto_anual = pedir_numero("  Monto anual: ")
            montos = []
            for periodo in periodos:
                montos.append(monto_anual / len(periodos))
        else:
            montos = pedir_por_periodo("  Monto", periodos)
        es_depreciacion = pedir_si_no("  ¿Es depreciación?")
        gastos[nombre] = {"montos": montos, "es_depreciacion": es_depreciacion}
    return gastos


def capturar_otras_cuentas(tipo):
    cuentas = {}
    cantidad = pedir_entero(f"¿Cuántas otras cuentas de {tipo} tiene? ")
    for i in range(cantidad):
        nombre = pedir_texto("  Nombre de la cuenta: ", cuentas)
        cuentas[nombre] = pedir_numero("  Saldo: ")
    return cuentas


def capturar_balance():
    while True:
        print("\n--- BALANCE GENERAL INICIAL ---")
        balance = {}
        for cuenta in CUENTAS_ACTIVO:
            balance[cuenta] = pedir_numero(cuenta + ": ")
        balance["Depreciación acumulada"] = pedir_numero("Depreciación acumulada: ")
        balance["otros_activos"] = capturar_otras_cuentas("activo circulante")
        for cuenta in CUENTAS_PASIVO_CAPITAL:
            balance[cuenta] = pedir_numero(cuenta + ": ")
        balance["otros_pasivos"] = capturar_otras_cuentas("pasivo a corto plazo")

        activo = sum(balance["otros_activos"].values()) - balance["Depreciación acumulada"]
        for cuenta in CUENTAS_ACTIVO:
            activo = activo + balance[cuenta]

        pasivo_capital = sum(balance["otros_pasivos"].values())
        for cuenta in CUENTAS_PASIVO_CAPITAL:
            pasivo_capital = pasivo_capital + balance[cuenta]

        if round(activo - pasivo_capital, 2) == 0:
            print("El balance inicial cuadra:", formato(activo))
            return balance
        print("No cuadra. Activo:", formato(activo), "| Pasivo + capital:", formato(pasivo_capital))
        print("Vuelve a capturarlo.")


def capturar_politicas():
    print("\n--- POLÍTICAS ---")
    return {
        "cobro_saldo_clientes": pedir_porcentaje("Porcentaje a cobrar del saldo inicial de clientes"),
        "cobro_ventas": pedir_porcentaje("Porcentaje a cobrar de las ventas del año"),
        "pago_saldo_proveedores": pedir_porcentaje("Porcentaje a pagar del saldo inicial de proveedores"),
        "pago_compras": pedir_porcentaje("Porcentaje a pagar de las compras del año"),
        "pago_isr_anterior": pedir_porcentaje("Porcentaje a pagar del ISR por pagar inicial"),
        "tasa_isr": pedir_porcentaje("Tasa de ISR"),
        "tasa_ptu": pedir_porcentaje("Tasa de PTU"),
        "compra_activo_fijo": pedir_numero("Compra de activo fijo en el año: "),
    }


def capturar_datos():
    print("\n--- CONFIGURACIÓN ---")
    empresa = pedir_texto("Nombre de la empresa: ")
    anio = pedir_entero("Año a presupuestar: ", 1900)
    periodos = []
    cantidad_periodos = pedir_entero("¿Cuántos periodos tendrá el presupuesto? ", 1)
    for i in range(cantidad_periodos):
        periodos.append(pedir_texto(f"Nombre del periodo {i + 1}: ", periodos))

    materiales = capturar_materiales(periodos)
    productos = capturar_productos(periodos, materiales)
    print("\n--- MANO DE OBRA ---")
    cuota_hora = pedir_por_periodo("Cuota por hora", periodos)
    gastos_indirectos = capturar_gastos("gastos indirectos de fabricación", periodos)
    gastos_operacion = capturar_gastos("gastos de operación", periodos)
    porcentaje_comisiones = pedir_porcentaje("\nPorcentaje de comisiones sobre ventas")
    balance = capturar_balance()
    politicas = capturar_politicas()

    return {
        "empresa": empresa,
        "anio": anio,
        "periodos": periodos,
        "materiales": materiales,
        "productos": productos,
        "cuota_hora": cuota_hora,
        "gastos_indirectos": gastos_indirectos,
        "gastos_operacion": gastos_operacion,
        "porcentaje_comisiones": porcentaje_comisiones,
        "balance": balance,
        "politicas": politicas,
    }


def cedula_ventas(datos):
    periodos = datos["periodos"]
    filas = {}
    total_ventas = [0] * len(periodos)
    for nombre, producto in datos["productos"].items():
        importe = []
        for i in range(len(periodos)):
            importe.append(producto["unidades_vender"][i] * producto["precio"][i])
            total_ventas[i] = total_ventas[i] + importe[i]
        filas[nombre + " - Unidades a vender"] = con_total(producto["unidades_vender"])
        filas[nombre + " - Precio de venta"] = producto["precio"] + [None]
        filas[nombre + " - Importe de venta"] = con_total(importe)
    filas["TOTAL DE VENTAS"] = con_total(total_ventas)
    return filas, total_ventas


def cedula_clientes(datos, ventas_anuales):
    politicas = datos["politicas"]
    saldo_inicial = datos["balance"]["Clientes"]
    total_clientes = saldo_inicial + ventas_anuales
    cobranza_saldo = saldo_inicial * politicas["cobro_saldo_clientes"]
    cobranza_ventas = ventas_anuales * politicas["cobro_ventas"]
    total_entradas = cobranza_saldo + cobranza_ventas
    saldo_final = total_clientes - total_entradas
    renglones = {
        "Saldo inicial de clientes": saldo_inicial,
        "(+) Ventas del año": ventas_anuales,
        "(=) Total de clientes": total_clientes,
        "Cobranza del saldo inicial": cobranza_saldo,
        "Cobranza de ventas del año": cobranza_ventas,
        "(=) Total de entradas": total_entradas,
        "Saldo final de clientes": saldo_final,
    }
    return renglones


def cedula_produccion(datos):
    periodos = datos["periodos"]
    filas = {}
    unidades_producir = {}
    for nombre, producto in datos["productos"].items():
        total_unidades = []
        inventario_inicial = []
        producir = []
        inicial = producto["inventario_inicial"]
        for i in range(len(periodos)):
            final = producto["inventario_final"][i]
            total_unidades.append(producto["unidades_vender"][i] + final)
            inventario_inicial.append(inicial)
            producir.append(total_unidades[i] - inicial)
            inicial = final
        unidades_producir[nombre] = producir

        vender_anual = sum(producto["unidades_vender"])
        final_anual = producto["inventario_final"][-1]
        filas[nombre + " - Unidades a vender"] = con_total(producto["unidades_vender"])
        filas[nombre + " - (+) Inventario final"] = producto["inventario_final"] + [final_anual]
        filas[nombre + " - (=) Total de unidades"] = total_unidades + [vender_anual + final_anual]
        filas[nombre + " - (-) Inventario inicial"] = inventario_inicial + [inventario_inicial[0]]
        filas[nombre + " - (=) Unidades a producir"] = con_total(producir)
    return filas, unidades_producir


def cedula_requerimientos(datos, unidades_producir):
    periodos = datos["periodos"]
    filas = {}
    total_requerido = {}
    for material in datos["materiales"]:
        total_requerido[material] = [0] * len(periodos)

    for nombre, producto in datos["productos"].items():
        for material in datos["materiales"]:
            cantidades = []
            for i in range(len(periodos)):
                cantidades.append(unidades_producir[nombre][i] * producto["consumo"][material])
                total_requerido[material][i] = total_requerido[material][i] + cantidades[i]
            filas[nombre + " - Material " + material] = con_total(cantidades)

    for material in total_requerido:
        filas["TOTAL MATERIAL " + material] = con_total(total_requerido[material])
    return filas, total_requerido


def cedula_compras(datos, total_requerido):
    periodos = datos["periodos"]
    filas = {}
    total_compras = [0] * len(periodos)
    for nombre, material in datos["materiales"].items():
        requerido = total_requerido[nombre]
        total_material = []
        inventario_inicial = []
        comprar = []
        importe = []
        inicial = material["inventario_inicial"]
        for i in range(len(periodos)):
            final = material["inventario_final"][i]
            total_material.append(requerido[i] + final)
            inventario_inicial.append(inicial)
            comprar.append(total_material[i] - inicial)
            importe.append(comprar[i] * material["costo"][i])
            total_compras[i] = total_compras[i] + importe[i]
            inicial = final

        final_anual = material["inventario_final"][-1]
        filas[nombre + " - Requerimiento"] = con_total(requerido)
        filas[nombre + " - (+) Inventario final"] = material["inventario_final"] + [final_anual]
        filas[nombre + " - (=) Total de material"] = total_material + [sum(requerido) + final_anual]
        filas[nombre + " - (-) Inventario inicial"] = inventario_inicial + [inventario_inicial[0]]
        filas[nombre + " - (=) Material a comprar"] = con_total(comprar)
        filas[nombre + " - Costo de compra"] = material["costo"] + [None]
        filas[nombre + " - Importe de compra"] = con_total(importe)
    filas["COMPRAS TOTALES"] = con_total(total_compras)
    return filas, total_compras


def cedula_proveedores(datos, compras_anuales):
    politicas = datos["politicas"]
    saldo_inicial = datos["balance"]["Proveedores"]
    total_proveedores = saldo_inicial + compras_anuales
    pago_saldo = saldo_inicial * politicas["pago_saldo_proveedores"]
    pago_compras = compras_anuales * politicas["pago_compras"]
    total_salidas = pago_saldo + pago_compras
    saldo_final = total_proveedores - total_salidas
    renglones = {
        "Saldo inicial de proveedores": saldo_inicial,
        "(+) Compras del año": compras_anuales,
        "(=) Total de proveedores": total_proveedores,
        "Pago del saldo inicial": pago_saldo,
        "Pago de compras del año": pago_compras,
        "(=) Total de salidas": total_salidas,
        "Saldo final de proveedores": saldo_final,
    }
    return renglones


def cedula_mano_obra(datos, unidades_producir):
    periodos = datos["periodos"]
    filas = {}
    total_horas = [0] * len(periodos)
    total_importe = [0] * len(periodos)
    for nombre, producto in datos["productos"].items():
        horas = []
        importe = []
        for i in range(len(periodos)):
            horas.append(unidades_producir[nombre][i] * producto["horas"])
            importe.append(horas[i] * datos["cuota_hora"][i])
            total_horas[i] = total_horas[i] + horas[i]
            total_importe[i] = total_importe[i] + importe[i]
        filas[nombre + " - Horas requeridas"] = con_total(horas)
        filas[nombre + " - Importe de mano de obra"] = con_total(importe)
    filas["Cuota por hora"] = datos["cuota_hora"] + [None]
    filas["TOTAL DE HORAS"] = con_total(total_horas)
    filas["TOTAL DE MANO DE OBRA"] = con_total(total_importe)
    return filas, total_horas, total_importe


def cedula_gastos_indirectos(datos, horas_anuales):
    periodos = datos["periodos"]
    filas = {}
    total_gastos = [0] * len(periodos)
    for nombre, gasto in datos["gastos_indirectos"].items():
        for i in range(len(periodos)):
            total_gastos[i] = total_gastos[i] + gasto["montos"][i]
        if gasto["es_depreciacion"]:
            nombre = nombre + " (no se paga)"
        filas[nombre] = con_total(gasto["montos"])
    filas["TOTAL DE GASTOS INDIRECTOS"] = con_total(total_gastos)

    if horas_anuales > 0:
        tasa = sum(total_gastos) / horas_anuales
    else:
        tasa = 0
    filas_tasa = {
        "Total de gastos indirectos": sum(total_gastos),
        "(/) Total de horas de mano de obra": horas_anuales,
        "(=) Tasa por hora": tasa,
    }
    return filas, filas_tasa, total_gastos, tasa


def cedula_gastos_operacion(datos, total_ventas):
    periodos = datos["periodos"]
    filas = {}
    total_gastos = [0] * len(periodos)
    for nombre, gasto in datos["gastos_operacion"].items():
        for i in range(len(periodos)):
            total_gastos[i] = total_gastos[i] + gasto["montos"][i]
        if gasto["es_depreciacion"]:
            nombre = nombre + " (no se paga)"
        filas[nombre] = con_total(gasto["montos"])

    comisiones = []
    for i in range(len(periodos)):
        comisiones.append(total_ventas[i] * datos["porcentaje_comisiones"])
        total_gastos[i] = total_gastos[i] + comisiones[i]
    filas["Comisiones"] = con_total(comisiones)
    filas["TOTAL DE GASTOS DE OPERACIÓN"] = con_total(total_gastos)
    return filas, total_gastos, sum(comisiones)


def cedula_costo_unitario(datos, tasa):
    tablas = []
    costos_unitarios = {}
    ultima_cuota = datos["cuota_hora"][-1]
    for nombre, producto in datos["productos"].items():
        filas = {}
        for material, info_material in datos["materiales"].items():
            costo = info_material["costo"][-1]
            cantidad = producto["consumo"][material]
            filas["Material " + material] = [costo, cantidad, costo * cantidad]
        filas["Mano de obra"] = [ultima_cuota, producto["horas"], ultima_cuota * producto["horas"]]
        filas["Gastos indirectos"] = [tasa, producto["horas"], tasa * producto["horas"]]

        costo_unitario = 0
        for fila in filas.values():
            costo_unitario = costo_unitario + fila[2]
        filas["COSTO UNITARIO"] = [None, None, costo_unitario]

        costos_unitarios[nombre] = costo_unitario
        tablas.append(("10. Costo unitario de " + nombre, filas, ["Costo", "Cantidad", "Costo unitario"]))
    return tablas, costos_unitarios


def cedula_inventarios_finales(datos, costos_unitarios):
    filas_materiales = {}
    total_materiales = 0
    for nombre, material in datos["materiales"].items():
        unidades = material["inventario_final"][-1]
        costo = material["costo"][-1]
        filas_materiales["Material " + nombre] = [unidades, costo, unidades * costo]
        total_materiales = total_materiales + unidades * costo
    filas_materiales["TOTAL"] = [None, None, total_materiales]

    filas_productos = {}
    total_productos = 0
    for nombre, producto in datos["productos"].items():
        unidades = producto["inventario_final"][-1]
        costo = costos_unitarios[nombre]
        filas_productos["Producto " + nombre] = [unidades, costo, unidades * costo]
        total_productos = total_productos + unidades * costo
    filas_productos["TOTAL"] = [None, None, total_productos]

    columnas = ["Unidades", "Costo unitario", "Costo total"]
    tablas = [
        ("11. Inventario final de materiales", filas_materiales, columnas),
        ("11. Inventario final de productos terminados", filas_productos, columnas),
    ]
    return tablas, total_materiales, total_productos


def estado_costo_produccion_ventas(datos, resumen):
    balance = datos["balance"]
    material_disponible = balance["Inventario de materiales"] + resumen["compras"]
    materiales_utilizados = material_disponible - resumen["inventario_final_materiales"]
    costo_produccion = materiales_utilizados + resumen["mano_obra"] + resumen["gastos_indirectos"]
    produccion_disponible = costo_produccion + balance["Inventario de productos terminados"]
    costo_ventas = produccion_disponible - resumen["inventario_final_productos"]
    return {
        "Inventario inicial de materiales": balance["Inventario de materiales"],
        "(+) Compras de materiales": resumen["compras"],
        "(=) Material disponible": material_disponible,
        "(-) Inventario final de materiales": resumen["inventario_final_materiales"],
        "(=) Materiales utilizados": materiales_utilizados,
        "(+) Mano de obra directa": resumen["mano_obra"],
        "(+) Gastos indirectos de fabricación": resumen["gastos_indirectos"],
        "(=) Costo de producción": costo_produccion,
        "(+) Inventario inicial de productos terminados": balance["Inventario de productos terminados"],
        "(=) Producción disponible": produccion_disponible,
        "(-) Inventario final de productos terminados": resumen["inventario_final_productos"],
        "(=) Costo de ventas": costo_ventas,
    }


def estado_resultados(datos, resumen, costo_ventas):
    politicas = datos["politicas"]
    utilidad_bruta = resumen["ventas"] - costo_ventas
    utilidad_operacion = utilidad_bruta - resumen["gastos_operacion"]
    if utilidad_operacion > 0:
        isr = utilidad_operacion * politicas["tasa_isr"]
        ptu = utilidad_operacion * politicas["tasa_ptu"]
    else:
        isr = 0
        ptu = 0
    utilidad_neta = utilidad_operacion - isr - ptu
    return {
        "Ventas": resumen["ventas"],
        "(-) Costo de ventas": costo_ventas,
        "(=) Utilidad bruta": utilidad_bruta,
        "(-) Gastos de operación": resumen["gastos_operacion"],
        "(=) Utilidad de operación": utilidad_operacion,
        "(-) ISR": isr,
        "(-) PTU": ptu,
        "(=) Utilidad neta": utilidad_neta,
    }


def estado_flujo_efectivo(datos, clientes, proveedores, resumen):
    balance = datos["balance"]
    politicas = datos["politicas"]
    efectivo_disponible = balance["Efectivo"] + clientes["(=) Total de entradas"]
    pago_isr = balance["ISR por pagar"] * politicas["pago_isr_anterior"]
    total_salidas = (
        proveedores["(=) Total de salidas"]
        + resumen["mano_obra"]
        + resumen["gastos_pagados"]
        + politicas["compra_activo_fijo"]
        + pago_isr
    )
    return {
        "Saldo inicial de efectivo": balance["Efectivo"],
        "(+) Cobranza de ventas del año": clientes["Cobranza de ventas del año"],
        "(+) Cobranza del saldo inicial": clientes["Cobranza del saldo inicial"],
        "(=) Efectivo disponible": efectivo_disponible,
        "(-) Pago de compras del año": proveedores["Pago de compras del año"],
        "(-) Pago del saldo inicial de proveedores": proveedores["Pago del saldo inicial"],
        "(-) Pago de mano de obra directa": resumen["mano_obra"],
        "(-) Pago de gastos (sin depreciación)": resumen["gastos_pagados"],
        "(-) Compra de activo fijo": politicas["compra_activo_fijo"],
        "(-) Pago de ISR del año anterior": pago_isr,
        "(=) Total de salidas": total_salidas,
        "(=) Saldo final de efectivo": efectivo_disponible - total_salidas,
    }


def balance_general(datos, clientes, proveedores, resumen, resultados, flujo):
    balance = datos["balance"]
    politicas = datos["politicas"]
    renglones = {}

    renglones["Efectivo"] = flujo["(=) Saldo final de efectivo"]
    renglones["Clientes"] = clientes["Saldo final de clientes"]
    for cuenta, saldo in balance["otros_activos"].items():
        renglones[cuenta] = saldo
    renglones["Inventario de materiales"] = resumen["inventario_final_materiales"]
    renglones["Inventario de productos terminados"] = resumen["inventario_final_productos"]
    activo_circulante = sum(renglones.values())
    renglones["Total de activo circulante"] = activo_circulante

    planta_equipo = balance["Planta y equipo"] + politicas["compra_activo_fijo"]
    depreciacion_acumulada = balance["Depreciación acumulada"] + resumen["depreciacion"]
    renglones["Terreno"] = balance["Terreno"]
    renglones["Planta y equipo"] = planta_equipo
    renglones["Depreciación acumulada"] = -depreciacion_acumulada
    activo_total = activo_circulante + balance["Terreno"] + planta_equipo - depreciacion_acumulada
    renglones["ACTIVO TOTAL"] = activo_total

    isr_por_pagar = balance["ISR por pagar"] - flujo["(-) Pago de ISR del año anterior"] + resultados["(-) ISR"]
    renglones["Proveedores"] = proveedores["Saldo final de proveedores"]
    renglones["Documentos por pagar"] = balance["Documentos por pagar"]
    renglones["ISR por pagar"] = isr_por_pagar
    renglones["PTU por pagar"] = resultados["(-) PTU"]
    pasivo_corto_plazo = (
        proveedores["Saldo final de proveedores"]
        + balance["Documentos por pagar"]
        + isr_por_pagar
        + resultados["(-) PTU"]
    )
    for cuenta, saldo in balance["otros_pasivos"].items():
        renglones[cuenta] = saldo
        pasivo_corto_plazo = pasivo_corto_plazo + saldo
    renglones["Total de pasivo a corto plazo"] = pasivo_corto_plazo
    renglones["Préstamos bancarios"] = balance["Préstamos bancarios"]
    pasivo_total = pasivo_corto_plazo + balance["Préstamos bancarios"]
    renglones["PASIVO TOTAL"] = pasivo_total

    capital_contable = balance["Capital contribuido"] + balance["Capital ganado"] + resultados["(=) Utilidad neta"]
    renglones["Capital contribuido"] = balance["Capital contribuido"]
    renglones["Capital ganado"] = balance["Capital ganado"]
    renglones["Utilidad del ejercicio"] = resultados["(=) Utilidad neta"]
    renglones["Total de capital contable"] = capital_contable
    renglones["SUMA DE PASIVO Y CAPITAL"] = pasivo_total + capital_contable
    renglones["Diferencia (debe ser 0)"] = abs(round(activo_total - pasivo_total - capital_contable, 2))
    return renglones


def calcular(datos):
    columnas = datos["periodos"] + ["Total"]
    cedulas = {}

    filas, total_ventas = cedula_ventas(datos)
    cedulas[1] = [("1. Presupuesto de ventas", filas, columnas)]

    clientes = cedula_clientes(datos, sum(total_ventas))
    cedulas[2] = [("2. Clientes y flujo de entradas", en_columna(clientes), ["Importe"])]

    filas, unidades_producir = cedula_produccion(datos)
    cedulas[3] = [("3. Presupuesto de producción", filas, columnas)]

    filas, total_requerido = cedula_requerimientos(datos, unidades_producir)
    cedulas[4] = [("4. Requerimiento de materiales", filas, columnas)]

    filas, total_compras = cedula_compras(datos, total_requerido)
    cedulas[5] = [("5. Presupuesto de compras de materiales", filas, columnas)]

    proveedores = cedula_proveedores(datos, sum(total_compras))
    cedulas[6] = [("6. Proveedores y flujo de salidas", en_columna(proveedores), ["Importe"])]

    filas, total_horas, total_mano_obra = cedula_mano_obra(datos, unidades_producir)
    cedulas[7] = [("7. Presupuesto de mano de obra directa", filas, columnas)]

    filas, filas_tasa, total_indirectos, tasa = cedula_gastos_indirectos(datos, sum(total_horas))
    cedulas[8] = [
        ("8. Presupuesto de gastos indirectos de fabricación", filas, columnas),
        ("Tasa de gastos indirectos por hora", en_columna(filas_tasa), ["Importe"]),
    ]

    filas, total_operacion, comisiones = cedula_gastos_operacion(datos, total_ventas)
    cedulas[9] = [("9. Presupuesto de gastos de operación", filas, columnas)]

    cedulas[10], costos_unitarios = cedula_costo_unitario(datos, tasa)
    cedulas[11], inventario_materiales, inventario_productos = cedula_inventarios_finales(datos, costos_unitarios)

    gastos_pagados = comisiones
    depreciacion = 0
    for grupo in [datos["gastos_indirectos"], datos["gastos_operacion"]]:
        for gasto in grupo.values():
            if gasto["es_depreciacion"]:
                depreciacion = depreciacion + sum(gasto["montos"])
            else:
                gastos_pagados = gastos_pagados + sum(gasto["montos"])

    resumen = {
        "ventas": sum(total_ventas),
        "compras": sum(total_compras),
        "mano_obra": sum(total_mano_obra),
        "gastos_indirectos": sum(total_indirectos),
        "gastos_operacion": sum(total_operacion),
        "gastos_pagados": gastos_pagados,
        "depreciacion": depreciacion,
        "inventario_final_materiales": inventario_materiales,
        "inventario_final_productos": inventario_productos,
    }

    costo = estado_costo_produccion_ventas(datos, resumen)
    resultados = estado_resultados(datos, resumen, costo["(=) Costo de ventas"])
    flujo = estado_flujo_efectivo(datos, clientes, proveedores, resumen)
    balance = balance_general(datos, clientes, proveedores, resumen, resultados, flujo)

    estados = [
        ("Estado de costo de producción y ventas", costo),
        ("Estado de resultados", resultados),
        ("Estado de flujo de efectivo", flujo),
        ("Balance general", balance),
    ]
    return cedulas, estados


def ver_cedulas(datos, cedulas):
    nombres = [
        "Ventas", "Clientes", "Producción", "Requerimiento de materiales", "Compras de materiales",
        "Proveedores", "Mano de obra directa", "Gastos indirectos de fabricación",
        "Gastos de operación", "Costo unitario", "Inventarios finales",
    ]
    while True:
        print("\n--- CÉDULAS ---")
        for i in range(len(nombres)):
            print(f"{i + 1}. {nombres[i]}")
        print("0. Regresar")
        numero = pedir_entero("Elige una cédula: ")
        if numero == 0:
            return
        if numero > 11:
            print("Opción no válida.")
            continue
        print("\n" + datos["empresa"])
        for titulo, filas, columnas in cedulas[numero]:
            mostrar_tabla(f"{titulo} {datos['anio']}", filas, columnas)


def ver_estados(datos, estados):
    for titulo, renglones in estados:
        print("\n" + datos["empresa"])
        mostrar_tabla(f"{titulo} {datos['anio']}", en_columna(renglones), ["Importe"])


def main():
    datos = None
    while True:
        print("\n========== PRESUPUESTO MAESTRO ==========")
        print("1. Capturar datos de la empresa")
        print("2. Ver cédulas")
        print("3. Ver estados financieros")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            datos = capturar_datos()
            cedulas, estados = calcular(datos)
            print("\nDatos capturados y presupuesto calculado.")
        elif opcion == "2" or opcion == "3":
            if datos is None:
                print("\nPrimero captura los datos de la empresa.")
            elif opcion == "2":
                ver_cedulas(datos, cedulas)
            else:
                ver_estados(datos, estados)
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")


main()
