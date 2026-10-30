# David Bianchi's EZKinetics image, built from moleculemaker/EZKinetics-inferencing and pinned
# by digest. It holds the method's code and trained models in /usr/app/EZKinetics and runs on
# the base image's Python. ESM and ChemBERTa weights are not in it; they download at runtime
# to their default cache under /root/.cache, which the backend mounts on the shared volume.
FROM davidbianchi/ezkinetics:version1.0@sha256:5942fb13be06a09435df6dafbbdb6906e047aa96906a1525a01b6816203fce7c

# Not /code: the backend mounts its own config files under /code/app/cfg in the job container
WORKDIR /opt/job

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wrapper/ wrapper/

ENTRYPOINT ["python", "-m", "wrapper.entrypoint"]
