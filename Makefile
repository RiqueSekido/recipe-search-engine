.PHONY: run

run:
	.\.venv\Scripts\python.exe -m streamlit run scripts/app.py --server.address 127.0.0.1 --server.port 8501
