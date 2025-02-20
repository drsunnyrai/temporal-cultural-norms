import pandas as pd
import os
import re
import matplotlib.pyplot as plt

def parse_file_to_dataframe(file_path):
    data = {'token': [], 'm_desc': []}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            key_value_pairs = line.split('|')
            
            token = None
            m_desc = None
            syn_label = None
            
            for pair in key_value_pairs:
                key, value = pair.split('=')
                key = key.strip()
                value = value.strip()
                
                if key == 'token':
                    token = value
                elif key == 'm_desc':
                    m_desc = value
                elif key == 'syn_label':
                    syn_label = value
            
            if token and m_desc and syn_label == 'O':
                data['token'].append(token)
                data['m_desc'].append(m_desc)
    
    df = pd.DataFrame(data)
    return df

def load_and_merge_lexicons(file_path_1, file_path_2):
    df1 = pd.read_csv(file_path_1)
    df2 = pd.read_csv(file_path_2)
    
    combined_df = pd.concat([df1[['word']], df2[['word']]]).drop_duplicates().reset_index(drop=True)
    return combined_df

# Change keywords as needed
keywords = ['shame', 'shamed', 'shameful', 'ashamed', 'proud', 'prouder', 'proudly', 'pride']
print("List of unique keywords:", keywords)

def read(file_path):
    l = []
    try:
        with open(file_path, "r") as f:
            l = f.readlines()
    except:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                l = f.readlines()
        except:
            try:
                with open(file_path, "r", encoding="ascii") as f:
                    l = f.readlines()
            except:
                try:
                    with open(file_path, "r", encoding="SHIFT_JIS") as f:
                        l = f.readlines()
                except:
                    try:
                        with open(file_path, "r", encoding="windows-1253") as f:
                            l = f.readlines()
                    except:
                        try:
                            with open(file_path, "r", encoding="UTF-8-SIG") as f:
                                l = f.readlines()
                        except:
                            try:
                                with open(file_path, "r", encoding="TIS-620") as f:
                                    l = f.readlines()
                            except:
                                q = 0
    return l

def get_filenames(dir):
    filenames = []
    for filename in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, filename)):
            filenames.append(filename)
    return filenames

# USER: Specify input and output directory paths and output file name
input_dir = "../input/Korea"
output_dir = "../parsed_input"
output_file_name = "korea"

filenames = get_filenames(input_dir)

# Extracting the filenames by years and reading the content
movies_data = []
for movie_id, filename in enumerate(filenames, start=1):
    clean_filename = filename.replace(".srt", "").strip()

    release_year = clean_filename.split("_")[0].strip()

    if not release_year.isdigit() or not (1900 <= int(release_year) <= 2024):
        continue

    movie_name = clean_filename.split("_", 1)[1].strip()

    file_dir = os.path.join(input_dir, filename)
    subtitle_content = read(file_dir)

    movies_data.append([movie_name, release_year, subtitle_content])

movies_df = pd.DataFrame(movies_data, columns=['movie_name', 'release_year', 'subtitle_content'])

movies_df['release_year'] = movies_df['release_year'].astype(int)

def get_decade(year):
    return "%ss" % ((year // 10) * 10)

movies_df['decade'] = movies_df['release_year'].apply(get_decade)

decade_counts = movies_df['decade'].value_counts().sort_index()

def parse_subtitles(subtitle_list):
    parsed = []
    current_timestamp = None
    current_text = []

    for line in subtitle_list:
        timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})', line)
        if timestamp_match:
            if current_timestamp and current_text:
                parsed.append("%s: %s" % (current_timestamp, ''.join(current_text).strip()))
            current_timestamp = timestamp_match.group(1)
            current_text = []
        elif line.strip() and not line.strip().isdigit():
            current_text.append(line)
    
    if current_timestamp and current_text:
        parsed.append("%s: %s" % (current_timestamp, ''.join(current_text).strip()))
    
    return parsed

movies_df['subtitle_content'] = movies_df['subtitle_content'].apply(parse_subtitles)

movies_subset_df = movies_df.drop_duplicates(subset=['movie_name', 'release_year']).reset_index(drop=True)
print(f"num of movies {movies_subset_df.shape[0]}")
movie_id_map = {}
next_movie_id = 1

