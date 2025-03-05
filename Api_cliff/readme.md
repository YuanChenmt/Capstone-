1.create VE

python -m venv venv
source venv/bin/activate

1.1 If run localy
	python app.py
	http:// ...(on your browser)


2. install reguired packages
pip install openai gradio pandas




3.Running through docker

cd to docker directory

- terminal:

- docker build -t openapi-project:latest .
-docker run --env-file apikey.env -p 7860:7860 openapi-project:latest

(Try conversation on chatbot:  "Please load the CSV from sample.csv")


