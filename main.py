import streamlit as st
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


base_url = 'https://github.com'
# =====================Topics======================================

def get_topics_page():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)

    if response.status_code != 200:
        raise Exception("Failed to Load Page {}".format(topics_url))

    doc = bs(response.text, 'html.parser')
    return doc

def get_topic_titles(doc):
    selection_class = "f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_title_tags = doc.find_all('p', {'class' : selection_class})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)

    return topic_titles

def get_topic_descs(doc):
    desc_selector = "f5 color-fg-muted mb-0 mt-1"
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_descs = []
    for tag in topic_desc_tags:
        topic_descs.append(tag.text.strip())
    return topic_descs

def get_topic_urls(doc):
    url_selector  ="no-underline flex-1 d-flex flex-column"
    topic_link_tags = doc.find_all('a', {'class': url_selector })
    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])

    return topic_urls

def scrape_topics():
    topics_url = "https://github.com/topics"
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception("Failed to load page {}".format(topics_url))

    doc = bs(response.text, 'html.parser')
    topics_dict = {
        'title' : get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_urls(doc)
    }

    return pd.DataFrame(topics_dict)

# ========================================topic_repos==============================

def get_topic_page(topic_url):
    response = requests.get(topic_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))

    topic_doc = bs(response.text, 'html.parser')
    return topic_doc

def get_topic_repos(topic_doc):
    h3_selection_class = "f3 color-fg-muted text-normal lh-condensed"
    repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class})
    star_tags = topic_doc.find_all('span', 'Counter js-social-count')

    topic_repos_dict = {'username':[],
                        'repo_name':[],
                        'stars':[],
                        'repo_url':[],}

    #get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])

    df = pd.DataFrame(topic_repos_dict)
    
    return df

# the h3 tag will help in getting the name of the sub-topic of a particular topic
def get_repo_info(h3_tag, star_tag):
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = star_tag.text.strip()
    return username, repo_name, stars, repo_url

# Streamlit App
def main():
  
    st.title("GitHub Topics Explorer")

    topics_df = scrape_topics()

    selected_topic = st.selectbox("Select a topic", topics_df['title'])
    selected_topic_url = topics_df[topics_df['title'] == selected_topic]['url'].values[0]

    st.write(f"## {selected_topic}")
    st.write(topics_df[topics_df['title'] == selected_topic]['description'].values[0])

    st.write("### Top Repositories:")
    topic_doc = get_topic_page(selected_topic_url)
    repos_df = get_topic_repos(topic_doc)
    

    # Display a table with clickable links
    table_html = "<table><tr><th>Username</th><th>Repo Name</th><th>Stars</th><th>Link</th></tr>"
    for index, row in repos_df.iterrows():
        table_html += f"<tr><td>{row['username']}</td><td>{row['repo_name']}</td><td>{row['stars']}</td><td><a href='{row['repo_url']}' target='_blank'>Link</a></td></tr>"
    table_html += "</table>"

    st.write(table_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
