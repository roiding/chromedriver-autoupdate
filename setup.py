import setuptools

with open("README.md",'r',encoding='utf-8') as fh:
    long_description = fh.read()



setuptools.setup(
    name="chromedriver_autoupdate", #模块名称
    version='x.x.x', #当前版本
    author="roiding", # 作者
    author_email="maodoulove19950815@gmail.com", #作者邮箱
    description="chromedriver的自动更新", #模块介绍
    long_description=long_description, #模块详细介绍
    long_description_content_type="text/markdown", #模块详细介绍格式
    url="https://github.com/roiding/chromedriver-autoupdate", #项目地址
    packages=setuptools.find_packages(), #自动找到项目中倒入的模块
    # 模块元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=['requests','tqdm'],
    python_requires='>=3.6'
)