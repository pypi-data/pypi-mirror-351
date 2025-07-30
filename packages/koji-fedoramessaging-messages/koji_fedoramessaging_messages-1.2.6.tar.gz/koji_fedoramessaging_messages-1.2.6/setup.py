# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['koji_fedoramessaging_messages']

package_data = \
{'': ['*']}

install_requires = \
['fedora-messaging>=3.0.1']

entry_points = \
{'fedora.messages': ['koji_fedoramessaging.build.BuildStateChangeV1 = '
                     'koji_fedoramessaging_messages.build:BuildStateChangeV1',
                     'koji_fedoramessaging.package.ListChangeV1 = '
                     'koji_fedoramessaging_messages.package:ListChangeV1',
                     'koji_fedoramessaging.repo.DoneV1 = '
                     'koji_fedoramessaging_messages.repo:DoneV1',
                     'koji_fedoramessaging.repo.InitV1 = '
                     'koji_fedoramessaging_messages.repo:InitV1',
                     'koji_fedoramessaging.rpm.SignV1 = '
                     'koji_fedoramessaging_messages.rpm:SignV1',
                     'koji_fedoramessaging.tag.TagV1 = '
                     'koji_fedoramessaging_messages.tag:TagV1',
                     'koji_fedoramessaging.tag.UntagV1 = '
                     'koji_fedoramessaging_messages.tag:UntagV1',
                     'koji_fedoramessaging.task.TaskStateChangeV1 = '
                     'koji_fedoramessaging_messages.task:TaskStateChangeV1']}

setup_kwargs = {
    'name': 'koji-fedoramessaging-messages',
    'version': '1.2.6',
    'description': 'A schema package for messages sent by the koji-fedoramessaging plugin',
    'long_description': '# koji-fedoramessaging messages\n\nA schema package for [koji-fedoramessaging](http://github.com/fedora-infra/koji-fedoramessaging).\n\nSee the [detailed documentation](https://fedora-messaging.readthedocs.io/en/latest/messages.html) on packaging your schemas.\n\n\n## Rebuilding for Fedora Infra\n\nAt the moment this package is not in Fedora. To build a RPM for Fedora Infra, follow the following steps:\n\n- checkout the latest tag: `git checkout v1.2.6`\n- build the SRPM with Packit: `packit srpm --no-update-release`\n- build the RPM in koji: `koji build f42-infra python-koji-fedoramessaging-messages-1.2.6-1.fc42.src.rpm`\n- move the RPM to the production tag: `koji move f42-infra-stg f42-infra python-koji-fedoramessaging-messages-1.2.6-1.fc42`\n',
    'author': 'Fedora Infrastructure Team',
    'author_email': 'infrastructure@lists.fedoraproject.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/fedora-infra/koji-fedoramessaging-messages',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
