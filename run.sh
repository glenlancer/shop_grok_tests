#!/bin/bash

python3 -m venv grok_venv
source grok_venv/bin/activate
pip install -r requirements.txt
python shop_grok_tests.py run-all 