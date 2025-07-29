""" unit tests for aedev.setup_project portion. """
import os
import pytest
import setuptools
import shutil

from aedev.setup_project import (
    APP_PRJ, DJANGO_PRJ, MINIMUM_PYTHON_VERSION, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, PLAYGROUND_PRJ, ROOT_PRJ,
    PYPI_PROJECT_ROOT, REPO_CODE_DOMAIN, REPO_GROUP_SUFFIX, REQ_FILE_NAME, REQ_DEV_FILE_NAME, PARENT_FOLDERS,
    VERSION_PREFIX, VERSION_QUOTE,
    code_file_title, code_file_version, code_version, find_package_data, namespace_guess, pev_str, pev_val,
    project_env_vars)

from ae.base import (
    BUILD_CONFIG_FILE, DOCS_FOLDER, PACKAGE_INCLUDE_FILES_PREFIX, PY_CACHE_FOLDER, PY_EXT, PY_INIT, TEMPLATES_FOLDER,
    TESTS_FOLDER,
    norm_path, write_file)


class TestHelpers:
    """ test helper functions """
    def test_code_file_title(self):
        tst_file = 'test_code_title.py'
        title_str = "this is an example of a code file title string"

        try:
            write_file(tst_file, f'''""" {title_str}\n\n    docstring body start here..."""\n''')
            assert code_file_title(tst_file) == title_str

            write_file(tst_file, f'''"""\n{title_str}\n====================\n    docstring body start here..."""\n''')
            assert code_file_title(tst_file) == title_str
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_code_file_title_invalid_file_content(self):
        tst_file = 'test_code_title.py'
        try:
            write_file(tst_file, "")                       # empty file
            assert not code_file_title(tst_file)

            write_file(tst_file, "\n\n this is no docstring and no title")    # invalid docstring/title
            assert not code_file_title(tst_file)
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_code_file_title_invalid_file_name(self):
        assert not code_file_title('::invalid_file_name::')

    def test_code_file_version(self):
        tst_file = 'test_code_version.py'
        version_str = '33.22.111pre'
        try:
            write_file(tst_file, f"{VERSION_PREFIX}{version_str}{VERSION_QUOTE}  # comment\nversion = '9.6.3'")
            assert code_file_version(tst_file) == version_str
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_code_file_version_invalid_file_content(self):
        tst_file = 'test_code_version.py'
        try:
            write_file(tst_file, "")                       # empty file
            assert not code_file_version(tst_file)

            write_file(tst_file, "version__ = '1.2.3'")    # invalid version var prefix
            assert not code_file_version(tst_file)
        finally:
            if os.path.exists(tst_file):
                os.remove(tst_file)

    def test_code_file_version_invalid_file_name(self):
        assert not code_file_version('::invalid_file_name::')

    def test_code_version(self):
        version = '333.222.111pre'
        assert code_version(f"{VERSION_PREFIX}{version}{VERSION_QUOTE}  # comment\nversion = '9.6.3'") == version

    def test_code_version_errors(self):
        assert code_version("") == ""
        assert code_version(b"") == ""
        assert code_version(bytes([0xda])) == ""

    def test_find_package_data_build_file(self):
        project_name = 'tst_app_with_build_file'
        pkg_path = os.path.join(TESTS_FOLDER, project_name)
        file1 = os.path.join(pkg_path, BUILD_CONFIG_FILE)
        path2 = os.path.join(pkg_path, 'deep_dir')
        file2 = os.path.join(path2, BUILD_CONFIG_FILE)
        try:
            os.makedirs(path2)
            write_file(file1, "# build file content (included)")
            write_file(file2, "# deeper build file content (excluded)")

            pkg_data = find_package_data(pkg_path)
            assert len(pkg_data) == 1
            files = pkg_data['']
            assert files[0] == os.path.relpath(file1, pkg_path)
            assert len(files) == 1

            files = find_package_data(norm_path(pkg_path))[""]  # test absolute path
            assert files[0] == os.path.relpath(file1, pkg_path)
            assert len(files) == 1
        finally:
            if os.path.exists(pkg_path):
                shutil.rmtree(pkg_path)

    def test_find_package_data_docs(self):
        project_name = 'tst_docs'
        pkg_path = os.path.join(TESTS_FOLDER, project_name)
        doc_path = os.path.join(pkg_path, DOCS_FOLDER)
        build_path = os.path.join(doc_path, "_build")
        auto_path = os.path.join(doc_path, "_autosummary")
        img_path = os.path.join(doc_path, "img")
        file1 = os.path.join(doc_path, "conf.py")
        file2 = os.path.join(build_path, "any_build_file.py")
        file3 = norm_path(os.path.join(auto_path, "any_sum_file.rst"))
        file4 = norm_path(os.path.join(img_path, "my_included_pic.jpg"))
        try:
            os.makedirs(build_path)
            os.makedirs(auto_path)
            os.makedirs(img_path)

            write_file(file1, "# doc config file content (included)")
            write_file(file2, "# doc build file content (excluded)")
            write_file(file3, "# doc auto_summary file content (excluded)")
            write_file(file4, "# doc image resource file (included)")

            files = find_package_data(pkg_path)[""]
            assert os.path.relpath(file1, pkg_path) in files
            assert os.path.relpath(file4, pkg_path) in files
            assert len(files) == 2

            files = find_package_data(norm_path(pkg_path))[""]  # test absolute path
            assert os.path.relpath(file1, pkg_path) in files
            assert os.path.relpath(file4, pkg_path) in files
            assert len(files) == 2
        finally:
            if os.path.exists(pkg_path):
                shutil.rmtree(pkg_path)

    def test_find_package_data_img(self):
        project_name = 'tst_pkg_with_resources'
        pkg_path = os.path.join(TESTS_FOLDER, project_name)
        path1 = os.path.join(pkg_path, 'img')
        file1 = os.path.join(path1, 'res.ext')
        path2 = os.path.join(path1, 'res_deep')
        file2 = os.path.join(path2, 'res2.ext')
        path2d = os.path.join(path1, PY_CACHE_FOLDER)
        file2d = os.path.join(path2d, 'res2d.ext')
        file3 = os.path.join(pkg_path, 'included_widgets.kv')
        try:
            os.makedirs(path2)
            os.makedirs(path2d)
            write_file(file1, "some resource content")
            write_file(file2, "res content2")
            write_file(file2d, "res content2d (excluded)")
            write_file(file3, "kv language content")

            files = find_package_data(pkg_path)[""]
            assert os.path.relpath(file1, pkg_path) in files
            assert os.path.relpath(file2, pkg_path) in files
            assert os.path.relpath(file2d, pkg_path) not in files
            assert os.path.relpath(file3, pkg_path) in files
            assert len(files) == 3
        finally:
            if os.path.exists(pkg_path):
                shutil.rmtree(pkg_path)

    def test_find_package_data_portion_snd(self):
        namespace_name = "tst"
        portion_name = "ns_pkg_with_resources"
        project_name = namespace_name + "_" + portion_name
        prj_path = os.path.join(TESTS_FOLDER, project_name)
        pkg_path = os.path.join(prj_path, namespace_name, portion_name)
        path1 = os.path.join(pkg_path, 'snd')
        file1 = os.path.join(path1, 'res.mp3')
        path2 = os.path.join(path1, 'res_deep')
        file2 = os.path.join(path2, 'res2.wav')
        file3 = os.path.join(pkg_path, 'widgets.kv')
        try:
            os.makedirs(path2)
            write_file(file1, "some resource content")
            write_file(file2, "res content2")
            write_file(file3, "kv language content")

            files = find_package_data(pkg_path)[""]
            assert files[0] == os.path.relpath(file3, pkg_path)
            assert files[1] == os.path.relpath(file1, pkg_path)
            assert files[2] == os.path.relpath(file2, pkg_path)
            assert len(files) == 3
        finally:
            if os.path.exists(prj_path):
                shutil.rmtree(prj_path)

    def test_find_package_data_templates(self):
        project_name = 'tst_prj_with_templates'
        pkg_path = os.path.join(TESTS_FOLDER, project_name)
        file0 = os.path.join(pkg_path, "non_tpl_file_name")
        file1 = os.path.join(pkg_path, TEMPLATES_FOLDER, "any_file_name")
        path2 = os.path.join(pkg_path, TEMPLATES_FOLDER, "deep_dir")
        file2 = os.path.join(path2, "some_other_template.ext")
        try:
            os.makedirs(path2)

            write_file(file0, "# non-template file content (not-included)")
            write_file(file1, "# root template file content (included)")
            write_file(file2, "# deeper template file content (included)")

            files = find_package_data(pkg_path)[""]
            assert os.path.relpath(file1, pkg_path) in files
            assert os.path.relpath(file2, pkg_path) in files
            assert len(files) == 2
        finally:
            if os.path.exists(pkg_path):
                shutil.rmtree(pkg_path)

    def test_find_package_data_updater(self):
        project_name = 'tst_app_with_updater_or_bootstrap'
        pkg_path = os.path.join(TESTS_FOLDER, project_name)
        file1 = os.path.join(pkg_path, PACKAGE_INCLUDE_FILES_PREFIX + "any_suffix")
        path2 = os.path.join(pkg_path, PACKAGE_INCLUDE_FILES_PREFIX + "deep_dir")
        file2 = os.path.join(path2, "some_included_file.ext")
        path2d = os.path.join(path2, "even_deeper")
        file2d = os.path.join(path2d, "other_included_file")
        path3 = os.path.join(pkg_path, "deep_not_included_dir")
        file3 = os.path.join(path3, PACKAGE_INCLUDE_FILES_PREFIX + "other_suffix")
        try:
            os.makedirs(path2d)
            os.makedirs(path3)

            write_file(file1, "# root file content (included)")
            write_file(file2, "# deeper include file content (included)")
            write_file(file2d, "# deeper include file content (included)")
            write_file(file3, "# deeper file content (excluded)")

            files = find_package_data(pkg_path)[""]
            assert os.path.relpath(file1, pkg_path) in files
            assert os.path.relpath(file2, pkg_path) in files
            assert os.path.relpath(file2d, pkg_path) in files
            assert os.path.relpath(file3, pkg_path) not in files
            assert len(files) == 3
        finally:
            if os.path.exists(pkg_path):
                shutil.rmtree(pkg_path)

    def test_namespace_guess_fail(self):
        assert namespace_guess(TESTS_FOLDER) == ""  # invalid project root dir
        assert namespace_guess("not_existing_project_dir") == ""

    def test_namespace_guess_portion(self):
        namespace = 'yz'
        portion_name = 'portion_name'
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = namespace + "_" + portion_name
        project_path = os.path.join(parent_dir, project_name)
        namespace_dir = os.path.join(project_path, namespace)
        try:
            os.makedirs(namespace_dir)
            main_file = os.path.join(namespace_dir, portion_name + PY_EXT)
            write_file(main_file, "# main file of module portion")
            assert namespace_guess(project_path) == namespace
            os.remove(main_file)

            portion_dir = os.path.join(namespace_dir, portion_name)
            os.makedirs(portion_dir)
            main_file = os.path.join(namespace_dir, "__init__" + PY_EXT)
            write_file(main_file, "# main file of package portion")
            assert namespace_guess(project_path) == namespace
            os.remove(main_file)

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_namespace_guess_setup_project(self):
        assert namespace_guess("") == "aedev"
        assert namespace_guess(os.getcwd()) == "aedev"

    def test_namespace_guess_root(self):
        namespace = 'xz'
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = por_dir = os.path.join(parent_dir, namespace + "_" + namespace)

        try:
            os.makedirs(por_dir)

            main_file = os.path.join(por_dir, namespace + PY_EXT)
            write_file(main_file, "# main file of non-namespace module")
            assert not namespace_guess(project_path)
            os.remove(main_file)

            main_file = os.path.join(por_dir, "main" + PY_EXT)
            write_file(main_file, "# main file of non-namespace project")
            assert not namespace_guess(project_path)
            os.remove(main_file)

            main_file = os.path.join(por_dir, "__init__" + PY_EXT)
            write_file(main_file, "# main file of non-namespace package")
            assert not namespace_guess(project_path)
            os.remove(main_file)

            por_dir = os.path.join(por_dir, namespace)
            os.makedirs(por_dir)

            main_file = os.path.join(por_dir, namespace + PY_EXT)
            write_file(main_file, "# main file of namespace root module")
            assert namespace_guess(project_path) == namespace
            os.remove(main_file)

            main_file = os.path.join(por_dir, "main" + PY_EXT)
            write_file(main_file, "# main file of namespace root main")
            assert namespace_guess(project_path) == namespace
            os.remove(main_file)

            por_dir = os.path.join(por_dir, namespace)
            os.makedirs(por_dir)
            main_file = os.path.join(por_dir, "__init__" + PY_EXT)
            write_file(main_file, "# main file of namespace root package")
            assert namespace_guess(project_path) == namespace
            os.remove(main_file)

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    # noinspection PyTypeChecker
    def test_pev_str(self):
        """ test helper to determine variable string values of a project env variable. """
        assert pev_str({'a': 1}, "b") == ""
        assert pev_str(dict(a=1), "b") == ""
        with pytest.raises(AssertionError):
            assert pev_str(dict(a=1), "a") == ""
        assert pev_str(dict(a="1"), "a") == "1"

    # noinspection PyTypeChecker
    def test_pev_val(self):
        """ test helper to determine variable values of a project env var. """
        assert pev_val(dict(a=1), "b") == ""
        assert pev_val(dict(a=1), "a") == 1


