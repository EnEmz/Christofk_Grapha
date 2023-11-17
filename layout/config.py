# config.py

import pandas as pd
import os

from layout.utilities_layout import generate_classes_checklist_options_with_met_names

# Get the current working directory
current_directory = os.getcwd()

# Filename of the metabolite classes file
filename = "metabolite_classes.csv"

# Construct the full path to metabolite classes file
path_met_pathway_list = os.path.join(current_directory, filename)

# Insert your preselected options for the normalization of the pool data
normalization_preselected = ['trifluoromethanesulfonate', 'quantity/sample']

df_met_group_list = pd.read_csv(path_met_pathway_list)
df_met_group_list = df_met_group_list.drop_duplicates(keep='first').dropna(how='all')

# For metabolite classes selection in modal
classes_options_w_mets, tooltips = generate_classes_checklist_options_with_met_names(df_met_group_list)

# Preselected classes in the class selection modal
met_class_list_preselected = [
                            'glycolysis',
                            'TCA', 
                            'amino acid',
                            'PPP',
                            "polyol-pathway",
                            "nucleotide",
                            "lipid metabolism",
                            "energy-carrier",
                            "redox",
                            "urea cycle",
                            "SAM-cycle",
                            "vitamin",
                            "SCFAs",
                            "bile acid",
                            "small-molecule",
                            "succinilation",
                            "purine intermediate",
                            "tryptophan metabolism",
                            "histidine metabolism"
                            ]

# Color palette for isotopologue bar pltos and iso distribution plot
iso_color_palette = [
    "#C4C3C3",  # Light Gray
    "#FA8072",  # Salmon
    "#5F9EA0",  # Cadet Blue
    "#DAA520",  # Goldenrod
    "#9932CC",  # Dark Orchid
    "#228B22",  # Forest Green
    "#DDA0DD",  # Plum
    "#1E90FF",  # Dodger Blue
    "#808000",  # Olive
    "#FF1493",  # Deep Pink
    "#4682B4",  # Steel Blue
    "#D2691E",  # Chocolate
    "#FF7F50",  # Coral
    "#8FBC8F",  # Dark Sea Green
    "#4169E1",  # Royal Blue
    "#B0E0E6",  # Powder Blue
    "#A0522D",  # Sienna
    "#008080",  # Teal
    "#800000",  # Maroon
    "#FFD700",  # Gold
    "#6A5ACD",  # Slate Blue
    "#7FFF00",  # Chartreuse
    "#DB7093",  # Pale Violet Red
    "#FFA500",  # Orange
    "#8A2BE2",  # Blue Violet
    "#20B2AA",  # Light Sea Green
    "#FF4500",  # Orange Red
    "#00FFFF",  # Aqua
    "#DA70D6",  # Orchid
    "#32CD32",  # Lime Green
    "#BA55D3",  # Medium Orchid
    "#F08080",  # Light Coral
    "#2E8B57",  # Sea Green
    "#FAA460",  # Sandy Brown
    "#FF6347",  # Tomato
    "#90EE90",  # Light Green
    "#7B68EE",  # Medium Slate Blue
    "#FF69B4",  # Hot Pink
    "#3CB371",  # Medium Sea Green
    "#B22222",  # Firebrick
]
