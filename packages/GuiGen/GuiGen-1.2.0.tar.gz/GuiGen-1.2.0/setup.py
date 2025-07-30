from setuptools import setup, find_packages

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    
    with open('requirements.txt', 'r', encoding='utf-8') as req:
        reqs = req.readlines()

    setup(
        name='GuiGen',
        description='GuiGen',
        author='Filip Matejko',
        author_email='matejkofilip@gmail.com',
        version='1.2.0',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/FilipM13/GuiGen',
        packages=find_packages(
            where='src',
            exclude=['tests']
        ),
        package_dir={'': 'src'},
        python_requires='>=3.9',
        install_requires=reqs,
        package_data={"": ['**/*.html', '**/*.js', '**/*.css', '**/*.jinja2']},
        include_package_data=True
    )
