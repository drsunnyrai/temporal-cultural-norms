# %%
prompt = """
Social emotions are emotions that depend on one's appraisal or consideration of another person's thoughts, feelings, or actions. For this task, the social emotions of interest are **shame**, **guilt**, **embarrassment**, **pride**, and **hubris**. Below are definitions of these emotions: 
\n\n
* **Shame**: A highly unpleasant self-conscious emotion arising from the sense of there being something dishonorable, immodest, or indecorous in one's own conduct or circumstances. 

* **Guilt**: A self-conscious emotion characterized by a painful appraisal of having done (or thought) something that is wrong and often by a readiness to take action designed to undo or mitigate this wrong. It is distinct from shame, in which there is the additional strong fear of one's deeds being publicly exposed to judgment or ridicule. 

* **Embarrassment**: A self-conscious emotion in which a person feels awkward or flustered in other people's company or because of the attention of others, such as when being observed. 

* **Pride**: is a self-conscious emotion that occurs when a goal has been attained and one's achievement has been recognized and approved by others. It differs from joy and happiness in that these emotions do not require the approval of others to be experienced. 

* **Hubris** is arrogant pride or presumption. Overconfidence is a synonym of hubris.

\n\nTask: For the given movie subtitles spoken by multiple characters, your task is to identify

     \n\n1. if any of the characters is experiencing social emotion, return yes, else no.
     \n2. If yes, who is experiencing a social emotion?
     \n3. If yes, which social emotion? 
     \n4. If yes, infer the gender of the person who experiences social emotion.
     \n5. What is the reason behind experiencing social emotion?

\n\n The answer should be short and in the CSV format given below.
     \n <experience_social_emotion, character, social_emotion, gender, reason>\
     \n\nInput: [2935.572 - 2940.093] And l want to know, how low did you go?
Look at you. You're glowing!
[2940.253 - 2942.413] You ain't got the sense God gave you.
[2942.572 - 2944.133] ANGELA:
All l've got to say is.. .
[2944.293 - 2946.573] ...thank God it was just a little fling...
[2946.733 - 2948.453] ...and you're not seeing him again.
[2948.612 - 2951.573] You should be ashamed
for being so desperate.
[2951.733 - 2955.013] Angela, you need to take
your pregnant behind home right now.
[2955.172 - 2956.613] You could spoil a wet dream.
[2956.773 - 2960.653] For your information, l'm not completely
stupid, nor have l committed any crime.
[2960.813 - 2963.293] All l did was sleep with him.
[2963.452 - 2965.093] Damn!
     \nOutput: yes, Angela, shame, female, for being desperate and sleeping with a man
\n\nInput: [1163.287 - 1166.461] It's not easy. I'm sure
I make it look easy.
[1168.751 - 1171.22] - You guys better not be inhaling.
- Hi.
[1171.295 - 1176.426] Lelaina, Vickie was just
promoted to manager of The Gap.
[1176.634 - 1179.763] - Shut up.
- It's not even a big deal.
[1180.096 - 1183.942] The old manager tried to kill herself
by eating a whole pot of poinsettias.
[1184.475 - 1188.946] - Still, I'm so proud of you!
- I'll be making $400 a week.
[1189.355 - 1191.904] We're never gonna have
rent problems again.
[1192.441 - 1194.443] Troy, aren't you excited?
[1194.694 - 1196.617] I'm bursting with fruit flavor.
[1196.696 - 1198.744] Guys, I just thought of something.
[1198.823 - 1204.33] I'm manager of The Gap. I'm
responsible for all those T-shirts
\nOutput: yes, Vickie, female, pride, for being promoted to manager and earning more money.

"""

# %%
import openai
import pandas as pd
import os

# %%
# TODO: replace it with your own openai api key
api_key = ""
gpt_model = "gpt-4o"

# TODO: Change the output_file_name 
output_folder_path = "gpt_data/"
output_file_name = output_folder_path + f"entire_japanese-subset_{gpt_model}.csv"

# TODO: Uncomment if you want to validate api key before using
# def check_openai_api_key(api_key):
#     client = openai.OpenAI(api_key=api_key)
#     try:
#         client.models.list()
#     except openai.AuthenticationError:
#         return False
#     else:
#         return True

# if check_openai_api_key(api_key):
#     print("Valid OpenAI API key.")
# else:
#     print("Invalid OpenAI API key.")

# %%
def compute_gpt(dialogue, temp=0.5):
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": dialogue},
            ],
            temperature=temp,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        output = response.choices[0].message.content.strip()
        output_list = [item.strip() for item in output.split(",", maxsplit=4)]

        if len(output_list) == 5:
            return output_list
        else:
            print(f"Malformed GPT output: {output}")
            return [None] * 5  # Return placeholders if the format is incorrect
    except Exception as e:
        print(f"Error during GPT processing: {e}")
        return [None] * 5

# %%
# Load data
# TODO: Change the path based on corresponding file name
input_folder_path = "parsed_input/"
path = input_folder_path + "japanese-subset_matching.csv"
overlaps_df = pd.read_csv(path)

# TODO: uncomment if you want to run on a subset first
# overlaps_df = overlaps_df.sample(n=3, random_state=42)

# Initialize new columns if they don’t exist
new_columns = ["experience_social_emotion", "character", "social_emotion", "gender", "reason"]
for col in new_columns:
    if col not in overlaps_df.columns:
        overlaps_df[col] = None

# Check if output file exists
if os.path.exists(output_file_name):
    # If it exists, load it and continue from where it left off
    saved_df = pd.read_csv(output_file_name)
    overlaps_df.update(saved_df)  # Update the DataFrame with saved progress

# %%
try:
    for index, row in overlaps_df.iterrows():
        if pd.notnull(row["experience_social_emotion"]):
            print(f"Skipping already processed index: {index}")
            continue

        # Process the row and update DataFrame
        result = compute_gpt(row["context"], temp=0.5)
        print(f"Processing row at index: {index}")
        overlaps_df.loc[index, new_columns] = result

        # Save the updated DataFrame after processing each row
        overlaps_df.to_csv(output_file_name, index=False)
except KeyboardInterrupt:
    print("Process interrupted! Partial results saved.")
except Exception as e:
    print(f"An error occurred: {e}")

# %%
print("Processing complete!")
