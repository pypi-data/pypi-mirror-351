"""Main command line interface for the syllabus package."""

# pylint: disable=C0116, C0115, W0613, E1120, W0107, W0622

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import click

from syllabus.sync import  compile_syllabus, renumber_lessons, regroup_lessons, check_structure, metafy_lessons
from syllabus import __version__  # Import the package version


logger = logging.getLogger(__name__)


def setup_logging(verbose):

    if verbose == 1:
        log_level = logging.INFO
    elif verbose > 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)s: %(message)s')
    logger.setLevel(log_level)


@dataclass
class Context:

    verbose: bool = False
    exceptions: bool = False
    lesson_dir: Path = None



@click.group()
@click.option('-v', '--verbose', count=True, help="Increase verbosity level.")
@click.option('-e', '--exceptions', is_flag=True, help="Raise exceptions on errors.")
@click.option('-d', '--dir', type=click.Path(), help="Set the working directory.", default=Path('.'))
@click.option('-l', '--lesson-dir', type=click.Path(), help="Set the lesson directory.", default=None)
@click.pass_context
def cli(ctx, verbose, exceptions, dir, lesson_dir):
    setup_logging(verbose)

    ctx.obj = Context()
    ctx.obj.verbose = verbose > 0
    ctx.obj.exceptions = exceptions
    
    if dir:
        if not Path(dir).exists():
            logger.error(
                "Error: The working directory %s does not exist.", dir)
            exit(1)
        os.chdir(dir)
    
    # Set the lesson directory
    if lesson_dir:
        lesson_path = Path(lesson_dir)
    else:
        lesson_path = Path('lessons')  # Default to 'lessons' in current directory
    
    # Check if the lesson directory exists
    if not lesson_path.exists():
        logger.error(f"Error: The lesson directory {lesson_path} does not exist.")
        exit(1)
    
    ctx.obj.lesson_dir = lesson_path





@click.command()
def version():
    """Show the version and exit."""
    print(f"Syllabus CLI version {__version__}")


cli.add_command(version)


@click.command()
@click.pass_context
def check(ctx):
    """Validate the structure of the lesson directory."""
    
    lesson_dir = ctx.obj.lesson_dir

    # Use lesson_dir from argument if provided, otherwise use the one from context
    target_dir = Path(lesson_dir) if lesson_dir else ctx.obj.lesson_dir
    
    if not target_dir.exists():
        logger.error("Error: The lesson directory %s does not exist.", target_dir)
        exit(1)

    try:
        check_structure(target_dir)
    except Exception as e:
        logger.error("Error: %s", e)
        exit(1)
        

cli.add_command(check)



@click.command()
@click.option('-g', '--regroup', is_flag=True, help="Regroup lessons with the same basename.")
@click.option('-n', '--renumber', is_flag=True, help="Renumber lessons in the directory.")
@click.option('-m', '--metafy', is_flag=True, help="Add metadata to lessons.")
@click.option('-i', '--increment', type=int, default=1, help="Increment the lesson numbers by this amount.")
@click.option('-f', '--file', type=str, help="Specify the syllabus file.")
@click.pass_context
def compile(ctx, regroup, renumber, increment, metafy, file):
    """Read the lessons and compile a syllabus"""
    
    lesson_dir = ctx.obj.lesson_dir

    # Use lesson_dir from argument if provided, otherwise use the one from context
    target_dir = Path(lesson_dir) if lesson_dir else ctx.obj.lesson_dir
    
    if not target_dir.exists():
        logger.error("Error: The lesson directory %s does not exist.", target_dir)
        exit(1)
    
    if regroup:
        regroup_lessons(
            lesson_dir=target_dir,
            dryrun=False,
        )
    
    if renumber:
        renumber_lessons(
            lesson_dir=target_dir,
            increment=increment,
            dryrun=False,
        )
    
    if metafy:
        metafy_lessons(
            lesson_dir=target_dir,
            dryrun=False,
        )
    
    course = compile_syllabus(lesson_dir=target_dir)
    
    def rel_path(a, b):
        return str(Path(os.path.relpath(b, start=a)))

    
    if file == '-':
        print(course.to_yaml)
    elif file is None:
        file = target_dir/'.jtl'/'syllabus.yaml'
        
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        course.module_dir = rel_path(Path(file).parent,target_dir)
        Path(file).write_text(course.to_yaml())
        print(f"Course YAML written to {file}")
    else:
        course.module_dir = rel_path(Path(file).parent,target_dir)
        Path(file).write_text(course.to_yaml())
        print(f"Course YAML written to {file}")
        
        

cli.add_command(compile, name='compile')


@click.command()
@click.option('-d', '--dryrun', is_flag=True, help="Perform a dry run without renaming files.")
@click.option('-i', '--increment', type=int, default=1, help="Increment the lesson numbers by this amount.")
@click.pass_context
def renumber(ctx, dryrun, increment):
    """Renumber lessons."""
    
    lesson_dir = ctx.obj.lesson_dir

    # Use lesson_dir from argument if provided, otherwise use the one from context
    target_dir = Path(lesson_dir) if lesson_dir else ctx.obj.lesson_dir
    
    if not target_dir.exists():
        logger.error("Error: The lesson directory %s does not exist.", target_dir)
        exit(1)
        
    renumber_lessons(lesson_dir=target_dir, increment=increment, dryrun=dryrun)


cli.add_command(renumber, name='renumber')


@click.command()
@click.option('-d', '--dryrun', is_flag=True, help="Perform a dry run without renaming files.")
@click.pass_context
def regroup(ctx, dryrun):
    """Regroup lessons with the same basename into directories"""
    
    lesson_dir = ctx.obj.lesson_dir

    # Use lesson_dir from argument if provided, otherwise use the one from context
    target_dir = Path(lesson_dir) if lesson_dir else ctx.obj.lesson_dir
    
    if not target_dir.exists():
        logger.error("Error: The lesson directory %s does not exist.", target_dir)
        exit(1)
        
    regroup_lessons(lesson_dir=target_dir, dryrun=dryrun)


cli.add_command(regroup, name='regroup')

@click.command()
@click.option('-d', '--dryrun', is_flag=True, help="Perform a dry run without modifying files.")
@click.pass_context
def meta(ctx, dryrun):
    """Setup metadata"""
    
    lesson_dir = ctx.obj.lesson_dir

    # Use lesson_dir from argument if provided, otherwise use the one from context
    target_dir = Path(lesson_dir) if lesson_dir else ctx.obj.lesson_dir
    
    if not target_dir.exists():
        logger.error("Error: The lesson directory %s does not exist.", target_dir)
        exit(1)
        
    metafy_lessons(lesson_dir=target_dir, dryrun=dryrun)


cli.add_command(meta, name='meta')


def run():
    cli()


if __name__ == "__main__":
    run()



