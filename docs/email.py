import csv
from datetime import datetime
from glob import glob
import json
from pathlib import Path
from pprint import pprint
from typing import Tuple
import unicodedata

def strip_accents(s):
    # https://stackoverflow.com/a/518232/7391782
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def parse_teacher(teacher_name: str) -> Tuple[str, str]:
    # Returns tuple of likely (lastname, firstname).
    # All teacher names appear to be lastname-firstname, so no detection/swapping needed.
    clean_name = teacher_name.strip().lower().replace("-", "").replace("'", "")
    clean_name = strip_accents(clean_name)  # remove accents
    names = clean_name.split(" ")
    if (not names) or len(names) < 2:
        return
    elif len(names) == 2:  # basic name
        return (names[0], names[1])
    elif len(names) == 3 and names[0] in ["Van", "De", "Le"]:  # correct with high certainty
        return (names[0] + names[1], names[2])
    else:  # heuristic: only one first name, will not always be right
        return ("".join(names[:-1]), names[-1])
    # do not leave any spaces inside names

# all_schools = {}  ## helper to generate empty dictionary for school-specific attributes
all_teachers = {}

for fn in (Path(__file__).resolve().parent / "data").glob("*_courses.json"):
    school = fn.name.split("_")[0]
    # all_schools[school] = {"email_pattern": ""}
    teachers = set()
    with open(fn) as f:
        courses_data = json.load(f)
    for course in courses_data:
        teachers.update(course["teachers"])
    parsed_teachers = set()
    for teacher in teachers:
        parsed_teacher = parse_teacher(teacher)
        if parsed_teacher:
            parsed_teachers.add((parsed_teacher, teacher))
    all_teachers[school] = parsed_teachers

# pprint(all_schools)
# for school, teachers in sorted(all_teachers.items()):
#     print(school, len(teachers))

school_attributes = {  # fn: first name, ln: last name, fl: first letter of first name
    'artevelde': {'email_pattern': '{fn}.{ln}@arteveldehs.be'},
    # ecam: Not easily retrievable from name. For example: Joëlle Bronckart -> brk@ecam.be ; Sylvie Van Emelen -> vml@ecam.be 
    'ecam': {'email_pattern': None},  
    'ecsedi-isalt': {'email_pattern': ''},
    'ehb': {'email_pattern': '{fn}.{ln}@ehb.be'},
    'he-ferrer': {'email_pattern': ''},
    'heaj': {'email_pattern': ''},
    'hech': {'email_pattern': '{fn}.{ln}@hech.be'},
    'hel': {'email_pattern': '{fn}.{ln}@hel.be'},
    'heldb': {'email_pattern': ''},
    'helmo': {'email_pattern': '{fl}.{ln}@helmo.be'},
    'henallux': {'email_pattern': '{fn}.{ln}@henallux.be'},  # dashes are preserved
    'hers': {'email_pattern': '{fn}.{ln}@hers.be'},
    'howest': {'email_pattern': '{fn}.{ln}@howest.be'},
    'ichec': {'email_pattern': '{fn}.{ln}@ichec.be'},
    'ihecs': {'email_pattern': ''},
    'ispg': {'email_pattern': ''},
    'issig': {'email_pattern': ''},
    'kuleuven': {'email_pattern': '{fn}.{ln}@kuleuven.be'},
    'odisee': {'email_pattern': '{fn}.{ln}@odisee.be'},
    'thomasmore': {'email_pattern': '{fn}.{ln}@thomasmore.be'},
    'uantwerpen': {'email_pattern': '{fn}.{ln}@uantwerpen.be'},
    'ucll': {'email_pattern': '{fn}.{ln}@ucll.be'},
    'uclouvain': {'email_pattern': '{fn}.{ln}@uclouvain.be'},
    'ugent': {'email_pattern': '{fn}.{ln}@ugent.be'},
    'uhasselt': {'email_pattern': '{fn}.{ln}@uhasselt.be'},
    'ulb': {'email_pattern': '{fn}.{ln}@ulb.be'},
    'uliege': {'email_pattern': '{fn}.{ln}@uliege.be'},
    'umons': {'email_pattern': '{fn}.{ln}@umons.ac.be'},
    'unamur': {'email_pattern': '{fn}.{ln}@unamur.be'},
    'uslb': {'email_pattern': '{fn}.{ln}@usaintlouis.be'},
    'vinci': {'email_pattern': '{fn}.{ln}@vinci.be'},
    'vives': {'email_pattern': '{fn}.{ln}@vives.be'},
    'vub': {'email_pattern': '{fn}.{ln}@vub.be'}
    }

with open(Path(__file__).resolve().parent / "email_addresses_{}.csv".format(datetime.now().strftime("%Y%m%d%H%M%S")), "w") as of:
    csvw = csv.writer(of)
    csvw.writerow(["School", "Name", "Email address", "Email sent?", "Reply received?"])
    for school, teachers in sorted(all_teachers.items()):
        email_template = school_attributes[school]['email_pattern']
        for parsed_name, name in sorted(teachers):
            csvw.writerow([
                school,
                name,
                email_template.format(**{
                'fn': parsed_name[1], 
                'ln': parsed_name[0], 
                'fl': parsed_name[1][0],  # first letter of first name
                }) if email_template else None,
            ])