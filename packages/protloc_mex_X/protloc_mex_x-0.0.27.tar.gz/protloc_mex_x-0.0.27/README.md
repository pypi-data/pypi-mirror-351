# ProtLoc-mex_X

## Introduction ProtLoc-mex_X

protloc_mex_X integrates two modules: ESM2_fr and feature_correlation. ESM2_fr is based on the ESM2(Supported by ESM2_650m) model and is capable of extracting feature representations from protein sequences, including 'cls', 'eos', 'mean', 'segment_mean', and 'pho'. On the other hand, the feature_correlation module provides Spearman correlation analysis functionality, enabling users to visualize correlation heatmaps and conduct feature crossover regression analysis. This allows users to explore the relationships between different data features and identify features that are relevant to the target feature.

## Installation

This project's core code has been uploaded to the PyPI repository. To get it using a conda virtual environment, follow the steps below:

First, create a new conda environment. For Windows systems, it is recommended to use conda Prompt for this task. On Linux systems, you can use the Terminal. (You can also modify the environment name as needed, here, we use "myenv" as an example):

```
conda create -n myenv python=3.9
```

Then, activate the environment you just created:

```
conda activate myenvs
```

Finally, use pip to install 'protloc_mex_X' within this environment:

```
pip install protloc_mex_X
```

### Dependencies

ProtLoc-mex_X requires Python == 3.9 or 3.10.

Below are the Python packages required by ProtLoc-mex_X, which are automatically installed with it:

```
dependencies = [
        "numpy ==1.20.3",
        "pandas ==1.4.1",
        "seaborn ==0.11.2",
        "matplotlib ==3.5.1"
]
```

and other not automatically installed but also required Python packages：

```
dependencies = [
       "torch ==1.12.1",
       "tqdm ==4.63.0",
       "re ==2.2.1",
       "sklearn ==1.2.2",
       "transformers ==4.26.1"
]
```

It is advised to obtain these dependent packages from their respective official sources, while carefully considering the implications of version compatibility.

## How to use ProtLoc-mex_X

ProtLoc-mex_X includes 2 modules: ESM2_fr and feature_corrlation.

### ESM2_fr

ESM2_fr is a pre-trained deep learning model based on the ESM2 model. It is capable of extracting representation features from protein sequences and further optimizing the feature representation through weighted averaging.

It contains one class and three functions. The class is named `Esm2LastHiddenFeatureExtractor`, which includes the following three methods: `get_last_hidden_features_combine()`, `get_last_hidden_phosphorylation_position_feature()`, and `get_amino_acid_representation()`. The functions present in the code are `get_last_hidden_features_single()`, `NetPhos_classic_txt_DataFrame()`, and `phospho_feature_sim_cosine_weighted_average()`.

#### Function  `get_last_hidden_features_single()`：

The `get_last_hidden_features_single()` function is utilized for extracting different types of representation features from the input protein sequences. It accepts protein sequence data `X_input`, along with the model tokenizer and model as inputs, and subsequently returns a DataFrame containing the extracted features.(note: Only single-batch inputs are supported.)

The `device_choose` parameter takes one of three values: [`'auto'`, `'cuda'`, `'cpu'`]. When set to `'auto'` (default), it automatically detects and uses GPU if available; otherwise, it uses the CPU. Additionally, setting it to `'cuda'` uses the GPU, and `'cpu'` uses the CPU directly for processing. Since v0.0.27, this parameter also supports CUDA device selection (e.g., `cuda:1`).

#### Class `Esm2LastHiddenFeatureExtractor()`：

The `Esm2LastHiddenFeatureExtractor()` class is used for extracting various types of representation features from protein sequences. It accepts amino acid sequence input, invokes the pre-trained ESM2 model, and obtains pre-trained representation vectors ('cls', 'eos', 'mean', 'segment_mean', 'pho').

The `get_last_hidden_features_combine()` function serves the same purpose as `get_last_hidden_features_single()`, but it is designed to handle multiple batches of input data. This function takes protein sequence data `X_input` as input and returns a DataFrame containing the combined features extracted from the multiple batches of protein sequence. The default value for the parameter `batch_size` is 32, which can be adjusted based on the specifications of the GPU memory to achieve faster inference speed.

The `get_last_hidden_phosphorylation_position_feature()` function extracts phosphorylation representation features from the input protein sequences. It takes protein sequence data `X_input` and returns a DataFrame containing phosphorylation representation features.

The `get_amino_acid_representation()` function is used to calculate representation features for a specific amino acid at a given position in a protein sequence. The main purpose is to support the characterization of phosphorylation sites.

