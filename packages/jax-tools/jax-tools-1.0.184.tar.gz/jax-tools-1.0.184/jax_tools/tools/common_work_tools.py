# -*- coding: utf-8 -*-
"""
Common work tools
"""
import shlex
import subprocess
import os
import shutil


def build_sphinx_doc(build_type: str = 'html', working_dir: str = None,
                     release_root_dir: str = 'D:/Documents/Sphinx') -> None:
    """
    Build sphinx doc using sphinx-build
    Args:
        build_type (str): html or latex
        working_dir (str): working directory
        release_root_dir (str): Release root directory

    Returns:
        None
    """
    if working_dir is None:
        working_dir = os.path.dirname(os.path.abspath(__file__))
    # Enter the directory
    os.chdir(working_dir)
    # Get project name
    project_name = working_dir.split('-')[-1] if working_dir[0:2].isalnum() else os.path.basename(working_dir)


    if build_type == 'pdf':
        build_list = ['latex']
    elif build_type == 'all':
        build_list = ['html', 'latex']
        if os.path.exists(f'{release_root_dir}/{project_name}'):
            shutil.rmtree(f'{release_root_dir}/{project_name}/html', ignore_errors=True)
            shutil.rmtree(f'{release_root_dir}/{project_name}/latex', ignore_errors=True)
    elif build_type == 'html':
        build_list = ['html']
    elif build_type == 'latex':
        build_list = ['latex']
    else:
        raise ValueError('Invalid build_type. Please use "html", "latex", "pdf" or "all".')

    for build_type in build_list:
        # Define build dir
        build_dir = f'{release_root_dir}/{project_name}/{build_type}'
        _cmd = f'sphinx-build -b {build_type} source {build_dir}'
        subprocess.call(shlex.split(_cmd))
        if build_type == 'html':
            # Open the HTML file
            os.startfile(f'{build_dir}/index.html')
        elif build_type == 'latex':
            os.chdir(build_dir)
            conf_file = f'{working_dir}/source/conf.py'
            if not os.path.exists(conf_file):
                raise FileNotFoundError(f"Conf file not found at {conf_file}")
            with open(conf_file, encoding='utf-8') as fp:
                pdf_name = fp.read().split('project = ')[1].lstrip('u').lstrip('"').lstrip("'").split('"')[0]\
                .split("'")[0].lower().replace(' ', '')
            _cmd = f'xelatex {pdf_name}'
            # compile twice, first build for generate index and bibtex files, second to generate pdf include catalogue
            subprocess.call(shlex.split(_cmd))
            subprocess.call(shlex.split(_cmd))
            # Open the PDF file
            os.startfile(f'{pdf_name}.pdf')
