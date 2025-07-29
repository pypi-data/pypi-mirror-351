# Copyright (C) 2022--2024 the baldaquin team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Rudimentary release manager.
"""

from argparse import ArgumentParser
import time


from baldaquin import logger, execute_shell_command, DEFAULT_CHARACTER_ENCODING
from baldaquin import BALDAQUIN_VERSION_FILE_PATH, BALDAQUIN_RELEASE_NOTES_PATH, \
                      BALDAQUIN_TOML_FILE_PATH


INCREMENT_MODES = ('major', 'minor', 'patch')


def write_version_file(version: str, tag_date: str) -> None:
    """Write  the versioning info file with a given version string and build date.
    """
    logger.info(f'Writing versioning info to {BALDAQUIN_VERSION_FILE_PATH}...')
    logger.debug(f'Version: {version}')
    logger.debug(f'Tag date: {tag_date}')
    with open(BALDAQUIN_VERSION_FILE_PATH, 'w',
              encoding=DEFAULT_CHARACTER_ENCODING) as output_file:
        output_file.write(f"VERSION = '{version}'\nTAG_DATE = '{tag_date}'\n")
    logger.info('Done.')


def update_toml_file(old_version, new_version) -> None:
    """Update the pyproject.toml file with the new version.

    We should think about what the proper way to do this is. I see at least three
    avenues to out goal:

    * use the third-party module toml---this would probably be the most elegant
      solution, at the expense of adding one more dependence;
    * use the standard-lib tomllib module (which only support reading toml files)
      and provide a custom implementation for the write part;
    * use the brute force and do everything by hand in text format.

    For the time being I am leaning toward the last option, but we might want to
    revise this in the future.
    """
    # Read (and close) the input file.
    logger.info(f'Reading input file {BALDAQUIN_TOML_FILE_PATH}...')
    with open(BALDAQUIN_TOML_FILE_PATH, 'r', encoding=DEFAULT_CHARACTER_ENCODING) as input_file:
        lines = input_file.readlines()
    # Process the file content in memory---note this includes a check on the
    # version found in the file, and we should run this as early as possible in the
    # release process so that, if anything goes wrong, we do exit before we mess
    # with the repo.
    for i, line in enumerate(lines):
        if line.startswith('version'):
            _, version = line.strip('\n').split(' = ')
            version = version.strip('"')
            if version != old_version:
                raise RuntimeError(f'Unexpected version found in {BALDAQUIN_TOML_FILE_PATH} '
                                   f'({version}) vs ({old_version})')
            logger.debug(f'Version {version} found, target is {new_version}.')
            lines[i] = f'version = "{new_version}"\n'
    # Write the (updated) content to file.
    logger.info(f'Writing output file {BALDAQUIN_TOML_FILE_PATH}...')
    with open(BALDAQUIN_TOML_FILE_PATH, 'w', encoding=DEFAULT_CHARACTER_ENCODING) as output_file:
        output_file.writelines(lines)


def increment_version_file(mode: str, tag_date: str) -> str:
    """Update the __version__.py file.
    """
    logger.info('Updating versioning info file...')
    if mode not in INCREMENT_MODES:
        raise RuntimeError(f'Invalid incerement mode "{mode}"---valid modes are {INCREMENT_MODES}')
    logger.info(f'Reading {BALDAQUIN_VERSION_FILE_PATH}...')
    with open(BALDAQUIN_VERSION_FILE_PATH, 'r',
              encoding=DEFAULT_CHARACTER_ENCODING) as input_file:
        old_version = input_file.readline().split('=')[-1].strip(' \'\n')
    logger.debug(f'Previous version was {old_version}')
    major, minor, patch = (int(item) for item in old_version.split('.'))
    if mode == 'major':
        major += 1
        minor = 0
        patch = 0
    elif mode == 'minor':
        minor += 1
        patch = 0
    elif mode == 'patch':
        patch += 1
    new_version = f'{major}.{minor}.{patch}'
    logger.info(f'Target version is {new_version}')
    update_toml_file(old_version, new_version)
    write_version_file(new_version, tag_date)
    return new_version


def update_release_notes(version: str, tag_date: str) -> None:
    """This is appending the version string and the tag date at the top of the file.
    """
    title = '.. _release_notes:\n\nRelease notes\n=============\n\n'
    logger.info(f'Reading in {BALDAQUIN_RELEASE_NOTES_PATH}...')
    with open(BALDAQUIN_RELEASE_NOTES_PATH, 'r',
              encoding=DEFAULT_CHARACTER_ENCODING) as input_file:
        notes = input_file.read().strip('\n').strip(title)
    logger.info(f'Writing out {BALDAQUIN_RELEASE_NOTES_PATH}...')
    with open(BALDAQUIN_RELEASE_NOTES_PATH, 'w',
              encoding=DEFAULT_CHARACTER_ENCODING) as output_file:
        output_file.writelines(title)
        output_file.writelines(f'\n*baldaquin {version} ({tag_date})*\n\n')
        output_file.writelines(notes)
    logger.info('Done.')


def tag(mode):
    """Tag the actual package.
    """
    tag_date = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    execute_shell_command(['git', 'pull'])
    execute_shell_command(['git', 'status'])
    version = increment_version_file(mode, tag_date)
    update_release_notes(version, tag_date)
    msg = f'Prepare for tag {version}.'
    execute_shell_command(['git', 'commit', '-a', '-m', msg])
    execute_shell_command(['git', 'push'])
    msg = 'Tagging version {version}.'
    execute_shell_command(['git', 'tag', '-a', version, '-m', f'"{msg}"'])
    execute_shell_command(['git', 'push', '--tags'])
    execute_shell_command(['git', 'status'])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('mode', type=str, choices=INCREMENT_MODES, help='Tag increment mode')
    args = parser.parse_args()
    tag(args.mode)