The `device_choose` parameter takes one of three values: [`'auto'`, `'cuda'`, `'cpu'`]. When set to `'auto'` (default), it automatically detects and uses GPU if available; otherwise, it uses the CPU. Additionally, setting it to `'cuda'` uses the GPU, and `'cpu'` uses the CPU directly for processing.

#### Function  `NetPhos_classic_txt_DataFrame()` ：

The `NetPhos_classic_txt_DataFrame()` function is designed to extract sequence information from the provided text data, which is derived from NetPhos (https://services.healthtech.dtu.dk/services/NetPhos-3.1/), and then it returns the extracted data in the form of a DataFrame.

#### Function `phospho_feature_sim_cosine_weighted_average()` ：

The `phospho_feature_sim_cosine_weighted_average()` function calculates the weighted average of phosphorylation features for protein sequences and returns the input DataFrame updated with weighted average values, which provide a characterization of the entire amino acid sequence's phosphorylation pattern.

#### For using ESM2_fr example, this case is conducted using the online loading method for the esm2_t33_650M_UR50D model. For offline usage or information on other scales of the esm2 model, please visit the official esm2 [website](https://huggingface.co/facebook/esm2_t33_650M_UR50D).

```python
# Import necessary libraries and modules
>>> from transformers import AutoTokenizer, AutoModelForMaskedLM
>>> import torch
>>> import pandas as pd
>>> from protloc_mex_X.ESM2_fr import Esm2LastHiddenFeatureExtractor, get_last_hidden_features_single, phospho_feature_sim_cosine_weighted_average

# Initialize the tokenizer and model with the pretrained ESM2 model
>>> tokenizer = AutoTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")
>>> model = AutoModelForMaskedLM.from_pretrained("facebook/esm2_t33_650M_UR50D", output_hidden_states=True)

# Create a DataFrame containing protein sequences
>>> protein_sequence_df = pd.DataFrame({
...     'Entry' : ['protein1','protein2'],
...     'Sequence': ['ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY']
... })

# Initialize the feature extractor. If you wish to directly utilize 'cuda'/'cpu', simply replace 'auto' with 'cuda'/'cpu'
>>> feature_extractor = Esm2LastHiddenFeatureExtractor(tokenizer, model,
...                                                    compute_cls=True, compute_eos=True, compute_mean=True, compute_segments=True,
···                                                    device_choose = 'auto')

# Perform feature extraction on the protein sequences
>>> human_df_represent = feature_extractor.get_last_hidden_features_combine(protein_sequence_df, sequence_name='Sequence', batch_size= 1)
```

#### Example for pho feature representation:

1. First, simulate the result of a Netphos prediction for phosphorylation sites. The key is to obtain the phosphorylation sites, and note that the numbering of phosphorylation sites starts from 1. Of course, you can also provide your own phosphorylation site results.

```python
# Import the necessary modules and packages
>>> import os
>>> import protloc_mex_X
>>> from protloc_mex_X.ESM2_fr import NetPhos_classic_txt_DataFrame
>>> import random
>>> import re

# Load the example data. This serves as a sample dataset containing phosphorylation site predictions from NetPhos.
>>> example_data = os.path.join(protloc_mex_X.__path__[0], "examples", "test1.txt")
>>> with open(example_data, "r") as f:
...     data = f.read()

# Use regular expressions to extract specific patterns and store them in a DataFrame.
>>> pattern = r".*YES"
>>> result_df = NetPhos_classic_txt_DataFrame(pattern, data)

# Assign the 'Entry' column values to be the same as the 'Sequence' column.
>>> result_df.loc[:, 'Entry'] = result_df.loc[:, 'Sequence']

"""
Please be aware that the following sequence is randomly generated for demonstration purposes only. 
In real-world applications, one should utilize complete gene sequences, as NetPhos only provides 6-base pair phosphorylation site predictions, which do not represent complete gene sequences.
"""
# Convert 'position' to integer for further analysis.
# Generate random amino acid sequences for demonstration.

# Define a function to generate a random sequence of amino acids with a minimum length.
>>> def generate_random_sequence(min_length):
...     amino_acids = 'ACDEFGHIKLMNPQRSTVWY'  # 20 standard amino acids
...     return ''.join(random.choice(amino_acids) for _ in range(min_length))

# Find the maximum position for each unique 'Entry' in the DataFrame.
>>> max_positions = result_df['position'].astype(int).groupby(result_df['Entry']).max()

# Create a dictionary to store the randomly generated sequences based on the maximum positions.
>>> generated_sequences = {entry: generate_random_sequence(pos) for entry, pos in max_positions.items()}

# Define a function to update the 'Sequence' column with the generated sequences.
>>> def update_sequence(row):
...     entry = row['Entry']
...     return generated_sequences[entry]

# Update the DataFrame with the generated sequences.
>>> result_df['Sequence'] = result_df.apply(update_sequence, axis=1)
```

2. Second, calculate the features of 'cls' and all 'pho' sites.

```python
>>> from transformers import AutoTokenizer, AutoModelForMaskedLM
>>> import torch
>>> import pandas as pd
>>> from protloc_mex_X.ESM2_fr import Esm2LastHiddenFeatureExtractor, phospho_feature_sim_cosine_weighted_average
>>> import re  # Import the re module for regular expressions

# Initialize tokenizer and model using Facebook's ESM2 pre-trained model
>>> tokenizer = AutoTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")
>>> model = AutoModelForMaskedLM.from_pretrained("facebook/esm2_t33_650M_UR50D", output_hidden_states=True)

# Create a DataFrame containing sample protein sequences
>>> protein_sequence_df = pd.DataFrame({
...     'Entry' : ['seq1', 'seq2'],
...     'Sequence': ['ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY']
... })

# Initialize a feature extractor to obtain hidden layer features from ESM2. If you wish to directly utilize 'cuda'/'cpu', simply replace 'auto' with 'cuda'/'cpu'
>>> feature_extractor = Esm2LastHiddenFeatureExtractor(tokenizer, model,
...                                                    compute_cls=True, compute_eos=False, 
...                                                    compute_mean=False, compute_segments=False, device_choose = 'auto')

# Use the feature extractor to get the feature representation of phosphorylation positions predicted by Netphos
>>> Netphos_df_represent = feature_extractor.get_last_hidden_phosphorylation_position_feature(result_df, sequence_name='Sequence', phosphorylation_positions='position', batch_size=2)

# Similarly, get the feature representation of human protein sequences
>>> human_df_represent = feature_extractor.get_last_hidden_features_combine(protein_sequence_df, sequence_name='Sequence', batch_size= 1)

# Set the DataFrame index to 'Entry' for Netphos representation
>>> Netphos_df_represent.set_index('Entry', inplace=True)

# Extract column names that match the pattern 'ESM2_clsX'
>>> cols = [col for col in human_df_represent.columns if re.match(r'ESM2_cls\d+', col)]

# Set the DataFrame index to 'Entry' for human representation and create a sub-DataFrame for cls columns
>>> human_df_represent.set_index('Entry', inplace=True)
>>> human_df_represent_cls = human_df_represent[cols]
```

3. Finally, obtain an overall 'pho' representation based on the similarity calculations between 'cls' and each 'pho'

```python
# Extract all column names that match the 'ESM2_phospho_posX' format.
>>> pho_cols = [col for col in Netphos_df_represent.columns if re.match(r'ESM2_phospho_pos\d+', col)]

# Create a sub-DataFrame consisting only of these specific columns.
>>> Netphos_df_represent_pho = Netphos_df_represent[pho_cols]

# Set the dimensions for feature calculation.
>>> dim = 1280

# Remove 'seq3' from Netphos_df_represent_pho to maintain consistency in amino acids between 'pho' and 'cls'.
>>> Netphos_df_represent_pho = Netphos_df_represent_pho.drop(Netphos_df_represent_pho[Netphos_df_represent_pho.index == 'seq3'].index)

# Calculate cls and pho_average features (where pho_average refers to the 'pho' features).
>>> human_df_represent_cls_pho = phospho_feature_sim_cosine_weighted_average(dim, human_df_represent_cls, Netphos_df_represent_pho)
```

## Citation

If our work has contributed to your research, we would greatly appreciate it if you could cite our work as follows. Please note that while this citation related to the article has been accepted for publication, it has not yet been formally published. We are pre-releasing the citation in accordance with the journal's policy, and this page will be updated once the article is officially online. Thank you for your understanding and support.

Zeyu Luo, et al. Interpretable Feature Extraction and Dimensionality Reduction in ESM2 for Protein Localization Prediction. Briefings in Bioinformatics. https://doi.org/10.1093/bib/bbad534.

If you are using the ESM-2 model in your project or research,  please refer to original work completed by the authors: Lin, Z., et al., Evolutionary-scale prediction of atomic level protein structure with a language model. bioRxiv, 2022: p. 2022.07.20.500902.