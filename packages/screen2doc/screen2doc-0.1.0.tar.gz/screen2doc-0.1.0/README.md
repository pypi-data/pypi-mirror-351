# Screen2Doc

Screen2Doc is a Python package that lets you automatically create step-by-step documentation by capturing screenshots and adding annotations.

## Features
- Manual screen capture
- Annotate each step
- Export to Markdown

## Installation
```bash
pip install screen2doc
```

## Usage
```python
from screen2doc import ScreenCapturer, AnnotationManager, Exporter

capturer = ScreenCapturer()
annotator = AnnotationManager()
exporter = Exporter()

step1 = capturer.capture()
annotator.add_annotation(1, "Open Settings")

step2 = capturer.capture()
annotator.add_annotation(2, "Go to Network Settings")

exporter.export_markdown(capturer.get_steps(), annotator.get_all_annotations())
```
