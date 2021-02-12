import git, os, json, uuid
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from unidiff import PatchSet
from datetime import datetime
from pony import orm
from api import variables
from api.provify import Provify
from api.models.base import db

provify = Provify();
app = Starlette(debug=True)

def commit(repo, add, branch='master', message='Auto commit'):
    has_changed = False;

    if add in repo.untracked_files:
        repo.git.add(add);
        if has_changed is False:
            has_changed = True;

    if repo.is_dirty() is True:
        if add in repo.git.diff(None, name_only=True).split('\n'):
            repo.git.add(add);
            if has_changed is False:
                has_changed = True;

    if has_changed is True:
        repo.git.commit('-m', message);
    
    return has_changed;

@app.route('/add', methods=["POST"])
async def add(request):

    try:
        notebook = await request.json();
    except:
        notebook = None;

    print("Received: " + str(notebook));

    if notebook and notebook["notebook"] and "name" in notebook["notebook"]: # is save
        repo = "./api/repo";
        repository = git.Repo(repo);
        user =  notebook["user"];
        folder = repo + "/" + user;
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        filename = notebook["notebook"]["name"];
        f = open(folder + "/" + filename, "w");
        f.write(notebook["code"]);
        f.close();

        with orm.db_session:
            variable_values = variables.extract_variable_values(repo, db.Expression.select());
       
        if len(variable_values):
            if commit(repository, user + "/" + filename):

                previous_sha = repository.commit("HEAD~1").hexsha if len(list(repository.iter_commits("HEAD"))) > 1 else "0000";
                sha = repository.commit("HEAD").hexsha;

                # Fixed values to be applied to each substitution for a given template (may be the whole template).
                fixed_values = {"templates": {
                    "saved": [
                        {"name": "notebookBefore", "value": filename + "_" + previous_sha},
                        {"name": "notebookAfter", "value": filename + '_' + sha},
                        {"name": "filename", "value": filename},
                        {"name": "commit", "value": sha},
                        {"name": "sha", "value": sha},
                        {"name": "author", "value": user},
                        {"name": "authorName", "value": user},
                        {"name": "saved", "value": filename + '_' + str(uuid.uuid1())},
                        {"name": "time", "value": str(datetime.fromisoformat(str(datetime.fromtimestamp(repository.commit("HEAD").committed_date))))},
                    ], 
                    "imported2": [
                        {"name": "notebook", "value": filename + '_' + sha},
                        {"name": "imported", "value": filename + '_' + str(uuid.uuid1())},
                    ],
                    "called": [
                        {"name": "notebook", "value": filename + '_' + sha},
                        {"name": "called", "value": filename + '_' + str(uuid.uuid1())},
                    ]
                }};

                provify.create_substitutions("covid", "pandas", fixed_values, variable_values);
                    
    return JSONResponse({});
