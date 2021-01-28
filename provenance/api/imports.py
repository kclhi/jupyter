import git, re, csv
from unidiff import PatchSet

def net_insertion(insert, lines):

    for line in lines:
        if line[0].lower()=="-" and line[1:].lower()==insert[1:].lower(): return 0;

    return 1;
    
def get_imports(repo):

    repository = git.Repo(repo);
    
    # Use git's 'intent to add' flag in order to include untracked files in diff.
    for file in repository.untracked_files:
        repository.git.add(file, N=True);

    unidiff_text = repository.git.diff(ignore_blank_lines=True, ignore_space_at_eol=True);
    patch_set = PatchSet(unidiff_text);
    imports = [];

    for patched_file in patch_set:
        
        # Combine hunks by splitting file
        for patched_line in str(patched_file).split("\n"):

            python_match = re.search("(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", patched_line);
            r_match = re.search("library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", patched_line);

            if patched_line.lower()[0]=="+":

                if net_insertion(patched_line, str(patched_file).split("\n"))<1: continue;
                
                if python_match or r_match:
                    imports.append({"language":("Python" if python_match else "R"), "library":(python_match[3] if python_match else r_match[2])});
    
    return imports;
