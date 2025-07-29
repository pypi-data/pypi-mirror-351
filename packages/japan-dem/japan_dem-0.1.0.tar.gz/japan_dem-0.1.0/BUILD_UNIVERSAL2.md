# Universal2 Wheel ビルド方法

## 概要

japan-dem の Python バインディングを Universal2 (ARM64 + x86_64) 形式でビルドする方法です。
GDAL の制約により、クロスコンパイルが難しいため、各アーキテクチャで個別にビルドする必要があります。

## 前提条件

- ARM64 Mac (Apple Silicon) と Intel Mac の両方へのアクセス
- または、Rosetta 2 を使用した x86_64 エミュレーション環境
- Python 3.9 以上
- maturin (`pip install maturin`)
- delocate (`pip install delocate`)

## ビルド手順

### 1. ARM64 Mac でのビルド

```bash
# ARM64 Mac で実行
cd /path/to/japan-dem

# ARM64 用 wheel をビルド
uv run maturin build --release --features python --target aarch64-apple-darwin

# 生成されたファイルを確認
ls target/wheels/
# japan_dem-0.1.0-cp39-abi3-macosx_11_0_arm64.whl
```

### 2. Intel Mac でのビルド

```bash
# Intel Mac で実行
cd /path/to/japan-dem

# x86_64 用 wheel をビルド
uv run maturin build --release --features python --target x86_64-apple-darwin

# 生成されたファイルを確認
ls target/wheels/
# japan_dem-0.1.0-cp39-abi3-macosx_10_12_x86_64.whl
```

### 3. Rosetta 2 を使用した x86_64 ビルド (ARM64 Mac で)

```bash
# Rosetta 2 環境で x86_64 Python をインストール
arch -x86_64 /bin/bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11

# x86_64 環境でビルド
arch -x86_64 uv run maturin build --release --features python

# ただし、GDAL のリンクエラーが発生する可能性があります
```

### 4. Wheel の結合

両方の wheel ファイルが用意できたら、`delocate-fuse` を使って結合します：

```bash
# 必要なツールをインストール
pip install delocate

# 2つの wheel を結合
delocate-fuse \
    target/wheels/japan_dem-0.1.0-cp39-abi3-macosx_11_0_arm64.whl \
    target/wheels/japan_dem-0.1.0-cp39-abi3-macosx_10_12_x86_64.whl \
    -w dist/

# 結果を確認
ls dist/
# japan_dem-0.1.0-cp39-abi3-macosx_10_12_universal2.whl
```

## GitHub Actions での自動ビルド

`.github/workflows/build-wheels.yml`:

```yaml
name: Build Universal2 Wheels

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos-arm64:
    runs-on: macos-14  # M1 runner
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: brew install gdal
      - name: Build wheel
        uses: PyO3/maturin-action@v1
        with:
          args: --release --features python --target aarch64-apple-darwin
      - uses: actions/upload-artifact@v4
        with:
          name: wheel-macos-arm64
          path: target/wheels/*.whl

  build-macos-x86:
    runs-on: macos-13  # Intel runner
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: brew install gdal
      - name: Build wheel
        uses: PyO3/maturin-action@v1
        with:
          args: --release --features python --target x86_64-apple-darwin
      - uses: actions/upload-artifact@v4
        with:
          name: wheel-macos-x86
          path: target/wheels/*.whl

  combine-wheels:
    needs: [build-macos-arm64, build-macos-x86]
    runs-on: macos-latest
    steps:
      - uses: actions/download-artifact@v4
      - name: Install delocate
        run: pip install delocate
      - name: Combine wheels
        run: |
          delocate-fuse \
            wheel-macos-arm64/*.whl \
            wheel-macos-x86/*.whl \
            -w dist/
      - uses: actions/upload-artifact@v4
        with:
          name: universal2-wheel
          path: dist/*.whl
```

## トラブルシューティング

### GDAL リンクエラー

x86_64 ビルドで GDAL のリンクエラーが発生する場合：

1. GDAL を適切なアーキテクチャでインストール
   ```bash
   # Intel Mac または Rosetta 環境で
   arch -x86_64 brew install gdal
   ```

2. 環境変数を設定
   ```bash
   export GDAL_HOME=/usr/local/opt/gdal
   export GDAL_DATA=$GDAL_HOME/share/gdal
   ```

### pkg-config エラー

クロスコンパイル時の pkg-config エラーの場合：

```bash
# pkg-config の設定
export PKG_CONFIG_ALLOW_CROSS=1
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
```

## 代替案

### Docker を使用したビルド

各アーキテクチャ用の Docker イメージを使用してビルドすることも可能です：

```dockerfile
# Dockerfile.x86_64
FROM --platform=linux/amd64 python:3.11
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev
# ...

# Dockerfile.arm64
FROM --platform=linux/arm64 python:3.11
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev
# ...
```

### 事前ビルド済みバイナリの配布

各アーキテクチャ用の wheel を個別に配布し、ユーザーの環境に応じて適切なものをインストールしてもらう方法もあります。