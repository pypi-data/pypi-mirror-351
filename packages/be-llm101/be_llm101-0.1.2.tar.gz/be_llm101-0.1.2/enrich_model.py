import random
import pandas as pd


# Function to enrich feedback with nuanced emotions
def enrich_feedback(feedback, sentiment):
    enrichments = {
        "Positive": [
            "It's a relief that the IT team responds so quickly, but sometimes the solutions feel like temporary fixes.",
            "The latest update improved efficiency, though it took a while to get used to the new interface.",
            "I appreciate the effort put into security, but the extra authentication steps can be frustrating when in a rush.",
            "The new system runs smoothly most of the time, though occasional slowdowns can be disruptive.",
            "I love how intuitive the dashboard is—finally, something that just works!",
        ],
        "Negative": [
            "The VPN is unreliable, making remote work a headache. I sometimes wonder if it’s worth the trouble.",
            "Training sessions were unhelpful—felt like we were just checking a box rather than actually learning.",
            "Helpdesk responses are polite but rarely solve my actual issue. It’s exhausting to go in circles.",
            "Updates seem to introduce more bugs than they fix, making it frustrating to rely on the system.",
            "I dread using the internal ticketing system; it feels like my requests vanish into a black hole.",
        ],
    }

    # Choose whether to append or replace feedback for variety
    if random.random() > 0.5:
        return feedback + " " + random.choice(enrichments[sentiment])
    else:
        return random.choice(enrichments[sentiment])


# Apply enrichment to the dataset
df = pd.read_excel("./shuffled_df_LLM101.xlsx")
df["Enriched Feedback"] = df.apply(
    lambda row: enrich_feedback(row["Unnamed: 3"], row["Unnamed: 2"]), axis=1
)

# Display a few enriched examples
print(df[["Unnamed: 2", "Unnamed: 3", "Enriched Feedback"]].head())

# Write to output-file
output_df = df[["Unnamed: 2", "Unnamed: 3", "Enriched Feedback"]]
df.to_markdown("output_df.txt")
