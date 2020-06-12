import git, os, json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from api import imports;
from api import provify;

app = Starlette(debug=True)

def commit(repo, branch='master', message='Auto commit'):
        has_changed = False;

        for file in repo.untracked_files:
            repo.git.add(file);
            if has_changed is False:
                has_changed = True;

        if repo.is_dirty() is True:
            for file in repo.git.diff(None, name_only=True).split('\n'):
                if file:
                    repo.git.add(file);
                    if has_changed is False:
                        has_changed = True;

        if has_changed is True:
            repo.git.commit('-m', message);


@app.route('/add', methods=["POST"])
async def add(request):

    try:
        notebook = await request.json();
    except:
        notebook = None;

    print("Received: " + str(notebook));

    if (notebook):
        if(notebook["notebook"] and "name" in notebook["notebook"]): # is save
            repo = "./api/repo";
            repository = git.Repo(repo);
            folder = './api/repo/' + notebook["user"];
            if not os.path.exists(folder):
                os.makedirs(folder)
            f = open(folder + "/" + notebook["notebook"]["name"], "w");
            f.write(notebook["code"]);
            f.close()
            commit(repository);
            csv = "./api/imports.csv";
            imports.get_imports(repo, csv);
            provify.provify_imports(csv, "templates/imported.json");

    return JSONResponse({});
