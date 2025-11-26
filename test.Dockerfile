FROM mariopique/imarina-load:latest

# Copy test requirements and install them
COPY ./requirements-dev.txt /app
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy test path initialization and test source code
COPY ./pytest.ini /app
COPY ./tests /app

# Run all tests verbose and stop on the first test failed
ENTRYPOINT ["pytest", "-v", "-s", "-x"]