{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7bfd2042-ce4c-48d4-bd02-2ea0001530a9",
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "import time\n",
    "from project.utils.config_loader import load_config\n",
    "\n",
    "class Monitor:\n",
    "    def __init__(self, env=\"dev\", log_path=\"project/logs/audit.log\"):\n",
    "        self.config = load_config(env)\n",
    "        self.log_path = log_path\n",
    "        self.accuracy_threshold = self.config[\"alerts\"].get(\"accuracy_threshold\", 0.85)\n",
    "        self.drift_threshold = self.config[\"alerts\"].get(\"drift_pvalue_threshold\", 0.05)\n",
    "\n",
    "    def tail_log(self):\n",
    "        \"\"\"อ่าน log แบบต่อเนื่อง\"\"\"\n",
    "        with open(self.log_path, \"r\") as f:\n",
    "            f.seek(0, 2)  # ไปท้ายไฟล์\n",
    "            while True:\n",
    "                line = f.readline()\n",
    "                if not line:\n",
    "                    time.sleep(1)\n",
    "                    continue\n",
    "                yield json.loads(line)\n",
    "\n",
    "    def check_alerts(self, log_entry):\n",
    "        \"\"\"ตรวจสอบเงื่อนไขแจ้งเตือน\"\"\"\n",
    "        module = log_entry.get(\"module\")\n",
    "        status = log_entry.get(\"status\")\n",
    "        message = log_entry.get(\"message\")\n",
    "\n",
    "        if \"drift\" in message.lower() and \"True\" in message:\n",
    "            self.notify(f\"🚨 Drift detected in {module}: {message}\")\n",
    "\n",
    "        if \"accuracy\" in message.lower():\n",
    "            acc_value = float(message.split(\"=\")[-1])\n",
    "            if acc_value < self.accuracy_threshold:\n",
    "                self.notify(f\"⚠️ Accuracy below threshold: {acc_value}\")\n",
    "\n",
    "        if status == \"FAIL\":\n",
    "            self.notify(f\"❌ Failure in {module}: {message}\")\n",
    "\n",
    "    def notify(self, msg):\n",
    "        \"\"\"แจ้งเตือน (console/email/webhook)\"\"\"\n",
    "        print(msg)\n",
    "        # TODO: integrate email/Slack/webhook ตาม config"
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
