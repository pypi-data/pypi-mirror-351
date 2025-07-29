#!/bin/bash
# 
# 本地測試 GitHub Actions 工作流程的腳本
# 
# 使用方法:
#   chmod +x test_github_actions.sh
#   ./test_github_actions.sh
#

set -e

echo "🧪 測試 GitHub Actions 工作流程準備情況..."
echo "================================================"

# 檢查必要的檔案
echo "📁 檢查必要檔案..."
required_files=(
    "setup.py"
    "pyproject.toml" 
    "requirements.txt"
    "requirements-dev.txt"
    "README.md"
    "LICENSE"
    "MANIFEST.in"
    "CHANGELOG.md"
    ".github/workflows/ci.yml"
    ".github/workflows/publish.yml"
    ".github/workflows/quality.yml"
    ".github/workflows/version.yml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
    fi
done

echo ""
echo "🐍 檢查 Python 環境..."

# 檢查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虛擬環境已啟用: $VIRTUAL_ENV"
else
    echo "⚠️  未檢測到虛擬環境"
fi

echo ""
echo "📦 測試打包流程..."

# 測試安裝依賴
echo "安裝打包依賴..."
python3 -m pip install --quiet --upgrade pip build twine wheel setuptools setuptools_scm

# 清理之前的構建
if [[ -d "dist" ]]; then
    rm -rf dist/
fi
if [[ -d "build" ]]; then
    rm -rf build/
fi

# 構建套件
echo "構建套件..."
python3 -m build

# 檢查構建結果
echo "檢查構建結果..."
if [[ -d "dist" ]]; then
    echo "✅ dist/ 目錄已創建"
    ls -la dist/
else
    echo "❌ dist/ 目錄未創建"
    exit 1
fi

# 檢查套件內容
echo "檢查套件內容..."
twine check dist/*

echo ""
echo "🧪 運行測試..."

# 運行測試套件
python3 -m pytest tests/ -v --tb=short

echo ""
echo "📋 檢查 setup.py 元數據..."
python3 setup.py check --metadata --strict

echo ""
echo "🔍 檢查 MANIFEST.in..."
if command -v check-manifest &> /dev/null; then
    check-manifest
else
    echo "⚠️  check-manifest 未安裝，跳過檢查"
fi

echo ""
echo "✅ 所有檢查完成！"
echo ""
echo "📝 下一步操作："
echo "1. 設定 GitHub Repository Secrets:"
echo "   - PYPI_API_TOKEN"
echo "   - TEST_PYPI_API_TOKEN"
echo ""
echo "2. 測試發佈到 TestPyPI:"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "3. 創建 Git tag 觸發自動發佈:"
echo "   git tag v1.0.1"
echo "   git push origin v1.0.1"
echo ""
echo "4. 或使用 GitHub Actions 手動觸發發佈"
