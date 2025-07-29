# Toncatsu: A Robust and Lightweight Map-Matching Library
頑健かつ軽量なマップマッチングライブラリ

## Overview 概要

**Toncatsu** is a Python package that extends the path-based map-matching logic originally developed in the GPS trajectory analysis tool *Catsudon* (Hara, 2017). This method improves robustness against GNSS errors by associating GPS observations with the nearest **links**, rather than the nearest **nodes**, enabling more stable and accurate estimation of movement paths across varying network granularities.

Toncatsuは、原（2017）が提案した移動軌跡解析ツールCatsudonのマップマッチング手法を発展させたPythonパッケージです。観測点を最も近いノードではなく最も近いリンクに対応づけることで、ネットワーク構造に依存しない、頑健なマップマッチングが可能になります。GNSS誤差への耐性を持ち、リンクの分割状況に左右されずに、より現実に近い経路推定が行えます。

## Features 特徴

- 🌍 **Link-based matching**: Reduces sensitivity to sparse or dense node distributions  
  　　**リンク基準のマッチング**：ノードの疎密による経路のばらつきを低減
- 🚀 **Fast search via kd-tree**: Efficient nearest-link search using spatial trees  
  　　**kd-treeを活用した高速探索**：空間木構造により近傍リンクを迅速に取得
- 🐍 **Pure Python / GeoPandas-based**: Easy to install and integrate  
  　　**GeoPandasベースの純Python実装**：環境構築が容易で拡張性が高い
- 🧪 **Benchmark tested**: Evaluated using standardized test datasets  
  　**ベンチマーク検証済み**：標準データセットを用いた評価を実施


## License ライセンス
MIT License

---

## Installation インストール

```bash
pip install toncatsu
```

(Coming soon to PyPI / PyPI公開予定)

## Usage 使い方

```python
from toncatsu import toncatsu

# Required DataFrames: node_df, link_df, observation_df
toncatsu(node_df, link_df, observation_df, output_dir="./output")
```

## Function: `toncatsu()` 関数の説明

Performs map-matching using GMNS-format node/link data and GPS observations.
GMNS形式のノード・リンク・GPS観測データを用いてマップマッチングを実行します。

**Parameters 引数:**

English
- `node_df`: DataFrame with columns: `'node_id'`, `'x_coord'`, `'y_coord'`  
- `link_df`: GeoDataFrame with columns: `'link_id'`, `'from_node_id'`, `'to_node_id'`, `'geometry'`  
- `observation_df`: DataFrame with columns: `'id'`, `'x_coord'`, `'y_coord'`  
- `output_dir`: Output directory for saving results

日本語
- `node_df`: `'node_id'`, `'x_coord'`, `'y_coord'` を含むDataFrame  
- `link_df`: `'link_id'`, `'from_node_id'`, `'to_node_id'`, `'geometry'` を含むGeoDataFrame  
- `observation_df`: `'id'`, `'x_coord'`, `'y_coord'` を含むDataFrame  
- `output_dir`: 結果を保存する出力先ディレクトリ
