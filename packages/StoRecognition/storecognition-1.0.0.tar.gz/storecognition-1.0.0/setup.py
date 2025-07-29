from setuptools import setup, find_packages

setup(
    name='StoRecognition',
    version='1.0.0',
    description='基于YOLOv8植物叶表气孔识别项目',
    author='gdf',
    author_email='1304245067@qq.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'stognition-login = StoRecognition.System_login:main',
            'stognition-no-login = StoRecognition.System_noLogin:main',
        ]
    }
)