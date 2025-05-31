FROM python:3.10-slim

RUN pip install \
    dagster \
    dagster-postgres \
    dagster-docker \
    confluent-kafka \
    python-dotenv \
    requests \
    hdfs

# Add code location code
WORKDIR /opt/dagster/app
COPY pipeline/src /opt/dagster/app/src

# Run dagster code server on port 4000
EXPOSE 4000
# CMD ["sleep", "30000"]
# CMD allows this to be overridden from run launchers or executors to execute runs and steps
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-m", "src.definitions"]