{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fb7fd164-27f2-4910-b8e9-b354fc10bad5",
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "logger.py\n",
    "---------\n",
    "Helper สำหรับบันทึก log ลง audit.log\n",
    "\"\"\"\n",
    "\n",
    "import os\n",
    "import datetime\n",
    "\n",
    "class AuditLogger:\n",
    "    def __init__(self, log_path=\"project/logs/audit.log\"):\n",
    "        self.log_path = log_path\n",
    "        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)\n",
    "\n",
    "    def log_event(self, module: str, action: str, status: str, details: str = \"\"):\n",
    "        \"\"\"\n",
    "        บันทึกเหตุการณ์ลง audit.log\n",
    "\n",
    "        Parameters\n",
    "        ----------\n",
    "        module : str\n",
    "            โมดูลที่ทำงาน เช่น 'features', 'models', 'pipeline'\n",
    "        action : str\n",
    "            กิจกรรม เช่น 'train_model', 'generate_features'\n",
    "        status : str\n",
    "            ผลลัพธ์ เช่น 'SUCCESS', 'FAIL', 'WARNING'\n",
    "        details : str\n",
    "            รายละเอียดเพิ่มเติม เช่น metrics, drift result\n",
    "        \"\"\"\n",
    "        timestamp = datetime.datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n",
    "        log_line = f\"[{timestamp}] | {module} | {action} | {status} | {details}\\n\"\n",
    "\n",
    "        with open(self.log_path, \"a\") as f:\n",
    "            f.write(log_line)\n",
    "\n",
    "        print(\"📝 Log saved:\", log_line.strip())"
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
