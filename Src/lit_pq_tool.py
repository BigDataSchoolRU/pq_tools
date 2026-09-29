from bottle import Bottle, template, static_file, route, post, request
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import struct
import os
from tpl_funcs import _
from typing import List,Dict # для более корректных определений функций и их параметров
app = Bottle()
@app.route('/static/<filepath:path>')
def server_static(
    filepath: str,
) -> static_file:
    #return static_file(filepath, root='/mnt/c/Users/mikhail.korolev/Documents/31.Parquet/bottle/static')
    return static_file(filepath, root='static')
def mkd(
    v: int,
) -> str:
    return f"{v:,}".replace(',', ' ')
def get_parquet_metadata(
    parquet_filename: str,
    conn: duckdb.DuckDBPyConnection,
) -> pandas.DataFrame:
    # Row-group / column-chunk metadata from DuckDB
    df = conn.execute(f"""
        SELECT
            row_group_id            AS rg_no,
            path_in_schema          AS column,
            encodings               AS encodings,
            data_page_offset        AS data_page_offset,
            dictionary_page_offset  AS dictionary_page_offset,
            index_page_offset       AS index_page_offset,
            bloom_filter_offset     AS bloom_filter_offset,
            bloom_filter_length     AS bloom_filter_length,
            total_compressed_size   AS total_compressed_size
        FROM pqmeta
    """).fetchdf()
    rows = []
    maxOffset = 0 # максимальное смещение, которое встретилось
    for r in df.itertuples(index=False):
        # ---- column data ------------------------------------------------
        # The column chunk starts at dictionary_page_offset if present,
        # otherwise at data_page_offset.
        if r.dictionary_page_offset is not None and not pd.isna(r.dictionary_page_offset):
            data_off = int(r.dictionary_page_offset)
        else:
            data_off = int(r.data_page_offset)
        data_size = int(r.total_compressed_size)
        rows.append({
            "el_type": "column data",
            "column":  r.column,
            "encodings": r.encodings,
            "rg_no":   int(r.rg_no),
            "offset":  data_off,
            "size":    data_size,
        })
        if data_off + data_size > maxOffset:
            maxOffset = data_off + data_size
        # ---- column index ----------------------------------------------
        if r.index_page_offset is not None and not pd.isna(r.index_page_offset):
            # offset index size isn't directly exposed by parquet_metadata;
            # the column index offset is index_page_offset and its length
            # can be found via the offset index. DuckDB doesn't expose the
            # length here, so we set size to 0 unless known.
            rows.append({
                "el_type": "column index",
                "column":  r.column,
                "encodings": None,
                "rg_no":   int(r.rg_no),
                "offset":  int(r.index_page_offset),
                "size":    0,   # length not exposed by parquet_metadata()
            })
            if int(r.index_page_offset) > maxOffset:
                maxOffset = int(r.index_page_offset)
        # ---- bloom filter ----------------------------------------------
        if r.bloom_filter_offset is not None and not pd.isna(r.bloom_filter_offset):
            bf_len = r.bloom_filter_length
            bf_len = int(bf_len) if bf_len is not None and not pd.isna(bf_len) else 0
            rows.append({
                "el_type": "bloom filter",
                "column":  r.column,
                "encodings": None,
                "rg_no":   int(r.rg_no),
                "offset":  int(r.bloom_filter_offset),
                "size":    bf_len,
            })
            if int(r.bloom_filter_offset) + bf_len > maxOffset:
                maxOffset = int(r.bloom_filter_offset) + bf_len
    # ---- footer ---------------------------------------------------------
    # Parquet file layout: ... <footer_metadata> <4-byte footer length> PAR1
    file_size = conn.sql("select size from filename").df().values.tolist()[0][0]
    footer_len = file_size - maxOffset
    footer_offset = maxOffset
    rows.append({
        "el_type": "footer",
        "column":  None,
        "encodings": None,
        "rg_no":   0, # let it be always within first row group
        "offset":  footer_offset,
        "size":    footer_len,
    })
    out = pd.DataFrame(rows, columns=["el_type", "column", "encodings", "rg_no", "offset", "size"])
    out["row"] = out["rg_no"].mod(2).astype(int)
    out = out.sort_values("offset").reset_index(drop=True)
    return out
@app.route('/static/<filepath:path>')
def server_static(
    filepath: str,
) -> static_file:
    #return static_file(filepath, root='/mnt/c/Users/mikhail.korolev/Documents/31.Parquet/bottle/static')
    return static_file(filepath, root='static')
