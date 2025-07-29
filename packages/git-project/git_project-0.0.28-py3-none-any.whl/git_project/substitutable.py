#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2020-present David A. Greene <dag@obbligato.org>

# SPDX-License-Identifier: AGPL-3.0-or-later

# Copyright 2024 David A. Greene

# This file is part of git-project

# git-project is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along
# with git-project. If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path

from .configobj import ConfigObject
from .shell import run_command_with_shell

class SubstitutableConfigObject(ConfigObject):
    """Base class for objects that use git-config as a backing store and allow
    substitution of config values.  Inherits from ConfigObject.

    Derived classes should implement the ConfigObject protocol.

    """
    def __init__(self, git, section, subsection, ident, **kwargs):
        """RunnableConfigObject construction.  This should be treated as a private
        method and all construction should occur through the get method.

        git: An object to query the repository and make config changes.

        project_section: git config section of the active project.

        subsection: An arbitrarily-long subsection appended to project_section

        ident: The name of this specific ConfigObject.

        **kwargs: Keyword arguments of property values to set upon construction.

        """
        super().__init__(git, section, subsection, ident, **kwargs)

    def substitute_value(self, git, project, string, formats=dict()):
        """Given a project, perform variable substitution on a string and return the
        result as a string.

        git: An object to query the repository and make config changes.

        project: The currently active Project.

        string: The string on which to perform substitution.

        """
        found_path = False

        # Substitute for project-global values.
        for key, value in project.iteritems():
            if key == self.get_subsection():
                value = self.get_ident()
            formats[key] = value

        # Substitute for values in self.
        for key, value in self.iteritems():
           formats[key] = value

        formats['project'] = project.get_section()
        formats['gitdir'] = str(git.get_gitdir())
        formats['git_common_dir'] = str(git.get_git_common_dir())
        formats['git_workdir'] = str(git.get_working_copy_root())

        current_branch = git.get_current_branch()
        if not current_branch:
            # See if we're rebasing and use the branch being rebased for the substitution.
            worktree = git.get_current_worktree()
            common_dir = git.get_git_common_dir()

            if worktree:
                common_dir = f'{common_dir}/worktrees/{worktree}'

            rebase_apply = f'{common_dir}/rebase-apply'
            rebase_merge = f'{common_dir}/rebase-merge'

            for rebase_path in (rebase_apply, rebase_merge):
                head_name = Path(f'{rebase_path}/head-name')
                if head_name.exists():
                    current_branch = git.refname_to_branch_name(head_name.read_text().strip())
                    break

        formats['branch'] = current_branch

        # Make sure substitutions don't reference themselves, to avoid an
        # infinite loop substituting.
        #
        # NOTE: This won't catch mutually-recursive situations like:
        #
        # path: {dir}/foo
        # dir: {path}/bar
        for key, value in formats.items():
            if f'{{{key}}}' in value:
                raise RuntimeError(
                    f'Recursive substitution: {key} is in {value}'
                )

        def try_format(string, formats):
            return eval(f"f'{string}'", formats)

        def add_scope(project, key, formats):
            scope = project.get_scope(key)
            if scope:
                value = scope.get_ident()
                formats[key] = value

        # Allow escaping braces by surrounding each brace with braces.  This is
        # not valid f-string syntax and is unlikely to be used in ordinary
        # config values.  Replace with an equally unlikely sequence, then
        # substitute on that string.

        escaped_braces = False
        while True:
            escaped_braces = escaped_braces or '{{}' in string or '{}}' in string
            if escaped_braces:
                string = string.replace('{{}', '[[[')
                string = string.replace('{}}', ']]]')
            try:
                newstring = try_format(string, formats)
            except KeyError as exception:
                # See if this is a scope name.
                for key in exception.args:
                    add_scope(project, key, formats)
                # Try again after adding scopes.
                newstring = try_format(string, formats)
            except NameError as exception:
                # args is simply the error  message, with the name surrounded by
                # '.  Use .name attribute after upgrading to python 3.10.
                for arg in exception.args:
                    key = arg.split("\'")[1]
                    add_scope(project, key, formats)
                # Try again after adding scopes.
                newstring = try_format(string, formats)

            changed = False if newstring == string else True
            string = newstring
            if not changed:
                if escaped_braces:
                    string = string.replace('[[[', '{')
                    string = string.replace(']]]', '}')
                break

        return string
