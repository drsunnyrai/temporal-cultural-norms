# temporal-cultural-norms
This is the code used to scrape subtitle data from OpenSubtitles and parse through subtitle contexts for explicit and random (matching vs. non-matching) mentions of **shame** and **pride**-related keywords. We also included a `.ipynb` file that persforms Agglomerative using SBERT on the processed data to form clusters and social norms.

### Setting up
Make sure to install all necessary python libaries and packages.
Stay in the root folder, and make sure to create the following directories:
- input/
- parsed_input/
- gpt_data/
- processed_data/

### Files
- scrape_subtitles.py
- parser_code/parser.py
- README.md
- gpt.py
- processing.py

#### Input (not included, check details below)
Raw data: If not already configured, make sure to create subdirectory input/ and upload raw data (subtitles data) for each country there.

Parsed data includes the **matching context** results from `parser_code` files.

GPT data includes data from calling GPT-4o on data from parsed data.


#### Output
This includes data from running **Sentence Embeddings (SBERT)** and **Agglomerative Clustering** on the *GPT Data*.
This includes several different files that range from the word embeddings (without duplicates), norm to cluster mappings, and the final results as well (that can be read in the notebook to create visualizations).

Please cross-check with the `.ipynb` notebook: `processing_ipynb` to see what each of the file means. 

### How to run

*Assuming you have access to Box and Venti*
1. Language and libraries. Make sure you have `python3` and all necessary libraries installed.
2. Obtain desired IMDB data from the Box drive, and upload it as a subdirectory named data/
i.e.
```
mkdir temporal-cultural-norms/data
*scp over data*
ls temporal-cultural-norms/data
Australia .csv		France .csv		Japan .csv		Nigeria .csv		United States .csv
Canada .csv		Germany .csv		Kenya .csv		Russia .csv
China .csv		India .csv		Korea .csv		UK .csv
```
3. Generate subtitles data for each country of interest by running 'python3 scrape_subtitles.py'
* Obtain and replace OpenSubtitles API key with yours
* You may need to configure the output directory
4. Parse through raw subtitles data to obtain `matching` vs `random` contexts
* Obtain contexts by running `python3 parser_code/parser.py`
This will output the `matching_{country}.csv` and `random_{random}.csv` files inside `parsed_input/` folder.
3. Call GPT-4o calls on the parsed data
* Obtain and replace the OpenAI key with yours
* Make sure you configure the directory to point to the correct parsed context files
* Run `python3 gpt.py`
4. Run either the python file or notebook file to process, analyze, and perform clustering on your results from part (3) (`processing.ipynb` or `processing.py`)
* Load the python notebook and run each cell. Make sure you configure the files and encoding and duplicate booleans as needed

### Citations
Please leave us a star and cite our paper(s) if you find our work helpful.
```
Citation to add in Github link - @misc{rai2024socialnormscinemacrosscultural,
      title={Social Norms in Cinema: A Cross-Cultural Analysis of Shame, Pride and Prejudice},
      author={Sunny Rai and Khushang Jilesh Zaveri and Shreya Havaldar and Soumna Nema and Lyle Ungar and Sharath Chandra Guntuku},
      year={2024},
      eprint={2402.11333},
      archivePrefix={arXiv},
      primaryClass={cs.CY},
      url={https://arxiv.org/abs/2402.11333},
}
```




