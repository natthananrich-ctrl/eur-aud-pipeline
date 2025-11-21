{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d369107f-6b37-4c33-88d6-b57b4ec22f8f",
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "config_loader.py\n",
    "----------------\n",
    "Utility สำหรับโหลด config ตาม environment (dev/test/prod)\n",
    "\"\"\"\n",
    "\n",
    "import yaml\n",
    "import os\n",
    "\n",
    "def load_config(env=\"dev\"):\n",
    "    \"\"\"\n",
    "    โหลดไฟล์ config ตาม environment\n",
    "    Args:\n",
    "        env (str): \"dev\", \"test\", หรือ \"prod\"\n",
    "    Returns:\n",
    "        dict: config ที่โหลดจากไฟล์ YAML\n",
    "    \"\"\"\n",
    "    path = f\"project/config/config_{env}.yaml\"\n",
    "    if not os.path.exists(path):\n",
    "        raise FileNotFoundError(f\"Config file not found: {path}\")\n",
    "\n",
    "    with open(path, \"r\") as f:\n",
    "        return yaml.safe_load(f)"
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
