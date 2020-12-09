import re
import sys
import cookiecutter


MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

module_name = '{{ cookiecutter.project_slug}}'

if not re.match(MODULE_REGEX, module_name):
    print('ERROR: The project slug (%s) is not a valid Python module name. Please do not use a - and use _ instead' % module_name)

    #Exit to cancel project
    sys.exit(1)

if ('{{ cookiecutter.author_name|lower}}' == 'your name (or your organization/company/team)'):
    print('Default author name to vizzuality')
    {{ cookiecutter.update({"author_name": 'vizzuality' }) }}



