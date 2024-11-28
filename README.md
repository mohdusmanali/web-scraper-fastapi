Web Scraper FastAPI Application
===============================

This project is a FastAPI application that scrapes dynamic websites to extract person-specific information such as:

*   Name
    
*   Contact Information
    
*   Images
    
*   Occupation
    
*   Family Details
    
*   Political Party Affiliation
    

The application can crawl through web pages starting from a given URL and return the extracted information in a structured JSON format.

Table of Contents
-----------------

*   [Features](https://stackedit.io/app#features)
    
*   [Requirements](https://stackedit.io/app#requirements)
    
*   [Installation](https://stackedit.io/app#installation)
    
*   [Usage](https://stackedit.io/app#usage)
    
    *   [Running the Application](https://stackedit.io/app#running-the-application)
        
    *   [API Endpoint](https://stackedit.io/app#api-endpoint)
        
    *   [Example Request](https://stackedit.io/app#example-request)
        
    *   [Example Response](https://stackedit.io/app#example-response)
        
*   [Configuration](https://stackedit.io/app#configuration)
    
*   [Limitations and Considerations](https://stackedit.io/app#limitations-and-considerations)
    
*   [License](https://stackedit.io/app#license)
    

Features
--------

*   **Dynamic Web Scraping**: Uses Playwright to render JavaScript and scrape dynamic content.
    
*   **Recursive Crawling**: Crawls linked pages within the same domain up to a specified depth.
    
*   **Data Extraction**: Utilizes spaCy for natural language processing to extract person-specific information.
    
*   **JSON Output**: Returns the extracted data as an array of person objects in JSON format.
    
*   **Configurable Depth**: Allows setting the maximum depth of crawling to control the scope.
    

Requirements
------------

*   Python 3.7 or higher
    
*   The following Python packages:
    
    *   fastapi
        
    *   uvicorn
        
    *   playwright
        
    *   beautifulsoup4
        
    *   spacy
        
    *   pydantic
        
*   spaCy language model:
    
    *   en\_core\_web\_sm
        

Installation
------------

1.  `git clone https://github.com/yourusername/web-scraper-fastapi.git && cd web-scraper-fastapi`
    
2.  `python -m venv venv`
    
3.  **Activate the Virtual Environment**
    
    *   On Windows: `venv\\Scripts\\activate`
        
    *   On Unix or MacOS: `source venv/bin/activate`
              
5.  **Install Playwright Browsers `python -m playwright install`
    
6.  **Download spacy Language Model `python -m spacy download en\_core\_web\_sm`
    

Usage
-----

### Running the Application

Start the FastAPI application using Uvicorn: `uvicorn main:app --reload --workers 1`

*   The --reload flag enables auto-reloading on code changes.
    
*   The --workers 1 ensures that only one process is used, which is important for resource management in this context.
    

### API Endpoint

*   **Endpoint**: /scrape
    
*   **Method**: POST
    
*   **Content-Type**: application/json
    
*   **Request Body Parameters**:
    
    *   url (string): The starting URL for the scraper.
        
    *   max\_depth (integer, optional): Maximum depth for recursive crawling. Default is 2.
        

### Example Request

#### Using cURL:

`curl -X POST "http://localhost:8000/scrape" \\ -H "Content-Type: application/json" \\ -d '{ "url": "https://embassyofalgeria.uk/the-ambassador/", "max\_depth": 2 }'`

#### Using HTTPie:

`http POST http://localhost:8000/scrape url="https://embassyofalgeria.uk/the-ambassador/" max\_depth:=2`

### Example Response

`[ { "name": "John Doe", "contact-information": "john.doe@example.com", "image": "https://example.com/images/john_doe.jpg", "family-detail": "John is married to Jane Doe.", "political_party_affiliation": "Member of the Example Party" }, { "name": "Jane Smith", "contact-information": "+1 555 123 4567", "image": "https://example.com/images/jane_smith.jpg", "family-detail": null, "political_party_affiliation": null } ]`

**Note**: The actual response will vary depending on the content of the website being scraped.

Configuration
-------------

### Modifying Crawling Depth

*   The max\_depth parameter controls how deep the crawler will go when following links.
    
*   Increase or decrease this value based on your requirements.
    

### Adjusting Timeouts

*   Modify the timeout parameter in page.goto(url, timeout=60000) to adjust how long the scraper waits for a page to load.
    
*   The timeout in future.result(timeout=600) controls how long the application waits for the scraping process to complete.
    

Limitations and Considerations
------------------------------

### Technical Limitations

*   **Cloudflare and Anti-Bot Measures**: Websites protected by Cloudflare or similar services may block scraping attempts. Bypassing such protections is not recommended and may be illegal.
    
*   **Data Accuracy**: The heuristic methods used for data extraction may not always accurately associate information with the correct person.
    
*   **Performance**: The application may be slow for large websites or higher max\_depth values due to the recursive crawling and data processing.