class TestProjectEnvVars:
    """ test project_env_vars() function """
    def test_module_var_patch_local_imported(self):
        import aedev.setup_project as dc
        assert dc.REQ_FILE_NAME == 'requirements.txt'
        try:
            dc.REQ_FILE_NAME = 'new_val'
            assert dc.REQ_FILE_NAME == 'new_val'
            assert REQ_FILE_NAME == 'requirements.txt'
        finally:
            dc.REQ_FILE_NAME = 'requirements.txt'  # reset aedev.setup_project-module-var-value for subsequent tests

    def test_module_var_patch_imported_in_other_module(self):
        oth_mod = 'other_module.py'
        try:
            write_file(oth_mod, "import aedev.setup_project as dc")
            # noinspection PyUnresolvedReferences
            from other_module import dc
            assert dc.REQ_FILE_NAME == 'requirements.txt'

            dc.REQ_FILE_NAME = 'new_val'
            assert dc.REQ_FILE_NAME == 'new_val'
            assert REQ_FILE_NAME == 'requirements.txt'
        finally:
            if os.path.isfile(oth_mod):
                os.remove(oth_mod)
            dc.REQ_FILE_NAME = 'requirements.txt'  # reset aedev.setup_project-module-var-value for subsequent tests

    def test_module_var_patch_imported_in_other_module_as(self):
        oth_mod = 'another_module.py'
        try:
            write_file(oth_mod, "from aedev.setup_project import REQ_FILE_NAME")
            # noinspection PyUnresolvedReferences
            from other_module import dc
            assert dc.REQ_FILE_NAME == 'requirements.txt'

            dc.REQ_FILE_NAME = 'new_val'
            assert dc.REQ_FILE_NAME == 'new_val'
            assert REQ_FILE_NAME == 'requirements.txt'
        finally:
            if os.path.isfile(oth_mod):
                os.remove(oth_mod)
            dc.REQ_FILE_NAME = 'requirements.txt'  # reset aedev.setup_project-module-var-value for subsequent tests

    def test_app_env(self):
        file_name = os.path.join(TESTS_FOLDER, BUILD_CONFIG_FILE)
        try:
            write_file(file_name, "spec")
            pev = project_env_vars(project_path=TESTS_FOLDER)
            assert pev['namespace_name'] == ""
            assert pev['project_name'] == TESTS_FOLDER
            assert pev['project_type'] == APP_PRJ
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_aedev_project_env_vars(self):
        namespace = 'aedev'
        module = 'setup_project'
        cur_dir = os.getcwd()

        pev = project_env_vars(from_setup=True)

        assert isinstance(pev, dict)
        assert pev['namespace_name'] == namespace
        assert pev['TEMPLATES_FOLDER'] == TEMPLATES_FOLDER == 'templates'
        assert pev['PYPI_PROJECT_ROOT'] == PYPI_PROJECT_ROOT == 'https://pypi.org/project'
        assert pev['MINIMUM_PYTHON_VERSION'] == MINIMUM_PYTHON_VERSION == '3.9'
        assert pev['REPO_CODE_DOMAIN'] == pev['repo_domain'] == REPO_CODE_DOMAIN == 'gitlab.com'
        assert pev['REQ_FILE_NAME'] == REQ_FILE_NAME == 'requirements.txt'
        assert pev['REQ_DEV_FILE_NAME'] == REQ_DEV_FILE_NAME == 'dev_requirements.txt'
        assert pev['project_path'] == cur_dir
        assert pev['project_type'] == 'module' == MODULE_PRJ
        assert pev['portion_name'] == module
        assert pev['version_file'] == os.path.join(cur_dir, namespace, module + PY_EXT)
        assert pev['project_name'] == namespace + '_' + module
        assert pev['pip_name'] == namespace + '-' + module.replace('_', '-')
        assert pev['import_name'] == namespace + '.' + module
        assert pev['project_version'] == code_file_version(os.path.join(cur_dir, namespace, module + PY_EXT))
        assert pev['repo_root']
        assert pev['repo_root'].endswith(namespace + REPO_GROUP_SUFFIX)
        assert pev['repo_pages']
        assert PYPI_PROJECT_ROOT in pev['pypi_url']

        assert len(pev['dev_require']) == 2
        assert 'aedev_aedev' in pev['dev_require']
        assert 'aedev_tpl_project' in pev['dev_require']
        assert pev['docs_require'] == []
        assert pev['install_require'] == ['ae_base']
        assert pev['setup_require'] == ['ae_base']
        assert len(pev['tests_require'])
        assert pev['portions_packages'] == ['aedev_tpl_project']
        assert pev['project_packages'] == ['aedev']
        assert pev['package_data'] == {'': []}

    def test_aedev_env_setup(self):
        namespace = 'aedev'
        module = 'setup_project'
        cur_dir = os.getcwd()

        from setup import pev  # project_env_vars() from setup.py of this portion

        assert isinstance(pev, dict)
        assert pev['namespace_name'] == namespace
        assert pev['TEMPLATES_FOLDER'] == TEMPLATES_FOLDER == 'templates'
        assert pev['PYPI_PROJECT_ROOT'] == PYPI_PROJECT_ROOT == 'https://pypi.org/project'
        assert pev['MINIMUM_PYTHON_VERSION'] == MINIMUM_PYTHON_VERSION == '3.9'
        assert pev['REPO_CODE_DOMAIN'] == pev['repo_domain'] == REPO_CODE_DOMAIN == 'gitlab.com'
        assert pev['REQ_FILE_NAME'] == REQ_FILE_NAME == 'requirements.txt'
        assert pev['REQ_DEV_FILE_NAME'] == REQ_DEV_FILE_NAME == 'dev_requirements.txt'
        assert pev['project_path'] == cur_dir
        assert pev['project_type'] == 'module' == MODULE_PRJ
        assert pev['portion_name'] == module
        assert pev['version_file'] == os.path.join(cur_dir, namespace, module + PY_EXT)
        assert pev['project_name'] == namespace + '_' + module
        assert pev['pip_name'] == namespace + '-' + module.replace('_', '-')
        assert pev['import_name'] == namespace + '.' + module
        assert pev['project_version'] == code_file_version(os.path.join(cur_dir, namespace, module + PY_EXT))
        assert pev['repo_root'].endswith(namespace + REPO_GROUP_SUFFIX)
        assert pev['repo_pages']
        assert PYPI_PROJECT_ROOT in pev['pypi_url']

        assert len(pev['dev_require']) == 2
        assert 'aedev_aedev' in pev['dev_require']
        assert 'aedev_tpl_project' in pev['dev_require']
        assert pev['docs_require'] == []
        assert pev['install_require'] == ['ae_base']
        assert pev['setup_require'] == ['ae_base']
        assert len(pev['tests_require'])

        assert pev['portions_packages'] == ['aedev_tpl_project']
        assert pev['project_packages'] == ['aedev']
        assert pev['package_data'] == {'': []}

    def test_django_env(self):
        file_name = os.path.join(TESTS_FOLDER, 'manage.py')
        try:
            write_file(file_name, "any content")
            pev = project_env_vars(project_path=TESTS_FOLDER)
            assert pev['namespace_name'] == ""
            assert pev['project_name'] == TESTS_FOLDER
            assert pev['project_type'] == DJANGO_PRJ
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_non_existent_env(self):
        empty_dir = os.path.join(os.getcwd(), TESTS_FOLDER, "empty_prj_dir")
        try:
            os.makedirs(empty_dir)

            pev = project_env_vars(project_path=empty_dir)
            assert isinstance(pev, dict)
            assert pev['namespace_name'] == ''
            assert pev['TEMPLATES_FOLDER'] == TEMPLATES_FOLDER == 'templates'
            assert pev['PYPI_PROJECT_ROOT'] == PYPI_PROJECT_ROOT == 'https://pypi.org/project'
            assert pev['MINIMUM_PYTHON_VERSION'] == MINIMUM_PYTHON_VERSION == '3.9'
            assert pev['REPO_CODE_DOMAIN'] == pev['repo_domain'] == REPO_CODE_DOMAIN == 'gitlab.com'
            assert pev['REQ_FILE_NAME'] == REQ_FILE_NAME == 'requirements.txt'
            assert pev['REQ_DEV_FILE_NAME'] == REQ_DEV_FILE_NAME == 'dev_requirements.txt'
            assert pev['project_path'] == empty_dir
            assert pev['project_type'] == NO_PRJ
            assert not pev['project_version']
            assert pev['repo_root']
            assert pev['repo_pages']

            assert pev['dev_require'] == []
            assert pev['docs_require'] == []
            assert pev['install_require'] == []
            assert pev['setup_require'] == ['aedev_setup_project']
            assert pev['tests_require'] == []

            assert pev['portions_packages'] == []
            assert not pev['project_packages']
            assert pev['package_data'] == {'': []}
        finally:
            if os.path.isdir(empty_dir):
                shutil.rmtree(empty_dir)

    def test_invalid_env_doesnt_raise(self):
        pev = project_env_vars(project_path="invalid_project_path")
        assert pev['project_type'] == NO_PRJ

    def test_empty_pev_doesnt_raise(self):
        file_name = os.path.join(TESTS_FOLDER, 'setup' + PY_EXT)
        try:
            write_file(file_name, "pev = {}")
            project_env_vars(project_path=TESTS_FOLDER)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_invalid_pev_doesnt_raise(self):
        file_name = os.path.join(TESTS_FOLDER, 'setup' + PY_EXT)
        try:
            write_file(file_name, "")
            project_env_vars(project_path=TESTS_FOLDER)

            write_file(file_name, "pev = ''")
            project_env_vars(project_path=TESTS_FOLDER)

            write_file(file_name, "pev = str")
            project_env_vars(project_path=TESTS_FOLDER)

            write_file(file_name, "pev = []")
            project_env_vars(project_path=TESTS_FOLDER)

            write_file(file_name, "pev = [str]")
            project_env_vars(project_path=TESTS_FOLDER)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_raise_syntax_error_in_setup_py(self):
        file_name = os.path.join(TESTS_FOLDER, 'setup' + PY_EXT)
        try:
            write_file(file_name, "- nothing * but : syntax / errors")
            with pytest.raises(SyntaxError):
                project_env_vars(project_path=TESTS_FOLDER)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_root_project_in_docs(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = os.path.join(parent_dir, "nsn")
        docs_dir = os.path.join(project_path, DOCS_FOLDER)
        common_dir = os.path.join(project_path, TEMPLATES_FOLDER)
        sphinx_conf = os.path.join(docs_dir, 'conf.py')
        cur_dir = os.getcwd()
        try:
            os.makedirs(docs_dir)
            os.makedirs(common_dir)
            write_file(sphinx_conf, "file-content-irrelevant")

            os.chdir(docs_dir)
            pev = project_env_vars(project_path='..')   # simulate call from within sphinx conf.py file
            os.chdir(cur_dir)

            assert pev['project_path'] == norm_path(project_path)
        finally:
            os.chdir(cur_dir)   # restore if project_env_vars() call throws exception
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_root_project_project_version(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        namespace = "nsn"
        project_path = os.path.join(parent_dir, namespace)
        docs_dir = os.path.join(project_path, DOCS_FOLDER)
        tpl_dir = os.path.join(project_path, TEMPLATES_FOLDER)
        file_name = os.path.join(project_path, namespace + PY_EXT)
        project_version = "12.33.444"
        try:
            os.makedirs(docs_dir)
            os.makedirs(tpl_dir)
            write_file(file_name, f"{VERSION_PREFIX}{project_version}{VERSION_QUOTE}")

            pev = project_env_vars(project_path=project_path)

            assert pev['project_version'] == project_version
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_project_readme_md(self):
        project_name = 'test_prj'
        package_dir = os.path.join(TESTS_FOLDER, project_name)
        readme_file_name = os.path.join(package_dir, 'README.md')
        readme_content = "read me file content"
        try:
            os.makedirs(package_dir)
            write_file(readme_file_name, readme_content)

            pev = project_env_vars(project_path=package_dir)

            assert pev_str(pev, 'long_desc_content') == readme_content
            assert pev_str(pev, 'long_desc_type') == 'text/markdown'
        finally:
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)      # including req_file_name

    def test_project_readme_rst(self):
        project_name = 'test_prj'
        package_dir = os.path.join(TESTS_FOLDER, project_name)
        readme_file_name = os.path.join(package_dir, 'README.rst')
        readme_content = "read me file content"
        try:
            os.makedirs(package_dir)
            write_file(readme_file_name, readme_content)

            pev = project_env_vars(project_path=package_dir)

            assert pev_str(pev, 'long_desc_content') == readme_content
            assert pev_str(pev, 'long_desc_type') == 'text/x-rst'
        finally:
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)      # including req_file_name

    def test_setuptools_find_namespace_packages(self):
        assert setuptools.find_namespace_packages(include=['aedev']) == ['aedev']

    def test_setup_kwargs_minimum_python_version(self):
        pev = project_env_vars("invalid_path")

        assert 'MINIMUM_PYTHON_VERSION' in pev
        assert pev['MINIMUM_PYTHON_VERSION'] == MINIMUM_PYTHON_VERSION
        assert pev_str(pev, 'MINIMUM_PYTHON_VERSION') == MINIMUM_PYTHON_VERSION

        assert pev['setup_kwargs']['python_requires'].endswith(MINIMUM_PYTHON_VERSION)
        assert any(MINIMUM_PYTHON_VERSION in _ for _ in pev['setup_kwargs']['classifiers'])

    def test_setup_py_pev_patched_defaults(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        project_name = "pkg_name"
        project_name_folder = "tst_pkg"
        project_path = os.path.join(parent_dir, project_name_folder)
        pev_file = os.path.join(project_path, 'pev.defaults')
        setup_file = os.path.join(project_path, 'setup' + PY_EXT)
        author = 'App Config Author Name'
        try:
            os.makedirs(project_path)
            write_file(pev_file,
                       "{"
                       + "'STK_AUTHOR': '" + author + "',"
                       + "'project_name': '" + project_name + "',"
                       + "}")
            write_file(setup_file, "from aedev.setup_project import project_env_vars\n"
                                   "pev = project_env_vars(from_setup=True)")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] == author
            assert pev['setup_kwargs']['author'] == author
            assert pev['project_name'] == project_name

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_setup_py_pev_patched_package_name(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        package_name = "pkg_name"
        project_name_folder = "tst_pkg"
        project_path = os.path.join(parent_dir, project_name_folder)
        pev_file = os.path.join(project_path, 'pev.defaults')
        setup_file = os.path.join(project_path, 'setup' + PY_EXT)
        author = 'App Config Author Name'
        try:
            os.makedirs(project_path)
            write_file(pev_file,
                       "{"
                       + "'STK_AUTHOR': '" + author + "',"
                       + "'package_name': '" + package_name + "',"
                       + "}")
            write_file(setup_file, "from aedev.setup_project import project_env_vars\n"
                                   "pev = project_env_vars(from_setup=True)")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] == author
            assert pev['setup_kwargs']['author'] == author
            assert pev['package_name'] == package_name

        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_setup_py_pev_patched_module_constant(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        project_name = "tst_pkg"
        project_path = os.path.join(parent_dir, project_name)
        setup_file = os.path.join(project_path, 'setup' + PY_EXT)
        author = 'Setup Py Patched Author Name'
        try:
            os.makedirs(project_path)
            write_file(setup_file, "import aedev.setup_project\n"
                                   f"aedev.setup_project.STK_AUTHOR = '{author}'\n"
                                   "pev = aedev.setup_project.project_env_vars(from_setup=True)")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] == author
            assert pev['setup_kwargs']['author'] == author
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_setup_py_pev_patched_module_constant_with_project_path(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        project_name = "tst_pkg"
        project_path = os.path.join(parent_dir, project_name)
        setup_file = os.path.join(project_path, 'setup' + PY_EXT)
        author = 'Setup Py Patched Author Name'
        try:
            os.makedirs(project_path)
            write_file(setup_file,
                       "from os.path import dirname as d\n"
                       "import aedev.setup_project\n"
                       f"aedev.setup_project.STK_AUTHOR = '{author}'\n"
                       "pev = aedev.setup_project.project_env_vars(project_path=d(__file__), from_setup=True)")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] == author
            assert pev['setup_kwargs']['author'] == author
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_setup_py_pev_patched_updates(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        project_name = "tst_pkg"
        project_path = os.path.join(parent_dir, project_name)
        pev_file = os.path.join(project_path, 'pev.updates')
        setup_file = os.path.join(project_path, 'setup' + PY_EXT)
        author = 'App Config Author Name'
        try:
            os.makedirs(project_path)
            write_file(setup_file, "from aedev.setup_project import project_env_vars\n"
                                   "pev = project_env_vars(from_setup=True)")
            write_file(pev_file, "{'setup_kwargs': {'author': '" + author + "'}}")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] != author
            assert pev['setup_kwargs']['author'] == author

            # another test also updating STK_AUTHOR
            write_file(pev_file, "{'STK_AUTHOR': '" + author + "', 'setup_kwargs': {'author': '" + author + "'}}")

            pev = project_env_vars(project_path=project_path)

            assert pev['STK_AUTHOR'] == author
            assert pev['setup_kwargs']['author'] == author
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)


