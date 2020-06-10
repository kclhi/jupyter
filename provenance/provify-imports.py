#!/usr/bin/env python3

import csv
from datetime import datetime
from collections import defaultdict
import pgt


# gather by commit
timeline = defaultdict(list)

with open('imports.csv') as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        k = (row['sha'], row['time'], row['author'])
        v = (row['filename'], row['import'], row['language'])
        timeline[k].append(v)


client = pgt.RabbitClient('localhost', 5672, 'flopsy', 'password', 'pgt')

# set up document
with open('templates/imported.json') as fh:
    t = fh.read()
client.new_template('imported', t)

client.new('covid', 'http://covid.kcl.ac.uk')
client.namespace('covid', 'pandas', 'http://covid.kcl.ac.uk/pandas')
client.register_template('covid', 'imported')


current_imports = defaultdict(list)
identifier = {}
imported_count = defaultdict(int)

# sort chronologically
for commit in sorted(timeline, key=lambda abc: abc[1]):
    # gather by file
    latest_imports = defaultdict(list)
    for filename, library, language in timeline[commit]:
        latest_imports[filename].append((library, language))

    for filename, imports in latest_imports.items():
        # filter existing imports
        new_imports = []
        for i in imports:
            if i not in current_imports[filename]:
                new_imports.append(i)

        if len(new_imports) == 0:
            continue

        for i in new_imports:
            print(commit, filename, i)

        # instantiate first new import
        s = pgt.Substitution()

        if filename in identifier:
            nb_id1 = identifier[filename]
        else:
            nb_id1 = filename + '_0000'
        s.add_ivar('notebookBefore', pgt.QualifiedName('', nb_id1))

        nb_id2 = filename + '_' + commit[0]
        s.add_ivar('notebookAfter', pgt.QualifiedName('', nb_id2))
        s.add_vvar('filename', filename)
        s.add_vvar('commit', commit[0])

        a_id = filename + '_' + str(imported_count[filename])
        s.add_ivar('imported', pgt.QualifiedName('', a_id))
        s.add_vvar('time', datetime.fromisoformat(commit[1]))

        s.add_ivar('author', pgt.QualifiedName('', commit[2]))

        init_import = new_imports[0]

        s.add_ivar('library', pgt.QualifiedName('', init_import[0]))
        s.add_vvar('libraryName', init_import[0])
        s.add_vvar('language', init_import[1])

        f_id = filename + '_' + commit[0]
        client.geninit('covid', 'imported', f_id, s.to_json())

        imported_count[filename] += 1

        # instantiate remaining new imports
        for i in new_imports[1:]:
            z = pgt.Substitution()

            a_id = filename + '_' + str(imported_count[filename])
            z.add_ivar('imported', pgt.QualifiedName('', a_id))
            z.add_vvar('time', datetime.fromisoformat(commit[1]))

            z.add_ivar('library', pgt.QualifiedName('', i[0]))
            z.add_vvar('libraryName', i[0])
            z.add_vvar('language', i[1])

            client.genzone('covid', 'imported', f_id, 'import', z.to_json())

            imported_count[filename] += 1

        client.genfinal('covid', 'imported', f_id)

        identifier[filename] = nb_id2
        current_imports[filename].extend(new_imports)
