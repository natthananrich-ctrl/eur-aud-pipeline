{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "92f33c54-8bd1-4735-984c-256f6d1206c9",
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "test_pipeline.py\n",
    "----------------\n",
    "Unit tests สำหรับ run_pipeline.py\n",
    "\"\"\"\n",
    "\n",
    "import os\n",
    "import pytest\n",
    "import pandas as pd\n",
    "from project.run_pipeline import run_pipeline\n",
    "from project.utils.config_loader import load_config\n",
    "\n",
    "@pytest.fixture\n",
    "def sample_config():\n",
    "    # โหลด config dev สำหรับทดสอบ\n",
    "    return load_config(env=\"dev\")\n",
    "\n",
    "def test_pipeline_runs_successfully(sample_config):\n",
    "    result = run_pipeline(env=\"dev\")\n",
    "    assert \"best_model\" in result\n",
    "    assert \"metrics\" in result\n",
    "    assert \"drift\" in result\n",
    "\n",
    "def test_pipeline_handles_missing_data(tmp_path, sample_config, monkeypatch):\n",
    "    # สร้างไฟล์ CSV ว่างเพื่อจำลอง error\n",
    "    empty_csv = tmp_path / \"empty.csv\"\n",
    "    pd.DataFrame().to_csv(empty_csv, index=False)\n",
    "\n",
    "    # monkeypatch ให้ config ใช้ไฟล์ว่าง\n",
    "    monkeypatch.setitem(sample_config[\"data\"], \"source_path\", str(empty_csv))\n",
    "\n",
    "    result = run_pipeline(env=\"dev\")\n",
    "    # pipeline ไม่ควรล้ม แต่ best_model อาจเป็น None\n",
    "    assert \"best_model\" in result\n",
    "\n",
    "def test_pipeline_audit_log_created():\n",
    "    # ตรวจสอบว่า audit.log ถูกสร้าง\n",
    "    log_path = \"audit.log\"\n",
    "    assert os.path.exists(log_path)\n",
    "    with open(log_path, \"r\") as f:\n",
    "        logs = f.read()\n",
    "    assert \"pipeline\" in logs\n",
    "    assert \"SUCCESS\" in logs or \"FAIL\" in logs"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
