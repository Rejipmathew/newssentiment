import streamlit as st
import feedparser
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

# Custom CSS for styling
st.markdown("""
    <style>
        /* Main background and text styling */
        .stApp {
            background-color: lightblue;
            color: darkblue;
        }

        /* Sidebar background styling */
        .css-1d391kg {
            background-color: lightgreen;
            color: darkblue;
        }

        /* Header styling */
        h1, h2, h3 {
            color: darkblue;
        }

        /* Table text color */
        table {
            color: yellow;
        }

        /* Links */
        a {
            color: darkblue;
        }
    </style>
""", unsafe_allow_html=True)

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

# Streamlit App
st.title("News Search & Sentiment Analysis")

# Left Sidebar
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

st.sidebar.subheader("Search News")
search_query = st.sidebar.text_input("Enter topic or keyword", "")

# Layout: Main Content and Right Sidebar
main_content, right_sidebar = st.columns([3, 1])

# Fetch news from selected RSS feed
news_data = fetch_news(news_url)

# Right Sidebar for Sentiment Summary and Word Cloud
with right_sidebar:
    if news_data:
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

        # Display Sentiment Counts
        st.subheader("Sentiment Summary")
        sentiment_df = pd.DataFrame(
            {"Sentiment": ["Positive", "Negative", "Neutral"], 
             "Count": [sentiment_counts["Positive"], sentiment_counts["Negative"], sentiment_counts["Neutral"]]}
        )

        # Apply dark blue text to the table using markdown
        sentiment_html = sentiment_df.to_html(index=False)
        sentiment_html = f"""
        <div style="color: darkblue; font-size: 14px;">
            {sentiment_html}
        </div>
        """
        st.markdown(sentiment_html, unsafe_allow_html=True)

        # Generate Word Cloud
        titles = [news["title"] for news in news_data]
        wordcloud = generate_wordcloud(titles)
        st.subheader("Word Cloud")
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

# Main Content
with main_content:
    if news_data:
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
