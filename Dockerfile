FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 DEMO_PUBLIC_MODE=1
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY pages ./pages
COPY utils ./utils
COPY assets ./assets
COPY data_public ./data_public
COPY .streamlit ./.streamlit
USER 10001
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=6s --start-period=30s CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8501')+'/_stcore/health',timeout=5)"
CMD ["sh", "-c", "exec python -m streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
