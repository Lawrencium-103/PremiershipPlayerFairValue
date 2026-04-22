import streamlit as st
import traceback
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

st.set_page_config(page_title="Live Player Intel", layout="wide", page_icon="🔍")

st.title("🔍 Live Player Intel & Sentiment Analysis")
st.markdown("Instantly scrape the web for the latest news to compute a **Hype Factor** index before bidding.")

if DDGS is None or TextBlob is None:
    st.error("Missing `ddgs` or `textblob` dependencies.")
    st.stop()

# Ensure session state for hype factor is initialized
if 'player_hype_metrics' not in st.session_state:
    st.session_state['player_hype_metrics'] = {}

player_name = st.text_input("Enter Player Name", "Jude Bellingham", help="Type the player name to fetch live context.")
query_type = st.selectbox("Intelligence Type", ["Recent News & Rumors", "Injury Status", "Recent Performance Stats"])

if st.button("Fetch Live Intel & Analyze Sentiment", type="primary"):
    with st.spinner("Scraping live data via DuckDuckGo..."):
        try:
            ddgs = DDGS()
            if query_type == "Recent News & Rumors":
                search_query = f"{player_name} transfer news rumor"
            elif query_type == "Injury Status":
                search_query = f"{player_name} injury update news latest"
            else:
                search_query = f"{player_name} stats goals assists last match"
                
            results = list(ddgs.text(search_query, max_results=5))
                
            if not results:
                st.warning("No results found. DuckDuckGo may be rate-limiting or your query is too narrow.")
            else:
                st.success(f"Retrieved top {len(results)} search fragments.")
                
                # Perform Sentiment Analysis
                sentiments = []
                for r in results:
                    content = r.get('body', '') + " " + r.get('title', '')
                    blob = TextBlob(content)
                    sentiments.append(blob.sentiment.polarity) # ranges from -1 to 1
                
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
                
                # Scale from -1 to 1 into -10% to +10% Hype Premium
                # e.g., max positive hype = 10% premium. max negative = 10% discount.
                hype_premium_bps = avg_sentiment * 10.0
                
                # Save to session state so Page 1 can consume it
                st.session_state['player_hype_metrics'][player_name.lower()] = {
                    'sentiment_score': avg_sentiment,
                    'hype_premium_percent': hype_premium_bps
                }
                
                # Display Sentiment Dashboard
                st.markdown("---")
                st.subheader("🧠 NLP Sentiment Analysis")
                c1, c2 = st.columns(2)
                c1.metric("Average Polarity Score (Range: -1 to 1)", f"{avg_sentiment:.2f}")
                
                if hype_premium_bps > 0:
                    c2.metric("Computed Hype Premium", f"+{hype_premium_bps:.1f}%", f"Increases Hard Cap")
                else:
                    c2.metric("Computed Form Discount", f"{hype_premium_bps:.1f}%", f"Decreases Hard Cap", delta_color="inverse")
                    
                st.info("💡 *The Hype Premium is globally saved and will automatically adjust the Hard Cap on the **Transfer Estimator** page.*")
                
                st.markdown("---")
                st.subheader("Raw Data Snippets")
                for i, r in enumerate(results):
                    with st.container():
                        blob_local = TextBlob(r.get('body', '')).sentiment.polarity
                        color = "green" if blob_local > 0.1 else ("red" if blob_local < -0.1 else "gray")
                        
                        st.markdown(f"#### [{r.get('title', 'Unknown Title')}]({r.get('href', '#')})")
                        st.markdown(f"> *{r.get('body', 'No summary provided.')}*")
                        st.caption(f"Snippet Sentiment: :{color}[{blob_local:.2f}]")
                        st.divider()
                        
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            with st.expander("Show Traceback"):
                st.code(traceback.format_exc())

st.markdown("---")
st.caption("Powered by `ddgs` and `TextBlob` NLP.")