def getColumns(
    dbName: str,
) -> List:
    conn = duckdb.connect(dbName)
    cols = [ el[0] for el in conn.sql(f"SELECT name FROM pqschema").to_df().values.tolist()[1:] ]
    conn.close()
    return cols
@app.get('/')
def entryPoint(
) -> template:
    lang = request.query.lang or "en"
    ctx = {
        "fn": "",
        "lang": lang,
        "filename": _("no file selected yet",lang),
        "request": request,
    }
    return template('main',**ctx)
def prepMeta(
    PQ_FILE: str,
    dbName: str,
    S3_KEY: str,
    S3_SECRET: str,
):
    # удалим базу если существует
    if os.path.exists(dbName):
        os.remove(dbName)
    conn = duckdb.connect(dbName)
    if PQ_FILE.lower().find("s3://")>=0: # работаем через HTTPS
        conn.sql("drop secret if exists ya_s3_secret")
        conn.sql(f"""
            CREATE SECRET ya_s3_secret (
                TYPE s3, PROVIDER config,
                KEY_ID '{S3_KEY}',
                SECRET '{S3_SECRET}',
                ENDPOINT "storage.yandexcloud.net", REGION 'ru-central1')
        """)
    # save parquet filename and metadata - будем работать с первым файлом (в случае, если их несколько)
    conn.sql(f"create table filename as SELECT filename as name, size FROM read_blob('{PQ_FILE}') limit 1")
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0] # уточним название файла с которым работаем для последующей формы
    conn.sql(f"create table pqmeta as SELECT * FROM parquet_metadata('{PQ_FILE}')")
    conn.sql(f"create table pqschema as SELECT * FROM parquet_schema('{PQ_FILE}')")
    conn.close()
@app.post('/main')
@app.get('/main')
def showMainForm(
) -> template:
    if request.query.fn=="": # работа с новым файлом
        PQ_FILE = request.forms.input_file # приезжает из формы
        PQ_ALIAS = request.forms.input_alias # приезжает из формы, передается в дальнейшие формы
        S3_KEY = request.forms.input_key
        S3_SECRET = request.forms.input_secret
        dbName = f"/tmp/{PQ_ALIAS}.duckdb"
        prepMeta( PQ_FILE, dbName, S3_KEY, S3_SECRET)
    else: # продолжаем работать с тем же файлом - мета уже создана
        PQ_ALIAS = request.query.fn # приезжает из формы, передается в дальнейшие формы
        dbName = f"/tmp/{PQ_ALIAS}.duckdb"
        conn = duckdb.connect(dbName)
        PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
        conn.close()
    lang = request.query.lang # приезжает из формы
    print("LANG",lang)
    ctx = {
        "fn": PQ_ALIAS,
        "lang": lang,
        "filename": PQ_FILE,
        "request": request,
    }
    return template('main',**ctx)
def prepChart(
    dbName: str,
) -> go.Figure:
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    mdf = get_parquet_metadata(PQ_FILE,conn)
    conn.close()
    fig = px.bar(
        mdf,
        x="size",
        y="row",
        base="offset",
        orientation="h",
        color="el_type",                       # <-- color by type, not element
        custom_data=["column", "el_type", "offset", "size", "encodings", "rg_no"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" # column name
            "type: %{customdata[1]}<br>"
            "offset: %{customdata[2]:,}<br>"
            "size: %{customdata[3]:,} bytes<br>"
            "encoding: %{customdata[4]}"
            "<extra>RG: %{customdata[5]}</extra>"
        )
    )
    fig.update_layout(
        barmode="overlay",
        showlegend=True,
        xaxis_title="Byte offset",
        yaxis_visible=False,
        bargap=0,
    )
    color_map = {
        "column data":  "#4C78A8",
        "column index": "#F58518",
        "bloom filter": "#54A24B",
        "footer":       "#B279A2",
    }
    for tr in fig.data:
        tr.marker.color = color_map.get(tr.name, tr.marker.color)
    return fig
@app.post('/chart')
def showChart(
) -> template:
    dbName = f"/tmp/{request.query.fn}.duckdb"
    fig = prepChart(dbName)
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    conn.close()
    plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    lang = request.query.lang # приезжает из формы
    ctx = {
        "fn": request.query.fn,
        "lang": lang,
        "request": request,
        "filename": PQ_FILE,
        "chart_html": plotly_html
    }
    return template('show_byte_chart', **ctx )
