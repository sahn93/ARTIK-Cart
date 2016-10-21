## Dependencies

```
sudo dnf install bluez bluez-libs bluez-libs-devel
pip install -r requirements.txt
npm install
```

## How to run

### Client

```
sudo SERVER="HOST:PORT" python main.py
```

### Server

```
sudo SERVER="HOST:PORT" python liveplot.py
```
