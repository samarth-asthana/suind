<h1>Sentinel-2 NDVI Analysis</h1>

<p>This project demonstrates how we can leverage satellite data to monitor and analyze vegetation health, providing valuable insights for agricultural applications.</p>

<h2>Getting Started</h2>

<p>To run and test the application, follow these steps:</p>

<h3>Prerequisites</h3>
<ul>
  <li>Ensure you have Docker installed on your machine.</li>
</ul>

<h3>Build and Run the Docker Container</h3>

<ol>
  <li>
    <p>Build the Docker image:</p>
    <pre><code>docker build -t suind .</code></pre>
  </li>
  <li>
    <p>Run the Docker container:</p>
    <pre><code>docker run --name suind -p 8080:8080 --env-file .env suind</code></pre>
  </li>
</ol>

<h3>Test the API</h3>

<p>Once the Docker container is up and running, you can test the API endpoint <code>/query</code>.</p>

<h3>Example CURL Request</h3>

<p>Use the following CURL command to test the API:</p>

<pre><code>curl --location 'http://127.0.0.1:8080/query' \
--header 'Content-Type: application/json' \
--data '{
    "timestamp": "2024-07-15T00:00:00Z",
    "polygon": {
        "type": "Polygon",
        "coordinates": [
            [
                [12.4924, 41.8902],
                [12.4924, 41.8912],
                [12.4934, 41.8912],
                [12.4934, 41.8902],
                [12.4924, 41.8902]
            ]
        ]
    }
}'</code></pre>

<p>This will send a request to the <code>/query</code> endpoint with a specified timestamp and polygon coordinates. The API will return the mean and standard deviation of the NDVI values for the specified area.</p>
