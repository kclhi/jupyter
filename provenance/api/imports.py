import git, re, csv
from unidiff import PatchSet
from datetime import datetime

def get_imports(repo):

    repository = git.Repo(repo);
    uni_diff_text = repository.git.diff("HEAD~1" if len(list(repository.iter_commits("HEAD"))) > 1 else "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "HEAD", ignore_blank_lines=True, ignore_space_at_eol=True);
    patch_set = PatchSet(uni_diff_text);
    imports = [];

    for patched_file in patch_set:

        for patched_line in patched_file.__str__().split("\n"):

            python_match = re.search("(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", patched_line);
            r_match = re.search("library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", patched_line);

            if(patched_line.lower()[0]=="+"):
                if (python_match or r_match):
                    imports.append({"filename":patched_file.path.split("/")[len(patched_file.path.split("/"))-1], "author":patched_file.path.split("/")[0], "language":("Python" if python_match else "R"), "library":(python_match[3] if python_match else r_match[2]), "time":str(datetime.fromtimestamp(repository.commit("HEAD").committed_date)), "sha":repository.commit("HEAD").hexsha, "previous_sha":(repository.commit("HEAD~1").hexsha if len(list(repository.iter_commits("HEAD"))) > 1 else "0000")});
    
    return imports;
