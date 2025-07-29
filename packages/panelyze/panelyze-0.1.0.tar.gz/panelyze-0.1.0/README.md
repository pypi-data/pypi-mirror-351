# Panelyze

**Panelyze** is an interactive, Excel-like DataFrame viewer for Python built on top of [itables](https://github.com/mwouts/itables) and [ipywidgets](https://ipywidgets.readthedocs.io/). It allows users to explore, filter, and inspect pandas DataFrames directly inside Jupyter Notebooks or Google Colab — **with no need to write filtering logic or export to Excel**.

---

## Key Features

- ✅ Interactive DataFrame preview with scrollable, sortable, and searchable table
- ✅ Column-level filtering with dropdowns or text input
- ✅ **Missing value inspector** — show only rows with `NaN` values
- ✅ Integrated column selector with “Select All” toggle
- ✅ Optimized for **JupyterLab**, **Google Colab**, and **VS Code Notebooks**
- ✅ Zero configuration — just import and run

---

## Installation

Install from [PyPI](https://pypi.org/project/panelyze/):

```bash
pip install panelyze
```

---

## Usage

```python
from panelyze import panelyze
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Launch the interactive panel
panelyze(df)
```

No need to export to Excel — just scroll, sort, filter, and inspect directly inside your notebook.

---

## Requirements

Panelyze depends on the following Python packages:

- [`pandas`](https://pypi.org/project/pandas/)
- [`itables`](https://pypi.org/project/itables/)
- [`ipywidgets`](https://pypi.org/project/ipywidgets/)
- [`IPython`](https://pypi.org/project/ipython/)

These will be installed automatically with `pip`.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve functionality, performance, or documentation.

---

## Related Projects

- [pandas-profiling](https://github.com/ydataai/pandas-profiling) — automated EDA for pandas
- [sweetviz](https://github.com/fbdesignpro/sweetviz) — visualized data comparison and exploration
- [itables](https://github.com/mwouts/itables) — interactive pandas tables via DataTables.js

---

Made with ❤️ for the data science community.