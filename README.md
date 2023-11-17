# Christofk_Grapha

## Overview

Christofk_Grapha is a [Dash](https://github.com/plotly/dash) app designed for the quick and efficient visualization of metabolomics data. It produces high-quality, customizable, and interactive graphs that can be downloaded. The app is tailored to handle data structures outputted by [Accucor](https://github.com/XiaoyangSu/AccuCor). You can define metabolite classes for your metabolomics data in the `metabolite_classes.csv` file, which influences how analysis graphs are displayed.

The app automatically detects the presence of isotopologue data based on the "Normalized" Excel file sheet name and requires the metabolomics pool data to have the sheet name "PoolAfterDF" for recognition.

**Important**: Do not adjust header names or Excel sheet names in the data file or `metabolite_classes.csv` to ensure smooth functionality.

## Getting Started

- Ensure you have a virtual environment or Python 3.12 installed.
- Install the necessary Python packages from `requirements.txt`:

```bash
  # Navigate to the directory containing requirements.txt
  pip install -r requirements.txt
```

### Usage

1. **Run the App**:
   - Execute `index.py` to start the application.
   - In your terminal, Flask will start a local server on your computer and give a message that 'Dash app is running on: `http://127.0.0.1:8050/`'. Copy the http address `http://127.0.0.1:8050/` (or whatever is in your terminal) and paste it in your web browser.
   - You should be able to see Christofk_Grapha app.

2. **Upload Data**:
   - Upload data from the `Example Data` folder.

   _Note_: The `metabolite_classes.csv` is pre-configured for files in `Example Data` folder. Adjust `metabolite_classes.csv` according to the metabolite names in your data file.

### Using GitHub Codespaces

GitHub Codespaces offers a fully-configured development environment with all the necessary tools and dependencies for running Christofk_Grapha. Follow these steps to use Codespaces:

#### Open the Repository in Codespaces:

- Navigate to the GitHub repository and click on the **Code** button. 
- Select **Open with Codespaces** and then **New codespace**. 
- This will create a new development environment with everything set up as per the `.devcontainer` configuration.

#### Run the App in Codespaces:

- Once your Codespace is ready, use the built-in terminal to navigate to the project directory.
- Start the application by running `python index.py`. 
- The integrated terminal will display a URL like `https://port-8050-your-codespace-name.githubpreview.dev/`.
- Click the URL or copy and paste it into a browser tab to view the Christofk_Grapha app.

#### Upload and Test Data:

- The Codespace environment includes all files from the repository. You can access the `Example Data` folder and `metabolite_classes.csv` file directly.
- Test the application using these files or upload your data as needed.


### Available Analysis Graphs

#### Bulk Pool Size Heatmap
Displays a pool size heatmap of selected metabolite classes and checks statistical significance between each pair among selected sample groups.

#### Bulk Isotopologue Size Heatmap
Shows a heatmap of summed non-zero isotopologue values. Examines statistical significance between chosen sample groups for summed non-zero isotopologues.

#### Custom Pool Size Heatmap
Presents a pool size heatmap for a user-entered metabolite list from uploaded metabolite names.

#### Bulk Metabolomics
Offers a detailed view of isotopologue (if available) and pool metabolomics data. Statistical significance between selected two groups by the user is displayed directly on the metabolite graphs.

#### Isotopologue Distribution
Displays the isotopologue distribution of a selected metabolite between user-selected sample groups. Statistical significance between selected two groups by the user is displayed directly on the metabolite graphs.

#### Volcano Plot
Generates a volcano plot comparing user selected control and condition sample groups. On-click annotations are available to display metabolite names.

---

Statistical Significance is calculated using [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html) two-sided Student t-test.

**Version Information**: This is Christofk_Grapha version 1.0, with more updates anticipated. The system has been tested with Python versions 3.8 and 3.12. The provided `requirements.txt` file is tailored for Python 3.12.0.