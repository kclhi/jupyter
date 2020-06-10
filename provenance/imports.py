import git, re, csv
from unidiff import PatchSet
from datetime import datetime
with open('imports.csv', 'w', newline='') as csvfile:
	fieldnames = ['filename', 'author', 'language', 'import', 'time', 'sha'];
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames);
	writer.writeheader();
	repository = git.Repo("/home/martin/covid-1");
	commits = len(list(repository.iter_commits('HEAD')));
	for commit in range(1, commits):
		print(commit);
		uni_diff_text = repository.git.diff('HEAD~' + str(commit), 'HEAD~' + str(commit-1), ignore_blank_lines=True, ignore_space_at_eol=True)
		patch_set = PatchSet(uni_diff_text);
		for patched_file in patch_set:
			for patched_line in patched_file.__str__().split("\n"):
				python_match = re.search("(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", patched_line);
				r_match = re.search("library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", patched_line); 
				if("+" in patched_line.lower()):
					if (python_match or r_match):
						writer.writerow({'filename': patched_file.path.split("/")[len(patched_file.path.split("/"))-1], 'author':patched_file.path.split("/")[0], 'language':("Python" if python_match else "R"), 'import':(python_match[3] if python_match else r_match[2]), 'time':datetime.fromtimestamp(repository.commit('HEAD~' + str(commit-1)).committed_date), 'sha':repository.commit('HEAD~' + str(commit-1)).hexsha});
					elif ((not python_match and "import " in patched_line.lower()) or (not r_match and "library(" in patched_line.lower())):
						print("----> Check no match: " + patched_line.lower());
