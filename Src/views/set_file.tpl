% from tpl_funcs import _

% include("header.tpl", title=request.path)

<div class="container">
<h1 class="text-center">{{ _("Set parquet file name",lang) }}</h1>

<form method="post">

    <div class="row mb-3">
        <label for="inputFile" class="col-sm-1 col-form-label">{{ _("Path",lang) }}</label>
        <div class="col-sm-11">
            <input name="input_file" type="text" class="form-control" id="inputFile" aria-describedby="fileHelp">
            <div id="fileHelp" class="form-text">{{ _("Absolute path OR s3 url",lang) }}</div>
        </div>
    </div>

    <div class="row mb-3">
        <label for="fileAlias" class="col-sm-1 form-label">{{ _("File alias",lang) }}</label>
        <div class="col-sm-2">
            <input name="input_alias" type="text" class="form-control" id="fileAlias" aria-describedby="aliasHelp">
            <div id="aliasHelp" class="form-text">{{ _("File alias is used as filename for meta DB",lang) }}</div>
        </div>
        <label for="accessKey" class="col-sm-1 form-label">{{ _("Access key",lang) }}</label>
        <div class="col-sm-2">
            <input name="input_key" type="text" class="form-control" id="accessKey" aria-describedby="keyHelp">
            <div id="keyHelp" class="form-text">{{ _("S3 access key for S3, keep empty for local files",lang) }}</div>
        </div>
        <label for="secret" class="col-sm-1 form-label">Secret</label>
        <div class="col-sm-5">
            <input name="input_secret" type="text" class="form-control" id="secret" aria-describedby="secretHelp">
            <div id="secretHelp" class="form-text">{{ _("Secret for S3 access key, keep empty for local files",lang) }}</div>
        </div>
    </div>

    <button type="submit" formaction="/main?lang={{ lang }}" class="btn btn-primary">{{ _("Set file for further processing",lang) }}</button>

</form>

<hr>

<div class="row mb-3">
<p>

{{! _("This is the form to choose parquet file for further analysis,<br>",lang) }}
{{! _("filename is stored in database along with other meta information,<br>",lang) }}
{{! _("key and secret ARE NOT STORED, they are used once only to get parquet file metadata from S3.",lang) }}

</p>
</div>

</div>

% include("footer.tpl")
