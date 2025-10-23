# COPP AHP Tool — Local Server (Windows)

## 1️⃣ Install Python
- Install Python 3.9 or newer from [https://www.python.org/downloads/]
- During installation, tick **Add Python to PATH**.

## 2️⃣ Install Dependencies (Offline)
If your server is offline, download packages on another system:
```bash
pip download -r requirements.txt -d wheels/
```
Copy the `wheels` folder to the server and install:
```bash
pip install wheels\*.whl
```

## 3️⃣ Run the App
Double-click the `start_app.bat` file or run:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 4️⃣ Access the Tool
- On the same PC: http://localhost:8501  
- On another system in LAN: http://<SERVER-IP>:8501

## 5️⃣ Stop the App
Press **Ctrl + C** in the terminal window.
