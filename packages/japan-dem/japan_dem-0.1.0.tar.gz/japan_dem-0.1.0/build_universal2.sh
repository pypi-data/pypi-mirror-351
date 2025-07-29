#!/bin/bash
# Universal2 wheel build script for japan-dem

set -e

echo "🔨 Building Universal2 wheel for japan-dem"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf target/wheels
rm -rf dist
mkdir -p dist

# Build for ARM64
echo "🏗️  Building for ARM64..."
uv run maturin build --release --features python --target aarch64-apple-darwin

# Build for x86_64 (will fail on ARM Mac without cross-compilation setup)
echo "🏗️  Building for x86_64..."
echo "⚠️  Note: x86_64 build will fail on ARM Mac due to GDAL cross-compilation issues"
echo "   You need to build on an Intel Mac or use Rosetta"

# If you have both wheels, you can combine them using delocate-fuse
echo ""
echo "📦 To create a universal2 wheel, you need:"
echo "   1. Build on ARM64 Mac: maturin build --release --features python --target aarch64-apple-darwin"
echo "   2. Build on Intel Mac: maturin build --release --features python --target x86_64-apple-darwin"
echo "   3. Combine using: delocate-fuse wheel1.whl wheel2.whl -w dist/"

# Copy ARM64 wheel to dist for now
cp target/wheels/*.whl dist/ 2>/dev/null || true

echo "✅ ARM64 wheel built successfully"
echo "📁 Wheels are in: dist/"
ls -la dist/