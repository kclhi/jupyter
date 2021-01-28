import git, re, csv
from unidiff import PatchSet

def net_insertion(insert, lines):

    for line in lines:
        if line[0].lower()=="-" and line[1:].lower()==insert[1:].lower(): return 0;

    return 1;
    
def get_actions(repo, mappings):

    repository = git.Repo(repo);
    
    # Use git's 'intent to add' flag in order to include untracked files in diff.
    for file in repository.untracked_files:
        repository.git.add(file, N=True);

    unidiff_text = repository.git.diff(ignore_blank_lines=True, ignore_space_at_eol=True);
    patch_set = PatchSet(unidiff_text);
    actions = [];

    for patched_file in patch_set:
        
        # Combine hunks by splitting file
        for patched_line in str(patched_file).split("\n"):

            currentAction = {};

            if patched_line.lower()[0]=="+":
                
                if net_insertion(patched_line, str(patched_file).split("\n"))<1: continue;

                for mapping in mappings:
                    match = re.search(mapping.regex, patched_line);

                    if match:

                        if mapping.match_action.action=="text":
                            value=mapping.match_action.value;
                        elif mapping.match_action.action=="extract":
                            value=match[int(mapping.match_action.value)];
                        currentAction[mapping.var]=value;
            
            if len(currentAction): actions.append(currentAction);
                      
    return actions;
