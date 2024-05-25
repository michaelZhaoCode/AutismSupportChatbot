# AutismCanadaAI

This is a chatbot that efficiently retrieves relevant information from a databse of files using a clustering algorithm to answer questions relating to autism.

Usage:
1. clone this repo locally
2. type 'python -m venv myenv' in cmd
3. 'source venv/bin/activate'
4. 'pip install -r requirements.txt' to install packages
5. you can call the `create_pdfs` to populate your local dir with sample pdfs
6. call `populate_pdfs` to store the files in the db and create a cluster
7. call `chat` to use the chatbot
8. if you want to add more files to the db (automatically recomputes the cluster) you can call `add_pdf`
