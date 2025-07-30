import requests
import pandas as pd
from bs4 import BeautifulSoup

class Extract:
  

  # extract data from html table
  """
    Extraction from html needs multiple steps because it is not directly handled by pandas
    extract data from html by finding the table, extracting rows and columns,
  """
  
  @staticmethod
  def from_html_table(url):
    
    try:
      response = requests.get(url)
      response.raise_for_status()
      soup = BeautifulSoup(response.content, "html.parser")
      table = soup.find("table")
      
      if not table:
        raise ValueError("No table found at the provided URL.")
      
      
      rows = table.find_all("tr")
      data = []
      
      for row in rows:
        cols = row.find_all("td")
        data.append([col.text.strip() for col in cols]) #appends table data in cols after stripping the whitespace
        

      df = pd.DataFrame(data)
      return df
    
    except Exception as e:
      raise RuntimeError(f"Extraction failed: {e}")
    