def prepColChart(
    dbName: str,
    colName: str,
    lang: str,
) -> go.Figure:
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    df = conn.sql(f"""
        select
            num_values as num_rows,
            stats_min_value as min, 
            stats_max_value as max, 
            stats_null_count as nulls,
            row_group_id as rg
        from pqmeta 
        where 
            path_in_schema='{ colName }'
    """).df()
    conn.close()
    df["span"] = df["max"].astype(int) - df["min"].astype(int)
    df["rg_label"] = "RG " + df["rg"].astype(str)
    fig = px.bar(
        df,
        x="rg_label",
        y="span",
        base="min",
        orientation="v",
        custom_data=["rg", "num_rows", "min", "max", "nulls"],
    )
    fig.update_traces(
        marker_color="#4C78A8",
        marker_line_color="#2A4A6B",
        marker_line_width=1,
        hovertemplate=(
            "<b>Row group %{customdata[0]}</b><br>"
            "rows:  %{customdata[1]:,}<br>"
            "min:   %{customdata[2]:,}<br>"
            "max:   %{customdata[3]:,}<br>"
            "nulls: %{customdata[4]:,}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(
        title= colName + ": " +_("column stats (min/max) per row groups",lang),
        xaxis_title="",
        yaxis_title=_("value",lang),
        bargap=0.2,
        showlegend=False,
    )
    return fig
@app.post('/col_chart')
def showColChart(
) -> template:
    dbName = f"/tmp/{request.query.fn}.duckdb"
    lang = request.query.lang # приезжает из формы
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    if request.forms.field_name: # вызов из формы
        colName = request.forms.field_name
        fig = prepColChart(dbName,colName,lang)
        cols = request.forms.colstr.split(",")
        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        cols = [ el[0] for el in conn.sql(f"SELECT name FROM pqschema where type='INT32'").to_df().values.tolist()[1:] ]
        colName = cols[0]
        plotly_html = None
    conn.close()
    ctx = {
        "fn": request.query.fn,
        "lang": lang,
        "request": request,
        "filename": PQ_FILE,
        "columns": cols,
        "selected": colName,
        "chart_html": plotly_html
    }
    return template('show_col_chart', **ctx )
@app.post('/set_file')
@app.route('/set_file')
def setFile(
) -> template:
    lang = request.query.lang # приезжает из формы
    return template('set_file', request=request, lang=lang)
def prepOverview(
    dbName: str,
    lang: str,
) -> List:
    conn = duckdb.connect(dbName)
    PQ_FILE,size = conn.sql("select name,size from filename").df().values.tolist()[0]
    grpNum = conn.sql("select max(row_group_id)+1 from pqmeta").df().values.tolist()[0][0]
    rowNum = int(conn.sql("select sum(num_values) from pqmeta where column_id=0").df().values.tolist()[0][0])
    rszList = conn.sql("select num_values, count(*) from pqmeta where column_id=0 group by 1").df().values.tolist()
    compressions = str(conn.sql("SELECT list(DISTINCT compression) FROM pqmeta").fetchone()[0])
    encList = conn.sql("""
    SELECT
        encoding,
        string_agg(DISTINCT path_in_schema, ', ' ORDER BY path_in_schema) AS columns
    FROM (
        SELECT
            path_in_schema,
            unnest(string_split(encodings, ',')) AS encoding
        FROM pqmeta
    )
    GROUP BY encoding
    ORDER BY encoding;
    """).df().values.tolist()
    bloomColsList = conn.sql("""
    SELECT DISTINCT path_in_schema AS column_name    FROM pqmeta
    WHERE bloom_filter_length IS NOT NULL
    ORDER BY column_name
    """).df().values.tolist()
    conn.close()
    return [
        [ 
            _("General info",lang), # заголовок секции
            [ # содержимое секции - набор пар "ключ, значение"
                ("filename",PQ_FILE),
                ("rows",mkd(rowNum)),
                ("row groups",grpNum),
                ("file size",mkd(size)+" bytes"),
                ("compressions",compressions),
            ]
        ],
        [
            _("Row Groups info",lang),
            [ (
                str(el[1])+" row groups have",
                mkd(el[0])+" rows"
              ) for el in rszList 
            ]
        ],
        [
            _("Encodings used",lang),
            [ (
                el[0], # encoding
                el[1] # columns
              ) for el in encList 
            ]
        ],
        [
            _("Bloom filter created",lang),
            [ (
                _("for columns",lang),
                ", ".join([ str(c[0]) for c in bloomColsList])
              ) 
            ]
        ]
    ]
@app.post('/show_stats')
def showOverview(
) -> template:
    lang = request.query.lang # приезжает из формы
    sections = prepOverview(f"/tmp/{request.query.fn}.duckdb",lang)
    ctx = {
        "fn": request.query.fn,
        "lang": lang,
        "request": request,
        "sections": sections
    }
    return template('show_stats',**ctx)
def prepRowGroupStats(
    dbName: str,
    lang: str,
    colName: str,
    rowGroupInd: int,
) -> Dict:
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    resDf = conn.sql(f"""
        select
            '{_("value",lang)}' as {_("name",lang)},
            path_in_schema,
            column_id,
            type, 
            num_values,
            stats_min_value, 
            stats_max_value, 
            stats_null_count,
            stats_distinct_count,
            encodings, 
            compression,
            index_page_offset, 
            bloom_filter_offset,
            bloom_filter_length,
            data_page_offset,
            dictionary_page_offset,
            total_compressed_size
        from pqmeta 
        where 
            row_group_id={rowGroupInd} 
            and path_in_schema='{colName}'
    """).df()
    comments = [
        _("Meta column description",lang),        
        _("Column name",lang),
        _("column_id",lang),
        _("type",lang), 
        _("num_values",lang),
        _("stats_min_value",lang), 
        _("stats_max_value",lang), 
        _("stats_null_count",lang),
        _("stats_distinct_count",lang),
        _("encodings",lang), 
        _("compression",lang),
        _("index_page_offset",lang), 
        _("bloom_filter_offset",lang),
        _("bloom_filter_length",lang),
        _("data_page_offset",lang),
        _("dictionary_page_offset",lang),
        _("total_compressed_size",lang),
    ]
    return dict(zip(resDf.columns,zip(resDf.iloc[0],comments)))
@app.post('/show_row_group_stats')
def showRowGroupStats(
) -> template:
    dbName = f"/tmp/{request.query.fn}.duckdb"
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    lang = request.query.lang # приезжает из формы
    if request.forms.field_name: # вызов через форму, т.е. уже все заполнено
        rowGroupInd = int(request.forms.grp_numb)
        colName = request.forms.field_name
        resRow = prepRowGroupStats(dbName,lang,colName,rowGroupInd)
        cols = request.forms.colstr.split(",")
        grpNum = int(request.forms.grpnumbstr)
    else: # первый вызов - из кнопки на главной форме, нужно заполнить поля формы
        grpNum = conn.sql("select max(row_group_id)+1 from pqmeta").df().values.tolist()[0][0]
        cols = [ el[0] for el in conn.sql(f"SELECT name FROM pqschema").to_df().values.tolist()[1:] ]
        resRow = None
        colName = cols[0]
        rowGroupInd = 0
    conn.close()
    ctx = {
        "title": "Row group stats",
        "fn": request.query.fn,
        "lang": lang,
        "request": request,
        "filename": PQ_FILE,
        "columns": cols,
        "grpnumb": grpNum,
        "selected": (colName,rowGroupInd),
        "statdict": resRow,
    }
    return template('get_row_group_stats',**ctx)
def probeBloomFilter(
    dbName: str,
    lang: str,
    colName: str,
    colValue: str,
) -> str:
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    grpNum = conn.sql("select max(row_group_id)+1 from pqmeta").df().values.tolist()[0][0]
    res = conn.sql(f"select row_group_id from parquet_bloom_probe('{PQ_FILE}', '{colName}', {colValue}) where bloom_filter_excludes").df().values
    conn.close()
    if len(res)>0:
        grList = res.tolist()
        if len(grList)<grpNum:
            retStr = f"""{_("Following row groups will be excluded",lang)}: {",".join([str(r[0]) for r in grList])}"""
        else:
            retStr = _("All row groups will be excluded",lang)
    else:
        retStr = _("No row groups will be excluded",lang)
    return retStr
@app.post('/probe_bloom')
def showProbeBloomFilter(
) -> template:
    dbName = f"/tmp/{request.query.fn}.duckdb"
    lang = request.query.lang # приезжает из формы
    conn = duckdb.connect(dbName)
    PQ_FILE = conn.sql("select name from filename").df().values.tolist()[0][0]
    if request.forms.input_probe: # вызов через форму, т.е. уже все заполнено
        colName = request.forms.field_name
        colValue = request.forms.input_probe
        cols = request.forms.colstr.split(",")
        retStr = probeBloomFilter(dbName,lang,colName,colValue)
    else: # первый вызов
        colName = request.forms.field_name
        cols = [ el[0] for el in conn.sql(f"select distinct(path_in_schema) from pqmeta where bloom_filter_offset is not NULL").to_df().values.tolist()[1:] ]
        colValue = ""
        retStr = None
    conn.close()
    ctx = {
        "title": "Probe bloom",
        "fn": request.query.fn,
        "lang": lang,
        "request": request,
        "filename": PQ_FILE,
        "columns": cols,
        "probestr": colValue,
        "selected": colName,
        "resstr": retStr,
    }
    return template('show_bloom',**ctx)