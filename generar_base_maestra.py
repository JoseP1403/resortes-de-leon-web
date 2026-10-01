import pandas as pd
import re

archivo_recesa = "Ventas redes RECESA.xlsx"
archivo_redelsa = "Ventas redes REDELSA.xlsx"


def limpiar_texto(texto):
    texto = str(texto).strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def extraer_categoria(texto):
    """
    Extrae la categoría desde filas tipo:

    PRODUCTO TERMINADO / PERNO
    -> PERNO

    REPUESTOS Y ACCESORIOS / ROLDANA / TORNILLERIA
    -> ROLDANA Y TORNILLERIA

    Regla:
    - Ignora el primer texto antes del primer "/".
    - Toma todos los textos después del primer "/".
    - Los une con " Y ".
    """
    texto = limpiar_texto(texto)

    if "/" not in texto:
        return None

    partes = [limpiar_texto(p) for p in texto.split("/") if limpiar_texto(p)]

    if len(partes) >= 2:
        return " Y ".join(partes[1:]).upper()

    return None


def transformar_redes(df_raw, empresa):

    filas = []

    data = df_raw.iloc[4:, :].copy()

    categoria_actual = "SIN CATEGORIA"
    categorias = []

    for valor in data[0]:
        texto = limpiar_texto(valor)

        # Si la fila no tiene código y tiene "/", es una fila de categoría.
        if not re.search(r"\[.*?\]", texto):
            categoria_detectada = extraer_categoria(texto)

            if categoria_detectada:
                categoria_actual = categoria_detectada

            categorias.append(None)

        else:
            categorias.append(categoria_actual)

    data["Categoria"] = categorias

    data["Codigo"] = data[0].astype(str).str.extract(r"\[(.*?)\]")

    data["Descripcion"] = data[0].astype(str).str.replace(
        r"\[.*?\]\s*",
        "",
        regex=True
    )

    data["Descripcion"] = data["Descripcion"].apply(limpiar_texto)

    data = data.dropna(subset=["Codigo"]).copy()

    for col in range(1, df_raw.shape[1], 3):

        mes = df_raw.iloc[1, col]

        if pd.isna(mes):
            continue

        temp = pd.DataFrame({
            "Empresa": empresa,
            "Codigo": data["Codigo"],
            "Descripcion": data["Descripcion"],
            "Categoria": data["Categoria"],
            "Mes": mes,
            "Total": data[col],
            "Cantidad": data[col + 1],
            "Precio_Promedio": data[col + 2]
        })

        filas.append(temp)

    df_final = pd.concat(filas, ignore_index=True)

    for columna in ["Total", "Cantidad", "Precio_Promedio"]:
        df_final[columna] = pd.to_numeric(df_final[columna], errors="coerce").fillna(0)

    df_final["Año"] = df_final["Mes"].astype(str).str.extract(r"(\d{4})").astype(int)

    df_final = df_final[
        (df_final["Total"] != 0) |
        (df_final["Cantidad"] != 0)
    ].copy()

    return df_final


def main():

    df_recesa_raw = pd.read_excel(
        archivo_recesa,
        sheet_name="Ventas_Recesa",
        header=None
    )

    df_redelsa_raw = pd.read_excel(
        archivo_redelsa,
        sheet_name="Ventas_Redelsa",
        header=None
    )

    df_recesa = transformar_redes(df_recesa_raw, "RECESA")
    df_redelsa = transformar_redes(df_redelsa_raw, "REDELSA")

    df_total = pd.concat(
        [df_recesa, df_redelsa],
        ignore_index=True
    )

    df_total.to_excel(
        "Base_Maestra_Redes.xlsx",
        index=False
    )

    print("Base_Maestra_Redes.xlsx generada correctamente")
    print("Filas:", len(df_total))
    print("Categorías detectadas:")
    print(df_total["Categoria"].value_counts())


if __name__ == "__main__":
    main()
