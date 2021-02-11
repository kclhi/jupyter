import git, re, csv
from unidiff import PatchSet

def net_insertion(insert, lines):

    for line in lines:
        if len(line) > 0 and line[0].lower()=="-" and line[1:].lower()==insert[1:].lower(): return 0;

    return 1;
    
def extract_variable_values(repo, expressions):

    repository = git.Repo(repo);
    
    # Use git's 'intent to add' flag in order to include untracked files in diff.
    for file in repository.untracked_files:
        repository.git.add(file, N=True);

    unidiff_text = repository.git.diff(ignore_blank_lines=True, ignore_space_at_eol=True);
    patch_set = PatchSet(unidiff_text);
    template_substitutions = {};

    for patched_file in patch_set:
        
        # Combine hunks by splitting file
        for patched_line in str(patched_file).split("\n"):
            
            if len(patched_line) > 1 and patched_line.lower()[0]=="+" and patched_line.lower()[1]!="+":
                
                if net_insertion(patched_line, str(patched_file).split("\n"))<1: continue;

                for expression in expressions:
                    match = re.search(expression.regex, patched_line);

                    if match:
                        
                        # Do different things to derive a value for a matched variable.
                        if expression.match_action.action=="text":
                            value=expression.match_action.value;
                        elif expression.match_action.action=="extract":
                            value=match[int(expression.match_action.value)];

                        for variable in expression.template_variable:
                            substitution_variable={};
                            substitution_variable["name"]=variable.name;
                            substitution_variable["value"]=value;
                            template_name = variable.template.name;
                            # A list of substitutions is maintained for each template. If len > 1 zones assumed.
                            last_substitution = template_substitutions.get(template_name,[[]])[-1];
                            # If the last substitution already contains the current mapped variable, 
                            # start a new substitution (zone).
                            if variable.name in [variable_name["name"] for variable_name in last_substitution]:
                                last_substitution=[];
                            last_substitution.append(substitution_variable);
                            # Associate new substitution (zone) with template.
                            if len(last_substitution)==1:
                                template_substitutions.setdefault(variable.template.name,[]).append(last_substitution);

    return {"templates": template_substitutions};
