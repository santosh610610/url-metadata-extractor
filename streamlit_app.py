import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import re

st.set_page_config(
    page_title="URL Metadata Extractor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
    }
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1f35 0%, #101420 100%);
    }

    .sidebar .sidebar-content {
    background-image: linear-gradient(#2e7bcf,#2e7bcf);
    color: white;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(107, 115, 255, 0.4);
    }
    .metadata-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1rem;
    }
    .keyword-tag {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for recent searches
if 'recent_searches' not in st.session_state:
    st.session_state.recent_searches = []

def get_domain(url):
    """Extract domain from URL."""
    try:
        parsed_uri = urlparse(url)
        return parsed_uri.netloc
    except:
        return url

def extract_metadata(url):
    """Extract metadata from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else ''
        
        # Extract description
        description = ''
        desc_meta = soup.find('meta', attrs={'name': ['description', 'Description']})
        if desc_meta:
            description = desc_meta.get('content', '')
        
        # Extract keywords
        keywords = []
        keywords_meta = soup.find('meta', attrs={'name': ['keywords', 'Keywords']})
        if keywords_meta:
            keywords = [k.strip() for k in keywords_meta.get('content', '').split(',') if k.strip()]
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if not src.startswith(('http://', 'https://')):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
                    src = base_url + src
                else:
                    src = url.rstrip('/') + '/' + src
            if src not in images:
                images.append(src)
        
        return {
            'title': title,
            'description': description,
            'keywords': keywords,
            'images': images[:10],  # Limit to 10 images
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Sidebar with recent searches
st.sidebar.title("Recent Searches")

# Main content
st.title("🔍 URL Metadata Extractor")

# URL input
url = st.text_input("Enter URL to analyze:", placeholder="https://example.com")

if st.button("Extract Metadata"):
    if url:
        with st.spinner("Extracting metadata..."):
            metadata = extract_metadata(url)
            
            # Add to recent searches
            search_entry = {
                'url': url,
                'domain': get_domain(url),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if search_entry not in st.session_state.recent_searches:
                st.session_state.recent_searches.insert(0, search_entry)
                if len(st.session_state.recent_searches) > 10:
                    st.session_state.recent_searches.pop()
            
            if 'error' in metadata:
                st.error(f"Error: {metadata['error']}")
            else:
                # Display metadata in a card
                st.markdown('<div class="metadata-card">', unsafe_allow_html=True)
                
                # Title
                st.subheader("Title")
                st.write(metadata['title'])
                
                # Description
                st.subheader("Description")
                st.write(metadata['description'])
                
                # Keywords
                if metadata['keywords']:
                    st.subheader("Keywords")
                    keywords_html = ' '.join([f'<span class="keyword-tag">{k}</span>' for k in metadata['keywords']])
                    st.markdown(keywords_html, unsafe_allow_html=True)
                
                # Images
                if metadata['images']:
                    st.subheader("Images")
                    cols = st.columns(3)
                    for idx, img_url in enumerate(metadata['images']):
                        try:
                            cols[idx % 3].image(img_url, use_column_width=True)
                        except:
                            pass
                
                st.markdown('</div>', unsafe_allow_html=True)

# Display recent searches in sidebar
for search in st.session_state.recent_searches:
    with st.sidebar.container():
        st.markdown(f"""
        <div style="
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
        ">
            <div style="font-weight: 500; color: white;">{search['domain']}</div>
            <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.6);">{search['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)
