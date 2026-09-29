% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Show column statistics chart",lang) }}</h1>

<a href="/main?lang={{ lang }}&fn={{ fn }}">{{ _("Home screen",lang) }}</a>

<form method="post">
    <input type="hidden" name="colstr" value="{{ ','.join(columns) }}">
    <div class="row mb-3">
        <label for="inputFile" class="col-sm-2 col-form-label">{{ _("Parquet path",lang) }}</label>
        <div class="col-sm-10">
            <input name="input_file" type="text" class="form-control" id="inputFile" readonly value="{{ filename }}" aria-describedby="fileHelp">
            <div id="fileHelp" class="form-text">{{ _("Filename is readonly and cannot be changed here...",lang) }}</div>
        </div>
    </div>

    <div class="row mb-3">
        <label for="fieldName" class="col-sm-2 col-form-label">{{ _("Field name",lang) }}</label>
        <div class="col-sm-4">
            <select name="field_name" id="fieldName" class="form-select">
            % for col in columns:      
                <option {{ "selected" if col==selected else "" }} value="{{ col }}">{{ col }}</option>
            % end
            </select>  
        </div>
    </div>
    <button type="submit" formaction="/col_chart?lang={{ lang }}&fn={{ fn }}" class="btn btn-primary">{{ _("Show column chart",lang) }}</button>
</form>

% if chart_html:
<br>

    {{!chart_html}}

% end

</div>

% include("footer.tpl")
