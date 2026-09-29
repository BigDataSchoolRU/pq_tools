% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("General parquet file info",lang) }}</h1>

<a href="/main?lang={{ lang }}&fn={{ fn }}">{{ _("Home screen",lang) }}</a>
    
    % for sect in sections:
    <h2>{{ sect[0] }}</h2>
    <table class="table w-auto table-striped">
      <tbody>
        % for rowEl in sect[1]:
            <tr>
                <th scope="row">{{ rowEl[0] }}</th>
                <td>{{ rowEl[1] }}</td>
            </tr>
        % end
      </tbody>
    </table>
    % end

</div>

% include("footer.tpl")