def extract_context(subtitle_list, keywords, num_lines, decade, name):
    global movie_id_map, next_movie_id
    
    contexts = []
    lexicon_words_list = []
    added_instances = set()
    
    if name not in movie_id_map:
        movie_id_map[name] = next_movie_id
        next_movie_id += 1
    movie_id = movie_id_map[name]
    
    subtitle_id = 1 

    # Separate storage for contexts with no keyword matches
    non_matching_data = {
        'context': [],
        'movie_name': [],
        'release_year': [],
        'decade': [],
        'movie_id': [],
        'subtitle_id': []
    }

    last_processed_line = -1
    i = 0
    
    while i < len(subtitle_list):
        line = subtitle_list[i]
        matched_keywords = []

        # Check if any keywords are in the current line
        for keyword in keywords:
            if isinstance(keyword, str):
                pattern = r'\b%s\b' % re.escape(keyword.replace('*', '.*'))
                
                if re.search(pattern, line, re.IGNORECASE):
                    matched_keywords.append(keyword)

        if matched_keywords and i > last_processed_line: 
            # Found keywords in line, so capture context around it
            start = max(i - num_lines, 0)
            end = min(i + num_lines + 1, len(subtitle_list))
            context = '\n'.join(subtitle_list[start:end])

            if context not in added_instances:
                contexts.append({
                    'movie_id': movie_id,
                    'subtitle_id': subtitle_id,
                    'movie_name': movie_name,
                    'release_year': release_year,
                    'decade': decade,
                    'context': context
                })
                lexicon_words_list.append(matched_keywords)
                added_instances.add(context)
                subtitle_id += 1

            last_processed_line = end - 1
            i = last_processed_line + 1
        elif not matched_keywords and i > last_processed_line:
            # Capture lines without any keywords
            start = max(i - num_lines, 0)
            end = min(i + num_lines + 1, len(subtitle_list))
            context = '\n'.join(subtitle_list[start:end])

            if context not in added_instances:
                non_matching_data['context'].append(context)
                non_matching_data['movie_name'].append(name)
                non_matching_data['release_year'].append(release_year)
                non_matching_data['decade'].append(decade)
                non_matching_data['movie_id'].append(movie_id)
                non_matching_data['subtitle_id'].append(subtitle_id)
                added_instances.add(context)
                subtitle_id += 1
            i += 1

    return contexts, lexicon_words_list, non_matching_data

def build_dataframe(movies_df, keywords, num_lines):
    data = {
        'movie_name': [],
        'release_year': [],
        'decade': [],
        'movie_id': [],
        'subtitle_id': [],
        'context': [],
        'lexicon_word_list': []
    }

    all_non_matching_data = {
        'movie_name': [],
        'release_year': [],
        'decade': [],
        'movie_id': [],
        'subtitle_id': [],
        'context': []
    }

    for index, row in movies_df.iterrows():
        subtitle_list = row['subtitle_content']
        movie_name = row['movie_name']
        release_year = row['release_year']
        decade = row['decade']

        contexts, lexicon_words_list, non_matching_data = extract_context(subtitle_list, keywords, num_lines, decade, movie_name)

        # Add matched contexts to main dataframe data
        for context, lexicon_words in zip(contexts, lexicon_words_list):
            data['movie_id'].append(context['movie_id'])
            data['subtitle_id'].append(context['subtitle_id'])
            data['movie_name'].append(movie_name)
            data['release_year'].append(release_year)
            data['decade'].append(decade)
            data['context'].append(context['context'])
            data['lexicon_word_list'].append(lexicon_words)

        # Add non-matching contexts to separate data structure
        all_non_matching_data['movie_id'].extend(non_matching_data['movie_id'])
        all_non_matching_data['subtitle_id'].extend(non_matching_data['subtitle_id'])
        all_non_matching_data['movie_name'].extend(non_matching_data['movie_name'])
        all_non_matching_data['release_year'].extend(non_matching_data['release_year'])
        all_non_matching_data['decade'].extend(non_matching_data['decade'])
        all_non_matching_data['context'].extend(non_matching_data['context'])
        
        # LOGGING: Uncomment if desired
        # print(f"done for index {index}")

    matched_df = pd.DataFrame(data)
    non_matched_df = pd.DataFrame(all_non_matching_data)
    return matched_df, non_matched_df

# Run the extraction and save both DataFrames
num_lines = 5
matched_df, non_matched_df = build_dataframe(movies_subset_df, keywords, num_lines)

# Save the matched and non-matched contexts as separate CSVs
# Specify output file paths
non_matched_df.to_csv(os.path.join(output_dir, f"{output_file_name}_random.csv"), index=False, escapechar='\\')
matched_df.to_csv(os.path.join(output_dir, f"{output_file_name}_matching.csv"), index=False, escapechar='\\')
print("Extraction and saving complete!")
