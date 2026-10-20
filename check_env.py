import subprocess, sys
venv_python = r'E:\HocCode\Python\Learn code cơ bản nâng cao\Khoa Hoc Du Lieu\TrainAI\.venv\Scripts\python.exe'
res = subprocess.run([venv_python, '-c', 'import pandas, numpy, matplotlib, seaborn, plotly, folium, wordcloud, networkx; print("core ok")'], capture_output=True, text=True, timeout=30)
print('stdout:', res.stdout.strip())
print('stderr:', res.stderr[:500] if res.stderr else '')
