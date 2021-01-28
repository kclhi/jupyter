import git, os, json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from unidiff import PatchSet
from datetime import datetime
from api import imports
from api import provify

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
        imported = imports.get_imports(repo);

        if len(imported):
            if commit(repository, user + "/" + filename):
                provify.provify_imports([{**library, **{"filename": filename, "author":user, "time":str(datetime.fromtimestamp(repository.commit("HEAD").committed_date)), "sha":repository.commit("HEAD").hexsha, "previous_sha":(repository.commit("HEAD~1").hexsha if len(list(repository.iter_commits("HEAD"))) > 1 else "0000")}} for library in imported], "templates/imported.json");
                    
    return JSONResponse({});
