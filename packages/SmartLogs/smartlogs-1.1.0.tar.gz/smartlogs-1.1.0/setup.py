from setuptools import find_packages, setup

setup(
    name="SmartLogs",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
        "pytest>=7.0.0",
        "PyYAML>=6.0",
    ],
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="📢 Um logger inteligente para projetos Python com suporte a logs coloridos, integração com Slack e Telegram, e recursos avançados de debug",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/SmartLogs",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
)
