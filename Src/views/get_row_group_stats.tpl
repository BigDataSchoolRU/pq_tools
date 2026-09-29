% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Show Row Group statistics",lang) }}</h1>

<a href="/main?lang={{ lang }}&fn={{ fn }}">{{ _("Home screen",lang) }}</a>

<form method="post">
    <input type="hidden" name="colstr" value="{{ ','.join(columns) }}">
    <input type="hidden" name="grpnumbstr" value="{{ grpnumb }}">
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
                <option {{ "selected" if col==selected[0] else "" }} value="{{ col }}">{{ col }}</option>
            % end
            </select>  
        </div>
        <label for="grpNo" class="col-sm-2 col-form-label">{{ _("Group number",lang) }}</label>
        <div class="col-sm-4">
            <select name="grp_numb" id="groupNumb" class="form-select">
            % for i in range(grpnumb):      
                <option {{ "selected" if i==selected[1] else "" }} value="{{ i }}">{{ i }}</option>
            % end
            </select>  
        </div>
    </div>
    <button type="submit" formaction="/show_row_group_stats?lang={{ lang }}&fn={{ fn }}" class="btn btn-primary">{{ _("Show row group stats",lang) }}</button>
</form>

% if statdict:
<br>
<table class="table w-auto table-striped">
<tbody>
% i = 0
% for k,v in statdict.items():
    % tag = "th" if i==0 else "td" 
    <tr>
        <th>{{ k }}</th>
        % for ln in v:
            <{{ tag }}>{{ ln }}</{{ tag }}>
        % end
    </tr>
    % i += 1
% end
</tbody>
</table>
% end

</div>
