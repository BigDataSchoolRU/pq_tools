% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Parquet file operations",lang) }} </h1>

% if lang!="en":
<a href="{{ request.path }}?lang=en&fn={{ fn }}">eng</a>
% end
% if lang!="ru":
<a href="{{ request.path }}?lang=ru&fn={{ fn }}">рус</a>
% end

% active = "" if fn else "disabled"

<form method="post">
    <div class="row mb-3">
        <label for="inputFile" class="col-sm-2 col-form-label">{{ _("Parquet path",lang) }}</label>
        <div class="col-sm-10">
            <input name="input_file" type="text" class="form-control" id="inputFile" readonly value="{{ filename }}" aria-describedby="fileHelp">
            <div id="fileHelp" class="form-text">{{ _("Filename is readonly and cannot be changed here...",lang) }}</div>
        </div>
    </div>
    <button type="submit" formaction="/set_file?lang={{ lang }}" class="btn btn-primary">{{ _("Choose file",lang) }}</button>
    <button type="submit" formaction="/show_stats?lang={{ lang }}&fn={{ fn }}" {{ active }} class="btn btn-primary">{{ _("Show general file info",lang) }}</button>
    <button type="submit" formaction="/show_row_group_stats?lang={{ lang }}&fn={{ fn }}" {{ active }} class="btn btn-primary">{{ _("Get row groups stats",lang) }}</button>
    <button type="submit" formaction="/chart?lang={{ lang }}&fn={{ fn }}" {{ active }} class="btn btn-primary">{{ _("Show file chart",lang) }}</button>
    <button type="submit" formaction="/col_chart?lang={{ lang }}&fn={{ fn }}" {{ active }} class="btn btn-primary">{{ _("Show column chart",lang) }}</button>
    <button type="submit" formaction="/probe_bloom?lang={{ lang }}&fn={{ fn }}" {{ active }} class="btn btn-primary">{{ _("Probe bloom filters",lang) }}</button>
</form>

% if fn=="":

<hr>

<div class="row mb-3">
<p>

{{! _("Set parquet filename via choose file button",lang) }}

</p>
</div>

% end

</div>

% include("footer.tpl")
