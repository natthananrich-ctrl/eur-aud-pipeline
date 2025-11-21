{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b9a5d465-922e-44f2-9b81-fbf789662c0c",
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "test_live_predictor.py\n",
    "----------------------\n",
    "Unit tests สำหรับ live_predictor.py\n",
    "\"\"\"\n",
    "\n",
    "import pytest\n",
    "import pandas as pd\n",
    "from project.live_predictor import LivePredictor\n",
    "from project.utils.config_loader import load_config\n",
    "\n",
    "@pytest.fixture\n",
    "def sample_config():\n",
    "    # โหลด config dev สำหรับทดสอบ\n",
    "    return load_config(env=\"dev\")\n",
    "\n",
    "def test_live_predictor_initialization(sample_config):\n",
    "    predictor = LivePredictor(env=\"dev\")\n",
    "    assert predictor.env == \"dev\"\n",
    "    assert predictor.config == sample_config\n",
    "\n",
    "def test_live_predictor_generate_signal(sample_config, monkeypatch):\n",
    "    predictor = LivePredictor(env=\"dev\")\n",
    "\n",
    "    # จำลอง input data\n",
    "    sample_data = pd.DataFrame({\n",
    "        \"open\": [1.0, 1.1, 1.2],\n",
    "        \"close\": [1.1, 1.2, 1.3],\n",
    "        \"volume\": [100, 200, 150]\n",
    "    })\n",
    "\n",
    "    # monkeypatch ให้โมเดลคืนค่า signal คงที่\n",
    "    class DummyModel:\n",
    "        def predict(self, X):\n",
    "            return [\"BUY\"]\n",
    "\n",
    "    predictor.model = DummyModel()\n",
    "\n",
    "    signal = predictor.generate_signal(sample_data)\n",
    "    assert signal == \"BUY\"\n",
    "\n",
    "def test_live_predictor_handles_error(monkeypatch):\n",
    "    predictor = LivePredictor(env=\"dev\")\n",
    "\n",
    "    # monkeypatch ให้โมเดล raise error\n",
    "    class BrokenModel:\n",
    "        def predict(self, X):\n",
    "            raise ValueError(\"Model failure\")\n",
    "\n",
    "    predictor.model = BrokenModel()\n",
    "\n",
    "    signal = predictor.generate_signal(pd.DataFrame())\n",
    "    # ต้องไม่ล้ม แต่คืนค่า fallback เช่น None หรือ \"HOLD\"\n",
    "    assert signal in [None, \"HOLD\"]"
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
