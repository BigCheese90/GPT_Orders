from setuptools import setup, find_packages
setup(name="EmailBestellImport", version="0.1", packages=find_packages(), install_requires=['pdfplumber',
                                                                                            'python-dotenv', 'openai',
                                                                                            'pydantic', 'pandas',
                                                                                            'rapidfuzz', 'fastapi',
                                                                                            'uvicorn'])

