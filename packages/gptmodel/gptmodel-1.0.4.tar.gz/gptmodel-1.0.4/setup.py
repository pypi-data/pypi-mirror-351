# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'gptmodel'
version = '1.0.4'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=['tqdm==4.67.1', 'numpy==1.25.2', 'torch==2.4.1', 'tiktoken==0.4.0'],
    url='https://github.com/sapiens-technology/gptmodel',
    license='Proprietary Software'
)
# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