class TestProjectTypeAndResources:
    """ project type, modules and resources unit tests """
    def test_invalid_portion(self):
        project_path = "invalid_project_path"

        pev = project_env_vars(project_path=project_path)

        assert pev['project_type'] == NO_PRJ
        assert pev['project_path'] == norm_path(project_path)
        assert pev['project_name'] == project_path
        assert pev['namespace_name'] == ""

    def test_no_modules(self):
        prj_name = 'prj_nam'
        project_path = os.path.join(TESTS_FOLDER, prj_name)
        try:
            os.makedirs(project_path)

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == NO_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == prj_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)

    def test_tests_folder_with_conftest(self):
        pev = project_env_vars(project_path=TESTS_FOLDER)
        assert pev['project_type'] == NO_PRJ
        assert pev['project_path'] == norm_path(TESTS_FOLDER)
        assert pev['project_name'] == TESTS_FOLDER
        assert pev['namespace_name'] == ""

    def test_app_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'app_project'
        project_path = os.path.join(parent_dir, project_name)
        file_name = os.path.join(project_path, BUILD_CONFIG_FILE)
        try:
            os.makedirs(project_path)
            write_file(file_name, "spec content")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == APP_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_app_namespace_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        namespace_name = 'nsn'
        portion_name = 'app_project'
        project_name = namespace_name + '_' + portion_name
        project_path = os.path.join(parent_dir, project_name)
        namespace_sub_dir = os.path.join(project_path, namespace_name)
        try:
            os.makedirs(namespace_sub_dir)
            write_file(os.path.join(namespace_sub_dir, "main" + PY_EXT), "# app main file")
            write_file(os.path.join(project_path, BUILD_CONFIG_FILE), "spec content")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == APP_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == namespace_name
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_app_project_no_namespace(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'appName'
        project_path = os.path.join(parent_dir, project_name)
        try:
            os.makedirs(project_path)
            write_file(os.path.join(project_path, "main" + PY_EXT), "# app main module")
            write_file(os.path.join(project_path, BUILD_CONFIG_FILE), "spec content")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == APP_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_django_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'django_project'
        project_path = os.path.join(parent_dir, project_name)
        file_name = os.path.join(project_path, 'manage.py')
        try:
            os.makedirs(project_path)
            write_file(file_name, "any content")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == DJANGO_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_module_template_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'tpl_project'
        project_path = os.path.join(parent_dir, project_name)
        template_path = os.path.join(project_path, TEMPLATES_FOLDER)
        try:
            os.makedirs(template_path)
            write_file(os.path.join(project_path, project_name + PY_EXT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == MODULE_PRJ
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_package_template_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'tpl_project'
        project_path = os.path.join(parent_dir, project_name)
        package_path = os.path.join(project_path, project_name)
        template_path = os.path.join(project_path, TEMPLATES_FOLDER)
        try:
            os.makedirs(package_path)
            os.makedirs(template_path)
            write_file(os.path.join(package_path, PY_INIT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == PACKAGE_PRJ
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_playground_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_name = 'test_project_playground'
        project_path = os.path.join(parent_dir, project_name)
        try:
            os.makedirs(project_path)
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == PLAYGROUND_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_namespace_template_module_project(self):
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        namespace_name = 'nsn'
        portion_name = 'tpl_project'
        project_name = namespace_name + '_' + portion_name
        project_path = os.path.join(parent_dir, project_name)
        template_path = os.path.join(project_path, TEMPLATES_FOLDER)
        namespace_path = os.path.join(project_path, namespace_name)
        try:
            os.makedirs(template_path)
            os.makedirs(namespace_path)
            write_file(os.path.join(namespace_path, portion_name + PY_EXT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == MODULE_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == namespace_name
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_namespace_root_project_module(self):
        namespace = 'rootX'  # no_underscore
        project_name = namespace + "_" + namespace
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = os.path.join(parent_dir, project_name)
        portion_path = os.path.join(project_path, namespace)
        try:
            os.makedirs(portion_path)
            write_file(os.path.join(portion_path, namespace + PY_EXT), "# namespace root main/version file")
            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == ROOT_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == namespace
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_namespace_root_project_package(self):
        namespace = 'namespace'
        project_name = namespace + "_" + namespace
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = os.path.join(parent_dir, project_name)
        nss_dir = os.path.join(project_path, namespace, namespace)
        try:
            os.makedirs(os.path.join(nss_dir, namespace))   # simulate root package
            write_file(os.path.join(nss_dir, PY_INIT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")

            pev = project_env_vars(project_path=project_path)
            assert pev['project_type'] == ROOT_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == namespace
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_one_module(self):
        mod_name = pkg_name = 'tst_pkg'
        project_path = os.path.join(TESTS_FOLDER, pkg_name)
        module_path = os.path.join(project_path, mod_name + PY_EXT)
        try:
            os.makedirs(project_path)
            write_file(module_path, "v = 3")

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == MODULE_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == pkg_name
            assert pev['namespace_name'] == ""
            # assert pev['project_modules'] == (mod_name, )
        finally:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)

    def test_one_namespace_module(self):
        namespace = 'nsn'
        mod_name = 'tst_mod1'
        pkg_name = namespace + '_' + mod_name
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0])
        project_path = os.path.join(parent_dir, pkg_name)
        por_folder = os.path.join(project_path, namespace)
        module_path = os.path.join(por_folder, mod_name + PY_EXT)
        try:
            os.makedirs(por_folder)
            write_file(module_path, "v = 3")

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == MODULE_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == pkg_name
            assert pev['namespace_name'] == namespace
            # assert pev['project_modules'] == (mod_name, )
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_sub_package(self):
        project_name = 'tst_sub_pkg'
        mod_name = 'module1'
        project_path = os.path.join(TESTS_FOLDER, project_name)
        tst_file1 = os.path.join(project_path, PY_INIT)
        tst_file2 = os.path.join(project_path, mod_name + PY_EXT)
        try:
            os.makedirs(project_path)
            write_file(tst_file1, "v = 3")
            write_file(tst_file2, "v = 6")

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == PACKAGE_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
            # assert pev['project_modules'] == (mod_name, )
        finally:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)

    def test_namespace_sub_package(self):
        namespace = 'namespace'
        project_name = 'tst_sub_pkg'
        mod_name = 'module1'
        parent_dir = os.path.join(TESTS_FOLDER, PARENT_FOLDERS[-1])
        project_path = os.path.join(parent_dir, namespace + '_' + project_name)
        package_root = os.path.join(project_path, namespace, project_name)
        tst_file1 = os.path.join(package_root, PY_INIT)
        tst_file2 = os.path.join(package_root, mod_name + PY_EXT)
        try:
            os.makedirs(package_root)
            write_file(tst_file1, "v = 3")
            write_file(tst_file2, "v = 6")

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == PACKAGE_PRJ
            assert pev['project_path'] == norm_path(project_path)
            assert pev['project_name'] == namespace + '_' + project_name
            assert pev['portion_name'] == project_name
            assert pev['namespace_name'] == namespace
            # assert pev['project_modules'] == (mod_name, )
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_two_modules_package(self):
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_init = os.path.join(TESTS_FOLDER, PY_INIT)
        tst_file1 = os.path.join(TESTS_FOLDER, mod1 + PY_EXT)
        tst_file2 = os.path.join(TESTS_FOLDER, mod2 + PY_EXT)
        try:
            write_file(tst_init, "v = 3")
            write_file(tst_file1, "v = 6")
            write_file(tst_file2, "v = 99")

            pev = project_env_vars(project_path=TESTS_FOLDER)

            assert pev['project_type'] == PACKAGE_PRJ
            assert pev['project_path'] == norm_path(TESTS_FOLDER)
            assert pev['project_name'] == TESTS_FOLDER
            assert pev['namespace_name'] == ""
            # assert len(pev['project_modules']) >= 2     # == 4 (including conftest.py and test_setup_project.py)
            # assert mod1 in pev['project_modules'] and mod2 in pev['project_modules']
        finally:
            if os.path.exists(tst_init):
                os.remove(tst_init)
            if os.path.exists(tst_file1):
                os.remove(tst_file1)
            if os.path.exists(tst_file2):
                os.remove(tst_file2)

    def test_two_modules_no_init(self):
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_file1 = os.path.join(TESTS_FOLDER, mod1 + PY_EXT)
        tst_file2 = os.path.join(TESTS_FOLDER, mod2 + PY_EXT)
        try:
            write_file(tst_file1, "v = 3")
            write_file(tst_file2, "v = 55")

            pev = project_env_vars(project_path=TESTS_FOLDER)

            assert pev['project_type'] == NO_PRJ
            assert pev['project_path'] == norm_path(TESTS_FOLDER)
            assert pev['project_name'] == TESTS_FOLDER
            assert pev['namespace_name'] == ""
            # assert 'conftest' in pev['project_modules']
            # assert os.path.splitext(os.path.basename(__file__))[0] in pev['project_modules']
            # assert mod1 in pev['project_modules']
            # assert mod2 in pev['project_modules']
        finally:
            if os.path.exists(tst_file1):
                os.remove(tst_file1)
            if os.path.exists(tst_file2):
                os.remove(tst_file2)

    def test_two_namespace_modules_no_init(self):
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_file1 = os.path.join(TESTS_FOLDER, mod1 + PY_EXT)
        tst_file2 = os.path.join(TESTS_FOLDER, mod2 + PY_EXT)
        try:
            write_file(tst_file1, "v = 3")
            write_file(tst_file2, "v = 55")

            pev = project_env_vars(project_path=TESTS_FOLDER)

            assert pev['project_type'] == NO_PRJ
            assert pev['project_path'] == norm_path(TESTS_FOLDER)
            assert pev['project_name'] == TESTS_FOLDER
            assert pev['namespace_name'] == ""
            # assert 'conftest' in pev['project_modules']
            # assert os.path.splitext(os.path.basename(__file__))[0] in pev['project_modules']
            # assert mod1 in pev['project_modules']
            # assert mod2 in pev['project_modules']
        finally:
            if os.path.exists(tst_file1):
                os.remove(tst_file1)
            if os.path.exists(tst_file2):
                os.remove(tst_file2)

    def test_new_project_in_parent(self):
        project_name = PARENT_FOLDERS[0]
        parent_dir = norm_path(os.path.join(TESTS_FOLDER, project_name))
        try:
            os.makedirs(parent_dir)

            pev = project_env_vars(project_path=parent_dir)

            assert pev['project_type'] == PARENT_PRJ
            assert pev['project_path'] == parent_dir
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)

    def test_new_project_under_parent(self):
        project_name = 'new_prj'
        parent_dir = norm_path(os.path.join(TESTS_FOLDER, PARENT_FOLDERS[0]))
        project_path = os.path.join(parent_dir, project_name)
        try:
            os.makedirs(project_path)

            pev = project_env_vars(project_path=project_path)

            assert pev['project_type'] == NO_PRJ
            assert pev['project_path'] == project_path
            assert pev['project_name'] == project_name
            assert pev['namespace_name'] == ""
        finally:
            if os.path.exists(parent_dir):
                shutil.rmtree(parent_dir)
