% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Probe bloom filters",lang) }}</h1>

<a href="/main?lang={{ lang }}&fn={{ fn }}">{{ _("Home screen",lang) }}</a>

<form method="post">
    <input type="hidden" name="colstr" value="{{ ','.join(columns) }}">
    <input type="hidden" name="probestr" value="{{ probestr }}">
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
        <label for="grpNo" class="col-sm-2 col-form-label">{{ _("Probe value",lang) }}</label>
        <div class="col-sm-4">
            <input name="input_probe" type="text" class="form-control" id="inputProbe" aria-describedby="probeHelp" value="{{ probestr }}">
            <div id="probeHelp" class="form-text">{{ _("Probing takes time, wait for results to be refreshed below",lang) }}</div>
        </div>
    </div>
    <button type="submit" formaction="/probe_bloom?lang={{ lang }}&fn={{ fn }}" class="btn btn-primary">{{ _("Probe bloom filters",lang) }}</button>
</form>

% if resstr:
<br>
<b>{{ _("Column",lang) }}</b>: {{ selected }}<br>
<b>{{ _("Probe value",lang) }}</b>: {{ probestr}}<br>
<p> {{ resstr }} </p>
% end

<hr>

<div class="row mb-3">
<p>

{{! _("Probing bloom filter works only for local files (not for S3)",lang) }}

</p>
</div>

</div>
