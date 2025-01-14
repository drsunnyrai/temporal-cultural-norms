# %%
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import os
for dirname, _, filenames in os.walk('input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# %%
input_folder_path = "input/hollywood/"
# TODO: get these meta and subtitles data from Kaggle
MOVIES_META_PATH = input_folder_path + "movies_meta.csv"
MOVIES_SUB_PATH = input_folder_path + "movies_subtitles.csv"

# %%
meta_df = pd.read_csv(MOVIES_META_PATH)
meta_df.shape[0]

# %%
meta_df = meta_df.drop_duplicates()

# %%
movies_df = pd.read_csv(MOVIES_SUB_PATH)
movies_df = movies_df.drop_duplicates()

# %%
movies_df.shape[0]

# %%
meta_df['spoken_languages']

# %%
import ast

english_rows = meta_df[meta_df['spoken_languages'].apply(
    lambda x: any(d['name'] == 'English' for d in ast.literal_eval(x)) if isinstance(x, str) else 
              any(d['name'] == 'English' for d in x) if isinstance(x, list) else False
)].reset_index(drop=True)

# %%
movies_df = movies_df.drop_duplicates()

# Merge english_rows with movies_df on 'movie_id'
merged_df = pd.merge(english_rows, movies_df, on='imdb_id', how='inner')

print("Merged DataFrame with only rows containing 'English' and matching movie_ids:")
print(merged_df)

# %%
result_df = merged_df[['imdb_id', 'original_title', 'release_date','genres','start_time', 'end_time','text']]

# %%
result_df.shape[0]

# %%
result_df['release_date'] = pd.to_datetime(result_df['release_date'], errors='coerce')
result_df['decade'] = (result_df['release_date'].dt.year // 10) * 10
result_df.head()

# %%
result_df.shape[0]

# %%
duplicates = result_df[result_df.duplicated()]
# %%
result_df = result_df.dropna(subset=['release_date'])


# %%
result_df.shape[0]

# %%
def load_and_merge_lexicons(file_path_1, file_path_2):
    df1 = pd.read_csv(file_path_1)
    df2 = pd.read_csv(file_path_2)
    
    combined_df = pd.concat([df1[['word']], df2[['word']]]).drop_duplicates().reset_index(drop=True)
    return combined_df

# change to this list
keywords = ['shame', 'shamed', 'shameful', 'ashamed', 'proud', 'prouder', 'proudly', 'pride']
print("List of unique keywords:", keywords)

# %%
shame_df = result_df.copy()

# %%
import re
import pandas as pd

def extract_shame_context(df, keywords, num_lines=5):
    contexts_with_keywords = []
    contexts_without_keywords = []
    added_instances = set()
    movie_id_map = {}
    next_movie_id = 1
    subtitle_id = 1
    last_processed_line = -1
    i = 0

    while i < len(df):
        row = df.iloc[i]
        text = str(row['text']) if pd.notna(row['text']) else ""
        matched_keywords = []
        movie_name = row['original_title']

        # Assign unique movie_id if not already assigned
        if movie_name not in movie_id_map:
            movie_id_map[movie_name] = next_movie_id
            next_movie_id += 1
        movie_id = movie_id_map[movie_name]

        release_year = row['release_date']
        decade = row['decade']

        # Check for keywords in the current line
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                matched_keywords.append(keyword)

        if matched_keywords and i > last_processed_line: 
            # Found keywords, capture context around it
            start = max(i - num_lines, 0)
            end = min(i + num_lines + 1, len(df))
            context_df = df.iloc[start:end]
            
            context = '\n'.join(
                f"[{row['start_time']} - {row['end_time']}] {row['text']}"
                for _, row in context_df.iterrows()
            )

            if context not in added_instances:
                contexts_with_keywords.append({
                    'movie_id': movie_id,
                    'subtitle_id': subtitle_id,
                    'movie_name': movie_name,
                    'release_year': release_year,
                    'decade': decade,
                    'context': context,
                    'lexicon_word_list': matched_keywords  # Add matched keywords here
                })
                added_instances.add(context)
                subtitle_id += 1
            last_processed_line = end - 1
            i = last_processed_line + 1
        elif not matched_keywords and i > last_processed_line:
            # Capture context without keywords
            start = max(i - num_lines, 0)
            end = min(i + num_lines + 1, len(df))
            context_df = df.iloc[start:end]
            
            context = '\n'.join(
                f"[{row['start_time']} - {row['end_time']}] {row['text']}"
                for _, row in context_df.iterrows()
            )

            if context not in added_instances:
                contexts_without_keywords.append({
                    'movie_id': movie_id,
                    'subtitle_id': subtitle_id,
                    'movie_name': movie_name,
                    'release_year': release_year,
                    'decade': decade,
                    'context': context,
                    'lexicon_word_list': []  # Empty list when no keywords are matched
                })
                added_instances.add(context)
                subtitle_id += 1
        #     last_processed_line = end - 1
        #     i = last_processed_line + 1
        # else:
            i += 1
        print(f"done with row {i}!")


    return contexts_with_keywords, contexts_without_keywords
    
contexts_with_keywords, contexts_without_keywords = extract_shame_context(result_df, keywords)

df_with_keywords = pd.DataFrame(contexts_with_keywords)
df_without_keywords = pd.DataFrame(contexts_without_keywords)

# TODO: edit output_file_path as needed
output_folder_path = "../parsed_input/"
df_with_keywords.to_csv('matching_hollywood.csv', index=False, escapechar='\\')
df_without_keywords.to_csv('random_hollywood.csv', index=False, escapechar='\\')

print("done!")
