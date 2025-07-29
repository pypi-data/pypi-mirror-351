# EZIDS 🛡️  
**A Lightweight Python Host Intrusion Detection System with GUI**

EZIDS is a simple but functional host-based intrusion detection system (HIDS) built using Python and PyQt6. It monitors selected file paths for unexpected changes and reports suspicious activity using hashing and file watching. This project is designed to be educational, lightweight, and easy to extend or integrate into your own tools.

---

## 🔧 Features

- ✅ Real-time file monitoring
- ✅ Change detection via SHA256 hashing
- ✅ Persistent config and ignore lists
- ✅ GUI interface built with PyQt6
- ✅ Desktop-friendly cross-platform design (Linux-first)
- ✅ Easy install from [TestPyPI](https://test.pypi.org/project/ezids/)

---

## 🚀 Installation

You can install it using pip like this:

```bash
pip install ezids
```

> ⚠️ **Important:** You may also need to manually install `PyQt6` 

```bash
pip install PyQt6
```

You may also need system libraries on some distros:

```bash
sudo apt install libx11-xcb1 libxcb-cursor0 libglu1-mesa
```

---

## 🖥️ Usage

After installation, just run:

```bash
ezids
```

The GUI will open, allowing you to:
- Configure monitored paths in settings(May get errors if you don't do this first.)
- Initialize hash baselines
- Start/stop monitoring
- View event logs
- Customize ignore lists

---

## 🗂️ Project Structure

```
ezids/
├── ezids/
│   ├── main.py         # Entry point
│   ├── gui.py          # PyQt6 GUI
│   ├── ids_core.py     # Monitoring logic
│   └── resources/      # SVG icons for GUI
├── config.json         # Saved config
├── monitor_paths.txt   # Paths to monitor
├── ignore_files.txt    # Glob patterns to ignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🔍 How It Works

1. On **Init**, the app generates SHA256 hashes for files in configured directories.
2. On **Start**, a background thread monitors those directories.
3. When changes are detected, hashes are recomputed and compared.
4. Logs are generated for:
   - Modified files
   - Created/deleted files
   - Ignored paths
5. You can view all events in the GUI log window.

---



---

## 🧪 Developer Notes

Want to install from source?

```bash
git clone https://github.com/nolancoe/ezids.git
cd ezids
pip install .
```

Then run:

```bash
ezids
```

---

## 🛠️ Dependencies

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)
- System: `libx11-xcb1`, `libxcb-cursor0`, `libglu1-mesa` (for Linux Qt)

---

## 🤝 License

MIT License.

---

## ✍️ Author

Made with love and paranoia by **Nolan Coe**  
🐦 [twitter.com/yourhandle]  
🧠 [https://github.com/nolancoe]

---

## 🧱 Future Improvements

- Save/load config profiles
- Email alerts
- Headless (CLI-only) mode
- Signature-based detection
- Integration with systemd or tray icon

---
