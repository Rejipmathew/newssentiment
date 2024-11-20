import streamlit as st
import feedparser
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

# Function to fetch news from RSS feed
def fetch_news(feed_url):
    news_feed = feedparser.parse(feed_url)
    news_items = [
        {"title": entry.title, "link": entry.link}
        for entry in news_feed.entries
    ]
    return news_items

# Function to perform sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, polarity

# Generate a word cloud
def generate_wordcloud(text_list):
    combined_text = " ".join(text_list)
    wordcloud = WordCloud(width=300, height=300, background_color="white").generate(combined_text)
    return wordcloud

# Set app background
def set_background(image_path):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url({image_path});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit App
st.title("News Search & Sentiment Analysis")

# Add background image
set_background("https://www.example.com/background-image.jpg")  # Replace with your image URL or local path

st.sidebar.header("News Source Selection")
rss_feeds = {
    "NPR: Business News": "http://www.npr.org/rss/rss.php?id=1014",
    "NYT: Business News": "http://www.nytimes.com/services/xml/rss/nyt/WorldBusiness.xml",
    "NYT: Politics": "http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "NYT: World Business": "http://www.nytimes.com/services/xml/rss/nyt/WorldBusiness.xml",
    "AXIOS News": "http://www.axios.com/feeds/feed.rss",
    "The Atlantic Newsfeed": "http://www.theatlantic.com/feed/all",
    "CNN: Latest News": "http://rss.cnn.com/rss/edition.rss",
    "CNBC: Latest News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Investing News": "https://www.investing.com/rss/news.rss",
}

selected_feed_name = st.sidebar.radio("Select an RSS feed", list(rss_feeds.keys()))
news_url = rss_feeds[selected_feed_name]

# Fetch news and prepare autocomplete dictionary
news_data = fetch_news(news_url)
autocomplete_dict = [news["title"] for news in news_data]

st.sidebar.subheader("Search News")
search_query = st.sidebar.text_input("Enter topic or keyword", "")

# Autocomplete feature
st.sidebar.text("Autocomplete Suggestions:")
suggestions = [word for word in autocomplete_dict if search_query.lower() in word.lower()]
st.sidebar.write(suggestions[:5])  # Display top 5 suggestions

# Word cloud and Sentiment Analysis Table
if news_data:
    # Generate Word Cloud
    titles = [news["title"] for news in news_data]
    wordcloud = generate_wordcloud(titles)

    # Display Word Cloud in the Sidebar
    st.sidebar.subheader("Word Cloud")
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.sidebar.pyplot(fig)

    # Sentiment Analysis Table
    sentiment_table = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for news in news_data:
        sentiment, polarity = analyze_sentiment(news["title"])
        sentiment_table.append({
            "Title": news["title"],
            "Sentiment": sentiment,
            "Polarity": round(polarity, 2),
            "Link": news["link"]
        })
        sentiment_counts[sentiment] += 1

    # Display Sentiment Counts in Sidebar
    st.sidebar.subheader("Sentiment Summary")
    sentiment_df = pd.DataFrame(
        {"Sentiment": ["Positive", "Negative", "Neutral"], 
         "Count": [sentiment_counts["Positive"], sentiment_counts["Negative"], sentiment_counts["Neutral"]]}
    )
    st.sidebar.table(sentiment_df)

    # Filter news based on user search
    if search_query:
        st.write(f"Results for: **{search_query}**")
        filtered_table = [row for row in sentiment_table if search_query.lower() in row["Title"].lower()]
        filtered_df = pd.DataFrame(filtered_table)
    else:
        st.write("All News Articles:")
        filtered_df = pd.DataFrame(sentiment_table)

    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            st.subheader(row["Title"])
            st.markdown(f"[Read More]({row['Link']})")
            st.write(f"**Sentiment:** {row['Sentiment']} ({row['Polarity']:.2f})")
            st.write("---")

        st.write("### Sentiment Analysis Table")
        st.dataframe(filtered_df.drop(columns=["Link"]))
    else:
        st.write("No news articles found.")
else:
    st.write("No news data available.")
