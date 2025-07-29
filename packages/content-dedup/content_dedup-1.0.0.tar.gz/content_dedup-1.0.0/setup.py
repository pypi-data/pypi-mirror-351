import os
import re
from setuptools import setup, find_packages

# 讀取版本號從 __init__.py
def get_version():
    """從 __init__.py 讀取版本號"""
    init_file = os.path.join(os.path.dirname(__file__), 'content_dedup', '__init__.py')
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正則表達式匹配版本號
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in __init__.py")

# 讀取 README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 讀取基本依賴
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 定義額外依賴
extras_require = {
    # 開發依賴
    "dev": [
        "pytest>=6.0", 
        "pytest-cov>=3.0.0",  # 添加 pytest-cov 支援覆蓋率測試
        "black>=22.0.0", 
        "flake8>=4.0.0", 
        "mypy>=0.950",
        "coverage>=6.0.0",
        "pre-commit>=2.15.0"
    ],
    # 完整功能依賴（包含所有語言處理功能）
    "full": [
        "jieba>=0.42.0",      # 中文分詞
        "langdetect>=1.0.9",  # 語言檢測
        "nltk>=3.7.0"         # 英文文本處理
    ],
    # 中文處理專用
    "chinese": [
        "jieba>=0.42.0"
    ],
    # 進階語言檢測
    "langdetect": [
        "langdetect>=1.0.9"
    ],
    # 英文進階處理
    "english": [
        "nltk>=3.7.0"
    ]
}

# 添加 all 選項，包含所有可選依賴
all_deps = []
for deps in extras_require.values():
    all_deps.extend(deps)
extras_require["all"] = list(set(all_deps))

setup(
    name="content-dedup",
    version=get_version(),  # 動態讀取版本號
    author="changyy",
    author_email="changyy.csie@gmail.com",
    description="Intelligent content deduplication and clustering toolkit with multilingual support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changyy/py-content-dedup",
    project_urls={
        "Bug Tracker": "https://github.com/changyy/py-content-dedup/issues",
        "Documentation": "https://github.com/changyy/py-content-dedup/docs",
        "Repository": "https://github.com/changyy/py-content-dedup",
        "Changelog": "https://github.com/changyy/py-content-dedup/blob/main/CHANGELOG.md",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: Chinese (Simplified)", 
        "Natural Language :: English",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "content-dedup=content_dedup.cli:main",
        ],
    },
    keywords="deduplication clustering nlp content-analysis text-mining multilingual chinese english mixed-language",
    include_package_data=True,
    zip_safe=False,
)
