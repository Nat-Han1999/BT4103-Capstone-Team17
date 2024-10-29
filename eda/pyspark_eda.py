#!/usr/bin/env python
# coding: utf-8

# In[3]:


from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, countDistinct
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from pyspark.sql import functions as F


# In[61]:


import os
from dotenv import load_dotenv
from mongo_utils import get_database
import json
from bson import json_util
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
import nbconvert


# In[26]:


password = os.getenv("MONGO_DB_PASSWORD")
username = os.getenv("MONGO_DB_USERNAME")
collection = get_database("shrama_vasana_fund", "scraped_data", username, password)
documents = collection.find()
json_documents = json.loads(json_util.dumps(list(documents)))
with open("scraped_data.json", "w") as json_file:
    json.dump(json_documents, json_file, indent=4)


# In[27]:


# PySpark environment variables
os.environ["PYSPARK_PYTHON"] = "python3"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python3"

# Creating a Spark session
spark = SparkSession.builder \
    .master("local") \
    .appName("EDA Conversion") \
    .getOrCreate()

file_path = "scraped_data.json"
df = spark.read.option("multiLine", "true").json(file_path) # JSON structure is nested and spans multiple lines

df.show(5)


# In[28]:


df.printSchema()


# In[29]:


# row count
print(f"Total number of rows in the dataframe: {df.count()}")


# In[30]:


unique_urls_count = df.select("url").distinct().count()
print(f"Number of unique urls scraped: {unique_urls_count}")

unique_titles_count = df.select("title").distinct().count()
print(f"Number of unique titles scraped: {unique_titles_count}")

unique_images_count = df.select(F.explode("images").alias("image")).distinct().count()
print(f"Number of unique images scraped: {unique_images_count}")

unique_pdfs_count = df.select(F.explode("pdf_links").alias("pdf_link")).distinct().count()
print(f"Number of unique pdfs scraped: {unique_pdfs_count}")


# In[31]:


df_with_word_counts = df.withColumn("word_count", F.size(F.split(F.col("texts"), " ")))
total_word_count = df_with_word_counts.agg(F.sum("word_count")).first()[0]

print(f"Total word count of webpage texts: {total_word_count}")


# In[32]:


average_word_count = df_with_word_counts.agg(F.avg("word_count")).first()[0]

print(f"Average word count per webpage: {average_word_count:.2f}")


# In[33]:


texts = df.select("texts").rdd.flatMap(lambda x: x).collect() # list of strings


# In[34]:


def plot_word_cloud(texts):
    combined_text = ' '.join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Turn off the axis
    plt.show()


# In[35]:


# Plot word cloud for all webpage texts
plot_word_cloud(texts)


# In[36]:


pdf_texts = df.select("pdf_extracted").rdd.flatMap(lambda x: x).collect()
df_with_pdf_word_counts = df.withColumn("pdf_word_count", F.size(F.split(F.col("pdf_extracted"), " ")))
total_pdf_word_count = df_with_pdf_word_counts.agg(F.sum("pdf_word_count")).first()[0]
print(f"Total word count of all pdfs: {total_pdf_word_count}")
average_pdf_word_count = df_with_pdf_word_counts.agg(F.avg("pdf_word_count")).first()[0]
print(f"Average word count per pdf: {average_pdf_word_count:.2f}")


# In[37]:


# Plot word cloud for pdf texts
plot_word_cloud(pdf_texts)


# In[38]:


image_texts = df.select("image_extracted").rdd.flatMap(lambda x: x).collect()
df_with_image_word_counts = df.withColumn("image_word_count", F.size(F.split(F.col("image_extracted"), " ")))
total_image_word_count = df_with_image_word_counts.agg(F.sum("image_word_count")).first()[0]
print(f"Total word count of all images: {total_image_word_count}")
average_image_word_count = df_with_image_word_counts.agg(F.avg("image_word_count")).first()[0]
print(f"Average word count per image {average_image_word_count:.2f}")


# In[39]:


def get_top_words(text_list, num_words):
  CV = CountVectorizer(stop_words='english') 
  word_count = CV.fit_transform(text_list)

  word_sum = word_count.sum(axis=0)

  frequency = []
  for word, index in CV.vocabulary_.items():
    frequency.append((word, word_sum[0, index]))

  frequency = sorted(frequency, key=lambda x: x[1], reverse=True)[:num_words]
  return frequency


# In[40]:


def top_words_chart(texts, title): 
    texts = get_top_words(texts, 10)
    words = [] 
    freqs = []
    for text, freq in texts: 
        words.append(text)
        freqs.append(freq)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=freqs, y=words)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(title)
    plt.show()


# In[41]:


# Top 10 most frequently used texts
top_words_chart(texts, 'Top 10 Most Frequently Used Texts')


# In[42]:


# Top 10 most frequently used pdf texts
top_words_chart(pdf_texts, 'Top 10 Most Frequently Used PDF Texts')


# In[43]:


# Top 10 most frequently used image texts
top_words_chart(image_texts, 'Top 10 Most Frequently Used Image Texts')


# In[44]:


# Bi-grams: Identify common word pairs
def n_grams(text_list, n): 
    n_grams = []
    CV = CountVectorizer(ngram_range=(n, n), stop_words='english')
    ngrams = CV.fit_transform(texts)
    ngram_list = CV.get_feature_names_out()
    ngram_frequencies = ngrams.toarray().sum(axis=0)
    ngram_freq = sorted(list(zip(ngram_list, ngram_frequencies)), key=lambda x: x[1], reverse=True)
    for ngram, freq in ngram_freq[:10]:
        n_grams.append((ngram, freq))
    return n_grams


# In[45]:


def n_grams_chart(text_list, n, title):
    texts = n_grams(text_list, n)
    words = [] 
    freqs = []
    for text, freq in texts: 
        words.append(text)
        freqs.append(freq)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=freqs, y=words)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(title)
    plt.show()


# In[46]:


# Top 10 Frequently Used Word Pairs For Texts
n_grams_chart(texts, 2, "Top 10 Bi-grams for texts")


# In[47]:


# Top 10 Frequently Used Word Pairs For PDF Texts
n_grams_chart(pdf_texts, 2, "Top 10 Bi-grams for PDF Texts")


# In[48]:


# Top 10 Frequently Used Word Pairs For Image Texts
n_grams_chart(image_texts, 2, "Top 10 Bi-grams for Image Texts")


# In[62]:


def notebook_to_html(notebook_path):
    # Convert notebook to HTML
    html_exporter = nbconvert.HTMLExporter()
    html_exporter.exclude_input = True  
    body, _ = html_exporter.from_filename(notebook_path)

    # Save the HTML file
    html_path = notebook_path.replace(".ipynb", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"HTML file saved at {html_path}")

notebook_to_html("pyspark_eda.ipynb")

