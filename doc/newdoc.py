import pdoc
from pyuvs.misc.get_project_path import get_project_path
import os


class Documentation:
    def __init__(self):
        self.module = [pdoc.Module('pyuvs', context=pdoc.Context())]
        pdoc.link_inheritance(pdoc.Context())
        self.html_path = self.__get_path_where_to_put_html_doc()

    @staticmethod
    def __get_path_where_to_put_html_doc():
        return os.path.abspath(os.path.join(get_project_path(), 'doc/html'))

    def make_recursive_html(self, module):
        yield module.name, module.html(), bool(module.submodules())
        for submodules in module.submodules():
            yield from self.make_recursive_html(submodules)

    def make_doc(self):
        for mod in self.module:
            for module_name, html, is_folder in self.make_recursive_html(mod):
                if 'tests' in module_name:
                    continue
                self.make_folder(module_name) if is_folder else False
                abs_path = self.make_html_name(module_name, is_folder)
                with open(f'{abs_path}.html', 'w+') as html_file:
                    html_file.write(html)

    def make_folder(self, module_name):
        folder_name = module_name.replace('.', '/')
        folder_path = os.path.join(self.html_path, folder_name)
        self.make_folder_if_nonexistent(folder_path)

    @staticmethod
    def make_folder_if_nonexistent(folder_path):
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass

    def make_html_name(self, module_name, is_folder):
        name = module_name.replace('.', '/')
        relative_name = name + '/index' if is_folder else name
        return os.path.join(self.html_path, relative_name)


if __name__ == '__main__':
    Documentation().make_doc()
