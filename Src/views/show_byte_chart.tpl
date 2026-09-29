% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Overall file chart",lang) }}</h1>

<a href="/main?lang={{ lang }}&fn={{ fn }}">{{ _("Home screen",lang) }}</a>

    <div class="row mb-3">
        <label for="inputFile" class="col-sm-2 col-form-label">{{ _("Parquet path",lang) }}</label>
        <div class="col-sm-10">
            <input name="input_file" type="text" class="form-control" id="inputFile" readonly value="{{ filename }}" aria-describedby="fileHelp">
            <div id="fileHelp" class="form-text">{{ _("Filename is readonly and cannot be changed here...",lang) }}</div>
        </div>
    </div>

    {{!chart_html}}

</div>

% include("footer.tpl")
