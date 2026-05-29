docker run -it --rm \
  --name n8n \
  --user root \
  -p 5678:5678 \
  -e NODES_EXCLUDE="[]" \
  -e N8N_USER_FOLDER=/home/node \
  -e N8N_RESTRICT_FILE_ACCESS_TO=/data \
  -v n8n_data:/home/node/.n8n \
  -v /Users/user/git/n8n_project/incoming_docs:/data/incoming_docs \
  -v /Users/user/git/n8n_project/scripts:/scripts:ro \
  -v /Users/user/git/n8n_project/extracted_images:/data/extracted_images \
  -v /Users/user/git/n8n_project/output_docs:/data/output_docs:rw \
  n8n-python

