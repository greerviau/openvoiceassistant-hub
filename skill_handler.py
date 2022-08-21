skill_imports = {}

def imports(skills):
    for skill in skills:
        print('Importing ', skill)
        skill_imports[skill] = __import__(f'skills.{skill}', fromlist=[''])

def skill_response(context):
    tag = context['tag']
    skill = context['skill']
    method = getattr(skill_imports[tag], skill)
    method(context)