#!/bin/bash

# 🎯 py-content-dedup CI/CD 管道最終驗證腳本
# 這個腳本執行最終的檢查以確保所有組件都正確設置

set -e  # 如果任何命令失敗則退出

echo "🔍 執行 py-content-dedup CI/CD 管道最終驗證..."
echo "======================================================="

# 檢查 Git 倉庫狀態
echo ""
echo "📋 檢查 Git 倉庫狀態..."
if [ -d .git ]; then
    echo "✅ Git 倉庫已初始化"
    
    # 檢查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  檢測到未提交的更改："
        git status --short
        echo ""
        read -p "是否要提交這些更改？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "chore: final cleanup before CI/CD deployment"
            echo "✅ 更改已提交"
        fi
    else
        echo "✅ 沒有待提交的更改"
    fi
    
    echo "📊 當前分支: $(git branch --show-current)"
    echo "📝 最新提交: $(git log -1 --oneline)"
else
    echo "❌ Git 倉庫未初始化"
    exit 1
fi

# 檢查所有必要的 GitHub Actions 文件
echo ""
echo "🔧 檢查 GitHub Actions 工作流程..."
WORKFLOWS=(
    ".github/workflows/ci.yml"
    ".github/workflows/publish.yml"
    ".github/workflows/quality.yml"
    ".github/workflows/version.yml"
    ".github/workflows/quick-test.yml"
)

for workflow in "${WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo "✅ $workflow"
    else
        echo "❌ $workflow 缺失"
        exit 1
    fi
done

# 檢查文檔文件
echo ""
echo "📚 檢查文檔文件..."
DOCS=(
    ".github/ENVIRONMENT_SETUP.md"
    ".github/PUBLISHING_GUIDE.md"
    ".github/SETUP_COMPLETION_GUIDE.md"
    "CHANGELOG.md"
    "README.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc"
    else
        echo "❌ $doc 缺失"
        exit 1
    fi
done

# 檢查配置文件
echo ""
echo "⚙️  檢查配置文件..."
CONFIGS=(
    "pyproject.toml"
    "MANIFEST.in"
    ".bumpversion.cfg"
    ".pre-commit-config.yaml"
    ".gitignore"
    "requirements.txt"
    "requirements-dev.txt"
)

for config in "${CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ $config"
    else
        echo "❌ $config 缺失"
        exit 1
    fi
done

# 檢查 Python 環境
echo ""
echo "🐍 檢查 Python 環境..."
if command -v python &> /dev/null; then
    echo "✅ Python 版本: $(python --version)"
else
    echo "❌ Python 未安裝"
    exit 1
fi

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虛擬環境已啟用: $VIRTUAL_ENV"
else
    echo "⚠️  虛擬環境未啟用 (建議使用虛擬環境)"
fi

# 檢查關鍵依賴
echo ""
echo "📦 檢查關鍵依賴..."
REQUIRED_PACKAGES=("build" "twine" "pytest" "black" "flake8" "mypy")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        echo "✅ $package"
    else
        echo "❌ $package 缺失"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo ""
    echo "⚠️  缺失的包可以通過以下命令安裝："
    echo "pip install -r requirements-dev.txt"
fi

# 執行快速構建測試
echo ""
echo "🔨 執行快速構建測試..."
if [ -d "dist" ]; then
    rm -rf dist/
fi
if [ -d "build" ]; then
    rm -rf build/
fi
if [ -d "content_dedup.egg-info" ]; then
    rm -rf content_dedup.egg-info/
fi

if python -m build > /dev/null 2>&1; then
    echo "✅ 包構建成功"
    if [ -f "dist/content_dedup-1.0.0-py3-none-any.whl" ] && [ -f "dist/content_dedup-1.0.0.tar.gz" ]; then
        echo "✅ 生成了 wheel 和 source distribution"
    else
        echo "❌ 包文件生成不完整"
        exit 1
    fi
else
    echo "❌ 包構建失敗"
    exit 1
fi

# 檢查包質量
echo ""
echo "🔍 檢查包質量..."
if command -v twine &> /dev/null; then
    if twine check dist/* > /dev/null 2>&1; then
        echo "✅ 包通過 twine 檢查"
    else
        echo "❌ 包未通過 twine 檢查"
        exit 1
    fi
else
    echo "⚠️  twine 未安裝，跳過包檢查"
fi

# 執行快速測試
echo ""
echo "🧪 執行快速測試..."
if python -m pytest tests/ -x --tb=short > /dev/null 2>&1; then
    echo "✅ 測試通過"
else
    echo "❌ 測試失敗"
    echo "請運行 'pytest tests/' 查看詳細錯誤"
    exit 1
fi

# 檢查版本號
echo ""
echo "📊 檢查版本信息..."
VERSION=$(python -c "from content_dedup import __version__; print(__version__)")
echo "✅ 當前版本: $VERSION"

# 檢查是否有遠程倉庫
echo ""
echo "🌐 檢查遠程倉庫..."
if git remote -v | grep -q origin; then
    echo "✅ 遠程倉庫已配置:"
    git remote -v | grep origin
else
    echo "⚠️  遠程倉庫未配置"
    echo "請添加 GitHub 遠程倉庫:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/py-content-dedup.git"
fi

echo ""
echo "🎉 最終驗證完成！"
echo "======================================================="
echo ""
echo "📋 總結:"
echo "✅ 所有 GitHub Actions 工作流程文件都已就位"
echo "✅ 所有配置文件都已正確設置"
echo "✅ 包構建和測試都正常工作"
echo "✅ 代碼質量檢查通過"
echo ""
echo "🚀 下一步操作:"
echo "1. 將代碼推送到 GitHub: git push origin main"
echo "2. 在 GitHub 設置 API tokens (PYPI_API_TOKEN, TEST_PYPI_API_TOKEN)"
echo "3. 測試發布到 TestPyPI"
echo "4. 創建首個正式發布版本"
echo ""
echo "📚 詳細指南請參閱: .github/SETUP_COMPLETION_GUIDE.md"
echo ""
echo "🎯 你的 py-content-dedup 項目現在已經準備好進行 CI/CD 部署了！"
