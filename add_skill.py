import json
import os
import click

@click.command()
@click.option('--skill', default=None)
@click.option('--active_skills', default='active_skills.json')
def add_skill(skill, active_skills):
    if skill:
        available_skills = os.listdir('skills')
        if skill in available_skills:
            if os.path.exists('active_skills.json'):
                active_skills = json.load(open('active_skills.json'))
            else:
                active_skills = []

            active_skills.append(skill)
            with open('active_skills.json', 'w') as file:
                file.write(json.dumps(active_skills, indent=4))
        else:
            print(f'Skill {skill} does not exist')
    else:
        print('Specify a skill')

if __name__ == '__main__':
    add_skill()