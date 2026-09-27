"""Andamiaje del panel de la Parte 2. Renómbrenlo si quieren.

MATERIAL PROVISTO. Lo que ya está escrito acá —los imports, la configuración
de la página y el cargador de datos— es infraestructura y no se evalúa: son
las mismas líneas para cualquier panel sobre este dataset. Lo que sí se evalúa
son las cuatro secciones de más abajo.

Las secciones están en un orden que funciona, pero no es obligatorio:
reordenarlas o renombrarlas no descuenta. Lo que se corrige es que las cuatro
cosas estén y que cada gráfico explique por qué está ahí.

Para trabajar:

    uv run streamlit run mi_panel.py

Streamlit reejecuta el archivo completo cada vez que alguien mueve un control,
así que el navegador se actualiza solo al guardar.
"""

from pathlib import Path

import polars as pl
import streamlit as st
import plotly.express as px

RUTA_DATOS = Path(__file__).parent / "data" / "raw" / "penguins.csv"

st.set_page_config(
    page_title="Pingüinos de Palmer", page_icon="🐧", layout="wide"
)
st.title("🐧 Pingüinos del archipiélago de Palmer")


@st.cache_data
def cargar_datos() -> pl.DataFrame:
    """Lee el CSV sin modificarlo.

    `null_values=["NA"]` es necesario: el archivo viene de R, donde `NA` marca
    los faltantes. Sin ese argumento, polars lee las columnas numéricas como
    texto. Con él, los nulos quedan adentro — que es lo que queremos, porque
    este laboratorio no limpia nada.
    """
    return pl.read_csv(RUTA_DATOS, null_values=["NA"])


df = cargar_datos()

#raise NotImplementedError(
#    "Completen las cuatro secciones de este archivo y borren esta línea "
#    "antes de ejecutar el programa."
#)

# --- 1) La tabla interactiva -----------------------------------------------
#
# Una tabla con el dataset que el lector pueda ordenar por cualquier columna y
# filtrar con al menos dos controles: uno categórico y uno de rango numérico.
# Esos mismos filtros deben afectar también a los cuatro gráficos. Los
# registros sin valor en la columna del filtro numérico quedan fuera de la
# selección filtrada. Si ningún registro cumple los filtros, muestren un aviso.
#
# Ordenar y buscar los trae `st.dataframe` de fábrica, sin programar nada.
# Filtrar no: los controles devuelven la selección y ustedes filtran el
# DataFrame antes de pasárselo a la tabla. Denle formato a las columnas, que
# `flipper_length_mm` no es un encabezado para mostrarle a un cliente.
#
#   https://docs.streamlit.io/develop/api-reference/data/st.dataframe
#   https://docs.streamlit.io/develop/api-reference/data/st.column_config
#   https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
#   https://docs.streamlit.io/develop/api-reference/widgets/st.slider

st.header("Exploración de los datos")

st.sidebar.header("Filtros")

especies = sorted(
    df["species"]
    .drop_nulls()
    .unique()
    .to_list()
)

especies_seleccionadas = st.sidebar.multiselect(
    "Especie",
    options=especies,
    default=especies,
)

masa_min = int(df["body_mass_g"].min())
masa_max = int(df["body_mass_g"].max())

rango_masa = st.sidebar.slider(
    "Masa corporal (g)",
    min_value=masa_min,
    max_value=masa_max,
    value=(masa_min, masa_max),
    step=50,
)

df_filtrado = df.filter(
    pl.col("species").is_in(especies_seleccionadas)
    & pl.col("body_mass_g").is_between(
        rango_masa[0],
        rango_masa[1],
        closed="both",
    )
)


# --- 2) La calidad de los datos --------------------------------------------
#
# Un informe visible en la página, calculado sobre el CSV completo aunque se
# apliquen filtros: qué columnas tienen nulos y cuántos, cuál es el valor
# inesperado de `sex` y cómo pueden afectar esos problemas los recuentos,
# filtros o gráficos del panel.
#
# Las cifras se calculan desde `df`, no se escriben a mano: si el
# archivo cambiara, un número escrito a mano queda mintiendo.
#
#   https://docs.streamlit.io/develop/api-reference/status/st.warning

st.header("Calidad de los datos")

nulos = pl.DataFrame({
    "columna": df.columns,
    "nulos": [
        df[columna].null_count()
        for columna in df.columns
    ],
})

nulos_con_valores = nulos.filter(
    pl.col("nulos") > 0
)

st.subheader("Valores faltantes")

st.dataframe(
    nulos_con_valores,
    hide_index=True,
    width="stretch",
    column_config={
        "columna": st.column_config.TextColumn(
            "Columna"
        ),
        "nulos": st.column_config.NumberColumn(
            "Cantidad de nulos",
            format="%d",
        ),
    },
)


### 
st.subheader("Valores inesperados en `sex`")

sex_esperados = ["MALE", "FEMALE"]

valores_inesperados = (
    df
    .filter(
        pl.col("sex").is_not_null()
        & ~pl.col("sex").is_in(sex_esperados)
    )
    .group_by("sex")
    .len()
)


st.subheader("¿Cómo afectan estos problemas al panel?")

