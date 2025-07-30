# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'hurmodel'
version = '1.1.1'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=['torch==2.4.1', 'tiktoken==0.4.0', 'numpy==1.25.2', 'psutil==7.0.0', 'tqdm==4.67.1'],
    url='https://github.com/sapiens-technology/hurmodel',
    license='Proprietary Software'
)
# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
