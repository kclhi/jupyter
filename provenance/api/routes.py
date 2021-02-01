import git, os, json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from unidiff import PatchSet
from datetime import datetime
from pony import orm
from api import variables
from api import provify
from api.models.base import db

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

        db.bind(provider='sqlite', filename='mappings.sqlite');
        db.generate_mapping();
        with orm.db_session:
            variable_substitutions = variables.get_variable_substitutions(repo, db.Expression.select());

        print(variable_substitutions);
        
        if len(variable_substitutions):
            if commit(repository, user + "/" + filename):
                provify.create_substitution({**variable_substitutions, **{"filename": filename, "author":user, "time":str(datetime.fromtimestamp(repository.commit("HEAD").committed_date)), "sha":repository.commit("HEAD").hexsha, "previous_sha":(repository.commit("HEAD~1").hexsha if len(list(repository.iter_commits("HEAD"))) > 1 else "0000")}});
                    
    return JSONResponse({});