st.markdown(
    """
    **Valores nulos**
    Respecto a los valores nulos, existen 5 columnas con nulos de los cuales 4 de estas columnas tienen 2 nulos en total y una de ellas tiene 10 nulos.
    En caso de querer realizar cálculos tales valores nulos podrían causar problemas de cómputo. Respecto a los filtros, cuando se selccione una especie,
    los pinguinos con entradas nulas podrían simplmenete no mostrarse. En términos de gráfico puede que los valores nulos sean tomados como ceros si no se
    tratan adecuadamente.

    **Valor inesperado en `sex`**
    En términos de recuento, el valor `.` puede ser tratado como una tercera categoría,
      además de `MALE` y `FEMALE` lo que es incorrecto. Es por ello que si se construye un filtro por sexo, `.` aparecería como una
      opción distinta si no se trata explícitamente. Respecto a los gráficos, una visualización agrupada o coloreada por `sex` puede
      mostrar un grupo adicional correspondiente a `.`, lo que podría llevar a una interpretación incorrecta de las categorías.
    """
)

# --- 3) Los cuatro gráficos ------------------------------------------------
#
# Cuatro gráficos a elección, de al menos dos tipos distintos. Pueden reusar
# los de la Parte 1 o construir otros. Van a necesitar `plotly.express`:
# impórtenlo arriba, con el resto.
#
# Cada gráfico lleva, JUNTO A ÉL Y VISIBLE EN LA PÁGINA, por qué esa
# información es útil y por qué eligieron esa visualización. Un comentario en
# el código no cuenta: quien abre el panel no lee el código.
#
#   https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
#   https://docs.streamlit.io/develop/api-reference/text/st.caption
#   https://docs.streamlit.io/develop/api-reference/layout/st.columns

st.header("Visualización de los datos filtrados")

if df_filtrado.is_empty():
    st.warning(
        "No hay registros que cumplan con los filtros seleccionados."
    )

else:

    st.subheader("1. Relación entre largo de aleta y masa corporal")

    datos_scatter = df_filtrado.drop_nulls(
        subset=["flipper_length_mm", "body_mass_g"]
    )

    fig_scatter = px.scatter(
        datos_scatter,
        x="flipper_length_mm",
        y="body_mass_g",
        color="species",
        labels={
            "flipper_length_mm": "Largo de aleta (mm)",
            "body_mass_g": "Masa corporal (g)",
            "species": "Especie",
        },
        title="Masa corporal según el largo de la aleta",
    )


    st.plotly_chart(
        fig_scatter,
        width="stretch",
        theme="streamlit",
    )

    st.caption(
        """
        Este gráfico permite visualizar la relación entre el largo
        de la aleta y la masa corporal. Se escoge este gráfico para tener un panorama general de la distribución de
        datos de los pinguinos diferenciados (por color) según la especie.

        """
    )

    st.subheader("2. Distribución de la masa corporal")

    datos_masa = df_filtrado.drop_nulls(
        subset=["body_mass_g"]
    )

    fig_hist = px.histogram(
        datos_masa,
        x="body_mass_g",
        color="species",
        barmode="overlay",
        opacity=0.65,
        labels={
            "body_mass_g": "Masa corporal (g)",
            "species": "Especie",
        },
        title="Distribución de la masa corporal por especie",
    )

    st.plotly_chart(
        fig_hist,
        width="stretch",
        theme="streamlit",
    )

    st.caption(
        """
        Este histograma permite observar cómo se distribuye la masa corporal
        de los pingüinos y en qué rangos se concentra la mayor cantidad de
        observaciones. Se eligió un histograma porque permite visualizar
        frecuencias de una variable numérica continua fácilmente.
        """
    )

    st.subheader("3. Comparación de masa corporal entre especies")

    fig_box = px.box(
        datos_masa,
        x="species",
        y="body_mass_g",
        color="species",
        labels={
            "species": "Especie",
            "body_mass_g": "Masa corporal (g)",
        },
        title="Masa corporal por especie",
    )

    st.plotly_chart(
        fig_box,
        width="stretch",
        theme="streamlit",
    )

    st.caption(
        """
        Este gráfico permite comparar detalladamente la masa corporal
        entre especies a comparación del primer gráfico, pues, se
        presenta la mediana, los cuartiles y posibles valores atípicos.
        Se eligió un boxplot porque resume la distribución de cada grupo
        y facilita su comparación.
        """
    )

    st.subheader("4. Cantidad de pingüinos por especie")

    conteo_especies = (
        df_filtrado
        .group_by("species")
        .len()
        .sort("len", descending=True)
    )

    fig_bar = px.bar(
        conteo_especies,
        x="species",
        y="len",
        labels={
            "species": "Especie",
            "len": "Cantidad de pingüinos",
        },
        title="Cantidad de observaciones por especie",
    )

    st.plotly_chart(
        fig_bar,
        width="stretch",
        theme="streamlit",
    )

    st.caption(
        """
        Este gráfico muestra cuántos registros de cada especie permanecen
        después de aplicar los filtros. Se eligió un gráfico de barras porque
        permite comparar directamente cantidades entre categorías.
        """
    )

# --- 4) El tema --------------------------------------------------------------
#
# Este no se programa acá: vive en `.streamlit/config.toml`, al lado de este
# archivo. Ya existe, con las claves comentadas — descoméntenlas y decidan sus
# colores.
#
# Para comprobar que el suyo está haciendo algo: renombren el archivo,
# reinicien el panel y vean si cambia. Si no cambia, no lo configuraron.
#
#   https://docs.streamlit.io/develop/concepts/configuration/theming
