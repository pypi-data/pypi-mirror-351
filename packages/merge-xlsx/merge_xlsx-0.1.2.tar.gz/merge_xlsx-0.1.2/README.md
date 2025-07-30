# 📊 merge-xlsx

**merge-xlsx** is a simple yet powerful CLI tool to merge multiple single-sheet `.xlsx` files into one workbook.  
Built for anyone tired of manually copying and pasting Excel data!

## 🚀 Why did I build this?

I often found myself with dozens (sometimes hundreds!) of Excel files, each with a single sheet, that needed to be combined into one file for analysis or reporting.  
Doing this by hand was tedious, error-prone, and just not fun.  
Existing tools were either too complex, required Excel itself, or didn’t handle my use case well.

**merge-xlsx** solves this with a single command!

## ⚡️ Features

- 🟢 Merge any number of `.xlsx` files (single-sheet) into one
- 🎨 Beautiful progress bar and colored output (thanks to [rich](https://github.com/Textualize/rich))
- 🏃 Fast and memory-efficient (uses [pandas](https://pandas.pydata.org/))
- 🐍 Python 3.13+ support

## 📦 Installation

The recommended way is with [pipx](https://pypa.github.io/pipx/):

```sh
pipx install merge-xlsx
```

## 🛠 Usage

```sh
merge-xlsx file1.xlsx file2.xlsx ... -o merged.xlsx
```

You can use wildcards to select files:

```sh
merge-xlsx /path/to/files/*.xlsx -o merged.xlsx
```

## 🧩 Edge Cases & Notes

- All input files must have a single sheet.
- All files should have the same columns (otherwise, pandas will fill missing columns with NaN).
- Output file will overwrite if it already exists.
- Large files are supported, but memory usage depends on total data size.
- Files with different encodings or corrupt files may cause errors.

## 🚧 Possible Improvements

- [ ] Option for plain/clear stdout (no rich output)
- [ ] Support for multi-sheet files (merge specific sheets)
- [ ] Column mapping or reordering
- [ ] Output to CSV or other formats
- [ ] GUI version

## 🤝 Contributing

PRs and suggestions are welcome!
Please open an issue if you find a bug or have a feature request.

## 📄 License

MIT © Vinícius Costa

## 🌟 Star this project if you find it useful
