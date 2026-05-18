import pandas as pd
import numpy as np
import json
import re
import calendar
from pathlib import Path

EXCEL_FILE = "Base_Maestra_Redes.xlsx"
OUTPUT_FILE = "datos.json"

month_order = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

month_labels_short = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}

month_labels_full = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def mes_num(value):
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip().lower()
    parts = re.split(r"\s+|-|/", text)

    for part in parts:
        if part in month_order:
            return month_order[part]

    return month_order.get(text)


def validate_columns(df):
    required_columns = [
        "Empresa",
        "Codigo",
        "Descripcion",
        "Categoria",
        "Mes",
        "Total",
        "Cantidad",
        "Precio_Promedio",
        "Año",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            "Faltan estas columnas en el Excel: " + ", ".join(missing)
        )


def main():
    excel_path = Path(EXCEL_FILE)

    if not excel_path.exists():
        raise FileNotFoundError(
            f"No encontré el archivo {EXCEL_FILE}. "
            "Asegúrate de que esté en la misma carpeta que actualizar.py"
        )

    df = pd.read_excel(excel_path)

    validate_columns(df)

    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
    df["Año"] = pd.to_numeric(df["Año"], errors="coerce").fillna(0).astype(int)

    df["Mes_Num"] = df["Mes"].apply(mes_num)

    if df["Mes_Num"].isna().any():
        meses_no_reconocidos = df.loc[df["Mes_Num"].isna(), "Mes"].unique()
        raise ValueError(
            "Hay meses que no pude reconocer: "
            + ", ".join(map(str, meses_no_reconocidos))
        )

    df = df.sort_values(["Año", "Mes_Num"])

    monthly = (
        df.groupby(["Año", "Mes_Num"], as_index=False)
        .agg(
            total=("Total", "sum"),
            units=("Cantidad", "sum"),
        )
        .sort_values(["Año", "Mes_Num"])
    )

    labels = [
        month_labels_short[int(row.Mes_Num)]
        for row in monthly.itertuples()
    ]

    full_labels = [
        f"{month_labels_full[int(row.Mes_Num)]} {int(row.Año)}"
        for row in monthly.itertuples()
    ]

    totals = [round(float(value), 2) for value in monthly["total"]]
    units = [int(round(float(value))) for value in monthly["units"]]

    pivot = (
        df.pivot_table(
            index=["Año", "Mes_Num"],
            columns="Empresa",
            values="Total",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    pivot = (
        monthly[["Año", "Mes_Num"]]
        .merge(pivot, on=["Año", "Mes_Num"], how="left")
        .fillna(0)
    )

    recesa = (
        [round(float(value), 2) for value in pivot["RECESA"]]
        if "RECESA" in pivot.columns
        else [0] * len(pivot)
    )

    redelsa = (
        [round(float(value), 2) for value in pivot["REDELSA"]]
        if "REDELSA" in pivot.columns
        else [0] * len(pivot)
    )

    company = df.groupby("Empresa").agg(
        total=("Total", "sum"),
        units=("Cantidad", "sum"),
    )

    recesa_total = (
        round(float(company.loc["RECESA", "total"]), 2)
        if "RECESA" in company.index
        else 0
    )

    redelsa_total = (
        round(float(company.loc["REDELSA", "total"]), 2)
        if "REDELSA" in company.index
        else 0
    )

    recesa_units = (
        int(round(float(company.loc["RECESA", "units"])))
        if "RECESA" in company.index
        else 0
    )

    redelsa_units = (
        int(round(float(company.loc["REDELSA", "units"])))
        if "REDELSA" in company.index
        else 0
    )

    # =========================================================
    # TOP PRODUCTOS POR VENTAS
    # =========================================================

    products_df = (
        df.groupby("Descripcion", as_index=False)
        .agg(
            total=("Total", "sum"),
            units=("Cantidad", "sum"),
        )
        .sort_values("total", ascending=False)
        .head(7)
    )

    products = [
        {
            "name": str(row.Descripcion),
            "val": round(float(row.total), 2),
        }
        for row in products_df.itertuples()
    ]

    # =========================================================
    # TOP CATEGORÍA POR UNIDADES
    # =========================================================

    top_category_df = (
        df.groupby("Categoria", as_index=False)
        .agg(
            units=("Cantidad", "sum")
        )
        .sort_values("units", ascending=False)
    )

    top_category = str(top_category_df.iloc[0]["Categoria"])
    top_category_units = int(round(float(top_category_df.iloc[0]["units"])))

    details = []

    for (year, month), group in df.groupby(["Año", "Mes_Num"], sort=True):
        total = float(group["Total"].sum())
        qty = float(group["Cantidad"].sum())

        rec = float(
            group.loc[group["Empresa"].eq("RECESA"), "Total"].sum()
        )

        red = float(
            group.loc[group["Empresa"].eq("REDELSA"), "Total"].sum()
        )

        product_summary = (
            group.groupby("Descripcion", as_index=False)
            .agg(
                total=("Total", "sum"),
                units=("Cantidad", "sum"),
            )
        )

        top_value = product_summary.sort_values(
            "total",
            ascending=False,
        ).iloc[0]

        top_units = product_summary.sort_values(
            "units",
            ascending=False,
        ).iloc[0]

        days_in_month = calendar.monthrange(int(year), int(month))[1]

        details.append(
            {
                "month": f"{month_labels_full[int(month)]} {int(year)}",
                "total": round(total, 2),
                "recesa": round(rec, 2),
                "redelsa": round(red, 2),
                "units": int(round(qty)),
                "daily": round(total / days_in_month, 2),
                "topValueProduct": str(top_value["Descripcion"]),
                "topValueTotal": round(float(top_value["total"]), 2),
                "topUnitsProduct": str(top_units["Descripcion"]),
                "topUnitsQty": int(round(float(top_units["units"]))),
            }
        )

    best_index = int(np.argmax(totals))

    datos = {
        "labels": labels,
        "fullLabels": full_labels,
        "totals": totals,
        "units": units,
        "recesa": recesa,
        "redelsa": redelsa,
        "recesaTotal": recesa_total,
        "redelsaTotal": redelsa_total,
        "recesaUnits": recesa_units,
        "redelsaUnits": redelsa_units,
        "grandTotal": round(sum(totals), 2),
        "grandUnits": int(sum(units)),

        # NUEVO KPI
        "topCategory": top_category,
        "topCategoryUnits": top_category_units,

        "products": products,
        "details": details,
        "bestMonth": full_labels[best_index],
        "bestTotal": totals[best_index],
        "periodLabel": f"{full_labels[0]} – {full_labels[-1]}",
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=2)

    print("datos.json generado correctamente")
    print(f"Ventas totales: Q{datos['grandTotal']:,.2f}")
    print(f"Unidades: {datos['grandUnits']:,}")
    print(f"Top categoría: {datos['topCategory']} ({datos['topCategoryUnits']:,} uds.)")
    print(f"Período: {datos['periodLabel']}")


if __name__ == "__main__":
    main()