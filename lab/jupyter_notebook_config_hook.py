
import io, requests
from notebook.utils import to_api_path

_script_exporter = None

def script_post_save(model, os_path, contents_manager, **kwargs):
    from nbconvert.exporters.script import ScriptExporter
    if model['type'] != 'notebook': return
    global _script_exporter
    if _script_exporter is None: _script_exporter = ScriptExporter(parent=contents_manager)
    log = contents_manager.log
    script, resources = _script_exporter.from_filename(os_path)
    log.info("Sending file.");
    requests.get('http://temp')

c.FileContentsManager.post_save_hook = script_post_save
