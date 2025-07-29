from setuptools import setup, find_packages

setup(
    name="JTechRobotFrameworkAI",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "robotframework>=6.1.1",
        "google-generativeai>=0.3.2",
        "langchain>=0.1.0",
        "langchain-google-genai>=0.0.5",
        "crewai>=0.11.0",
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.0",
    ],
    python_requires=">=3.9",
    author="JTech",
    author_email="angelo@jtech.eng.br",
    description="Uma biblioteca Robot Framework com recursos de IA usando Google Generative AI e CrewAI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jtech-eng/jtech-robotframework-ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
