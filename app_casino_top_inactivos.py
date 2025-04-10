
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="App de Cargas - Casino", layout="wide")

st.title("🎰 App de Análisis de Cargas del Casino")

seccion = st.sidebar.radio("Seleccioná una sección:", ["🔝 Top 10 de Cargas", "📉 Jugadores Inactivos"])

# FUNCIONES AUXILIARES
def preparar_dataframe(df):
    df = df.rename(columns={
        "operación": "Tipo",
        "Depositar": "Monto",
        "Retirar": "?1",
        "Wager": "?2",
        "Límites": "?3",
        "Balance antes de operación": "Saldo",
        "Fecha": "Fecha",
        "Tiempo": "Hora",
        "Iniciador": "UsuarioSistema",
        "Del usuario": "Plataforma",
        "Sistema": "Admin",
        "Al usuario": "Jugador",
        "IP": "Extra"
    })
    columnas_esperadas = [
        "ID", "Tipo", "Monto", "?1", "?2", "?3", "Saldo",
        "Fecha", "Hora", "UsuarioSistema", "Plataforma", "Admin", "Jugador", "Extra"
    ]
    if len(df.columns) == len(columnas_esperadas):
        df.columns = columnas_esperadas
        return df
    else:
        return None

# SECCIÓN 1: TOP 10 DE CARGAS
if seccion == "🔝 Top 10 de Cargas":
    st.header("🔝 Top 10 por Monto y Cantidad de Cargas")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas recientes:", type=["xlsx", "xls", "csv"], key="top10")

    if archivo:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        df = preparar_dataframe(df)

        if df is not None:
            df_cargas = df[df["Tipo"] == "in"]
            df_cargas["Fecha"] = pd.to_datetime(df_cargas["Fecha"])

            top_monto = (
                df_cargas.groupby("Jugador")
                .agg(Monto_Total_Cargado=("Monto", "sum"), Cantidad_Cargas=("Jugador", "count"))
                .sort_values(by="Monto_Total_Cargado", ascending=False)
                .head(10)
                .reset_index()
            )

            top_cant = (
                df_cargas.groupby("Jugador")
                .agg(Cantidad_Cargas=("Jugador", "count"), Monto_Total_Cargado=("Monto", "sum"))
                .sort_values(by="Cantidad_Cargas", ascending=False)
                .head(10)
                .reset_index()
            )

            st.subheader("💰 Top 10 por Monto Total Cargado")
            st.dataframe(top_monto)

            st.subheader("🔢 Top 10 por Cantidad de Cargas")
            st.dataframe(top_cant)

            # Exportación
            writer = pd.ExcelWriter("Top10_Cargas.xlsx", engine="xlsxwriter")
            top_monto.to_excel(writer, sheet_name="Top Monto", index=False)
            top_cant.to_excel(writer, sheet_name="Top Cantidad", index=False)
            writer.close()

            with open("Top10_Cargas.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="Top10_Cargas.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")

# SECCIÓN 2: JUGADORES INACTIVOS
elif seccion == "📉 Jugadores Inactivos":
    st.header("📉 Detección de Jugadores Inactivos")
    archivo_inactivos = st.file_uploader("📁 Subí tu archivo con historial amplio de cargas:", type=["xlsx", "xls", "csv"], key="inactivos")

    dias_limite = st.number_input("📆 Mostrar jugadores que no cargan hace al menos X días:", min_value=1, value=7)

    if archivo_inactivos:
        if archivo_inactivos.name.endswith(".csv"):
            df2 = pd.read_csv(archivo_inactivos)
        else:
            df2 = pd.read_excel(archivo_inactivos)

        df2 = preparar_dataframe(df2)

        if df2 is not None:
            df2["Fecha"] = pd.to_datetime(df2["Fecha"])
            df2 = df2[df2["Tipo"] == "in"]

            hoy = pd.to_datetime(datetime.date.today())
            ultima_carga = df2.groupby("Jugador")["Fecha"].max().reset_index()
            ultima_carga["Dias_inactivo"] = (hoy - ultima_carga["Fecha"]).dt.days

            inactivos = ultima_carga[ultima_carga["Dias_inactivo"] >= dias_limite].sort_values(by="Dias_inactivo", ascending=False)

            st.subheader("🚫 Jugadores Inactivos")
            st.dataframe(inactivos)

            inactivos.to_excel("Jugadores_Inactivos.xlsx", index=False)
            with open("Jugadores_Inactivos.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel de Inactivos", f, file_name="Jugadores_Inactivos.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")
